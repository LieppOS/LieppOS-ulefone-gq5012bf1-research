// SPDX-License-Identifier: GPL-2.0
/* Clean-room reconstruction of GQ5012BF1 stock hynitron.ko. */
#include <linux/module.h>
#include <linux/i2c.h>
#include <linux/input.h>
#include <linux/interrupt.h>
#include <linux/gpio.h>
#include <linux/of.h>
#include <linux/of_device.h>
#include <linux/of_gpio.h>
#include <linux/slab.h>
#include <linux/workqueue.h>
#include <linux/delay.h>
#include <linux/kobject.h>
#include <linux/sysfs.h>
#include <linux/mutex.h>
#include <linux/pm_wakeup.h>
#include <linux/fortify-string.h>

#ifndef HYNITRON_ALLOW_FW_PROGRAMMING
#define HYNITRON_ALLOW_FW_PROGRAMMING 0
#endif
#if HYNITRON_ALLOW_FW_PROGRAMMING != 0 && HYNITRON_ALLOW_FW_PROGRAMMING != 1
#error "HYNITRON_ALLOW_FW_PROGRAMMING must be 0 or 1"
#endif

#define HYN_NAME "hyn_ts"
#define HYN_COMPAT "hynitron,hyn_ts"
#define HYN_IRQ_NAME "Hynitron Touch Int"
#define HYN_SYSFS_NAME "hynitron_debug"
#define CST_REG_TOUCH 0x00
#define CST_REG_DEEP_SLEEP 0xe5
#define CST_DEEP_SLEEP 0x03
#define CST_REG_FW_INFO 0xa6
#define CST_REG_CHIP_ID 0xa7
#define CST_REG_GESTURE 0xd3
#define CST_REG_GESTURE_ENABLE 0xec
#define CST_TOUCH_BYTES 9
#define CST_FW_PAYLOAD_SIZE 0x3c00
#define HYN_KEEP __used noinline

extern char second_touch_fw_version[30];
extern int yft_touchpanel_device_add(struct i2c_driver *driver, int used);
extern int yft_set_touch_device_used(char *name, int used);

#include "firmware_cst8xx.inc"
#include "firmware_cst816t.inc"

struct hynitron_ts_platform_data {
	int irq_gpio;
	int reset_gpio;
	int vdd_gpio;
	unsigned long irq_gpio_flags;
	u32 max_touch_num;
	u32 x_resolution;
	u32 y_resolution;
	bool have_key;
	u32 key_number;
	u32 key_y_coord;
	u32 key_code[4];
};

struct hyn_gesture_state {
	u8 mode;
	u8 active;
	u8 gesture_id;
	u8 point_num;
	u16 x[255];
	u16 y[255];
	u32 report_key;
};

struct hynitron_ts_data {
	struct i2c_client *client;
	struct device *dev;
	struct input_dev *input_dev;
	struct hynitron_ts_platform_data *pdata;
	struct work_struct work;
	struct workqueue_struct *wq;
	struct kobject *kobj;
	struct mutex sysfs_lock;
	int irq;
	u16 chip_type;
	u16 project_id;
	u16 module_id;
	u16 fw_version;
	u16 checksum;
	u16 chip_series;
	u8 product_line;
	u8 bootloader_addr;
	u32 checkcode;
	bool apk_upgrade_flag;
	bool irq_disabled;
	bool suspended;
	u8 work_mode;
	const u8 *selected_fw;
	u32 selected_fw_len;
};

static struct hynitron_ts_data *hyn_ts_data;
int tiny_tpgesture_status;
static struct hyn_gesture_state hyn_gesture_data;

HYN_KEEP int hyn_i2c_read(struct i2c_client *client, char *wbuf, int wlen,
			char *rbuf, int rlen)
{
	int ret;
	if (!client)
		return -1;
	ret = i2c_master_send(client, wbuf, wlen);
	if (ret < 0)
		pr_err("3[HYN][Error]i2c_master_send error\n");
	ret = i2c_master_recv(client, rbuf, rlen);
	if (ret < 0) {
		dev_err(&client->dev, "3[HYN][Error]i2c_master_recv i2c read error.\n");
		return ret;
	}
	return ret;
}

HYN_KEEP int hyn_i2c_write(struct i2c_client *client, char *buf, int len)
{
	int ret;
	if (!client)
		return -1;
	ret = i2c_master_send(client, buf, len);
	if (ret < 0)
		pr_err("3[HYN][Error]i2c_master_send error\n");
	return ret;
}

HYN_KEEP int hyn_i2c_write_byte(struct i2c_client *client, u8 reg, u8 value)
{
	char b[2] = { reg, value };
	return hyn_i2c_write(client, b, 2);
}

