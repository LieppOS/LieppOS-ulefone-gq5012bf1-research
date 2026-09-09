// SPDX-License-Identifier: GPL-2.0
/*
 * Static reconstruction of Ulefone GQ5012BF1 sh366003_fg.ko.
 *
 * IMPORTANT: gauge data-flash programming is compiled in but fail-closed in
 * the development build.  Set SH366003_ALLOW_AFI_PROGRAMMING=1 only to make
 * an oracle-parity build; never enable it on development hardware.
 */
#include <linux/bitops.h>
#include <linux/delay.h>
#include <linux/device.h>
#include <linux/i2c.h>
#include <linux/jiffies.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/of.h>
#include <linux/power_supply.h>
#include <linux/slab.h>
#include <linux/string.h>
#include <linux/workqueue.h>

#ifndef SH366003_ALLOW_AFI_PROGRAMMING
#define SH366003_ALLOW_AFI_PROGRAMMING 0
#endif

#define SH366003_NAME                 "sh366003"
#define SH366003_PSY_NAME             "3rd-gauge"
#define SH366003_I2C_ADDR             0x55
#define SH366003_DEVICE_ID            0x0603
#define SH366003_PROFILE_VERSION      0x5a93
#define SH366003_AFI_VERSION          0x8cd3
#define SH366003_MIN_UPDATE_SOC       11
#define SH366003_MIN_FCC              3500
#define SH366003_MONITOR_FIRST        2500
#define SH366003_MONITOR_PERIOD       1250
#define SH366003_UPDATE_DELAY         3000

#define CMD_MAC                       BIT(27)
#define CMD_CONTROL                   BIT(26)
#define CMD_DEVICE_ID                 (CMD_CONTROL | 0x0001)
#define SBS_CONTROL                   0x00
#define SBS_TEMP                      0x06
#define SBS_VOLTAGE                   0x08
#define SBS_BATTERY_STATUS            0x0a
#define SBS_CURRENT                   0x0c
#define SBS_REMAINING_CAPACITY        0x10
#define SBS_FCC                       0x12
#define SBS_INT_TEMP                  0x28
#define SBS_CYCLE_COUNT               0x2a
#define SBS_RSOC                      0x2c
#define SBS_SOH                       0x2e
#define SBS_VCHG                      0x30
#define SBS_ICHG                      0x32
#define SBS_MAC                       0x3e
#define SBS_MAC_DATA                  0x40
#define SBS_MAC_CHECKSUM              0x60

#define MAC_SEAL                      0x0030
#define MAC_RESET                     0x0041
#define MAC_AFI_VERSION               0x0046
#define MAC_MANUFACTURER_NAME         0x004c
#define MAC_PROFILE_DATE              0x004d
#define MAC_SERIAL                    0x004e
#define MAC_SAFETY_ALERT              0x0050
#define MAC_SAFETY_STATUS             0x0051
#define MAC_PF_ALERT                  0x0052
#define MAC_PF_STATUS                 0x0053
#define MAC_OPERATION_STATUS          0x0054
#define MAC_CHARGING_STATUS           0x0055
#define MAC_GAUGING_STATUS            0x0056
#define MAC_MANUFACTURING_STATUS      0x0057
#define MAC_MAX_VOLTAGE_BLOCK         0x0060
#define MAC_RECOVER_21                0x0021
#define MAC_RECOVER_67                0x0067
#define MAC_DA_STATUS1                0x0071
#define MAC_RUN_STATE                 0x00c1
#define MAC_POST_UPDATE_BLOCK         0x00c5
#define MAC_FW_TEXT                   0x40d9

extern char fuelgauge_fw_version[30];
extern int yft_fuelgauge_device_add(struct i2c_driver *driver, int used);
extern int yft_set_fuelgauge_device_used(char *name, int used);

static volatile int sh366003_allow_afi_programming =
	SH366003_ALLOW_AFI_PROGRAMMING;
u8 fg_sh366003_log;
const char *device2str = SH366003_NAME;
static char gauge_interface[10] __maybe_unused = "I2C";
static u16 chipid;
static struct class *sh_fg_class;

