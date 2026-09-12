// SPDX-License-Identifier: GPL-2.0
/*
 * Static source reconstruction of the GQ5012BF1 HXYTECH CO5300 TinyLCD
 * transport.  Recovered from the stock Android 6.1.115 module, DT and HAL.
 */
#include <linux/compat.h>
#include <linux/delay.h>
#include <linux/fs.h>
#include <linux/gpio.h>
#include <linux/iio/consumer.h>
#include <linux/interrupt.h>
#include <linux/ioctl.h>
#include <linux/kernel.h>
#include <linux/miscdevice.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/of.h>
#include <linux/of_gpio.h>
#include <linux/pinctrl/consumer.h>
#include <linux/slab.h>
#include <linux/spi/spi.h>
#include <linux/timekeeping.h>
#include <linux/uaccess.h>
#include <linux/vmalloc.h>
#include <linux/workqueue.h>

#define TINY_LCD_NAME              "spi_tiny_lcd_co5300"
#define TINY_LCD_MISC_NAME         "tiny_lcd_miscdev"
#define TINY_LCD_FULL_WIDTH        340U
#define TINY_LCD_CROP_WIDTH        320U
#define TINY_LCD_FULL_FRAME        (340U * 340U * 2U)
#define TINY_LCD_CROP_FRAME        (320U * 320U * 2U)
#define TINY_LCD_SPI_HZ            52000000U
#define TINY_LCD_READ_HZ           1000000U
#define TINY_LCD_XFER_BUFFER       4096U
#define TINY_LCD_DELAY_CMD         0x0000fffcU

#define TINY_LCM_IOC_POWER_ENABLE       0x00006b37U
#define TINY_LCM_IOC_POWER_DISABLE      0x00006b38U
#define TINY_LCM_IOC_BL_ENABLE          0x00006b39U
#define TINY_LCM_IOC_BL_DISABLE         0x00006b3aU
#define TINY_LCM_IOC_BL_CONTROL         0x40086b3bU
#define TINY_LCM_IOC_WRITE_FRAME        0x40086b3cU
#define TINY_LCM_IOC_FRAME_STATUS       0xc0086b3dU
#define TINY_LCM_IOC_TP_GESTURE_ENABLE  0x00006b3eU
#define TINY_LCM_IOC_TP_GESTURE_DISABLE 0x00006b3fU
#define TINY_LCM_IOC_POWER_AOD          0x00006b40U
#define TINY_LCM_IOC_FRAME_SIZE         0x40086b41U

extern int yft_tinylcd_device_add(struct spi_driver *driver, int used);
extern int yft_set_tinylcd_device_used(char *name, int used);
extern void tiny_tp_power_contorl(int enable);
extern void tiny_tp_gesture_contorl(int enable);
extern struct spi_driver spi_tiny_lcd_driver;

struct tiny_lcd_init_record {
	u32 command;
	u8 count;
	u8 parameters[23];
};

struct tiny_lcd_frame_size {
	u32 width;
	u32 height;
};

struct tiny_lcd_data {
	struct spi_device *spi;
	int reset_gpio;
	int dc_gpio;
	int en_1v8_gpio;
	int en_2v8_gpio;
	int backlight_gpio;
	int te_gpio;
	u8 *tx_buffer;
	u8 *rx_buffer;
	u8 power_on;
	u8 frame_send_enable;
	u8 frame_send_end;
};

static struct tiny_lcd_data g_data;
static struct delayed_work tiny_lcd_te_work;
static int yft_tiny_lcd_te_irqnum;
static struct pinctrl *stl_pinctrl;
static struct pinctrl_state *stl_spi1_mo_as_spi1_mo;
static struct pinctrl_state *stl_spi1_mo_as_gpio;
static struct pinctrl_state *stl_spi1_mi_as_spi1_mi;
static struct pinctrl_state *stl_spi1_mi_as_gpio;
static struct pinctrl_state *stl_spi1_clk_as_spi1_clk;
static struct pinctrl_state *stl_spi1_clk_as_gpio;
static struct pinctrl_state *stl_spi1_cs_as_spi1_cs;
static struct pinctrl_state *stl_spi1_cs_as_gpio;

