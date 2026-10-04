// SPDX-License-Identifier: GPL-2.0
/*
 * GQ5012BF1 rear "TinyLCD" driver: HXYTECH/CO5300-class 340x340 RGB565 panel on
 * a MediaTek SPI bus with a TE interrupt and a misc-device frame ABI.
 *
 * Source reconstruction of the shipped vendor_dlkm/spi_tiny_co5300_lcd.ko
 * (SHA-256 39eecad8254c2fc69f9c8d52902b443b3adc64c79c4c6a529af19b4b1f2a9742).
 *
 * Every log statement in the stock module passes __func__ and __LINE__ of the
 * original (lost) source file.  The original line numbers are recovered from
 * the immediate operands in the shipped object and pinned below with #line so
 * that the reconstruction reproduces the stock code bytes.  #line has no other
 * semantic effect.
 */
#include <linux/compat.h>
#include <linux/delay.h>
#include <linux/fs.h>
#include <linux/gpio.h>
#include <linux/iio/consumer.h>
#include <linux/iio/iio.h>
#include <linux/interrupt.h>
#include <linux/kernel.h>
#include <linux/miscdevice.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/of.h>
#include <linux/of_gpio.h>
#include <linux/pinctrl/consumer.h>
#include <linux/regulator/consumer.h>
#include <linux/slab.h>
#include <linux/spi/spi.h>
#include <linux/timekeeping.h>
#include <linux/uaccess.h>
#include <linux/vmalloc.h>
#include <linux/workqueue.h>