struct sh_fg_chip {
	struct device *dev;
	struct i2c_client *client;
	struct mutex io_lock;
	struct mutex soc_lock;
	struct mutex voltage_lock;
	struct mutex current_lock;
	struct mutex temp_lock;
	u8 address;
	char manufacturer[8];
	u32 regs[16];
	struct delayed_work monitor_work;
	struct delayed_work update_work;
	int soc;
	int voltage;
	int cached_current;
	int temp;
	int fallback_soc;
	int fallback_voltage;
	int fallback_current;
	int fallback_temp;
	int use_fallback;
	int force_upgrade;
	struct power_supply *psy;
	struct power_supply_desc psy_desc;
	struct power_supply_config psy_cfg;
	u8 adapter_status;
	int gauge_soh;
	int display_soh;
	int cycle_count;
	int remaining_capacity;
	int fcc;
	int reserved_360;
	int vchg;
	int ichg;
	int battery_status;
	int serial;
	int maximum_voltage_sum;
	int manufacturing_date;
	int manufacturing_day;
	int manufacturing_month;
	int manufacturing_year;
	int auto_update;
};

static struct sh_fg_chip *g_sm;
static u8 cmp_buff[512];

static const u32 sh366003_regs[16] = {
	0x08000001, 0x08000000, 0x0100006e, 0x00000006,
	0x0000002c, 0x00000064, 0x00000008, 0x0000000c,
	0x0000001e, 0x00000006, 0x0000000c, 0x0000000e,
	0x88000041, 0x0000001a, 0x0000003c, 0x04000001,
};

#include "sinofs_afi_data.inc"

noinline int sh_fg_get_soc(void)
{
	if (!g_sm)
		return 0;
	return g_sm->use_fallback == 1 ? g_sm->fallback_soc : g_sm->soc;
}

noinline int sh_fg_get_vbat(void)
{
	if (!g_sm)
		return 0;
	return g_sm->use_fallback == 1 ? g_sm->fallback_voltage : g_sm->voltage;
}

noinline int sh_fg_get_ibat(void)
{
	if (!g_sm)
		return 0;
	return g_sm->use_fallback == 1 ? g_sm->fallback_current : g_sm->cached_current;
}

noinline int sh_fg_get_tbat(void)
{
	if (!g_sm)
		return 0;
	return g_sm->use_fallback == 1 ? g_sm->fallback_temp : g_sm->temp;
}

static noinline int fg_read_sbs_word(struct sh_fg_chip *sm, u32 command,
				     u16 *value)
{
	s32 ret;

	mutex_lock(&sm->io_lock);
	if (command & CMD_MAC) {
		ret = i2c_smbus_write_word_data(sm->client, SBS_MAC,
						command & 0xffff);
		if (ret < 0)
			goto out;
		msleep(3);
		ret = i2c_smbus_read_word_data(sm->client, SBS_MAC_DATA);
	} else if (command & CMD_CONTROL) {
		ret = i2c_smbus_write_word_data(sm->client, SBS_CONTROL,
						command & 0xffff);
		if (ret < 0)
			goto out;
		mdelay(10);
		ret = i2c_smbus_read_word_data(sm->client, SBS_CONTROL);
	} else {
		ret = i2c_smbus_read_word_data(sm->client, command & 0xff);
	}
	if (ret >= 0)
		*value = ret;
out:
	mutex_unlock(&sm->io_lock);
	return ret < 0 ? ret : 0;
}

static noinline int fg_read_block(struct sh_fg_chip *sm, u32 command,
				  u8 length, u8 *data)
{
	struct i2c_msg msgs[2];
	u8 reg = SBS_MAC_DATA;
	int ret;

	mutex_lock(&sm->io_lock);
	ret = i2c_smbus_write_word_data(sm->client, SBS_MAC, command & 0xffff);
	if (ret < 0)
		goto out;
	msleep(3);
	msgs[0].addr = sm->client->addr;
	msgs[0].flags = 0;
	msgs[0].len = 1;
	msgs[0].buf = &reg;
	msgs[1].addr = sm->client->addr;
	msgs[1].flags = I2C_M_RD;
	msgs[1].len = length;
	msgs[1].buf = data;
	ret = i2c_transfer(sm->client->adapter, msgs, 2);
	if (ret >= 0)
		ret = 0;
out:
	mutex_unlock(&sm->io_lock);
	return ret;
}

static noinline int fg_read_SOC(struct sh_fg_chip *sm)
{
	s32 ret;

	mutex_lock(&sm->io_lock);
	ret = i2c_smbus_read_word_data(sm->client, SBS_RSOC);
	mutex_unlock(&sm->io_lock);
	if (ret < 0)
		return ret;
	mutex_lock(&sm->soc_lock);
	sm->soc = ret;
	mutex_unlock(&sm->soc_lock);
	return 0;
}