int tiny_lcm_number;
static u64 backlight_step;
static u8 pic_from_user[TINY_LCD_FULL_FRAME];
static const void *current_backlight_level;
static u32 pre_framesize;
static DEFINE_MUTEX(buf_lock);
static u64 power_enable_status;
static u8 pre_irq_en;
static u64 backlight_enable_status;
static u64 tiny_lcd_tp_control_status;
static struct tiny_lcd_frame_size framesize = {
	.width = TINY_LCD_FULL_WIDTH,
	.height = TINY_LCD_FULL_WIDTH,
};
static u64 write_frame_status = 1;

#include "gImage_logo.inc"
#include "init_setting.inc"

static __always_inline int tiny_lcd_gpio_output(int gpio, int value)
{
	struct gpio_desc *desc = gpio_to_desc(gpio);

	if (!desc)
		return -EINVAL;
	return gpiod_direction_output_raw(desc, value);
}

static __always_inline void tiny_lcd_select_spi(bool spi_mode)
{
	if (IS_ERR_OR_NULL(stl_pinctrl))
		return;
	pinctrl_select_state(stl_pinctrl, spi_mode ?
			     stl_spi1_mo_as_spi1_mo : stl_spi1_mo_as_gpio);
	pinctrl_select_state(stl_pinctrl, spi_mode ?
			     stl_spi1_mi_as_spi1_mi : stl_spi1_mi_as_gpio);
	pinctrl_select_state(stl_pinctrl, spi_mode ?
			     stl_spi1_clk_as_spi1_clk : stl_spi1_clk_as_gpio);
	pinctrl_select_state(stl_pinctrl, spi_mode ?
			     stl_spi1_cs_as_spi1_cs : stl_spi1_cs_as_gpio);
}

static ssize_t spidev_sync_read_data(u8 command)
{
	struct spi_transfer transfer = { };
	struct spi_message message;
	int ret;

	ret = tiny_lcd_gpio_output(g_data.dc_gpio, 0);
	if (ret)
		return ret;

	g_data.tx_buffer[0] = command;
	g_data.tx_buffer[1] = 0;
	g_data.rx_buffer[0] = 0;
	g_data.rx_buffer[1] = 0;
	transfer.tx_buf = g_data.tx_buffer;
	transfer.rx_buf = g_data.rx_buffer;
	transfer.len = 2;
	transfer.speed_hz = TINY_LCD_READ_HZ;
	spi_message_init(&message);
	spi_message_add_tail(&transfer, &message);
	if (g_data.spi)
		spi_sync(g_data.spi, &message);
	return g_data.rx_buffer[1];
}

static void spidev_sync_write_cmd(u8 command)
{
	struct spi_transfer transfer = { };
	struct spi_message message;
	u8 *buffer;

	if (tiny_lcd_gpio_output(g_data.dc_gpio, 0))
		return;
	buffer = vmalloc(1);
	if (!buffer)
		return;
	*buffer = command;
	transfer.tx_buf = buffer;
	transfer.len = 1;
	transfer.speed_hz = TINY_LCD_SPI_HZ;
	spi_message_init(&message);
	spi_message_add_tail(&transfer, &message);
	if (g_data.spi)
		spi_sync(g_data.spi, &message);
	vfree(buffer);
}

static void spidev_sync_write_data(u8 value)
{
	struct spi_transfer transfer = { };
	struct spi_message message;
	u8 *buffer;

	if (tiny_lcd_gpio_output(g_data.dc_gpio, 1))
		return;
	buffer = vmalloc(1);
	if (!buffer)
		return;
	*buffer = value;
	transfer.tx_buf = buffer;
	transfer.len = 1;
	transfer.speed_hz = TINY_LCD_SPI_HZ;
	spi_message_init(&message);
	spi_message_add_tail(&transfer, &message);
	if (g_data.spi)
		spi_sync(g_data.spi, &message);
	vfree(buffer);
}