HYN_KEEP int hyn_i2c_read_byte(struct i2c_client *client, u8 reg, u8 *value)
{
	return hyn_i2c_read(client, (char *)&reg, 1, (char *)value, 1);
}

HYN_KEEP int hyn_i2c_write_bytes(unsigned short reg, unsigned char *buf,
			       unsigned short len, unsigned char reg_len)
{
	unsigned char mbuf[600];
	if (len + reg_len > sizeof(mbuf))
		fortify_panic(__func__);
	if (reg_len == 1) mbuf[0] = reg;
	else { mbuf[0] = reg >> 8; mbuf[1] = reg; }
	memcpy(mbuf + reg_len, buf, len);
	return hyn_i2c_write(hyn_ts_data->client, (char *)mbuf, len + reg_len);
}

HYN_KEEP int hyn_i2c_read_bytes(unsigned short reg, unsigned char *buf,
			      unsigned short len, unsigned char reg_len)
{
	unsigned char rb[2];
	if (reg_len == 1) rb[0] = reg;
	else { rb[0] = reg >> 8; rb[1] = reg; }
	return hyn_i2c_read(hyn_ts_data->client, (char *)rb, reg_len,
			    (char *)buf, len);
}

HYN_KEEP int cst3xx_i2c_read(struct i2c_client *client, unsigned char *buf, int len)
{
	int ret = -1, retry = 0;
	while (retry++ < 2) { ret = i2c_master_recv(client, buf, len); if (ret > 0) break; }
	return ret;
}
HYN_KEEP int cst3xx_i2c_write(struct i2c_client *client, unsigned char *buf, int len)
{
	int ret = -1, retry = 0;
	while (retry++ < 2) { ret = i2c_master_send(client, buf, len); if (ret > 0) break; }
	return ret;
}
HYN_KEEP int cst3xx_i2c_read_register(struct i2c_client *client,
				    unsigned char *buf, int len)
{
	int ret = cst3xx_i2c_write(client, buf, 2);
	if (ret <= 0) return ret;
	return cst3xx_i2c_read(client, buf, len);
}

HYN_KEEP void hyn_reset_watchdog_proc(void) { }
HYN_KEEP int hyn_reset_proc(int high_delay_ms)
{
	if (!hyn_ts_data) return -ENODEV;
	gpiod_direction_output_raw(gpio_to_desc(hyn_ts_data->pdata->reset_gpio), 0);
	mdelay(20);
	hyn_reset_watchdog_proc();
	gpiod_direction_output_raw(gpio_to_desc(hyn_ts_data->pdata->reset_gpio), 1);
	if (high_delay_ms)
		mdelay(high_delay_ms);
	return 0;
}
HYN_KEEP void hyn_irq_disable(void)
{
	if (hyn_ts_data && !hyn_ts_data->irq_disabled) {
		disable_irq_nosync(hyn_ts_data->irq);
		hyn_ts_data->irq_disabled = true;
	}
}
HYN_KEEP void hyn_irq_enable(void)
{
	if (hyn_ts_data && hyn_ts_data->irq_disabled) {
		enable_irq(hyn_ts_data->irq);
		hyn_ts_data->irq_disabled = false;
	}
}

static void hyn_release_all_finger(void)
{
	if (!hyn_ts_data || !hyn_ts_data->input_dev) return;
	input_event(hyn_ts_data->input_dev, EV_KEY, BTN_TOUCH, 0);
	input_event(hyn_ts_data->input_dev, EV_SYN, SYN_MT_REPORT, 0);
	input_event(hyn_ts_data->input_dev, EV_SYN, SYN_REPORT, 0);
}

static HYN_KEEP void cst3xx_touch_down(struct input_dev *d, s32 id, s32 x, s32 y, s32 w)
{
	input_event(d, EV_ABS, ABS_MT_TRACKING_ID, id);
	input_event(d, EV_ABS, ABS_MT_TOUCH_MAJOR, w >> 3);
	input_event(d, EV_ABS, ABS_MT_POSITION_X, x);
	input_event(d, EV_ABS, ABS_MT_POSITION_Y, y);
	input_event(d, EV_ABS, ABS_MT_WIDTH_MAJOR, w);
	input_event(d, EV_KEY, BTN_TOUCH, 1);
	input_event(d, EV_SYN, SYN_MT_REPORT, 0);
}
static HYN_KEEP void cst3xx_touch_up(struct input_dev *d, s32 id)
{
	input_event(d, EV_ABS, ABS_MT_TRACKING_ID, -1);
	input_event(d, EV_KEY, BTN_TOUCH, 0);
	input_event(d, EV_SYN, SYN_MT_REPORT, 0);
}
static HYN_KEEP void tpd_up(int x, int y) { cst3xx_touch_up(hyn_ts_data->input_dev, 0); }
static HYN_KEEP void tpd_down(int x, int y, int p, int id)
{
	cst3xx_touch_down(hyn_ts_data->input_dev, id, x, y, 0x28);
}