static noinline int fg_read_Voltage(struct sh_fg_chip *sm)
{
	s32 ret;

	mutex_lock(&sm->io_lock);
	ret = i2c_smbus_read_word_data(sm->client, SBS_VOLTAGE);
	mutex_unlock(&sm->io_lock);
	if (ret < 0)
		return ret;
	mutex_lock(&sm->voltage_lock);
	sm->voltage = ret;
	mutex_unlock(&sm->voltage_lock);
	return 0;
}

static noinline int fg_read_Current(struct sh_fg_chip *sm)
{
	s32 ret;
	int value;

	mutex_lock(&sm->io_lock);
	ret = i2c_smbus_read_word_data(sm->client, SBS_CURRENT);
	mutex_unlock(&sm->io_lock);
	if (ret < 0)
		return ret;
	value = (s16)ret;
	if (value < 0)
		value = -value;
	mutex_lock(&sm->current_lock);
	sm->cached_current = value * 1000;
	mutex_unlock(&sm->current_lock);
	return 0;
}

static noinline int fg_read_ExtTemperature(struct sh_fg_chip *sm)
{
	s32 ret;

	mutex_lock(&sm->io_lock);
	ret = i2c_smbus_read_word_data(sm->client, SBS_TEMP);
	mutex_unlock(&sm->io_lock);
	if (ret < 0)
		return ret;
	mutex_lock(&sm->temp_lock);
	sm->temp = ret - 2731;
	mutex_unlock(&sm->temp_lock);
	return 0;
}

static noinline int fg_read_IntTemperature(struct sh_fg_chip *sm, u16 *value)
{
	return fg_read_sbs_word(sm, SBS_INT_TEMP, value);
}

static noinline int fg_read_IntManufacturedate(struct sh_fg_chip *sm)
{
	u8 data[2] = { 0 };
	int ret;
	u16 d;

	ret = fg_read_block(sm, CMD_MAC | MAC_PROFILE_DATE, 2, data);
	if (ret < 0)
		return ret;
	d = data[0] | (data[1] << 8);
	sm->manufacturing_date = d;
	sm->manufacturing_day = d & 0x1f;
	sm->manufacturing_month = (d >> 5) & 0x0f;
	sm->manufacturing_year = (d >> 9) + 1980;
	return 0;
}

static noinline int fg_read_fcc(struct sh_fg_chip *sm)
{
	s32 ret;

	mutex_lock(&sm->io_lock);
	ret = i2c_smbus_read_word_data(sm->client, SBS_FCC);
	mutex_unlock(&sm->io_lock);
	if (ret >= 0)
		sm->fcc = ret;
	return ret < 0 ? ret : 0;
}

noinline bool hal_fg_init(struct i2c_client *client)
{
	struct sh_fg_chip *sm = i2c_get_clientdata(client);
	u16 value;

	return sm && fg_read_sbs_word(sm, sm->regs[0], &value) >= 0;
}

static noinline int fg_gauge_unseal(struct sh_fg_chip *sm)
{
	static const u16 keys[] = { 0x5678, 0x1234, 0xcdef, 0x90ab };
	u16 status;
	int i, ret;

	for (i = 0; i < ARRAY_SIZE(keys); i++) {
		mutex_lock(&sm->io_lock);
		ret = i2c_smbus_write_word_data(sm->client, SBS_CONTROL, keys[i]);
		mutex_unlock(&sm->io_lock);
		if (ret < 0)
			return ret;
		msleep(3);
	}
	ret = fg_read_sbs_word(sm, CMD_MAC | MAC_OPERATION_STATUS, &status);
	if (ret < 0)
		return ret;
	return (status & 0x0300) ? -EACCES : 0;
}

static noinline int fg_gauge_seal(struct sh_fg_chip *sm)
{
	u16 status;
	int ret;

	mutex_lock(&sm->io_lock);
	ret = i2c_smbus_write_word_data(sm->client, SBS_MAC, MAC_SEAL);
	mutex_unlock(&sm->io_lock);
	if (ret < 0)
		return ret;
	msleep(3);
	return fg_read_sbs_word(sm, CMD_MAC | MAC_OPERATION_STATUS, &status);
}