static void tiny_lcd_set_window(u32 width, size_t len)
{
	u16 first;
	u16 last;

	if (width == TINY_LCD_CROP_WIDTH && len == TINY_LCD_CROP_FRAME) {
		first = 10;
		last = 329;
	} else if (width == TINY_LCD_FULL_WIDTH && len == TINY_LCD_FULL_FRAME) {
		first = 0;
		last = 339;
	} else {
		return;
	}

	spidev_sync_write_cmd(0x2a);
	spidev_sync_write_data(first >> 8);
	spidev_sync_write_data(first & 0xff);
	spidev_sync_write_data(last >> 8);
	spidev_sync_write_data(last & 0xff);
	spidev_sync_write_cmd(0x2b);
	spidev_sync_write_data(first >> 8);
	spidev_sync_write_data(first & 0xff);
	spidev_sync_write_data(last >> 8);
	spidev_sync_write_data(last & 0xff);
	spidev_sync_write_cmd(0x2c);
}

static void spidev_sync_write_multi_data(const u8 *data, size_t len)
{
	struct spi_transfer transfer = { };
	struct spi_message message;
	u8 *buffer;

	if (current_backlight_level != data) {
		spidev_sync_write_cmd(0x51);
		spidev_sync_write_data((u8)backlight_step);
		spidev_sync_write_cmd(0x2c);
		current_backlight_level = data;
	}
	if (pre_framesize != framesize.width) {
		tiny_lcd_set_window(framesize.width, len);
		pre_framesize = framesize.width;
	}
	if (tiny_lcd_gpio_output(g_data.dc_gpio, 1))
		return;

	mutex_lock(&buf_lock);
	buffer = vmalloc(len);
	if (!buffer) {
		mutex_unlock(&buf_lock);
		return;
	}
	memcpy(buffer, data, len);
	transfer.tx_buf = buffer;
	transfer.len = len;
	transfer.speed_hz = TINY_LCD_SPI_HZ;
	spi_message_init(&message);
	spi_message_add_tail(&transfer, &message);
	if (g_data.spi)
		spi_sync(g_data.spi, &message);
	vfree(buffer);
	mutex_unlock(&buf_lock);
}

static __always_inline void tiny_lcd_run_init(void)
{
	unsigned int i;
	unsigned int j;

	for (i = 0; i < ARRAY_SIZE(init_setting); i++) {
		if (init_setting[i].command == TINY_LCD_DELAY_CMD) {
			mdelay(init_setting[i].count);
			continue;
		}
		spidev_sync_write_cmd((u8)init_setting[i].command);
		for (j = 0; j < init_setting[i].count; j++)
			spidev_sync_write_data(init_setting[i].parameters[j]);
	}
}

static void tiny_lcd_power_enable_func(unsigned long enable)
{
	if (!enable) {
		if (g_data.power_on != 1)
			return;
		if (!pre_irq_en) {
			disable_irq(yft_tiny_lcd_te_irqnum);
			pre_irq_en = 1;
		}
		backlight_step = 0;
		current_backlight_level = NULL;
		spidev_sync_write_cmd(0x28);
		mdelay(20);
		spidev_sync_write_cmd(0x10);
		mdelay(220);
		tiny_lcd_gpio_output(g_data.reset_gpio, 0);
		mdelay(20);
		tiny_lcd_gpio_output(g_data.en_2v8_gpio, 0);
		mdelay(20);
		tiny_lcd_gpio_output(g_data.en_1v8_gpio, 0);
		mdelay(20);
		tiny_lcd_select_spi(false);
		g_data.power_on = 0;
		return;
	}

	if (g_data.power_on == 1) {
		g_data.frame_send_end = 1;
		return;
	}

	tiny_lcd_select_spi(true);
	mdelay(20);
	tiny_lcd_gpio_output(g_data.en_1v8_gpio, 1);
	mdelay(20);
	tiny_lcd_gpio_output(g_data.en_2v8_gpio, 1);
	mdelay(20);
	tiny_lcd_gpio_output(g_data.reset_gpio, 1);
	mdelay(15);
	tiny_lcd_gpio_output(g_data.reset_gpio, 0);
	mdelay(30);
	tiny_lcd_gpio_output(g_data.reset_gpio, 1);
	mdelay(120);
	tiny_lcd_run_init();
	g_data.power_on = 1;
	g_data.frame_send_end = 1;
	if (pre_irq_en) {
		enable_irq(yft_tiny_lcd_te_irqnum);
		pre_irq_en = 0;
	}
}