static HYN_KEEP void hyn_check_gesture(struct input_dev *input, int id)
{
	unsigned int key = 0;
	/* Stock IDs: letter/arrow gestures plus 0xcc/0xe5 double/tip click. */
	switch (id) {
	case 0x24: key = KEY_O; break; case 0x31: key = KEY_W; break;
	case 0x32: key = KEY_M; break; case 0x33: key = KEY_E; break;
	case 0x34: key = KEY_C; break; case 0x46: key = KEY_S; break;
	case 0x54: key = KEY_V; break; case 0x65: key = KEY_Z; break;
	case 0x21: key = KEY_RIGHT; break; case 0x22: key = KEY_LEFT; break;
	case 0x23: key = KEY_UP; break; case 0x20: key = KEY_DOWN; break;
	case 0xcc: case 0xe5: key = KEY_POWER; break;
	default: return;
	}
	if (hyn_gesture_data.report_key == key) return;
	hyn_gesture_data.report_key = key;
	input_event(input, EV_KEY, key, 1);
	input_event(input, EV_SYN, SYN_REPORT, 0);
	input_event(input, EV_KEY, key, 0);
	input_event(input, EV_SYN, SYN_REPORT, 0);
}

HYN_KEEP int hyn_gesture_readdata(void)
{
	u8 state, buf[12] = { 0 }, reg = CST_REG_GESTURE;
	int ret;
	if (!hyn_ts_data || !hyn_gesture_data.active || !hyn_gesture_data.mode)
		return -1;
	ret = hyn_i2c_read_byte(hyn_ts_data->client, CST_REG_GESTURE_ENABLE, &state);
	if (ret < 0 || state != 1) return -1;
	ret = hyn_i2c_read(hyn_ts_data->client, (char *)&reg, 1, (char *)buf, sizeof(buf));
	if (ret < 0) return ret;
	hyn_gesture_data.gesture_id = buf[0];
	hyn_gesture_data.point_num = 1;
	hyn_gesture_data.x[0] = ((buf[8] & 0xf) << 8) | buf[9];
	hyn_gesture_data.y[0] = ((buf[10] & 0xf) << 8) | buf[11];
	hyn_check_gesture(hyn_ts_data->input_dev, buf[0]);
	return 0;
}
HYN_KEEP void hyn_irq_gesture_mode(void)
{
	hyn_irq_disable();
	irq_set_irq_type(hyn_ts_data->irq,
			 IRQF_TRIGGER_FALLING | IRQF_NO_SUSPEND);
	hyn_irq_enable();
}
HYN_KEEP void hyn_irq_normal_mode(void)
{
	hyn_irq_disable();
	irq_set_irq_type(hyn_ts_data->irq,
			 hyn_ts_data->pdata->irq_gpio_flags);
	hyn_irq_enable();
}
HYN_KEEP int hyn_gesture_suspend(void)
{
	u8 state = 0; int i;
	if (!hyn_gesture_data.mode) return -1;
	hyn_i2c_write_byte(hyn_ts_data->client, CST_REG_GESTURE_ENABLE, 1);
	msleep(10);
	for (i = 0; i < 3; i++) {
		hyn_i2c_read_byte(hyn_ts_data->client, CST_REG_GESTURE_ENABLE, &state);
		if (state == 1) break;
		hyn_i2c_write_byte(hyn_ts_data->client, CST_REG_GESTURE_ENABLE, 1);
		msleep(10);
	}
	hyn_gesture_data.active = 1; hyn_gesture_data.report_key = 0;
	hyn_gesture_data.gesture_id = 0; hyn_irq_gesture_mode();
	return 0;
}
HYN_KEEP int hyn_gesture_resume(void)
{
	if (!hyn_gesture_data.mode) return -1;
	hyn_gesture_data.active = 0; hyn_gesture_data.report_key = 0;
	hyn_gesture_data.gesture_id = 0; hyn_irq_normal_mode();
	hyn_i2c_write_byte(hyn_ts_data->client, CST_REG_GESTURE_ENABLE, 0);
	return 0;
}
HYN_KEEP void hyn_gesture_recovery(struct i2c_client *client) { if (hyn_gesture_data.active) hyn_gesture_suspend(); }