static __always_inline int afi_raw_write(struct sh_fg_chip *sm, u8 address, u8 reg,
			 const u8 *payload, u8 len)
{
	struct i2c_msg msg;
	u8 buffer[160];
	int ret, retry;

	if (!len || len >= 0x9f)
		return -EINVAL;
	buffer[0] = reg;
	memcpy(buffer + 1, payload, len);
	msg.addr = address >> 1;
	msg.flags = 0;
	msg.len = len + 1;
	msg.buf = buffer;
	for (retry = 0; retry < 2; retry++) {
		mutex_lock(&sm->io_lock);
		ret = i2c_transfer(sm->client->adapter, &msg, 1);
		mutex_unlock(&sm->io_lock);
		if (ret >= 0)
			return 0;
		msleep(50);
	}
	return ret;
}

static __always_inline int afi_raw_read(struct sh_fg_chip *sm, u8 address, u8 reg,
			u8 *buffer, u8 len)
{
	struct i2c_msg msgs[2];
	int ret, retry;

	msgs[0].addr = address >> 1;
	msgs[0].flags = 0;
	msgs[0].len = 1;
	msgs[0].buf = &reg;
	msgs[1].addr = address >> 1;
	msgs[1].flags = I2C_M_RD;
	msgs[1].len = len;
	msgs[1].buf = buffer;
	for (retry = 0; retry < 2; retry++) {
		mutex_lock(&sm->io_lock);
		ret = i2c_transfer(sm->client->adapter, msgs, 2);
		mutex_unlock(&sm->io_lock);
		if (ret >= 0)
			return 0;
		msleep(50);
	}
	return ret;
}

noinline int file_decode_process(struct sh_fg_chip *sm,
				 char *name)
{
	size_t pos = 0;
	int ret = 0;

	if (strcmp(name, "sinofs_afi_data"))
		return -ENOENT;
	if (!sh366003_allow_afi_programming)
		return -EPERM;
	ret = fg_gauge_unseal(sm);
	if (ret < 0)
		return ret;
	ret = fg_gauge_unseal(sm);
	if (ret < 0)
		goto seal;

	while (pos < sizeof(sinofs_afi_data)) {
		const u8 *r = sinofs_afi_data + pos;
		u8 op = r[0];
		u8 len;

		if (op == 1) {
			if (pos + 4 > sizeof(sinofs_afi_data)) {
				ret = -EINVAL;
				break;
			}
			len = r[3];
			ret = afi_raw_read(sm, r[1], r[2], cmp_buff, len);
			pos += 4;
		} else if (op == 2 || op == 3) {
			if (pos + 4 > sizeof(sinofs_afi_data)) {
				ret = -EINVAL;
				break;
			}
			len = r[3];
			if (pos + 4 + len > sizeof(sinofs_afi_data)) {
				ret = -EINVAL;
				break;
			}
			if (op == 2)
				ret = afi_raw_write(sm, r[1], r[2], r + 4, len);
			else {
				int i;

				ret = afi_raw_read(sm, r[1], r[2], cmp_buff, len);
				if (!ret)
					for (i = 0; i < len; i++)
						if (cmp_buff[i] != r[4 + i]) {
							ret = -EIO;
							break;
						}
			}
			pos += 4 + len;
		} else if (op == 4) {
			if (pos + 4 > sizeof(sinofs_afi_data)) {
				ret = -EINVAL;
				break;
			}
			msleep((r[2] << 8) | r[3]);
			pos += 4;
		} else {
			ret = -EINVAL;
			break;
		}
		if (ret < 0)
			break;
	}
seal:
	fg_gauge_seal(sm);
	return ret;
}

static void sh_fg_refresh_basic(struct sh_fg_chip *sm)
{
	fg_read_SOC(sm);
	fg_read_Voltage(sm);
	fg_read_Current(sm);
	fg_read_ExtTemperature(sm);
	fg_read_fcc(sm);
}