static void tiny_lcd_te_work_handler(struct work_struct *work)
{
	size_t len;

	(void)work;
	if (write_frame_status != 3)
		return;
	if (g_data.frame_send_enable == 1 && g_data.frame_send_end != 0) {
		len = framesize.width == TINY_LCD_CROP_WIDTH ?
			TINY_LCD_CROP_FRAME : TINY_LCD_FULL_FRAME;
		spidev_sync_write_multi_data(gImage_logo, len);
	}
	write_frame_status = 1;
}

static irqreturn_t yft_tiny_lcd_te_isr(int irq, void *dev_id)
{
	(void)irq;
	(void)dev_id;
	if (g_data.frame_send_enable == 1)
		queue_delayed_work_on(WORK_CPU_UNBOUND, system_wq,
				      &tiny_lcd_te_work, 0);
	return IRQ_HANDLED;
}

static ssize_t tiny_lcd_power_enable_show(struct device_driver *driver,
					  char *buf)
{
	return scnprintf(buf, PAGE_SIZE, "%llu\n", power_enable_status);
}

static ssize_t tiny_lcd_power_enable_store(struct device_driver *driver,
					   const char *buf, size_t count)
{
	u64 value;

	if (kstrtoull(buf, 10, &value))
		return -EINVAL;
	if (value > 1)
		return count;
	power_enable_status = value;
	tiny_lcd_power_enable_func(value);
	return count;
}

static ssize_t tiny_lcd_bl_enable_show(struct device_driver *driver, char *buf)
{
	return scnprintf(buf, PAGE_SIZE, "%llu\n", backlight_enable_status);
}

static ssize_t tiny_lcd_bl_enable_store(struct device_driver *driver,
					const char *buf, size_t count)
{
	u64 value;

	if (kstrtoull(buf, 10, &value))
		return -EINVAL;
	if (value > 1)
		return count;
	backlight_enable_status = value;
	backlight_step = value;
	return count;
}

static ssize_t tiny_lcd_backlight_control_show(struct device_driver *driver,
					       char *buf)
{
	return scnprintf(buf, PAGE_SIZE, "%llu\n", backlight_step);
}

static ssize_t tiny_lcd_backlight_control_store(struct device_driver *driver,
						const char *buf, size_t count)
{
	u64 value;

	if (kstrtoull(buf, 10, &value))
		return -EINVAL;
	backlight_step = value;
	return count;
}

static ssize_t tiny_lcd_write_frame_show(struct device_driver *driver,
					 char *buf)
{
	return scnprintf(buf, PAGE_SIZE, "%llu\n", write_frame_status);
}

static ssize_t tiny_lcd_write_frame_store(struct device_driver *driver,
					  const char *buf, size_t count)
{
	u64 value;

	if (kstrtoull(buf, 10, &value))
		return -EINVAL;
	if (value != 1)
		return count;
	memcpy(pic_from_user, gImage_logo, TINY_LCD_FULL_FRAME);
	spidev_sync_write_multi_data(gImage_logo, TINY_LCD_FULL_FRAME);
	if (write_frame_status == TINY_LCD_FULL_FRAME)
		write_frame_status = 1;
	else if ((s64)write_frame_status < 0)
		write_frame_status = 2;
	else
		write_frame_status = 0;
	return count;
}

static ssize_t tiny_lcd_tp_control_show(struct device_driver *driver, char *buf)
{
	return scnprintf(buf, PAGE_SIZE, "%llu\n", tiny_lcd_tp_control_status);
}

static ssize_t tiny_lcd_tp_control_store(struct device_driver *driver,
					const char *buf, size_t count)
{
	u64 value;

	if (kstrtoull(buf, 10, &value))
		return -EINVAL;
	if (value > 1)
		return count;
	tiny_tp_power_contorl(value);
	tiny_lcd_tp_control_status = value;
	return count;
}