static void cst8xx_touch_report(struct work_struct *work)
{
	u8 b[CST_TOUCH_BYTES] = { 0 }, reg = CST_REG_TOUCH;
	u8 count, event, id, area; u16 x, y;
	if (!hyn_ts_data) return;
	pm_wakeup_dev_event(hyn_ts_data->dev, 5000, true);
	if (hyn_gesture_data.active) { hyn_gesture_readdata(); hyn_irq_enable(); return; }
	if (hyn_i2c_read(hyn_ts_data->client, (char *)&reg, 1, (char *)b, sizeof(b)) < 0) {
		hyn_irq_enable(); return;
	}
	count = b[1] & 0x0f;
	if (count > 1) count = 1;
	if (!count) { tpd_up(0, 0); input_event(hyn_ts_data->input_dev, EV_SYN, SYN_REPORT, 0); hyn_irq_enable(); return; }
	event = b[2] >> 6; x = ((b[2] & 0xf) << 8) | b[3];
	id = b[4] >> 4; y = ((b[4] & 0xf) << 8) | b[5]; area = b[7] >> 4;
	if (event == 0 || event == 2) cst3xx_touch_down(hyn_ts_data->input_dev, id, x, y, area ? area : 0x28);
	else cst3xx_touch_up(hyn_ts_data->input_dev, id);
	input_event(hyn_ts_data->input_dev, EV_SYN, SYN_REPORT, 0);
	hyn_irq_enable();
}
static HYN_KEEP void cst3xx_touch_report(struct work_struct *work) { cst8xx_touch_report(work); }

static irqreturn_t hyn_eint_interrupt_handler(int irq, void *dev_id)
{
	hyn_irq_disable();
	if (hyn_ts_data && hyn_ts_data->wq) queue_work(hyn_ts_data->wq, &hyn_ts_data->work);
	return IRQ_HANDLED;
}

HYN_KEEP void hyn_enter_deep_sleep(void)
{
	(void)hyn_i2c_write_byte(hyn_ts_data->client, CST_REG_DEEP_SLEEP, CST_DEEP_SLEEP);
}

HYN_KEEP void hyn_ts_data_init(struct i2c_client *client)
{
	hyn_ts_data->client = client;
	hyn_ts_data->dev = &client->dev;
	hyn_ts_data->chip_type = 0x00b7;
	hyn_ts_data->chip_series = 800;
	hyn_ts_data->product_line = 2;
	hyn_ts_data->bootloader_addr = 0x15;
	hyn_ts_data->checkcode = 0xffffffff;
	client->addr = 0x15;
}

static int hyn_parse_dt(struct device *dev, struct hynitron_ts_platform_data *p)
{
	struct device_node *np = dev->of_node; enum of_gpio_flags flags;
	u32 coords[2], v;
	if (!np) return -ENODEV;
	(void)of_find_property(np, "hynitron,display-coords", NULL);
	p->irq_gpio = of_get_named_gpio_flags(np, "hynitron,irq-gpio", 0, &flags);
	p->reset_gpio = of_get_named_gpio_flags(np, "hynitron,reset-gpio", 0, &flags);
	p->vdd_gpio = of_get_named_gpio_flags(np, "hynitron,vdd-gpio", 0, &flags);
	if (!of_property_read_u32_array(np, "hynitron,display-coords", coords, 2)) {
		p->x_resolution = coords[0]; p->y_resolution = coords[1];
	}
	if (!of_property_read_u32(np, "hynitron,max-touch-number", &v)) p->max_touch_num = v;
	p->have_key = of_find_property(np, "hynitron,have-key", NULL) != NULL;
	return 0;
}
HYN_KEEP int hyn_platform_data_init(struct hynitron_ts_data *ts)
{
	ts->pdata = kzalloc(sizeof(*ts->pdata), GFP_KERNEL);
	if (!ts->pdata) return -ENOMEM;
	return hyn_parse_dt(ts->dev, ts->pdata);
}

HYN_KEEP int cst8xx_firmware_info(struct i2c_client *client)
{
	u8 reg = CST_REG_FW_INFO, b[6] = { 0 }; int ret;
	ret = hyn_i2c_read(client, (char *)&reg, 1, (char *)b, 6);
	if (ret < 0) return ret;
	hyn_ts_data->project_id = b[1]; hyn_ts_data->module_id = b[2];
	hyn_ts_data->fw_version = b[3]; hyn_ts_data->checksum = b[4];
	sprintf(second_touch_fw_version, "Vno: %x. %x. %x. %x.\n",
		hyn_ts_data->fw_version, hyn_ts_data->checksum,
		hyn_ts_data->module_id, hyn_ts_data->project_id);
	return 0;
}
HYN_KEEP int cst3xx_firmware_info(struct i2c_client *client) { return cst8xx_firmware_info(client); }
HYN_KEEP int hyn_firmware_info(struct i2c_client *client) { return cst8xx_firmware_info(client); }