static noinline void fg_update_workfunc(struct work_struct *work)
{
	struct sh_fg_chip *sm = container_of(to_delayed_work(work),
					     struct sh_fg_chip, update_work);
	struct device_node *node;
	const __be32 *boot;
	int len = 0, bootmode = 0;
	int trigger, ret, tries;
	u16 status;
	u8 block[32];

	if (sm->adapter_status == 2 || sm->soc < SH366003_MIN_UPDATE_SOC)
		return;
	node = of_find_node_by_path("/chosen");
	if (!node)
		node = of_find_node_by_path("/chosen@0");
	if (node) {
		boot = of_get_property(node, "atag,boot", &len);
		if (boot && len >= 12)
			bootmode = be32_to_cpu(boot[2]);
	}
	if (bootmode == 8 || bootmode == 9)
		return;
	trigger = (sm->force_upgrade < 0 ? 0 : sm->force_upgrade) |
		  sm->auto_update;
	if (trigger <= 0)
		return;

	sm->fallback_soc = sm->soc;
	sm->fallback_voltage = sm->voltage;
	sm->fallback_current = sm->cached_current;
	sm->fallback_temp = sm->temp;
	sm->use_fallback = 1;
	ret = file_decode_process(sm, "sinofs_afi_data");
	msleep(1000);
	for (tries = 0; tries < 5; tries++) {
		sh_fg_refresh_basic(sm);
		if (sm->soc || sm->voltage)
			break;
		msleep(100);
	}
	if (!ret && !fg_read_sbs_word(sm, CMD_MAC | MAC_RUN_STATE, &status)) {
		if (!(status & BIT(14))) {
			mutex_lock(&sm->io_lock);
			i2c_smbus_write_word_data(sm->client, SBS_MAC,
						  MAC_RECOVER_21);
			mutex_unlock(&sm->io_lock);
			msleep(200);
		}
		if (!(status & BIT(15))) {
			mutex_lock(&sm->io_lock);
			i2c_smbus_write_word_data(sm->client, SBS_MAC,
						  MAC_RECOVER_67);
			mutex_unlock(&sm->io_lock);
			msleep(200);
		}
		fg_read_block(sm, CMD_MAC | MAC_POST_UPDATE_BLOCK,
			      sizeof(block), block);
		hal_fg_init(sm->client);
	}
	sm->use_fallback = 0;
	sm->force_upgrade = -1;
}

static noinline void fg_monitor_workfunc(struct work_struct *work)
{
	struct sh_fg_chip *sm = container_of(to_delayed_work(work),
					     struct sh_fg_chip, monitor_work);
	struct power_supply *charger;
	union power_supply_propval val = { 0 };
	u16 word;
	u8 da[32];
	int i;

	charger = power_supply_get_by_name("primary_chg");
	if (charger && !power_supply_get_property(charger,
						 POWER_SUPPLY_PROP_ONLINE, &val))
		sm->adapter_status = val.intval ? 2 : 0;
	else
		sm->adapter_status = 0;

	if (!fg_read_sbs_word(sm, SBS_VCHG, &word))
		sm->vchg = word;
	if (!fg_read_sbs_word(sm, SBS_ICHG, &word))
		sm->ichg = word;
	if (!fg_read_sbs_word(sm, SBS_BATTERY_STATUS, &word))
		sm->battery_status = word;
	fg_read_Voltage(sm);
	fg_read_Current(sm);
	fg_read_IntTemperature(sm, &word);
	fg_read_ExtTemperature(sm);
	if (!fg_read_sbs_word(sm, SBS_SOH, &word))
		sm->gauge_soh = word;
	if (!fg_read_sbs_word(sm, SBS_CYCLE_COUNT, &word))
		sm->cycle_count = word;
	if (!fg_read_sbs_word(sm, SBS_REMAINING_CAPACITY, &word))
		sm->remaining_capacity = word;
	fg_read_fcc(sm);
	for (i = MAC_SAFETY_ALERT; i <= MAC_MANUFACTURING_STATUS; i++)
		fg_read_sbs_word(sm, CMD_MAC | i, &word);
	fg_read_block(sm, CMD_MAC | MAC_DA_STATUS1, sizeof(da), da);
	mutex_lock(&sm->io_lock);
	i2c_smbus_read_word_data(sm->client, SBS_CURRENT);
	mutex_unlock(&sm->io_lock);
	queue_delayed_work(system_wq, &sm->monitor_work,
			   SH366003_MONITOR_PERIOD);
}

static enum power_supply_property sh_fg_battery_props[] = {
	POWER_SUPPLY_PROP_STATUS,
	POWER_SUPPLY_PROP_PRESENT,
	POWER_SUPPLY_PROP_VOLTAGE_NOW,
	POWER_SUPPLY_PROP_CURRENT_NOW,
	POWER_SUPPLY_PROP_CAPACITY,
	POWER_SUPPLY_PROP_TEMP,
	POWER_SUPPLY_PROP_CHARGE_FULL_DESIGN,
	POWER_SUPPLY_PROP_TECHNOLOGY,
	POWER_SUPPLY_PROP_CYCLE_COUNT,
	POWER_SUPPLY_PROP_HEALTH,
};