static DRIVER_ATTR_RW(tiny_lcd_power_enable);
static DRIVER_ATTR_RW(tiny_lcd_bl_enable);
static DRIVER_ATTR_RW(tiny_lcd_backlight_control);
static DRIVER_ATTR_RW(tiny_lcd_write_frame);
static DRIVER_ATTR_RW(tiny_lcd_tp_control);

static long tiny_lcd_ioctl(struct file *file, unsigned int cmd,
			   unsigned long arg)
{
	void __user *argp = (void __user *)arg;
	size_t missing;
	u64 value;

	switch (cmd) {
	case TINY_LCM_IOC_POWER_ENABLE:
		tiny_lcd_power_enable_func(1);
		break;
	case TINY_LCM_IOC_POWER_DISABLE:
		tiny_lcd_power_enable_func(0);
		break;
	case TINY_LCM_IOC_BL_ENABLE:
		g_data.frame_send_enable = 1;
		tiny_lcd_power_enable_func(2);
		break;
	case TINY_LCM_IOC_BL_DISABLE:
		g_data.frame_send_enable = 0;
		tiny_lcd_power_enable_func(0);
		break;
	case TINY_LCM_IOC_BL_CONTROL:
		if (copy_from_user(&value, argp, sizeof(value)))
			return -1;
		backlight_step = value;
		break;
	case TINY_LCM_IOC_WRITE_FRAME:
		write_frame_status = 2;
		if (g_data.frame_send_enable != 1) {
			write_frame_status = 3;
			break;
		}
		missing = copy_from_user(gImage_logo, argp,
					 TINY_LCD_FULL_FRAME);
		if (missing) {
			memset(gImage_logo + TINY_LCD_FULL_FRAME - missing, 0,
			       missing);
			write_frame_status = 3;
			return -1;
		}
		if (!g_data.frame_send_end)
			spidev_sync_write_multi_data(gImage_logo,
						      TINY_LCD_FULL_FRAME);
		write_frame_status = 3;
		break;
	case TINY_LCM_IOC_FRAME_STATUS:
		if (copy_to_user(argp, &write_frame_status,
				 sizeof(write_frame_status)))
			return -1;
		break;
	case TINY_LCM_IOC_TP_GESTURE_ENABLE:
		tiny_tp_power_contorl(1);
		mdelay(10);
		tiny_tp_gesture_contorl(1);
		break;
	case TINY_LCM_IOC_TP_GESTURE_DISABLE:
		tiny_tp_gesture_contorl(0);
		break;
	case TINY_LCM_IOC_POWER_AOD:
		tiny_lcd_power_enable_func(2);
		g_data.frame_send_end = 0;
		break;
	case TINY_LCM_IOC_FRAME_SIZE:
		if (copy_from_user(&framesize, argp, sizeof(framesize)))
			return -1;
		break;
	default:
		break;
	}
	return 0;
}

#ifdef CONFIG_COMPAT
static long tiny_lcd_compat_ioctl(struct file *file, unsigned int cmd,
				  unsigned long arg)
{
	if (!file->f_op || !file->f_op->unlocked_ioctl)
		return -ENOTTY;
	return file->f_op->unlocked_ioctl(file, cmd,
					  (unsigned long)compat_ptr(arg));
}
#endif

static int tiny_lcd_open(struct inode *inode, struct file *file)
{
	return 0;
}

static int tiny_lcd_release(struct inode *inode, struct file *file)
{
	return 0;
}

static const struct file_operations tiny_lcd_fops = {
	.owner = THIS_MODULE,
	.open = tiny_lcd_open,
	.release = tiny_lcd_release,
	.unlocked_ioctl = tiny_lcd_ioctl,
#ifdef CONFIG_COMPAT
	.compat_ioctl = tiny_lcd_compat_ioctl,
#endif
};

static struct miscdevice tiny_lcd_miscdev = {
	.minor = MISC_DYNAMIC_MINOR,
	.name = TINY_LCD_MISC_NAME,
	.fops = &tiny_lcd_fops,
};