HYN_KEEP int hyn_detect_bootloader(struct i2c_client *client)
{
	u8 cmd = 0xaa;
	int retry;
	int ret = -1;

	/* Stock CST8xx detection enters the ROM loader; it does not read 0xA7. */
	hyn_reset_proc(1);
	msleep(5);
	client->addr = 0x15;
	for (retry = 0; retry < 10; retry++) {
		cmd = 0xaa;
		if (hyn_i2c_write_bytes(0xa001, &cmd, 1, 2) < 0) {
			msleep(2);
			continue;
		}
		if (hyn_i2c_read_bytes(0xa003, &cmd, 1, 2) < 0 || cmd != 0x55) {
			msleep(2);
			continue;
		}
		ret = 0;
		break;
	}
	client->addr = 0x15;
	hyn_reset_proc(40);
	return ret;
}
static HYN_KEEP int hyn_find_fw_idx(u8 check_project_id)
{
	u16 type = hyn_ts_data->chip_type;
	u16 project = hyn_ts_data->project_id;
	if (check_project_id && project != 0)
		return -1;
	if (type == 0xb5) return 1;
	if (type == 0xb6) return 0;
	if (type == 0xb7) return 2;
	return -1;
}
HYN_KEEP int hyn_boot_update_fw(struct i2c_client *client)
{
	int idx, ret;

	idx = hyn_find_fw_idx(1);
	if (idx < 0)
		idx = hyn_find_fw_idx(0);
	if (idx == 1) {
		hyn_ts_data->selected_fw = cst816t_fw;
		hyn_ts_data->selected_fw_len = cst816t_fw_len;
	} else if (idx == 0 || idx == 2) {
		hyn_ts_data->selected_fw = cst8xx_fw;
		hyn_ts_data->selected_fw_len = cst8xx_fw_len;
	} else {
		return 0;
	}

	hyn_irq_disable();
	hyn_ts_data->work_mode = 1;
	/* The frozen stock CST78xx programming body is compiled out. */
	ret = cst8xx_firmware_info(client);
	hyn_irq_enable();
	hyn_ts_data->work_mode = 0;
#if HYNITRON_ALLOW_FW_PROGRAMMING
	/* No stock programmer exists in this ELF, so do not invent one. */
	return -ENOSYS;
#else
	return ret;
#endif
}
HYN_KEEP int hyn_update_firmware_init(struct i2c_client *client)
{
	int ret = hyn_firmware_info(client);

	hyn_ts_data->chip_series = 800;
	hyn_ts_data->product_line = 2;
	hyn_ts_data->bootloader_addr = 0x15;
	return ret;
}

HYN_KEEP int hyn_input_dev_int(struct hynitron_ts_data *ts)
{
	struct input_dev *in = input_allocate_device(); int ret;
	if (!in) return -ENOMEM;
	in->name = HYN_NAME; in->id.bustype = BUS_I2C; in->dev.parent = ts->dev;
	__set_bit(EV_SYN, in->evbit); __set_bit(EV_ABS, in->evbit); __set_bit(EV_KEY, in->evbit);
	__set_bit(BTN_TOUCH, in->keybit); __set_bit(INPUT_PROP_DIRECT, in->propbit);
	input_set_abs_params(in, ABS_MT_TRACKING_ID, 0, ts->pdata->max_touch_num, 0, 0);
	input_set_abs_params(in, ABS_MT_POSITION_X, 0, ts->pdata->x_resolution, 0, 0);
	input_set_abs_params(in, ABS_MT_POSITION_Y, 0, ts->pdata->y_resolution, 0, 0);
	input_set_abs_params(in, ABS_MT_TOUCH_MAJOR, 0, 255, 0, 0);
	input_set_abs_params(in, ABS_MT_WIDTH_MAJOR, 0, 200, 0, 0);
	ret = input_register_device(in); if (ret < 0) { input_free_device(in); return ret; }
	ts->input_dev = in;
	if (ts->chip_type == 0x00b7)
		INIT_WORK(&ts->work, cst8xx_touch_report);
	else
		INIT_WORK(&ts->work, cst3xx_touch_report);
	ts->wq = alloc_workqueue("hyn_wq", 0, 1); if (ts->wq) flush_workqueue(ts->wq);
	return 0;
}

HYN_KEEP int hyn_irq_init(struct i2c_client *client)
{
	const struct of_device_id *match; struct device_node *node;
	struct gpio_desc *desc = gpio_to_desc(hyn_ts_data->pdata->irq_gpio); int ret;
	node = of_find_matching_node_and_match(NULL, client->dev.driver->of_match_table, &match);
	if (!node || !desc) return -ENODEV;
	hyn_ts_data->irq = gpiod_to_irq(desc); hyn_ts_data->pdata->irq_gpio_flags = IRQF_TRIGGER_FALLING | IRQF_ONESHOT;
	ret = request_threaded_irq(hyn_ts_data->irq, NULL, hyn_eint_interrupt_handler,
				   hyn_ts_data->pdata->irq_gpio_flags, HYN_IRQ_NAME, hyn_ts_data);
	if (!ret) { client->irq = hyn_ts_data->irq; irq_set_irq_wake(hyn_ts_data->irq, 1); }
	return ret;
}

