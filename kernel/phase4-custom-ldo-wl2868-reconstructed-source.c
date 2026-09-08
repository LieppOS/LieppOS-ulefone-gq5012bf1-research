// SPDX-License-Identifier: GPL-2.0
/*
 * Reconstruction of Ulefone GQ5012BF1 custom_ldo_wl2868.ko.
 *
 * This is intentionally a raw-I2C/custom-ABI driver, not a regulator
 * framework driver.  The stock oracle exposes will_ldo_{vout,en} to
 * custom_ldo.ko and exposes a wl2864c misc device to camera userspace.
 */
#include <linux/i2c.h>
#include <linux/miscdevice.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/gpio/consumer.h>
#include <linux/fs.h>
#include <linux/slab.h>
#include <linux/uaccess.h>
#include <linux/delay.h>
#include <linux/kernel.h>

#define WL2864C_REG_ENABLE 0x0e
#define WL2864C_MAX_LDO 7
#define WL2864C_VOUT_FIRST 0x03

struct wl2864c_state {
	struct i2c_client *client;
	struct gpio_desc *reset;
	struct gpio_desc *vin1_en;
	int vin2_gpio;
	u8 chip_id;
	loff_t read_pos;
	bool opened;
};

static struct wl2864c_state wl2864c_data;

int wl2864c_vin2_power(int power)
{
	struct gpio_desc *desc = gpio_to_desc(wl2864c_data.vin2_gpio);

	gpiod_set_raw_value(desc, power != 0);
	return 0;
}

/* The two recovered constant tables are the compiler-visible stock tables.
 * The units of the exported voltage argument are not named in the oracle;
 * preserve the arithmetic rather than silently substituting regulator-uV
 * semantics from a donor driver.
 */
static const int wl2864c_vout_limit[WL2864C_MAX_LDO] =
	{ 60000, 60000, 120000, 120000, 120000, 120000, 120000 };
static const int wl2864c_vout_offset[WL2864C_MAX_LDO] =
	{ -6000, -6000, -12000, -12000, -12000, -12000, -12000 };
static const int wl2868c_vout_limit[WL2864C_MAX_LDO] =
	{ 49600, 49600, 150400, 150400, 150400, 150400, 150400 };
static const int wl2868c_vout_offset[WL2864C_MAX_LDO] =
	{ -4960, -4960, -15040, -15040, -15040, -15040, -15040 };

static int wl2864c_read_reg(u8 reg, u8 *value)
{
	struct i2c_msg msg[2];
	u8 command = reg;
	int ret;

	if (!wl2864c_data.client)
		return -ENODEV;
	msg[0] = (struct i2c_msg) {
		.addr = wl2864c_data.client->addr, .flags = 0,
		.len = 1, .buf = &command,
	};
	msg[1] = (struct i2c_msg) {
		.addr = wl2864c_data.client->addr, .flags = I2C_M_RD,
		.len = 1, .buf = value,
	};
	ret = i2c_transfer(wl2864c_data.client->adapter, msg, 2);
	return ret < 0 ? ret : 0;
}

static int wl2864c_write_reg(u8 reg, u8 value)
{
	struct i2c_msg msg;
	u8 data[2] = { reg, value };
	int ret;

	if (!wl2864c_data.client)
		return -ENODEV;
	msg = (struct i2c_msg) {
		.addr = wl2864c_data.client->addr, .flags = 0,
		.len = sizeof(data), .buf = data,
	};
	ret = i2c_transfer(wl2864c_data.client->adapter, &msg, 1);
	return ret < 0 ? ret : 0;
}

static noinline int wl2864c_vout_common(int ldo_num, int value, bool wl2868)
{
	const int *limit = wl2868 ? wl2868c_vout_limit : wl2864c_vout_limit;
	const int *offset = wl2868 ? wl2868c_vout_offset : wl2864c_vout_offset;
	int index, write_value, read_value, ret;

	if (ldo_num < 1 || ldo_num > WL2864C_MAX_LDO)
		return -1;
	index = ldo_num - 1;
	/* The stock arithmetic is signed value/100 followed by /125. */
	write_value = (value / 100 + offset[index]) / 125;
	if (limit[index] <= value)
		write_value = 0;
	ret = wl2864c_write_reg(WL2864C_VOUT_FIRST + index,
		(u8)write_value);
	read_value = 0;
	if (!ret)
		ret = wl2864c_read_reg(WL2864C_VOUT_FIRST + index,
			(u8 *)&read_value);
	dev_info(&wl2864c_data.client->dev,
		"%s: ldo_num=%d, ldo_vout(write_val:%x, read_val:%u), ret=%d\n",
		__func__, ldo_num, write_value & 0xff, read_value & 0xff, ret);
	return ret;
}