static __always_inline int tiny_lcd_request_gpio(struct device_node *node,
						 const char *property,
						 const char *label,
						 int initial, int *gpio)
{
	int ret;

	*gpio = of_get_named_gpio(node, property, 0);
	if (*gpio < 0)
		return *gpio;
	ret = gpio_request(*gpio, label);
	if (ret)
		return ret;
	return tiny_lcd_gpio_output(*gpio, initial);
}

static __always_inline int tiny_lcd_get_pinctrl(struct spi_device *spi)
{
#define LOOKUP_STATE(field, name) do { \
	field = pinctrl_lookup_state(stl_pinctrl, name); \
	if (IS_ERR(field)) return PTR_ERR(field); \
} while (0)
	stl_pinctrl = devm_pinctrl_get(&spi->dev);
	if (IS_ERR(stl_pinctrl))
		return PTR_ERR(stl_pinctrl);
	LOOKUP_STATE(stl_spi1_mo_as_spi1_mo, "stl_spi1_mo_as_spi1_mo");
	LOOKUP_STATE(stl_spi1_mo_as_gpio, "stl_spi1_mo_as_gpio");
	LOOKUP_STATE(stl_spi1_mi_as_spi1_mi, "stl_spi1_mi_as_spi1_mi");
	LOOKUP_STATE(stl_spi1_mi_as_gpio, "stl_spi1_mi_as_gpio");
	LOOKUP_STATE(stl_spi1_clk_as_spi1_clk, "stl_spi1_clk_as_spi1_clk");
	LOOKUP_STATE(stl_spi1_clk_as_gpio, "stl_spi1_clk_as_gpio");
	LOOKUP_STATE(stl_spi1_cs_as_spi1_cs, "stl_spi1_cs_as_spi1_cs");
	LOOKUP_STATE(stl_spi1_cs_as_gpio, "stl_spi1_cs_as_gpio");
#undef LOOKUP_STATE
	return 0;
}

static __always_inline int tiny_lcd_get_sensor_id(struct spi_device *spi)
{
	struct iio_channel *channel;
	int value;
	int ret;

	channel = iio_channel_get(&spi->dev, "tiny_lcd_adc");
	if (IS_ERR(channel))
		return PTR_ERR(channel);
	ret = iio_read_channel_processed(channel, &value);
	iio_channel_release(channel);
	if (ret < 0)
		return ret;
	if (value < 451 || value > 999)
		return -ENODEV;
	return 0;
}