static ssize_t hyn_tpfwver_show(struct device *d, struct device_attribute *a, char *buf)
{
	int ret; mutex_lock(&hyn_ts_data->sysfs_lock); ret = cst8xx_firmware_info(hyn_ts_data->client);
	if (ret < 0) ret = snprintf(buf, PAGE_SIZE, "read firmware version fail\n");
	else ret = snprintf(buf, PAGE_SIZE, "chip_version: 0x%02X,module_version:0x%02X,project_version:0x%02X,chip_type:0x%02X,checksum:0x%02X .\n", hyn_ts_data->fw_version, hyn_ts_data->module_id, hyn_ts_data->project_id, hyn_ts_data->chip_type, hyn_ts_data->checksum);
	mutex_unlock(&hyn_ts_data->sysfs_lock); return ret;
}
static ssize_t hyn_tpfwver_store(struct device *d, struct device_attribute *a, const char *b, size_t c) { return -EPERM; }
static ssize_t hyn_fwupdate_show(struct device *d, struct device_attribute *a, char *b) { return -EPERM; }
static ssize_t hyn_fwupdate_store(struct device *d, struct device_attribute *a, const char *b, size_t c) { return hyn_boot_update_fw(hyn_ts_data->client) < 0 ? -EPERM : c; }
static ssize_t hyn_tprwreg_show(struct device *d, struct device_attribute *a, char *out)
{
	u8 b[6] = { 0xd0, 0x4f };
	if (cst3xx_i2c_read_register(hyn_ts_data->client, b, sizeof(b)) < 0)
		return -1;
	return snprintf(out, 128, "buf0:%d,buf1:%d,buf2:%d,buf3:%d,buf4:%d,buf5:%d .\n",
		b[0], b[1], b[2], b[3], b[4], b[5]);
}
static ssize_t hyn_tprwreg_store(struct device *d, struct device_attribute *a, const char *b, size_t c)
{
	u8 v[16] = { 0 };
	size_t n = c ? c - 1 : 0;
	int ret = 0;
	if (n > sizeof(v)) n = sizeof(v);
	mutex_lock(&hyn_ts_data->sysfs_lock);
	memcpy(v, b, n);
	if (n == 1) {
		switch (v[0]) {
		case 0x30: ret = cst3xx_firmware_info(hyn_ts_data->client); break;
		case 0x31: hyn_irq_disable(); break;
		case 0x32: hyn_irq_enable(); break;
		case 0x33: ret = hyn_reset_proc(10); break;
		case 0x34: ret = hyn_boot_update_fw(hyn_ts_data->client); break;
		}
	} else if (n == 2 && v[0] == 0x31) {
		hyn_ts_data->work_mode = (v[1] >= 0x30 && v[1] <= 0x34) ? v[1] - 0x30 : 0;
	} else if (n > 2) {
		ret = cst3xx_i2c_write(hyn_ts_data->client, v, n);
	}
	mutex_unlock(&hyn_ts_data->sysfs_lock);
	return ret < 0 ? -1 : (ssize_t)c;
}
static ssize_t hyn_fwupgradeapp_show(struct device *d, struct device_attribute *a, char *b) { return -EPERM; }
static ssize_t hyn_fwupgradeapp_store(struct device *d, struct device_attribute *a, const char *b, size_t c)
{
	char fwname[256] = { 0 };
	u8 *fw;
	size_t len = hyn_ts_data->selected_fw_len;
	if (!len)
		return -ENOMEM;
	sprintf(fwname, "/mnt/%s", b);
	if (c && c - 1 + 5 < sizeof(fwname)) fwname[c - 1 + 5] = '\0';
	fw = kmalloc(len, GFP_KERNEL);
	if (!fw)
		return -ENOMEM;
	mutex_lock(&hyn_ts_data->sysfs_lock);
	/* Stock ELF has no linked file-reader or flash-programmer call here. */
	mutex_unlock(&hyn_ts_data->sysfs_lock);
	kfree(fw);
	return c;
}
static ssize_t hyntpfactorytest_show(struct device *d, struct device_attribute *a, char *b) { return 0; }
static ssize_t hyntpfactorytest_store(struct device *d, struct device_attribute *a, const char *b, size_t c) { return c; }
static ssize_t hyn_gesture_show(struct device *d, struct device_attribute *a, char *b) { return sprintf(b, "Gesture Mode: %s\nReg = %d\n", hyn_gesture_data.mode ? "On" : "Off", hyn_gesture_data.gesture_id); }
static ssize_t hyn_gesture_store(struct device *d, struct device_attribute *a, const char *b, size_t c) { if (b[0] == 1) hyn_gesture_data.mode = 1; else if (b[0] == 0) hyn_gesture_data.mode = 0; return c; }
static ssize_t hyn_gesture_buf_show(struct device *d, struct device_attribute *a, char *b) { return snprintf(b, PAGE_SIZE, "Gesture ID: 0x%x\nGesture PointNum: %d\nGesture Point Buf:\n  0(%4d,%4d) \n", hyn_gesture_data.gesture_id, hyn_gesture_data.point_num, hyn_gesture_data.x[0], hyn_gesture_data.y[0]); }
static ssize_t hyn_gesture_buf_store(struct device *d, struct device_attribute *a, const char *b, size_t c) { return -EPERM; }