static noinline int wl2864c_en_common(int ldo_num, int enable, bool wl2868)
{
	u8 value;
	int ret;

	if (ldo_num < 1 || ldo_num > WL2864C_MAX_LDO)
		return 0;
	ret = wl2864c_read_reg(WL2864C_REG_ENABLE, &value);
	if (ret)
		return ret;
	if (enable)
		value |= BIT(ldo_num - 1);
	else
		value &= ~BIT(ldo_num - 1);
	if (wl2868 && value == 0)
		value |= BIT(7);
	ret = wl2864c_write_reg(WL2864C_REG_ENABLE, value);
	dev_info(&wl2864c_data.client->dev,
		"%s: ldo_num=%d, ldo_en write val=%x, ret=%d\n",
		__func__, ldo_num, value, ret);
	return ret;
}

static noinline int wl2864c_ldo_vout(int ldo_num, int value)
{
	return wl2864c_vout_common(ldo_num, value, false);
}

static noinline int wl2864c_ldo_en(int ldo_num, int enable)
{
	return wl2864c_en_common(ldo_num, enable, false);
}

static noinline int wl2868c_ldo_vout(int ldo_num, int value)
{
	return wl2864c_vout_common(ldo_num, value, true);
}

static noinline int wl2868c_ldo_en(int ldo_num, int enable)
{
	return wl2864c_en_common(ldo_num, enable, true);
}

/* Critical inter-module ABI: keep these int,int prototypes and names. */
int will_ldo_vout(int ldo_num, int value)
{
	if (wl2864c_data.chip_id == 0x82)
		return wl2868c_ldo_vout(ldo_num, value);
	if (wl2864c_data.chip_id == 1)
		return wl2864c_ldo_vout(ldo_num, value);
	return -1;
}
EXPORT_SYMBOL_GPL(will_ldo_vout);

int will_ldo_en(int ldo_num, int enable)
{
	if (wl2864c_data.chip_id == 0x82)
		return wl2868c_ldo_en(ldo_num, enable);
	if (wl2864c_data.chip_id == 1)
		return wl2864c_ldo_en(ldo_num, enable);
	return -1;
}
EXPORT_SYMBOL_GPL(will_ldo_en);

static loff_t wl2864c_llseek(struct file *file, loff_t offset, int whence)
{
	printk(KERN_INFO "wl2864c_llseek: update read pos to %02llX\\n",
		(unsigned long long)wl2864c_data.read_pos);
	if (whence == SEEK_CUR)
		wl2864c_data.read_pos += offset;
	else
		wl2864c_data.read_pos = 0;
	return wl2864c_data.read_pos;
}

static noinline int wl2864c_open(struct inode *inode, struct file *file)
{
	if (wl2864c_data.opened)
		return -ENODEV;
	wl2864c_data.opened = true;
	wl2864c_data.read_pos = 0;
	return 0;
}

static noinline int wl2864c_release(struct inode *inode, struct file *file)
{
	wl2864c_data.opened = false;
	return 0;
}

static noinline ssize_t wl2864c_read(struct file *file, char __user *user,
		size_t count, loff_t *pos)
{
	char *out;
	size_t i, out_len = 0;
	int ret;
	u8 value, reg;

	if (count > 20)
		return -EINVAL;
	out = kmalloc(3264, GFP_KERNEL);
	if (!out)
		return -ENOMEM;
	for (i = 0; i < count; ++i) {
		reg = (u8)(*pos + i);
		ret = wl2864c_read_reg(reg, &value);
		if (ret) {
			kfree(out);
			return ret;
		}
		out[out_len++] = "0123456789ABCDEF"[(reg >> 4) & 0xf];
		out[out_len++] = "0123456789ABCDEF"[reg & 0xf];
		out[out_len++] = ' ';
		out[out_len++] = "0123456789ABCDEF"[(value >> 4) & 0xf];
		out[out_len++] = "0123456789ABCDEF"[value & 0xf];
		out[out_len++] = ' ';
	}
	if (copy_to_user(user, out, out_len)) {
		kfree(out);
		return -EFAULT;
	}
	*pos += count;
	kfree(out);
	return out_len;
}