static int spi_probe(struct spi_device *spi)
{
	struct device_node *node = spi->dev.of_node;
	u64 id0 = 0;
	u64 id1 = 0;
	ktime_t started;
	struct timespec64 elapsed;
	bool irq_requested = false;
	int ret;
	int i;

	memset(&g_data, 0, sizeof(g_data));
	g_data.reset_gpio = -1;
	g_data.dc_gpio = -1;
	g_data.en_1v8_gpio = -1;
	g_data.en_2v8_gpio = -1;
	g_data.backlight_gpio = -1;
	g_data.te_gpio = -1;
	g_data.spi = spi;
	spi->mode = SPI_MODE_3;
	spi->bits_per_word = 8;
	g_data.tx_buffer = kmalloc(TINY_LCD_XFER_BUFFER, GFP_KERNEL);
	g_data.rx_buffer = kmalloc(TINY_LCD_XFER_BUFFER, GFP_KERNEL);
	if (!g_data.tx_buffer || !g_data.rx_buffer) {
		ret = -ENOMEM;
		goto err_cleanup;
	}

	ret = tiny_lcd_request_gpio(node, "tiny_lcd,reset-gpio",
				    "tiny_lcd_reset", 0, &g_data.reset_gpio);
	if (ret)
		goto err_cleanup;
	ret = tiny_lcd_request_gpio(node, "tiny_lcd,en-1v8-gpio",
				    "tiny_lcd_en_1v8", 0, &g_data.en_1v8_gpio);
	if (ret)
		goto err_cleanup;
	ret = tiny_lcd_request_gpio(node, "tiny_lcd,dc-ctrl-gpio",
				    "tiny_lcd_dc", 0, &g_data.dc_gpio);
	if (ret)
		goto err_cleanup;
	ret = tiny_lcd_request_gpio(node, "tiny_lcd,en-2v8-gpio",
				    "tiny_lcd_en_2v8", 0, &g_data.en_2v8_gpio);
	if (ret)
		goto err_cleanup;
	ret = tiny_lcd_request_gpio(node, "tiny_lcd,backlight_gpio",
				    "tiny_lcd_backlight", 0,
				    &g_data.backlight_gpio);
	if (ret)
		goto err_cleanup;
	g_data.te_gpio = of_get_named_gpio(node, "tiny_lcd,te_gpio", 0);
	if (g_data.te_gpio < 0) {
		ret = g_data.te_gpio;
		goto err_cleanup;
	}
	ret = gpio_request(g_data.te_gpio, "tiny_lcd_te_gpio");
	if (ret)
		goto err_cleanup;
	ret = gpiod_direction_input(gpio_to_desc(g_data.te_gpio));
	if (ret)
		goto err_cleanup;

	ret = tiny_lcd_get_pinctrl(spi);
	if (ret) {
		dev_err(&spi->dev, "failed to obtain TinyLCD pinctrl: %d\n", ret);
		goto err_cleanup;
	}
	tiny_lcd_select_spi(true);
	mdelay(20);
	tiny_lcd_gpio_output(g_data.en_1v8_gpio, 1);
	mdelay(20);
	tiny_lcd_gpio_output(g_data.en_2v8_gpio, 1);
	mdelay(20);
	tiny_lcd_gpio_output(g_data.reset_gpio, 1);
	mdelay(15);
	tiny_lcd_gpio_output(g_data.reset_gpio, 0);
	mdelay(30);
	tiny_lcd_gpio_output(g_data.reset_gpio, 1);
	mdelay(120);

	ret = tiny_lcd_get_sensor_id(spi);
	if (ret)
		goto err_cleanup;
	for (i = 0; i < 3 && !id0; i++)
		id0 = spidev_sync_read_data(0xda);
	for (i = 0; i < 3 && !id1; i++)
		id1 = spidev_sync_read_data(0xdb);
	if (id0 != 0x33) {
		ret = -ENODEV;
		goto err_cleanup;
	}
	if (id1 == 0x11)
		tiny_lcm_number = 1;
	else if (id1 == 0x10)
		tiny_lcm_number = 2;

	yft_tiny_lcd_te_irqnum = gpiod_to_irq(gpio_to_desc(g_data.te_gpio));
	if (yft_tiny_lcd_te_irqnum < 0) {
		ret = yft_tiny_lcd_te_irqnum;
		goto err_cleanup;
	}
	ret = request_threaded_irq(yft_tiny_lcd_te_irqnum,
				   yft_tiny_lcd_te_isr, NULL,
				   IRQF_TRIGGER_FALLING, "tiny_lcd_te", NULL);
	if (ret) {
		/* Stock releases the mapped IRQ on this failure path. */
		free_irq(yft_tiny_lcd_te_irqnum, NULL);
		goto err_cleanup;
	}
	irq_requested = true;

	tiny_lcd_run_init();
	backlight_step = 255;
	started = ktime_get_boottime();
	memcpy(pic_from_user, gImage_logo, TINY_LCD_FULL_FRAME);
	spidev_sync_write_multi_data(pic_from_user, TINY_LCD_FULL_FRAME);
	elapsed = ns_to_timespec64(ktime_to_ns(ktime_sub(ktime_get_boottime(),
							    started)));
	pr_info("%s: initial frame %lld.%09ld\n", TINY_LCD_NAME,
		(long long)elapsed.tv_sec, elapsed.tv_nsec);
	mdelay(100);

	INIT_DELAYED_WORK(&tiny_lcd_te_work, tiny_lcd_te_work_handler);
	ret = driver_create_file(&spi_tiny_lcd_driver.driver,
				 &driver_attr_tiny_lcd_power_enable);
	if (!ret)
		ret = driver_create_file(&spi_tiny_lcd_driver.driver,
				 &driver_attr_tiny_lcd_bl_enable);
	if (!ret)
		ret = driver_create_file(&spi_tiny_lcd_driver.driver,
				 &driver_attr_tiny_lcd_backlight_control);
	if (!ret)
		ret = driver_create_file(&spi_tiny_lcd_driver.driver,
				 &driver_attr_tiny_lcd_write_frame);
	if (!ret)
		ret = driver_create_file(&spi_tiny_lcd_driver.driver,
				 &driver_attr_tiny_lcd_tp_control);
	if (ret)
		pr_err("%s: driver attribute creation failed: %d\n",
		       TINY_LCD_NAME, ret);

	ret = misc_register(&tiny_lcd_miscdev);
	if (ret)
		pr_err("%s: misc register failed: %d\n", TINY_LCD_NAME, ret);
	g_data.power_on = 1;
	g_data.frame_send_enable = 1;
	g_data.frame_send_end = 1;
	yft_set_tinylcd_device_used(TINY_LCD_NAME, 1);
	return 0;

err_cleanup:
	if (irq_requested)
		free_irq(yft_tiny_lcd_te_irqnum, NULL);
	if (g_data.en_1v8_gpio >= 0)
		gpio_free(g_data.en_1v8_gpio);
	if (g_data.en_2v8_gpio >= 0)
		gpio_free(g_data.en_2v8_gpio);
	if (g_data.backlight_gpio >= 0)
		gpio_free(g_data.backlight_gpio);
	if (g_data.dc_gpio >= 0)
		gpio_free(g_data.dc_gpio);
	if (g_data.te_gpio >= 0)
		gpio_free(g_data.te_gpio);
	if (g_data.reset_gpio >= 0)
		gpio_free(g_data.reset_gpio);
	kvfree(g_data.rx_buffer);
	kvfree(g_data.tx_buffer);
	return ret;
}