static DEVICE_ATTR(hyntpfwver, 0644, hyn_tpfwver_show, hyn_tpfwver_store);
static DEVICE_ATTR(hynfwupdate, 0644, hyn_fwupdate_show, hyn_fwupdate_store);
static DEVICE_ATTR(hyntprwreg, 0644, hyn_tprwreg_show, hyn_tprwreg_store);
static DEVICE_ATTR(hynfwupgradeapp, 0644, hyn_fwupgradeapp_show, hyn_fwupgradeapp_store);
static DEVICE_ATTR(hyntpfactorytest, 0644, hyntpfactorytest_show, hyntpfactorytest_store);
static DEVICE_ATTR(hyn_gesture_mode, 0644, hyn_gesture_show, hyn_gesture_store);
static DEVICE_ATTR(hyn_gesture_buf, 0644, hyn_gesture_buf_show, hyn_gesture_buf_store);
static struct attribute *hyn_attrs[] = { &dev_attr_hyntpfwver.attr, &dev_attr_hynfwupdate.attr, &dev_attr_hyntprwreg.attr, &dev_attr_hynfwupgradeapp.attr, &dev_attr_hyntpfactorytest.attr, NULL };
static const struct attribute_group hyn_attribute_group = { .attrs = hyn_attrs };
static struct attribute *hyn_gesture_mode_attrs[] = { &dev_attr_hyn_gesture_mode.attr, &dev_attr_hyn_gesture_buf.attr, NULL };
static const struct attribute_group hyn_gesture_group = { .attrs = hyn_gesture_mode_attrs };
HYN_KEEP int hyn_create_sysfs(struct i2c_client *client)
{
	hyn_ts_data->kobj = kobject_create_and_add(HYN_SYSFS_NAME, NULL);
	if (!hyn_ts_data->kobj) return -ENOMEM;
	return sysfs_create_group(hyn_ts_data->kobj, &hyn_attribute_group);
}
HYN_KEEP int hyn_create_gesture_sysfs(struct i2c_client *client)
{
	if (!hyn_ts_data->kobj)
		return 0;
	return sysfs_create_group(hyn_ts_data->kobj, &hyn_gesture_group);
}
HYN_KEEP void hyn_release_sysfs(struct i2c_client *client) { if (hyn_ts_data && hyn_ts_data->kobj) sysfs_remove_group(hyn_ts_data->kobj, &hyn_attribute_group); }
HYN_KEEP int hyn_gesture_init(struct input_dev *input, struct i2c_client *client)
{
	int keys[] = { KEY_POWER, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_O, KEY_E, KEY_M, KEY_W, KEY_S, KEY_V, KEY_Z, KEY_C }; int i;
	for (i = 0; i < ARRAY_SIZE(keys); i++) input_set_capability(input, EV_KEY, keys[i]);
	hyn_gesture_data.mode = 1; return hyn_create_gesture_sysfs(client);
}
HYN_KEEP int hyn_gesture_exit(void)
{
	if (hyn_ts_data && hyn_ts_data->kobj)
		sysfs_remove_group(hyn_ts_data->kobj, &hyn_gesture_group);
	return 0;
}

void tiny_tp_gesture_contorl(int enable)
{
	if (!hyn_ts_data) return;
	tiny_tpgesture_status = enable ? 1 : 0;
}
EXPORT_SYMBOL(tiny_tp_gesture_contorl);

void tiny_tp_power_contorl(int enable)
{
	if (!hyn_ts_data) return;
	if (!enable) {
		if (hyn_ts_data->suspended) return;
		hyn_ts_data->suspended = true; hyn_reset_proc(10);
		if (tiny_tpgesture_status) hyn_gesture_suspend();
		else { hyn_irq_disable(); hyn_enter_deep_sleep(); }
	} else {
		if (!hyn_ts_data->suspended) return;
		hyn_ts_data->suspended = false; hyn_reset_proc(40); hyn_release_all_finger();
		hyn_gesture_data.active = 0;
		if (tiny_tpgesture_status) hyn_gesture_resume(); else hyn_irq_enable();
	}
}
EXPORT_SYMBOL(tiny_tp_power_contorl);