static noinline int sh_fg_battery_get_property(struct power_supply *psy,
		enum power_supply_property psp, union power_supply_propval *val)
{
	struct sh_fg_chip *sm = power_supply_get_drvdata(psy);

	switch (psp) {
	case POWER_SUPPLY_PROP_STATUS:
		if (sm->adapter_status == 1 || sm->adapter_status == 2)
			val->intval = sh_fg_get_soc() == 100 ?
				POWER_SUPPLY_STATUS_FULL : POWER_SUPPLY_STATUS_CHARGING;
		else
			val->intval = POWER_SUPPLY_STATUS_DISCHARGING;
		break;
	case POWER_SUPPLY_PROP_PRESENT:
		val->intval = 1;
		break;
	case POWER_SUPPLY_PROP_VOLTAGE_NOW:
		val->intval = sh_fg_get_vbat();
		break;
	case POWER_SUPPLY_PROP_CURRENT_NOW:
		val->intval = sh_fg_get_ibat();
		break;
	case POWER_SUPPLY_PROP_CAPACITY:
		val->intval = sh_fg_get_soc();
		break;
	case POWER_SUPPLY_PROP_TEMP:
		val->intval = sh_fg_get_tbat();
		break;
	case POWER_SUPPLY_PROP_CHARGE_FULL_DESIGN:
		val->intval = sm->fcc;
		break;
	case POWER_SUPPLY_PROP_TECHNOLOGY:
		val->intval = POWER_SUPPLY_TECHNOLOGY_LION;
		break;
	case POWER_SUPPLY_PROP_CYCLE_COUNT:
		val->intval = sm->cycle_count;
		break;
	case POWER_SUPPLY_PROP_HEALTH:
		val->intval = POWER_SUPPLY_HEALTH_GOOD;
		break;
	default:
		return -EINVAL;
	}
	return 0;
}

static noinline void sh_fg_external_power_changed(struct power_supply *psy)
{
	struct sh_fg_chip *sm = power_supply_get_drvdata(psy);

	queue_delayed_work(system_wq, &sm->monitor_work, 0);
}

static ssize_t chipid_show(struct class *class, struct class_attribute *attr,
			   char *buf)
{
	return sprintf(buf, "%d\n", chipid);
}

static ssize_t chipid_store(struct class *class, struct class_attribute *attr,
			    const char *buf, size_t count)
{
	return count;
}

static ssize_t force_upgrade_show(struct class *class,
				  struct class_attribute *attr, char *buf)
{
	return sprintf(buf, "%d\n", g_sm ? g_sm->force_upgrade : -1);
}

static ssize_t force_upgrade_store(struct class *class,
				   struct class_attribute *attr,
				   const char *buf, size_t count)
{
	if (!g_sm)
		return -ENODEV;
	if (!sh366003_allow_afi_programming)
		return -EPERM;
	g_sm->force_upgrade = simple_strtoul(buf, NULL, 10);
	return count;
}

static ssize_t show_fw_version(struct class *class,
			       struct class_attribute *attr, char *buf)
{
	return sprintf(buf, "%s\n", fuelgauge_fw_version);
}

static ssize_t manufacturing_date_show(struct class *class,
				       struct class_attribute *attr, char *buf)
{
	return sprintf(buf, "%d\n", g_sm ? g_sm->manufacturing_date : 0);
}

static ssize_t manufacturing_date_store(struct class *class,
					struct class_attribute *attr,
					const char *buf, size_t count)
{
	unsigned int date;
	int ret;

	if (!g_sm)
		return -ENODEV;
	if (!sh366003_allow_afi_programming)
		return -EPERM;
	if (sscanf(buf, "%u", &date) != 1)
		return -EINVAL;
	ret = fg_gauge_unseal(g_sm);
	if (ret < 0)
		return ret;
	mutex_lock(&g_sm->io_lock);
	ret = i2c_smbus_write_word_data(g_sm->client, SBS_MAC,
						MAC_PROFILE_DATE);
	if (!ret) {
		msleep(3);
		ret = i2c_smbus_write_word_data(g_sm->client, SBS_MAC_DATA,
							date & 0xffff);
	}
	mutex_unlock(&g_sm->io_lock);
	fg_gauge_seal(g_sm);
	if (ret < 0)
		return ret;
	fg_read_IntManufacturedate(g_sm);
	return count;
}

static ssize_t manufacturing_year_show(struct class *class,
				       struct class_attribute *attr, char *buf)
{
	return sprintf(buf, "%d\n", g_sm ? g_sm->manufacturing_year : 0);
}