static void spi_remove(struct spi_device *spi)
{
	misc_deregister(&tiny_lcd_miscdev);
}

static const struct of_device_id spidev_dt_ids[] = {
	{ .compatible = "hxytech, spi_tiny_lcd" },
	{ }
};
MODULE_DEVICE_TABLE(of, spidev_dt_ids);

static const struct spi_device_id tiny_lcd_spi_ids[] = {
	{ "SSD1317", 0 },
	{ }
};
MODULE_DEVICE_TABLE(spi, tiny_lcd_spi_ids);

struct spi_driver spi_tiny_lcd_driver = {
	.driver = {
		.name = TINY_LCD_NAME,
		.bus = &spi_bus_type,
		.of_match_table = spidev_dt_ids,
	},
	.probe = spi_probe,
	.remove = spi_remove,
	.id_table = tiny_lcd_spi_ids,
};

struct tiny_lcd_boot_tag {
	u32 size;
	u32 tag;
	u32 bootmode;
	u32 boottype;
};

static int __init spi_tiny_lcd_init(void)
{
	struct device_node *node;
	const struct tiny_lcd_boot_tag *tag;
	u32 mode = 0;

	yft_tinylcd_device_add(&spi_tiny_lcd_driver, 0);
	node = of_find_node_by_path("/chosen@0");
	if (!node)
		node = of_find_node_by_path("/chosen");
	if (node) {
		tag = of_get_property(node, "atag,boot", NULL);
		if (tag)
			mode = tag->bootmode;
	}
	if (mode == 1 || mode == 5 || mode == 6 || mode == 8 || mode == 9)
		return 0;
	return spi_register_driver(&spi_tiny_lcd_driver);
}

static void __exit spi_tiny_lcd_exit(void)
{
	spi_unregister_driver(&spi_tiny_lcd_driver);
}

module_init(spi_tiny_lcd_init);
module_exit(spi_tiny_lcd_exit);

MODULE_AUTHOR("wangdong, <wangdong@agenewtech.com>");
MODULE_DESCRIPTION("SSD1317, OEL Display Module, QG-9696TSWXG04 VER B, 4-wire I SPI, 8bit 1-data-line");
MODULE_LICENSE("GPL v2");
MODULE_VERSION("v0.01");