#define TINY_LCD_TAG "tiny_lcd_co5300"
#define TINY_LCD_INFO(fmt, ...) \
	pr_info(TINY_LCD_TAG "[%s %d] " fmt, __func__, __LINE__, ##__VA_ARGS__)
#define TINY_LCD_ERR(fmt, ...) \
	pr_err(TINY_LCD_TAG "[%s %d]error: " fmt, __func__, __LINE__, ##__VA_ARGS__)

#define TINY_LCD_BUFSIZ		4096
#define TINY_LCD_SPI_HZ		52000000
#define TINY_LCD_READ_HZ	1000000
#define REGFLAG_DELAY		0xFFFC

#define TINY_LCM_IOC_MAGIC		'k'
#define TINY_LCM_IOC_POWER_ENABLE	_IO(TINY_LCM_IOC_MAGIC, 0x37)
#define TINY_LCM_IOC_POWER_DISABLE	_IO(TINY_LCM_IOC_MAGIC, 0x38)
#define TINY_LCM_IOC_BL_ENABLE		_IO(TINY_LCM_IOC_MAGIC, 0x39)
#define TINY_LCM_IOC_BL_DISABLE		_IO(TINY_LCM_IOC_MAGIC, 0x3a)
#define TINY_LCM_IOC_BL_CONTROL		_IOW(TINY_LCM_IOC_MAGIC, 0x3b, long)
#define TINY_LCM_IOC_WRITE_FRAME	_IOW(TINY_LCM_IOC_MAGIC, 0x3c, long)
#define TINY_LCM_IOC_FRAME_STATUS	_IOWR(TINY_LCM_IOC_MAGIC, 0x3d, long)
#define TINY_LCM_IOC_TP_GESTURE_ENABLE	_IO(TINY_LCM_IOC_MAGIC, 0x3e)
#define TINY_LCM_IOC_TP_GESTURE_DISABLE	_IO(TINY_LCM_IOC_MAGIC, 0x3f)
#define TINY_LCM_IOC_POWER_AOD		_IO(TINY_LCM_IOC_MAGIC, 0x40)
#define TINY_LCM_IOC_FRAME_SIZE		_IOW(TINY_LCM_IOC_MAGIC, 0x41, long)

/* Providers: yft_devinfo (registry) and hynitron (rear touch). */
extern int yft_tinylcd_device_add(struct spi_driver *driver, int used);
extern int yft_set_tinylcd_device_used(char *name, int used);
extern void tiny_tp_power_contorl(int enable);
extern void tiny_tp_gesture_contorl(int enable);

struct tiny_lcd_init_record {
	unsigned int command;
	unsigned char count;
	unsigned char parameters[23];
};

struct tiny_lcd_framesize {
	int width;
	int height;
};

struct tag_bootmode {
	u32 size;
	u32 tag;
	u32 bootmode;
	u32 boottype;
};

/*
 * Stock: clang splits this static aggregate into g_data.0 .. g_data.13
 * (fields 9 and 12 are never referenced and vanish).
 */
struct tiny_lcd_data {
	struct spi_device *spi;		/* 0 */
	int reset_gpio;			/* 1 */
	int dc_ctrl_gpio;		/* 2 */
	int en_1v8_gpio;		/* 3 */
	int en_2v8_gpio;		/* 4 */
	int bl_ctrl_gpio;		/* 5 */
	int te_gpio;			/* 6 */
	const u8 *tx_buffer;		/* 7 */
	u8 *rx_buffer;			/* 8 */
	u32 speed_hz;			/* 9: written, never read */
	u8 power_on;			/* 10 */
	u8 frame_send_enable;		/* 11 */
	u8 users;			/* 12: written, never read */
	u8 frame_send_end;		/* 13 */
};

int tiny_lcm_number;
static unsigned long backlight_step;
static struct delayed_work tiny_lcd_te_work;
static int yft_tiny_lcd_te_irqnum;
static struct tiny_lcd_data g_data;

static struct pinctrl *stl_pinctrl;
static struct pinctrl_state *stl_spi1_mo_as_spi1_mo;
static struct pinctrl_state *stl_spi1_mo_as_gpio;
static struct pinctrl_state *stl_spi1_mi_as_spi1_mi;
static struct pinctrl_state *stl_spi1_mi_as_gpio;
static struct pinctrl_state *stl_spi1_clk_as_spi1_clk;
static struct pinctrl_state *stl_spi1_clk_as_gpio;
static struct pinctrl_state *stl_spi1_cs_as_spi1_cs;
static struct pinctrl_state *stl_spi1_cs_as_gpio;

#include "gImage_logo.inc"
static u8 pic_from_user[340 * 340 * 2];

#include "init_setting.inc"

struct spi_driver spi_tiny_lcd_driver;

static unsigned long current_backlight_level;
static unsigned int pre_framesize;
static struct tiny_lcd_framesize framesize = { 340, 340 };
static struct mutex buf_lock;	/* stock: zero-initialised, never mutex_init()ed */

static ssize_t spidev_sync(struct spi_message *message)
{
	int status;
	struct spi_device *spi = g_data.spi;

	if (spi == NULL)
		status = -ESHUTDOWN;
	else
		status = spi_sync(spi, message);

	if (status == 0)
		status = message->actual_length;

	return status;
}

static inline ssize_t spidev_sync_read(size_t len)
{
	struct spi_transfer t = {
		.tx_buf = g_data.tx_buffer,
		.rx_buf = g_data.rx_buffer,
		.len = len,
		.speed_hz = TINY_LCD_READ_HZ,
	};
	struct spi_message m;

	spi_message_init(&m);
	spi_message_add_tail(&t, &m);
	return spidev_sync(&m);
}

static inline ssize_t spidev_sync_write(size_t len)
{
	struct spi_message m;
	struct spi_transfer t = {
		.tx_buf = g_data.tx_buffer,
		.len = len,
		.speed_hz = TINY_LCD_SPI_HZ,
	};
	u8 *buf;
	ssize_t status;

	buf = vmalloc(len);
	if (!buf)
#line 98
		printk("vmalloc error! (%s,%d)  error=%d\n", __func__, __LINE__, ENOMEM);
	memcpy(buf, g_data.tx_buffer, len);
	t.tx_buf = buf;
	spi_message_init(&m);
	spi_message_add_tail(&t, &m);
	status = spidev_sync(&m);
	vfree(buf);
	return status;
}

static void spidev_sync_write_cmd(u8 cmd)
{
	if (gpio_direction_output(g_data.dc_ctrl_gpio, 0)) {
#line 97
		TINY_LCD_ERR("[GPIO]set_direction for dc_ctrl gpio failed");
		return;
	}
	g_data.tx_buffer = &cmd;
	spidev_sync_write(1);
}

static void spidev_sync_write_data(u8 data)
{
	if (gpio_direction_output(g_data.dc_ctrl_gpio, 1)) {
#line 115
		TINY_LCD_ERR("[GPIO]set_direction for dc_ctrl gpio failed");
		return;
	}
	g_data.tx_buffer = &data;
	spidev_sync_write(1);
}

static void spidev_sync_write_multi_data(const u8 *data, size_t len)
{
	int status;

	if (current_backlight_level != backlight_step) {
#line 154
		TINY_LCD_INFO("spidev_sync_write_multi_data [%ld,%ld] \n", backlight_step, current_backlight_level);
		spidev_sync_write_cmd(0x51);
		spidev_sync_write_data(backlight_step);
		spidev_sync_write_cmd(0x2C);
		current_backlight_level = backlight_step;
	}

	if (pre_framesize != framesize.width) {
#line 163
		TINY_LCD_INFO("spidev_sync_write_multi_data [%d,%d] \n", pre_framesize, framesize.width);
		if (len == 320 * 320 * 2 && framesize.width == 320) {
			spidev_sync_write_cmd(0x2A);
			spidev_sync_write_data(0x00);
			spidev_sync_write_data(0x0A);
			spidev_sync_write_data(0x01);
			spidev_sync_write_data(0x49);
			spidev_sync_write_cmd(0x2B);
			spidev_sync_write_data(0x00);
			spidev_sync_write_data(0x0A);
			spidev_sync_write_data(0x01);
			spidev_sync_write_data(0x49);
			spidev_sync_write_cmd(0x2C);
		} else if (len == 340 * 340 * 2 && framesize.width == 340) {
			spidev_sync_write_cmd(0x2A);
			spidev_sync_write_data(0x00);
			spidev_sync_write_data(0x00);
			spidev_sync_write_data(0x01);
			spidev_sync_write_data(0x53);
			spidev_sync_write_cmd(0x2B);
			spidev_sync_write_data(0x00);
			spidev_sync_write_data(0x00);
			spidev_sync_write_data(0x01);
			spidev_sync_write_data(0x53);
			spidev_sync_write_cmd(0x2C);
		} else {
#line 169
			TINY_LCD_ERR("len=%zu, framesize=%d  is fail\n", len, framesize.width);
		}
		pre_framesize = framesize.width;
	}

	if (gpio_direction_output(g_data.dc_ctrl_gpio, 1)) {
#line 177
		TINY_LCD_ERR("[GPIO]set_direction for dc_ctrl gpio failed");
		return;
	}

	mutex_lock(&buf_lock);
	g_data.tx_buffer = data;
	status = spidev_sync_write(len);
	if (status < 0)
#line 185
		TINY_LCD_ERR("SPI transfer timed out");
	mutex_unlock(&buf_lock);
}

static ssize_t spidev_sync_read_data(u8 cmd)
{
	ssize_t ret;
	u8 *rx;

	ret = gpio_direction_output(g_data.dc_ctrl_gpio, 0);
	if (ret) {
#line 200
		TINY_LCD_ERR("[GPIO]set_direction for dc_ctrl gpio failed");
		return ret;
	}
	g_data.tx_buffer = &cmd;
	spidev_sync_read(2);
	rx = g_data.rx_buffer;
#line 208
		TINY_LCD_INFO("rx_data=%d,%d,\n", rx[0], rx[1]);
	return rx[1];
}

static int stl_parse_dt(void)
{
	struct device_node *np = g_data.spi->dev.of_node;
	int ret;

#line 218
	TINY_LCD_INFO("entry\n");
	g_data.reset_gpio = of_get_named_gpio(np, "tiny_lcd,reset-gpio", 0);
	g_data.en_1v8_gpio = of_get_named_gpio(np, "tiny_lcd,en-1v8-gpio", 0);
	g_data.en_2v8_gpio = of_get_named_gpio(np, "tiny_lcd,en-2v8-gpio", 0);
	g_data.dc_ctrl_gpio = of_get_named_gpio(np, "tiny_lcd,dc-ctrl-gpio", 0);
	g_data.bl_ctrl_gpio = of_get_named_gpio(np, "tiny_lcd,backlight_gpio", 0);
	g_data.te_gpio = of_get_named_gpio(np, "tiny_lcd,te_gpio", 0);
#line 249
	TINY_LCD_INFO("entry 111\n");

	if (gpio_is_valid(g_data.reset_gpio)) {
		ret = gpio_request(g_data.reset_gpio, "tl_reset_gpio");
		if (ret) {
#line 254
			TINY_LCD_ERR("[GPIO]reset gpio request failed");
			goto err_reset_gpio_req;
		}
		ret = gpio_direction_output(g_data.reset_gpio, 0);
		if (ret) {
#line 260
			TINY_LCD_ERR("[GPIO]set_direction for reset gpio failed");
			goto err_reset_gpio_dir;
		}
	}
	if (gpio_is_valid(g_data.en_1v8_gpio)) {
		ret = gpio_request(g_data.en_1v8_gpio, "tl_en_1v8_gpio");
		if (ret) {
#line 267
			TINY_LCD_ERR("[GPIO]en_1v8_gpio gpio request failed");
			goto err_reset_gpio_dir;
		}
		ret = gpio_direction_output(g_data.en_1v8_gpio, 0);
		if (ret) {
#line 273
			TINY_LCD_ERR("[GPIO]set_direction for en_1v8_gpio gpio failed");
			goto err_en_1v8_gpio_dir;
		}
	}
	if (gpio_is_valid(g_data.en_2v8_gpio)) {
		ret = gpio_request(g_data.en_2v8_gpio, "tl_en_2v8_gpio");
		if (ret) {
#line 280
			TINY_LCD_ERR("[GPIO]en_2v8_gpio gpio request failed");
			goto err_reset_gpio_dir;
		}
		ret = gpio_direction_output(g_data.en_2v8_gpio, 0);
		if (ret) {
#line 286
			TINY_LCD_ERR("[GPIO]set_direction for en_2v8_gpio gpio failed");
			goto err_en_2v8_gpio_dir;
		}
	}
	if (gpio_is_valid(g_data.dc_ctrl_gpio)) {
		ret = gpio_request(g_data.dc_ctrl_gpio, "dc_ctrl_gpio");
		if (ret) {
#line 293
			TINY_LCD_ERR("[GPIO]dc_ctrl_gpio gpio request failed");
			goto err_dc_ctrl_gpio_dir;
		}
		ret = gpio_direction_output(g_data.dc_ctrl_gpio, 0);
		if (ret) {
#line 299
			TINY_LCD_ERR("[GPIO]set_direction for dc_ctrl_gpio gpio failed");
			goto err_dc_ctrl_gpio_dir;
		}
	}
	if (gpio_is_valid(g_data.bl_ctrl_gpio)) {
		ret = gpio_request(g_data.bl_ctrl_gpio, "bl_ctrl_gpio");
		if (ret) {
#line 306
			TINY_LCD_ERR("[GPIO]bl_ctrl_gpio gpio request failed");
			goto err_bl_ctrl_gpio_dir;
		}
		ret = gpio_direction_output(g_data.bl_ctrl_gpio, 0);
		if (ret) {
#line 312
			TINY_LCD_ERR("[GPIO]set_direction for bl_ctrl_gpio gpio failed");
			goto err_bl_ctrl_gpio_dir;
		}
	}
	if (gpio_is_valid(g_data.te_gpio)) {
		ret = gpio_request(g_data.te_gpio, "te_gpio");
		if (ret) {
#line 319
			TINY_LCD_ERR("[GPIO]te_gpio gpio request failed");
			goto err_te_gpio_dir;
		}
		ret = gpio_direction_input(g_data.te_gpio);
		if (ret) {
#line 325
			TINY_LCD_ERR("[GPIO]set_direction for te_gpio gpio failed");
			goto err_te_gpio_dir;
		}
	}

#line 330
	TINY_LCD_INFO("entry 222\n");
	stl_pinctrl = devm_pinctrl_get(&g_data.spi->dev);
	if (IS_ERR(stl_pinctrl)) {
		ret = PTR_ERR(stl_pinctrl);
		dev_err(&g_data.spi->dev,
			"stl_pinctrl cannot find pinctrl and ret = (%d)\n", ret);
		return ret;
	}
	stl_spi1_mo_as_spi1_mo = pinctrl_lookup_state(stl_pinctrl, "stl_spi1_mo_as_spi1_mo");
	if (IS_ERR(stl_spi1_mo_as_spi1_mo)) {
		ret = PTR_ERR(stl_spi1_mo_as_spi1_mo);
		dev_err(&g_data.spi->dev, " Cannot find yft stl pinctrl stl_spi1_mo_as_spi1_mo!\n");
		return ret;
	}
	stl_spi1_mo_as_gpio = pinctrl_lookup_state(stl_pinctrl, "stl_spi1_mo_as_gpio");
	if (IS_ERR(stl_spi1_mo_as_gpio)) {
		ret = PTR_ERR(stl_spi1_mo_as_gpio);
		dev_err(&g_data.spi->dev, " Cannot find yft stl pinctrl stl_spi1_mo_as_gpio!\n");
		return ret;
	}
#line 353
	TINY_LCD_INFO("entry 333\n");
	stl_spi1_mi_as_spi1_mi = pinctrl_lookup_state(stl_pinctrl, "stl_spi1_mi_as_spi1_mi");
	if (IS_ERR(stl_spi1_mi_as_spi1_mi)) {
		ret = PTR_ERR(stl_spi1_mi_as_spi1_mi);
		dev_err(&g_data.spi->dev, " Cannot find yft stl pinctrl stl_spi1_mi_as_spi1_mi!\n");
		return ret;
	}
	stl_spi1_mi_as_gpio = pinctrl_lookup_state(stl_pinctrl, "stl_spi1_mi_as_gpio");
	if (IS_ERR(stl_spi1_mi_as_gpio)) {
		ret = PTR_ERR(stl_spi1_mi_as_gpio);
		dev_err(&g_data.spi->dev, " Cannot find yft stl pinctrl stl_spi1_mi_as_gpio!\n");
		return ret;
	}
	stl_spi1_clk_as_spi1_clk = pinctrl_lookup_state(stl_pinctrl, "stl_spi1_clk_as_spi1_clk");
	if (IS_ERR(stl_spi1_clk_as_spi1_clk)) {
		ret = PTR_ERR(stl_spi1_clk_as_spi1_clk);
		dev_err(&g_data.spi->dev, " Cannot find yft stl pinctrl stl_spi1_clk_as_spi1_clk!\n");
		return ret;
	}
	stl_spi1_clk_as_gpio = pinctrl_lookup_state(stl_pinctrl, "stl_spi1_clk_as_gpio");
	if (IS_ERR(stl_spi1_clk_as_gpio)) {
		ret = PTR_ERR(stl_spi1_clk_as_gpio);
		dev_err(&g_data.spi->dev, " Cannot find yft stl pinctrl stl_spi1_clk_as_gpio!\n");
		return ret;
	}
#line 380
	TINY_LCD_INFO("entry 444\n");
	stl_spi1_cs_as_spi1_cs = pinctrl_lookup_state(stl_pinctrl, "stl_spi1_cs_as_spi1_cs");
	if (IS_ERR(stl_spi1_cs_as_spi1_cs)) {
		ret = PTR_ERR(stl_spi1_cs_as_spi1_cs);
		dev_err(&g_data.spi->dev, " Cannot find yft stl pinctrl stl_spi1_cs_as_spi1_cs!\n");
		return ret;
	}
	stl_spi1_cs_as_gpio = pinctrl_lookup_state(stl_pinctrl, "stl_spi1_cs_as_gpio");
	if (IS_ERR(stl_spi1_cs_as_gpio)) {
		ret = PTR_ERR(stl_spi1_cs_as_gpio);
		dev_err(&g_data.spi->dev, " Cannot find yft stl pinctrl stl_spi1_cs_as_gpio!\n");
		return ret;
	}
	pinctrl_select_state(stl_pinctrl, stl_spi1_mo_as_spi1_mo);
	pinctrl_select_state(stl_pinctrl, stl_spi1_mi_as_spi1_mi);
	pinctrl_select_state(stl_pinctrl, stl_spi1_clk_as_spi1_clk);
	pinctrl_select_state(stl_pinctrl, stl_spi1_cs_as_spi1_cs);
#line 411
	TINY_LCD_INFO("successful \n");
	return 0;

err_en_1v8_gpio_dir:
	if (gpio_is_valid(g_data.en_1v8_gpio))
		gpio_free(g_data.en_1v8_gpio);
err_en_2v8_gpio_dir:
	if (gpio_is_valid(g_data.en_2v8_gpio))
		gpio_free(g_data.en_2v8_gpio);
err_bl_ctrl_gpio_dir:
	if (gpio_is_valid(g_data.bl_ctrl_gpio))
		gpio_free(g_data.bl_ctrl_gpio);
err_dc_ctrl_gpio_dir:
	if (gpio_is_valid(g_data.dc_ctrl_gpio))
		gpio_free(g_data.dc_ctrl_gpio);
err_te_gpio_dir:
	if (gpio_is_valid(g_data.te_gpio))
		gpio_free(g_data.te_gpio);
err_reset_gpio_dir:
	if (gpio_is_valid(g_data.reset_gpio))
		gpio_free(g_data.reset_gpio);
err_reset_gpio_req:
#line 436
	TINY_LCD_ERR("error:%d \n", ret);
	return ret;
}

static bool pre_irq_en;

static void tiny_enable_te_irq(bool irq_en)
{
#line 442
	TINY_LCD_INFO("irq_en:%d, pre_irq_en:%d\n", irq_en, !pre_irq_en);
	if (irq_en) {
		if (pre_irq_en == 1) {
			enable_irq(yft_tiny_lcd_te_irqnum);
			pre_irq_en = 0;
		}
	} else {
		if (!pre_irq_en) {
			disable_irq(yft_tiny_lcd_te_irqnum);
			pre_irq_en = 1;
		}
	}
}

static void tiny_lcd_te_work_handler(struct work_struct *work);
static irqreturn_t yft_tiny_lcd_te_isr(int irq, void *dev_id);

static int stl_irq_registration(void)
{
	int ret;

	yft_tiny_lcd_te_irqnum = gpio_to_irq(g_data.te_gpio);
#line 473
	TINY_LCD_INFO("irq:%d, flag:%x\n", yft_tiny_lcd_te_irqnum, IRQF_TRIGGER_FALLING);
	ret = request_irq(yft_tiny_lcd_te_irqnum, yft_tiny_lcd_te_isr,
			  IRQF_TRIGGER_FALLING, "tiny_lcd_te", NULL);
	return ret;
}

static ssize_t write_frame_status = 1;

static ssize_t tiny_lcd_write_frame_show(struct device_driver *ddri, char *buf)
{
#line 564
	TINY_LCD_INFO("show_tiny_lcd_write_frame_value %zd \n", write_frame_status);
	return scnprintf(buf, PAGE_SIZE, "%zd\n", write_frame_status);
}

static ssize_t tiny_lcd_write_frame_store(struct device_driver *ddri,
					  const char *buf, size_t count)
{
	unsigned long value = 0;

	if (kstrtoul(buf, 10, &value)) {
#line 573
		TINY_LCD_INFO("[%s]:  invalid value  faile\n", __func__);
		return -EINVAL;
	}
	if (value == 1)
#line 578
		TINY_LCD_INFO("store_tiny_lcd_write_frame_value 11 gImage_logo=%ld ,%ld\n", sizeof(gImage_logo), sizeof(gImage_logo));
	else
#line 582
		TINY_LCD_INFO("store_tiny_lcd_write_frame_value 00 gImage_logo=%ld ,%ld\n", sizeof(gImage_logo), sizeof(gImage_logo));
	memcpy(pic_from_user, gImage_logo, sizeof(gImage_logo));
	spidev_sync_write_multi_data(gImage_logo, sizeof(gImage_logo));
#line 588
	TINY_LCD_INFO("store_tiny_lcd_write_frame_value status is %ld ,write_frame_status=%zd ,%ld\n", value, write_frame_status, sizeof(gImage_logo));
	if (write_frame_status == sizeof(gImage_logo))
		write_frame_status = 1;
	else if (write_frame_status < 0)
		write_frame_status = 2;
	else
		write_frame_status = 0;
	return count;
}

static void spi_lcd_change_backlight(unsigned long en)
{
#line 601
	TINY_LCD_INFO("%s: en=%ld\n", __func__, en);
	backlight_step = en;
}

static ssize_t tiny_lcd_backlight_control_show(struct device_driver *ddri,
					       char *buf)
{
#line 616
	TINY_LCD_INFO("show_tiny_lcd_backlight_control_value %ld \n", backlight_step);
	return scnprintf(buf, PAGE_SIZE, "%ld\n", backlight_step);
}

static ssize_t tiny_lcd_backlight_control_store(struct device_driver *ddri,
						const char *buf, size_t count)
{
	unsigned long value = 0;

	if (kstrtoul(buf, 10, &value)) {
#line 626
		TINY_LCD_INFO("[%s]:  invalid value  faile\n", __func__);
		return -EINVAL;
	}
	spi_lcd_change_backlight(value);
#line 631
	TINY_LCD_INFO("store_tiny_lcd_backlight_control_value status is %ld \n", value);
	return count;
}

static void tiny_lcd_bl_enable_func(unsigned long en)
{
#line 638
	TINY_LCD_INFO("%s: en=%lu, Ignore operation !!\n", __func__, en);
}

static unsigned long backlight_enable_status;

static ssize_t tiny_lcd_bl_enable_show(struct device_driver *ddri, char *buf)
{
#line 647
	TINY_LCD_INFO("show_tiny_lcd_bl_enable_value %lu \n", backlight_enable_status);
	return scnprintf(buf, PAGE_SIZE, "%lu\n", backlight_enable_status);
}

static ssize_t tiny_lcd_bl_enable_store(struct device_driver *ddri,
					const char *buf, size_t count)
{
	if (kstrtoul(buf, 10, &backlight_enable_status)) {
#line 655
		TINY_LCD_INFO("[%s]:  invalid value  faile\n", __func__);
		return -EINVAL;
	}
	spi_lcd_change_backlight(backlight_enable_status);
#line 660
	TINY_LCD_INFO("store_tiny_lcd_bl_enable_value status is %lu \n", backlight_enable_status);
	return count;
}

static void tiny_lcd_suspend(void)
{
#line 667
	TINY_LCD_INFO("%s: start\n", __func__);
	if (g_data.power_on != 1)
		return;
	tiny_enable_te_irq(0);
	backlight_step = 0;
	current_backlight_level = 0;
	spidev_sync_write_cmd(0x28);
	mdelay(20);
	spidev_sync_write_cmd(0x10);
	mdelay(220);
	gpio_direction_output(g_data.reset_gpio, 0);
	mdelay(20);
	gpio_direction_output(g_data.en_2v8_gpio, 0);
	mdelay(20);
	gpio_direction_output(g_data.en_1v8_gpio, 0);
	mdelay(20);
	pinctrl_select_state(stl_pinctrl, stl_spi1_mo_as_gpio);
	pinctrl_select_state(stl_pinctrl, stl_spi1_mi_as_gpio);
	pinctrl_select_state(stl_pinctrl, stl_spi1_clk_as_gpio);
	pinctrl_select_state(stl_pinctrl, stl_spi1_cs_as_gpio);
	g_data.power_on = 0;
#line 693
	TINY_LCD_INFO("%s: end\n", __func__);
}

static void tiny_lcd_aod_suspend(void)
{
#line 699
	TINY_LCD_INFO("%s: start\n", __func__);
	mdelay(10);
#line 702
	TINY_LCD_INFO("%s: end\n", __func__);
}

static void push_table(struct tiny_lcd_init_record *table, unsigned int count)
{
	unsigned int i, j;

	for (i = 0; i < count; i++) {
		if (table[i].command == REGFLAG_DELAY) {
			mdelay(table[i].count);
			continue;
		}
		spidev_sync_write_cmd(table[i].command);
		for (j = 0; j < table[i].count; j++)
			spidev_sync_write_data(table[i].parameters[j]);
	}
}

static inline void initial_co5300(void)
{
#line 1059
	TINY_LCD_INFO("[%s] start  2\n", __func__);
	push_table(init_setting, ARRAY_SIZE(init_setting));
}

static void tiny_lcd_resume(void)
{
#line 708
	TINY_LCD_INFO("%s: start\n", __func__);
	if (g_data.power_on == 1) {
		g_data.frame_send_end = 1;
#line 712
		TINY_LCD_INFO("%s: aod 38\n", __func__);
		return;
	}
	pinctrl_select_state(stl_pinctrl, stl_spi1_mo_as_spi1_mo);
	pinctrl_select_state(stl_pinctrl, stl_spi1_mi_as_spi1_mi);
	pinctrl_select_state(stl_pinctrl, stl_spi1_clk_as_spi1_clk);
	pinctrl_select_state(stl_pinctrl, stl_spi1_cs_as_spi1_cs);
	mdelay(20);
	gpio_direction_output(g_data.en_1v8_gpio, 1);
	mdelay(20);
	gpio_direction_output(g_data.en_2v8_gpio, 1);
	mdelay(20);
	gpio_direction_output(g_data.reset_gpio, 1);
	mdelay(15);
	gpio_direction_output(g_data.reset_gpio, 0);
	mdelay(30);
	gpio_direction_output(g_data.reset_gpio, 1);
	mdelay(120);
	initial_co5300();
	g_data.power_on = 1;
	g_data.frame_send_end = 1;
	tiny_enable_te_irq(1);
#line 742
	TINY_LCD_INFO("%s: end\n", __func__);
}

static void tiny_lcd_power_enable_func(unsigned long en)
{
	if (en)
		tiny_lcd_resume();
	else
		tiny_lcd_suspend();
}

static unsigned long power_enable_status;

static ssize_t tiny_lcd_power_enable_show(struct device_driver *ddri, char *buf)
{
#line 780
	TINY_LCD_INFO("show_tiny_lcd_power_enable_value %lu \n", power_enable_status);
	return scnprintf(buf, PAGE_SIZE, "%lu\n", power_enable_status);
}

static ssize_t tiny_lcd_power_enable_store(struct device_driver *ddri,
					   const char *buf, size_t count)
{
	if (kstrtoul(buf, 10, &power_enable_status)) {
#line 788
		TINY_LCD_INFO("[%s]:  invalid value  faile\n", __func__);
		return -EINVAL;
	}
	tiny_lcd_power_enable_func(power_enable_status);
#line 793
	TINY_LCD_INFO("store_tiny_lcd_power_enable_value status is %lu \n", power_enable_status);
	return count;
}

static unsigned long tiny_lcd_tp_control_status;

static ssize_t tiny_lcd_tp_control_show(struct device_driver *ddri, char *buf)
{
#line 801
	TINY_LCD_INFO("show_tiny_lcd_tp_control_value %lu \n", tiny_lcd_tp_control_status);
	return scnprintf(buf, PAGE_SIZE, "%lu\n", tiny_lcd_tp_control_status);
}

static ssize_t tiny_lcd_tp_control_store(struct device_driver *ddri,
					 const char *buf, size_t count)
{
	if (kstrtoul(buf, 10, &tiny_lcd_tp_control_status)) {
#line 810
		TINY_LCD_INFO("[%s]:  invalid value  faile\n", __func__);
		return -EINVAL;
	}
	if (tiny_lcd_tp_control_status)
		tiny_tp_power_contorl(1);
	else
		tiny_tp_power_contorl(0);
#line 820
	TINY_LCD_INFO("store_tiny_lcd_tp_control_value status is %lu \n", tiny_lcd_tp_control_status);
	return count;
}

static DRIVER_ATTR_RW(tiny_lcd_power_enable);
static DRIVER_ATTR_RW(tiny_lcd_bl_enable);
static DRIVER_ATTR_RW(tiny_lcd_backlight_control);
static DRIVER_ATTR_RW(tiny_lcd_write_frame);
static DRIVER_ATTR_RW(tiny_lcd_tp_control);

static struct driver_attribute *tiny_lcd_attr_list[] = {
	&driver_attr_tiny_lcd_power_enable,
	&driver_attr_tiny_lcd_bl_enable,
	&driver_attr_tiny_lcd_backlight_control,
	&driver_attr_tiny_lcd_write_frame,
	&driver_attr_tiny_lcd_tp_control,
};

static int tiny_lcd_create_attr(struct device_driver *driver)
{
	int idx, err = 0;
	int num = ARRAY_SIZE(tiny_lcd_attr_list);

	for (idx = 0; idx < num; idx++) {
		err = driver_create_file(driver, tiny_lcd_attr_list[idx]);
		if (err) {
#line 850
			TINY_LCD_INFO("create driver file (%s) failed.\n", tiny_lcd_attr_list[idx]->attr.name);
			break;
		}
	}
	return err;
}

static long tiny_lcd_ioctl(struct file *file, unsigned int cmd,
			   unsigned long arg)
{
	void __user *argp = (void __user *)arg;
	unsigned long value = 0;

	switch (cmd) {
	case TINY_LCM_IOC_POWER_AOD:
#line 867
		TINY_LCD_INFO("TINY_LCM_IOC_POWER_AOD !! start \n");
		tiny_tp_power_contorl(0);
		tiny_lcd_aod_suspend();
		g_data.frame_send_end = 0;
#line 873
		TINY_LCD_INFO("TINY_LCM_IOC_POWER_AOD !!\n");
		break;
	case TINY_LCM_IOC_POWER_ENABLE:
#line 878
		TINY_LCD_INFO("TINY_LCM_IOC_POWER_ENABLE !! start\n");
		tiny_lcd_power_enable_func(1);
		tiny_tp_power_contorl(1);
#line 882
		TINY_LCD_INFO("TINY_LCM_IOC_POWER_ENABLE !!\n");
		break;
	case TINY_LCM_IOC_POWER_DISABLE:
#line 887
		TINY_LCD_INFO("TINY_LCM_IOC_POWER_DISABLE !! start \n");
		tiny_tp_power_contorl(0);
		tiny_lcd_power_enable_func(0);
#line 890
		TINY_LCD_INFO("TINY_LCM_IOC_POWER_DISABLE !!\n");
		break;
	case TINY_LCM_IOC_BL_ENABLE:
#line 895
		TINY_LCD_INFO("TINY_LCM_IOC_BL_ENABLE !! start \n");
		tiny_lcd_bl_enable_func(1);
		g_data.frame_send_enable = 1;
		write_frame_status = 1;
#line 898
		TINY_LCD_INFO("TINY_LCM_IOC_BL_ENABLE !!\n");
		break;
	case TINY_LCM_IOC_BL_DISABLE:
#line 903
		TINY_LCD_INFO("TINY_LCM_IOC_BL_DISABLE !! start\n");
		tiny_lcd_bl_enable_func(0);
		g_data.frame_send_enable = 0;
#line 905
		TINY_LCD_INFO("TINY_LCM_IOC_BL_DISABLE !!\n");
		break;
	case TINY_LCM_IOC_BL_CONTROL:
#line 910
		TINY_LCD_INFO("TINY_LCM_IOC_BL_CONTROL !!duty=%ld  start\n", value);
		if (copy_from_user(&value, argp, sizeof(value))) {
#line 912
			TINY_LCD_INFO("copy_from_user(..) failed.\n");
			return -1;
		}
		spi_lcd_change_backlight(value);
#line 917
		TINY_LCD_INFO("TINY_LCM_IOC_BL_CONTROL !!duty=%ld \n", value);
		break;
	case TINY_LCM_IOC_FRAME_SIZE:
#line 921
		TINY_LCD_INFO("TINY_LCM_IOC_FRAME_SIZE !!framesize:%dx%d, start\n", framesize.width, framesize.height);
		if (copy_from_user(&framesize, argp, sizeof(framesize))) {
#line 923
			TINY_LCD_INFO("copy_from_user(..) failed.\n");
			return -1;
		}
#line 927
		TINY_LCD_INFO("TINY_LCM_IOC_FRAME_SIZE !!framesize:%dx%d, end\n", framesize.width, framesize.height);
		break;
	case TINY_LCM_IOC_WRITE_FRAME:
		write_frame_status = 2;
		if (g_data.frame_send_enable == 1) {
			if (copy_from_user(gImage_logo, argp, sizeof(gImage_logo))) {
#line 935
				TINY_LCD_INFO("copy_from_user(..) failed.\n");
				write_frame_status = 3;
				return -1;
			}
			if (!g_data.frame_send_end) {
#line 943
				TINY_LCD_INFO("TINY_LCM_IOC_WRITE_FRAME !!\n");
				spidev_sync_write_multi_data(gImage_logo, sizeof(gImage_logo));
				write_frame_status = 1;
			} else {
				write_frame_status = 3;
			}
		} else {
#line 949
			TINY_LCD_INFO("TINY_LCM_IOC_WRITE_FRAME ignore, in recovery \n");
			write_frame_status = 3;
		}
		break;
	case TINY_LCM_IOC_FRAME_STATUS:
		if (copy_to_user(argp, &write_frame_status, sizeof(write_frame_status))) {
#line 956
			TINY_LCD_INFO("copy_from_user(..) failed.\n");
			return -1;
		}
		break;
	case TINY_LCM_IOC_TP_GESTURE_ENABLE:
#line 964
		TINY_LCD_INFO("TINY_LCM_IOC_TP_GESTURE_ENABLE !! start\n");
		tiny_tp_gesture_contorl(1);
#line 966
		TINY_LCD_INFO("TINY_LCM_IOC_TP_GESTURE_ENABLE !!\n");
		if (g_data.power_on != 1 || !g_data.frame_send_end) {
			tiny_tp_power_contorl(1);
			tiny_tp_power_contorl(0);
#line 972
			TINY_LCD_INFO("TINY_LCM_IOC_TP_GESTURE_ENABLE !!force tp reset\n");
		}
		break;
	case TINY_LCM_IOC_TP_GESTURE_DISABLE:
#line 976
		TINY_LCD_INFO("TINY_LCM_IOC_TP_GESTURE_DISABLE !! start\n");
		tiny_tp_gesture_contorl(0);
#line 978
		TINY_LCD_INFO("TINY_LCM_IOC_TP_GESTURE_DISABLE !!\n");
		break;
	default:
#line 982
		TINY_LCD_INFO("[%s] Error ID\n", __func__);
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
	.name = "tiny_lcd_miscdev",
	.fops = &tiny_lcd_fops,
};

static void showpic(void)
{
#line 1065
	TINY_LCD_INFO(" start\n");
	memcpy(pic_from_user, gImage_logo, sizeof(gImage_logo));
	spidev_sync_write_multi_data(pic_from_user, sizeof(pic_from_user));
#line 1068
	TINY_LCD_INFO(" end\n");
}

static int tiny_lcd_get_sensor_id(void)
{
	size_t tiny_lcd_id[2] = { 0, 0 };
	int retry;

	for (retry = 0; retry < 3; retry++) {
		tiny_lcd_id[0] = spidev_sync_read_data(0xDA);
#line 1119
		TINY_LCD_INFO(" retry=%d, read 0xDA data, tiny_lcd_id[0]=0x%zx\n", retry, tiny_lcd_id[0]);
		if (tiny_lcd_id[0])
			break;
	}
	for (retry = 0; retry < 3; retry++) {
		tiny_lcd_id[1] = spidev_sync_read_data(0xDB);
#line 1126
		TINY_LCD_INFO(" retry=%d, read 0xDB data, tiny_lcd_id[1]=0x%zx\n", retry, tiny_lcd_id[1]);
		if (tiny_lcd_id[1])
			break;
	}
	if (tiny_lcd_id[0] == 0x33) {
		if (tiny_lcd_id[1] == 0x11)
			tiny_lcm_number = 1;
		else if (tiny_lcd_id[1] == 0x10)
			tiny_lcm_number = 2;
#line 1136
		TINY_LCD_INFO("sensor id is ok !!tiny_lcd_id=0x%zx,0x%zx,tiny_lcm_number=%d\n", tiny_lcd_id[0], tiny_lcd_id[1], tiny_lcm_number);
		return 0;
	}
#line 1139
	TINY_LCD_INFO("sensor id is fail !!tiny_lcd_id=0x%zx,0x%zx,\n", tiny_lcd_id[0], tiny_lcd_id[1]);
	return -1;
}

static int tiny_lcd_get_adc_info(struct device *dev)
{
	int val = 0;
	int ret;
	int ch;
	struct iio_channel *chan;

	chan = iio_channel_get(dev, "tiny_lcd_adc");
	ret = IS_ERR(chan);
	if (ret) {
		if (PTR_ERR(chan) == -EPROBE_DEFER) {
#line 1172
			TINY_LCD_INFO("%s EPROBE_DEFER\n", __func__);
			return -EPROBE_DEFER;
		}
#line 1175
		TINY_LCD_INFO("fail to get iio channel (%d)", ret);
		return -1;
	}
	ch = chan->channel->channel;
	ret = iio_read_channel_processed(chan, &val);
	iio_channel_release(chan);
	if (ret < 0) {
#line 1183
		TINY_LCD_INFO("iio_read_channel_processed fail");
		return -1;
	}
#line 1187
	TINY_LCD_INFO("tiny_lcd_ch = %d, raw_val = %dmV\n", ch, val);
	return val;
}

static void tiny_lcd_power_on(void)
{
	mdelay(5);
	gpio_direction_output(g_data.en_1v8_gpio, 1);
	mdelay(10);
	gpio_direction_output(g_data.en_2v8_gpio, 1);
	mdelay(10);
	gpio_direction_output(g_data.reset_gpio, 1);
	mdelay(15);
	gpio_direction_output(g_data.reset_gpio, 0);
	mdelay(30);
	gpio_direction_output(g_data.reset_gpio, 1);
	mdelay(120);
}

static int spi_probe(struct spi_device *spi)
{
	int ret;
	int adc;
	ktime_t start_time, end_time;
	struct timespec64 ts;

#line 1197
	TINY_LCD_INFO("entry, of_node_full_name:%s \n", spi->dev.of_node ? spi->dev.of_node->full_name : "<no-node>");
	g_data.spi = spi;
	g_data.speed_hz = spi->max_speed_hz;
#line 1201
	TINY_LCD_INFO("speed_hz:%d \n", spi->max_speed_hz);
	if (!g_data.tx_buffer) {
		g_data.tx_buffer = kmalloc(TINY_LCD_BUFSIZ, GFP_KERNEL);
		if (!g_data.tx_buffer) {
#line 1206
			TINY_LCD_ERR("kmalloc error! (%s,%d) \n", __func__, __LINE__);
			goto err_free_rx;
		}
	}
	if (!g_data.rx_buffer) {
		g_data.rx_buffer = kmalloc(TINY_LCD_BUFSIZ, GFP_KERNEL);
		if (!g_data.rx_buffer)
			goto err_out;
	}
	spi->mode = SPI_MODE_3;
	spi->bits_per_word = 8;

	stl_parse_dt();
	tiny_lcd_power_on();
#line 1240
	TINY_LCD_INFO("entry, gpio ctl ok\n");

	adc = tiny_lcd_get_adc_info(&spi->dev);
	if (tiny_lcd_get_sensor_id() != 0 || !(adc > 450 && adc < 1000))
		goto err_free_gpio;
#line 1245
	TINY_LCD_INFO("get_sensor_id is ok!! \n");

	ret = stl_irq_registration();
	if (ret) {
#line 1253
		TINY_LCD_INFO("request irq failed");
		goto err_free_irq;
	}

	initial_co5300();
	backlight_step = 255;
	start_time = ktime_get_boottime();
	showpic();
	end_time = ktime_get_boottime();
	ts = ns_to_timespec64(ktime_to_ns(ktime_sub(end_time, start_time)));
#line 1267
	TINY_LCD_INFO("time interval is %lld,%ld\n", ts.tv_sec, ts.tv_nsec);
	mdelay(100);
#line 1271
	TINY_LCD_INFO(" start backlight\n");

	INIT_DELAYED_WORK(&tiny_lcd_te_work, tiny_lcd_te_work_handler);

	ret = tiny_lcd_create_attr(&spi_tiny_lcd_driver.driver);
	if (ret)
#line 1296
		TINY_LCD_INFO("tiny_lcd_create_attr fail: %d\n", ret);

	ret = misc_register(&tiny_lcd_miscdev);
	if (ret)
#line 1300
		TINY_LCD_INFO("Debug tools miscdev register failed");

	g_data.power_on = 1;
	g_data.frame_send_enable = 1;
	g_data.frame_send_end = 1;
	g_data.users = 1;
	yft_set_tinylcd_device_used("spi_tiny_lcd_co5300", 1);
	printk(KERN_INFO "YFT_DEVICE  tinylcd = 1\n");
#line 1315
	TINY_LCD_INFO("successful \n");
	return 0;

err_free_irq:
	free_irq(yft_tiny_lcd_te_irqnum, NULL);
err_free_gpio:
	if (gpio_is_valid(g_data.en_1v8_gpio))
		gpio_free(g_data.en_1v8_gpio);
	if (gpio_is_valid(g_data.en_2v8_gpio))
		gpio_free(g_data.en_2v8_gpio);
	if (gpio_is_valid(g_data.bl_ctrl_gpio))
		gpio_free(g_data.bl_ctrl_gpio);
	if (gpio_is_valid(g_data.dc_ctrl_gpio))
		gpio_free(g_data.dc_ctrl_gpio);
	if (gpio_is_valid(g_data.te_gpio))
		gpio_free(g_data.te_gpio);
	if (gpio_is_valid(g_data.reset_gpio))
		gpio_free(g_data.reset_gpio);
err_free_rx:
	if (g_data.rx_buffer)
		kvfree(g_data.rx_buffer);
err_out:
#line 1345
	TINY_LCD_INFO("fail \n");
	return -1;
}

static void spi_remove(struct spi_device *spi)
{
#line 1351
	TINY_LCD_INFO("entry\n");
	misc_deregister(&tiny_lcd_miscdev);
}

static void tiny_lcd_te_work_handler(struct work_struct *work)
{
	if (write_frame_status == 3) {
		if (g_data.frame_send_enable == 1 && g_data.frame_send_end)
			spidev_sync_write_multi_data(gImage_logo,
				framesize.width == 320 ? 320 * 320 * 2 :
							 340 * 340 * 2);
		write_frame_status = 1;
	}
}

static irqreturn_t yft_tiny_lcd_te_isr(int irq, void *dev_id)
{
	if (g_data.frame_send_enable == 1)
		schedule_delayed_work(&tiny_lcd_te_work, 0);
	return IRQ_HANDLED;
}

static const struct of_device_id spidev_dt_ids[] = {
	{ .compatible = "hxytech, spi_tiny_lcd" },
	{},
};
MODULE_DEVICE_TABLE(of, spidev_dt_ids);

struct spi_driver spi_tiny_lcd_driver = {
	.driver = {
		.name = "spi_tiny_lcd_co5300",
		.bus = &spi_bus_type,
		.owner = THIS_MODULE,
		.of_match_table = spidev_dt_ids,
	},
	.probe = spi_probe,
	.remove = spi_remove,
};

/* MediaTek log_store boot-mode helper. */
static int get_boot_mode(void)
{
	struct device_node *np_chosen;
	struct tag_bootmode *tag;

	np_chosen = of_find_node_by_path("/chosen");
	if (!np_chosen) {
		pr_notice("log_store: warning: not find node: '/chosen'\n");
		np_chosen = of_find_node_by_path("/chosen@0");
		if (!np_chosen) {
			pr_notice("log_store: warning: not find node: '/chosen@0'\n");
			return 0;
		}
	}
	tag = (struct tag_bootmode *)of_get_property(np_chosen, "atag,boot", NULL);
	if (!tag) {
		pr_notice("log_store: error: not find tag: 'atag,boot';\n");
		return 0;
	}
	pr_notice("log_store: bootmode: 0x%x boottype: 0x%x.\n",
		  tag->bootmode, tag->boottype);
	return tag->bootmode;
}

static int __init spi_tiny_lcd_init(void)
{
	int status;
	int tiny_lcd_boot_mode;

	yft_tinylcd_device_add(&spi_tiny_lcd_driver, 0);
	tiny_lcd_boot_mode = get_boot_mode();
#line 1386
	TINY_LCD_INFO("%s: tiny_lcd_boot_mode=%d\n", __func__, tiny_lcd_boot_mode);
	if (tiny_lcd_boot_mode == 1 || tiny_lcd_boot_mode == 5 ||
	    tiny_lcd_boot_mode == 6 || tiny_lcd_boot_mode == 8 ||
	    tiny_lcd_boot_mode == 9)
		return 0;
#line 1396
	TINY_LCD_INFO(KERN_ERR "(wyx_check_tiny)(%s,%d)", __func__, __LINE__);
	status = spi_register_driver(&spi_tiny_lcd_driver);
	if (status < 0) {
#line 1401
		TINY_LCD_ERR("status:%d \n", status);
		spi_unregister_driver(&spi_tiny_lcd_driver);
		return status;
	}
	return 0;
}

static void __exit spi_tiny_lcd_exit(void)
{
#line 1414
	TINY_LCD_INFO("entry\n");
	spi_unregister_driver(&spi_tiny_lcd_driver);
}

module_init(spi_tiny_lcd_init);
module_exit(spi_tiny_lcd_exit);

MODULE_AUTHOR("wangdong, <wangdong@agenewtech.com>");
MODULE_DESCRIPTION("SSD1317, OEL Display Module, QG-9696TSWXG04 VER B, 4-wire I SPI, 8bit 1-data-line");
MODULE_LICENSE("GPL v2");
MODULE_ALIAS("spi:SSD1317");
MODULE_VERSION("v0.01");