static ssize_t manufacturing_month_show(struct class *class,
					struct class_attribute *attr, char *buf)
{
	return sprintf(buf, "%d\n", g_sm ? g_sm->manufacturing_month : 0);
}

static ssize_t manufacturing_day_show(struct class *class,
				      struct class_attribute *attr, char *buf)
{
	return sprintf(buf, "%d\n", g_sm ? g_sm->manufacturing_day : 0);
}

static ssize_t manufacturename_show(struct class *class,
				    struct class_attribute *attr, char *buf)
{
	return sprintf(buf, "%s\n", g_sm ? g_sm->manufacturer : "");
}

static ssize_t serialnum_show(struct class *class,
			      struct class_attribute *attr, char *buf)
{
	return sprintf(buf, "%d\n", g_sm ? g_sm->serial : 0);
}

static ssize_t soh_show(struct class *class, struct class_attribute *attr,
			char *buf)
{
	int cycles;

	if (!g_sm)
		return sprintf(buf, "0\n");
	cycles = g_sm->cycle_count;
	if (cycles >= 0 && cycles <= 399)
		g_sm->display_soh -= cycles / 40;
	else if (cycles >= 400)
		g_sm->display_soh -= 10 + (cycles - 400) / 60;
	return sprintf(buf, "%d\n", g_sm->display_soh);
}

static struct class_attribute class_attr_sh_fg[] = {
	__ATTR(chipid, 0664, chipid_show, chipid_store),
	__ATTR(force_upgrade, 0664, force_upgrade_show, force_upgrade_store),
	__ATTR(fw_version, 0664, show_fw_version, chipid_store),
	__ATTR(manufacturing_date, 0664, manufacturing_date_show,
	       manufacturing_date_store),
	__ATTR(manufacturing_year, 0444, manufacturing_year_show, NULL),
	__ATTR(manufacturing_month, 0444, manufacturing_month_show, NULL),
	__ATTR(manufacturing_day, 0444, manufacturing_day_show, NULL),
	__ATTR(manufacturename, 0444, manufacturename_show, NULL),
	__ATTR(serialnum, 0444, serialnum_show, NULL),
	__ATTR(soh, 0444, soh_show, NULL),
	__ATTR_NULL,
};

static char *sh_fg_supplied_from[] = {
	"bms", "battery", "mtk-master-charger",
};