static int hyn_probe(struct i2c_client *client, const struct i2c_device_id *id)
{
	int ret; struct hynitron_ts_data *ts;
	(void)of_match_device(client->dev.driver->of_match_table, &client->dev);
	ts = kzalloc(sizeof(*ts), GFP_KERNEL); if (!ts) return -ENOMEM;
	hyn_ts_data = ts;
	ts->client = client;
	ts->dev = &client->dev;
	mutex_init(&ts->sysfs_lock);
	ret = hyn_platform_data_init(ts); if (ret) goto err;
	ret = gpio_request(ts->pdata->vdd_gpio, "hyn_vdd_gpio"); if (ret) goto err;
	gpiod_direction_output_raw(gpio_to_desc(ts->pdata->vdd_gpio), 1);
	ret = gpio_request(ts->pdata->irq_gpio, "hyn_irq_gpio"); if (ret) goto err_gpio_vdd;
	gpiod_direction_input(gpio_to_desc(ts->pdata->irq_gpio));
	ret = gpio_request(ts->pdata->reset_gpio, "hyn_reset_gpio"); if (ret) goto err_gpio_irq;
	gpiod_direction_output_raw(gpio_to_desc(ts->pdata->reset_gpio), 1);
	hyn_reset_proc(40);
	hyn_ts_data_init(client);
	mdelay(60);
	ret = hyn_firmware_info(client);
	if (ret < 0) {
		ret = hyn_detect_bootloader(client);
		if (ret < 0)
			goto err_gpio_reset;
		mdelay(100);
	}
	ret = hyn_input_dev_int(ts); if (ret) goto err_gpio_reset;
	ret = hyn_irq_init(client); if (ret) goto err_input;
	hyn_irq_disable();
	(void)hyn_update_firmware_init(client);
	ret = hyn_create_sysfs(client); if (ret) goto err_irq;
	ret = hyn_gesture_init(ts->input_dev, client); if (ret) goto err_irq;
	hyn_reset_proc(40); hyn_irq_enable();
	yft_set_touch_device_used(HYN_NAME, 1);
	return 0;
err_irq: free_irq(ts->irq, ts);
err_input: if (ts->input_dev) input_free_device(ts->input_dev);
err_gpio_reset: gpio_free(ts->pdata->reset_gpio);
err_gpio_irq: gpio_free(ts->pdata->irq_gpio);
err_gpio_vdd: gpio_free(ts->pdata->vdd_gpio);
err: kfree(ts->pdata); kfree(ts); hyn_ts_data = NULL; return ret;
}
static void hyn_remove(struct i2c_client *client)
{
	struct hynitron_ts_data *ts = hyn_ts_data; if (!ts) return;
	hyn_gesture_exit(); hyn_release_sysfs(client); free_irq(ts->irq, ts);
	if (ts->wq) flush_workqueue(ts->wq);
	if (ts->input_dev) input_free_device(ts->input_dev);
	gpio_free(ts->pdata->reset_gpio); gpio_free(ts->pdata->irq_gpio); gpio_free(ts->pdata->vdd_gpio);
	kfree(ts->pdata); kfree(ts); hyn_ts_data = NULL;
}
static int hyn_detect(struct i2c_client *client, struct i2c_board_info *info)
{
	memcpy(info->type, HYN_NAME, sizeof(HYN_NAME));
	return 0;
}
static const struct i2c_device_id hyn_tpd_id[] = { { HYN_NAME, 0 }, { } };
MODULE_DEVICE_TABLE(i2c, hyn_tpd_id);
static const struct of_device_id hyn_dt_match[] = { { .compatible = HYN_COMPAT }, { } };
MODULE_DEVICE_TABLE(of, hyn_dt_match);
static struct i2c_driver hynitron_i2c_driver = {
	.driver = { .name = HYN_NAME, .of_match_table = hyn_dt_match, .pm = NULL },
	.probe = hyn_probe, .remove = hyn_remove, .id_table = hyn_tpd_id, .detect = hyn_detect,
};
static int __init hynitron_driver_init(void) { yft_touchpanel_device_add(&hynitron_i2c_driver, 0); return i2c_add_driver(&hynitron_i2c_driver); }
static void __exit hynitron_driver_exit(void) { i2c_del_driver(&hynitron_i2c_driver); }
module_init(hynitron_driver_init);
module_exit(hynitron_driver_exit);
MODULE_AUTHOR("Hynitron Driver Team");
MODULE_DESCRIPTION("Hynitron Touchscreen Driver");
MODULE_LICENSE("GPL v2");