static int wl2864c_hex(char c)
{
	if (c >= '0' && c <= '9')
		return c - '0';
	if (c >= 'a' && c <= 'f')
		return c - 'a' + 10;
	if (c >= 'A' && c <= 'F')
		return c - 'A' + 10;
	return -1;
}

static noinline ssize_t wl2864c_write(struct file *file, const char __user *user,
		size_t count, loff_t *pos)
{
	char *in;
	size_t i;
	int hi, lo, ret = 0;
	u8 reg, value;

	if (count > 128)
		return -EINVAL;
	in = memdup_user(user, count);
	if (IS_ERR(in))
		return PTR_ERR(in);
	for (i = 0; i + 4 < count; i += 6) {
		hi = wl2864c_hex(in[i]);
		lo = wl2864c_hex(in[i + 1]);
		if (hi < 0 || lo < 0 || in[i + 2] != ' ') {
			ret = -ENODEV;
			break;
		}
		reg = (hi << 4) | lo;
		hi = wl2864c_hex(in[i + 3]);
		lo = wl2864c_hex(in[i + 4]);
		if (hi < 0 || lo < 0) {
			ret = -ENODEV;
			break;
		}
		value = (hi << 4) | lo;
		ret = wl2864c_write_reg(reg, value);
		if (ret)
			break;
	}
	kfree(in);
	return ret ? ret : count;
}

static const struct file_operations wl2864c_fops = {
	.owner = THIS_MODULE,
	.llseek = wl2864c_llseek,
	.read = wl2864c_read,
	.write = wl2864c_write,
	.open = wl2864c_open,
	.release = wl2864c_release,
};

static struct miscdevice wl2864c_miscdev = {
	.minor = MISC_DYNAMIC_MINOR,
	.name = "wl2864c",
	.fops = &wl2864c_fops,
};

static noinline int wl2864c_probe(struct i2c_client *client,
		const struct i2c_device_id *id)
{
	struct device *dev = &client->dev;
	int ret;
	u8 id_value = 0;

	wl2864c_data.client = client;
	wl2864c_data.reset = devm_gpiod_get(dev, "reset", GPIOD_OUT_HIGH);
	if (IS_ERR(wl2864c_data.reset)) {
		dev_err(dev, "failed to request reset GPIO: %ld\\n",
			PTR_ERR(wl2864c_data.reset));
		return PTR_ERR(wl2864c_data.reset);
	}
	gpiod_set_value(wl2864c_data.reset, 1);
	devm_gpiod_put(dev, wl2864c_data.reset);
	wl2864c_data.vin1_en = devm_gpiod_get(dev, "vin1_en", GPIOD_OUT_HIGH);
	if (IS_ERR(wl2864c_data.vin1_en)) {
		dev_err(dev, "failed to request vin1_en GPIO: %ld\\n",
			PTR_ERR(wl2864c_data.vin1_en));
		return PTR_ERR(wl2864c_data.vin1_en);
	}
	gpiod_set_value(wl2864c_data.vin1_en, 1);
	usleep_range(10000, 11000);
	gpiod_set_value(wl2864c_data.vin1_en, 0);
	usleep_range(10000, 11000);
	gpiod_set_value(wl2864c_data.vin1_en, 1);
	devm_gpiod_put(dev, wl2864c_data.vin1_en);
	msleep(1);

	ret = wl2864c_read_reg(0x00, &id_value);
	if (ret)
		return ret;
	wl2864c_data.chip_id = id_value;
	ret = misc_register(&wl2864c_miscdev);
	if (ret)
		return ret;
	return 0;
}

static noinline void wl2864c_remove(struct i2c_client *client)
{
	misc_deregister(&wl2864c_miscdev);
	wl2864c_data.chip_id = 0;
	wl2864c_data.client = NULL;
}

static const struct of_device_id wl2864c_dt_match[] = {
	{ .compatible = "will,wl2864c_pmu" },
	{ }
};
MODULE_DEVICE_TABLE(of, wl2864c_dt_match);

static const struct i2c_device_id wl2864c_id[] = {
	{ "wl2864c", 0 },
	{ }
};
MODULE_DEVICE_TABLE(i2c, wl2864c_id);

static struct i2c_driver wl2864c_i2c_driver = {
	.driver = {
		.name = "wl2864c",
		.of_match_table = wl2864c_dt_match,
	},
	.probe = wl2864c_probe,
	.remove = wl2864c_remove,
	.id_table = wl2864c_id,
};

module_i2c_driver(wl2864c_i2c_driver);
MODULE_DESCRIPTION("WL2864 & WL2868 Power IC Driver");
MODULE_LICENSE("GPL v2");