static noinline int sh_fg_probe(struct i2c_client *client,
				const struct i2c_device_id *id)
{
	struct sh_fg_chip *sm;
	u16 value = 0, afi = 0, profile = 0;
	u8 data[32] = { 0 };
	char fw_text[5] = "0000";
	int i, ret;

	sm = devm_kzalloc(&client->dev, sizeof(*sm), GFP_KERNEL);
	if (!sm)
		return -ENOMEM;
	sm->dev = &client->dev;
	sm->client = client;
	sm->address = client->addr;
	sm->soc = -61;
	sm->voltage = -61;
	sm->cached_current = -61;
	sm->force_upgrade = -1;
	sm->display_soh = 100;
	memcpy(sm->regs, sh366003_regs, sizeof(sm->regs));
	mutex_init(&sm->io_lock);
	mutex_init(&sm->soc_lock);
	mutex_init(&sm->voltage_lock);
	mutex_init(&sm->current_lock);
	mutex_init(&sm->temp_lock);
	i2c_set_clientdata(client, sm);
	g_sm = sm;

	ret = fg_read_sbs_word(sm, CMD_DEVICE_ID, &value);
	if (ret < 0 || value != SH366003_DEVICE_ID)
		return ret < 0 ? ret : -ENODEV;
	chipid = value;

	sh_fg_class = class_create(THIS_MODULE, "sh_fg");
	if (!IS_ERR(sh_fg_class))
		for (i = 0; class_attr_sh_fg[i].attr.name; i++) {
			ret = class_create_file(sh_fg_class, &class_attr_sh_fg[i]);
			if (ret)
				break;
		}

	fg_read_SOC(sm);
	fg_read_Voltage(sm);
	fg_read_Current(sm);
	fg_read_ExtTemperature(sm);
	fg_read_IntManufacturedate(sm);
	if (!fg_read_block(sm, CMD_MAC | MAC_FW_TEXT, 2, data)) {
		fw_text[0] = data[0];
		fw_text[1] = data[1];
		fw_text[2] = '\0';
	}
	if (!fg_read_block(sm, CMD_MAC | MAC_MANUFACTURER_NAME, 32, data)) {
		strncpy(sm->manufacturer, data, 7);
		sm->manufacturer[7] = '\0';
	}
	if (!fg_read_sbs_word(sm, CMD_MAC | MAC_SERIAL, &value))
		sm->serial = value;
	if (!fg_read_block(sm, CMD_MAC | MAC_MAX_VOLTAGE_BLOCK, 32, data))
		sm->maximum_voltage_sum = (data[0] | data[1] << 8) +
			(data[2] | data[3] << 8);

	snprintf(fuelgauge_fw_version, 30, "Vno:0x%02x-%s(%02d%02d)\n",
		 sm->manufacturing_date, fw_text,
		 sm->manufacturing_month, sm->manufacturing_day);

	for (i = 0; i < 5; i++) {
		fg_read_sbs_word(sm, CMD_MAC | MAC_AFI_VERSION, &afi);
		fg_read_sbs_word(sm, CMD_MAC | MAC_PROFILE_DATE, &profile);
		if (afi || profile)
			break;
	}
	fg_read_fcc(sm);
	if (!afi && !profile)
		sm->auto_update = -1;
	else
		sm->auto_update = profile != SH366003_PROFILE_VERSION ||
				  sm->fcc <= SH366003_MIN_FCC;

	if ((afi || profile) && !sm->soc && !sm->voltage) {
		sm->soc = 4;
		sm->voltage = 3600;
		sm->temp = 256;
		sm->fallback_soc = 4;
		sm->fallback_voltage = 3600;
		sm->fallback_temp = 256;
		sm->use_fallback = 1;
	}

	INIT_DELAYED_WORK(&sm->monitor_work, fg_monitor_workfunc);
	INIT_DELAYED_WORK(&sm->update_work, fg_update_workfunc);
	queue_delayed_work(system_wq, &sm->monitor_work, SH366003_MONITOR_FIRST);
	queue_delayed_work(system_wq, &sm->update_work, SH366003_UPDATE_DELAY);
	yft_set_fuelgauge_device_used(SH366003_NAME, 1);

	sm->psy_desc.name = SH366003_PSY_NAME;
	sm->psy_desc.type = POWER_SUPPLY_TYPE_BATTERY;
	sm->psy_desc.properties = sh_fg_battery_props;
	sm->psy_desc.num_properties = ARRAY_SIZE(sh_fg_battery_props);
	sm->psy_desc.get_property = sh_fg_battery_get_property;
	sm->psy_desc.external_power_changed = sh_fg_external_power_changed;
	sm->psy_cfg.drv_data = sm;
	sm->psy = devm_power_supply_register(sm->dev, &sm->psy_desc, &sm->psy_cfg);
	if (IS_ERR(sm->psy))
		return PTR_ERR(sm->psy);
	sm->psy->supplied_from = sh_fg_supplied_from;
	sm->psy->num_supplies = ARRAY_SIZE(sh_fg_supplied_from);
	return 0;
}

static noinline void sh_fg_remove(struct i2c_client *client)
{
}

static noinline void sh_fg_shutdown(struct i2c_client *client)
{
	pr_info("[sh366003] shutdown\n");
}

static const struct of_device_id sh_fg_match_table[] = {
	{ .compatible = "sh,sh366003" },
	{ }
};
MODULE_DEVICE_TABLE(of, sh_fg_match_table);

static const struct i2c_device_id sh_fg_id[] = {
	{ SH366003_NAME, 0 },
	{ }
};
MODULE_DEVICE_TABLE(i2c, sh_fg_id);

static struct i2c_driver sh_fg_driver = {
	.driver = {
		.name = SH366003_NAME,
		.of_match_table = sh_fg_match_table,
	},
	.probe = sh_fg_probe,
	.remove = sh_fg_remove,
	.shutdown = sh_fg_shutdown,
	.id_table = sh_fg_id,
};

static int __init sh366003_init(void)
{
	yft_fuelgauge_device_add(&sh_fg_driver, 0);
	return i2c_add_driver(&sh_fg_driver);
}

static void __exit sh366003_exit(void)
{
	i2c_del_driver(&sh_fg_driver);
}

module_init(sh366003_init);
module_exit(sh366003_exit);

MODULE_AUTHOR("Sinowealth");
MODULE_DESCRIPTION("SH SH366003 Gauge Driver");
MODULE_LICENSE("GPL v2");
