// SPDX-License-Identifier: GPL-2.0
/*
 * SinoWealth SH366003 fuel gauge driver (GQ5012BF1 "3rd-gauge").
 *
 * Binary-equivalent reconstruction of the stock Ulefone Armor 29 Pro
 * Thermal (GQ5012BF1) vendor_boot module sh366003_fg.ko
 * (sha256 527bddb4ddb11e94ed85e6969a10f807178cbb3f0fd326c8509824800a3d61a7).
 * SinoWealth "2022.10.17" Linux template + YFT (yft_devinfo) glue.
 *
 * Blank lines are placed so that every __LINE__ used by the log macros is
 * identical to the stock build (pad_lines.py expands the trailing @NNNN
 * markers of sh366003_fg.src.c, which are the stock __LINE__ values).
 *
 * sinofs_afi_data.inc (the 2142-byte SinoWealth AFI/profile program) is
 * device data and is not part of this source; it must be supplied by the
 * private build tree. As in stock, the update work programs it into the
 * gauge when MAC 0x004D != 0x5A93 or FCC < 3500 mAh.
 */
#define pr_fmt(fmt) "[sh366003] %s(%d): " fmt, __func__, __LINE__

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/i2c.h>
#include <linux/delay.h>
#include <linux/slab.h>
#include <linux/mutex.h>
#include <linux/of.h>
#include <linux/power_supply.h>
#include <linux/workqueue.h>
#include <linux/string.h>
#include <linux/device.h>

#define sh_info(fmt, ...)						\
do {									\
	if (fg_sh366003_log)						\
		pr_notice("[sh366003]" fmt, ##__VA_ARGS__);		\
} while (0)

#define CMDMASK_ALTMAC_R	0x08000000
#define CMDMASK_CNTL_R		0x04000000

#define CMD_CNTL		0x00
#define CMD_TEMP		0x06
#define CMD_VOLTAGE		0x08
#define CMD_BATTSTATUS		0x0A
#define CMD_CURRENT		0x0C
#define CMD_RC			0x10
#define CMD_FCC			0x12
#define CMD_INTTEMP		0x28
#define CMD_CYCLECOUNT		0x2A
#define CMD_SOC			0x2C
#define CMD_SOH			0x2E
#define CMD_VCHG		0x30
#define CMD_ICHG		0x32
#define CMD_ALTMAC		0x3E
#define CMD_ALTBLOCK		0x40
#define CMD_ALTCHK		0x60

#define CMD_SEAL		0x0030
#define CMD_RESET		0x0041
#define CMD_GAUGE_ENABLE	0x0021
#define CMD_LIFETIME_ENABLE	0x0067
#define CMD_AFI_STATIC_SUM	(CMDMASK_ALTMAC_R | 0x0046)
#define CMD_FWNO		(CMDMASK_ALTMAC_R | 0x004D)
#define CMD_MANUFACTURENAME	(CMDMASK_ALTMAC_R | 0x004C)
#define CMD_SERIALNUM		(CMDMASK_ALTMAC_R | 0x004E)
#define CMD_SAFETYALERT		(CMDMASK_ALTMAC_R | 0x0050)
#define CMD_OPERATION_STATUS	(CMDMASK_ALTMAC_R | 0x0054)
#define CMD_MAXVOLTAGE		(CMDMASK_ALTMAC_R | 0x0060)
#define CMD_DASTATUS1		(CMDMASK_ALTMAC_R | 0x0071)
#define CMD_OEMFLAG		(CMDMASK_ALTMAC_R | 0x00C1)
#define CMD_RUNSTATE_BLOCK	(CMDMASK_ALTMAC_R | 0x00C5)
#define CMD_MANUF_ASCII		(CMDMASK_ALTMAC_R | 0x40D9)
#define CMD_MANUFACTURE_DATE	0x4D

#define CMD_UNSEALKEY		0x12345678
#define CMD_FULLKEY		0x90ABCDEF

#define SH366003_DEVICE_ID	0x0603
#define AFI_NEW_STATIC_SUM	0x8CD3
#define AFI_NEW_FWNO		0x5A93
#define AFI_FCC_MIN		3500



enum sh_fg_reg_idx {
	SH_FG_REG_DEVICE_TYPE = 0, SH_FG_REG_CNTL_STATUS, SH_FG_REG_RA, SH_FG_REG_TEMP_OLD,
	SH_FG_REG_SOC, SH_FG_REG_SOH, SH_FG_REG_VOLTAGE, SH_FG_REG_CURRENT,
	SH_FG_REG_CYCLE, SH_FG_REG_TEMP, SH_FG_REG_CURRENT2, SH_FG_REG_FLAGS,
	SH_FG_REG_RESET, SH_FG_REG_1A, SH_FG_REG_3C, SH_FG_REG_CHIPID,
	NUM_REGS,
};

struct sh_fg_chip {
	struct device *dev;
	struct i2c_client *client;
	struct mutex i2c_rw_lock;
	struct mutex data_lock;
	struct mutex cali_lock;
	struct mutex upgrade_lock;
	struct mutex wrblk_lock;
	u8 chip;
	u8 manufacturename[7];
	u32 regs[NUM_REGS];
	struct delayed_work monitor_work;
	struct delayed_work update_work;
	int batt_soc;
	int batt_volt;
	int batt_curr;
	int batt_temp;
	int fallback_soc;
	int fallback_volt;
	int fallback_curr;
	int fallback_temp;
	int fallback_flag;
	int batt_soc_old;
	int batt_volt_old;
	int batt_curr_old;
	int force_upgrade;
	int term_volt;
	struct power_supply *fg_psy;
	struct power_supply_desc fg_psy_d;
	struct power_supply_config fg_psy_cfg;
	struct power_supply *chg_psy;
	struct power_supply *usb_psy;
	u8 adapter_status;
	int batt_soh;
	int display_soh;
	int batt_cycle;
	int batt_rc;
	int batt_fcc;
	int batt_dc;
	int batt_vchg;
	int batt_ichg;
	int batt_status;
	int serialnum;
	int maxvoltage;
	int manufacture_date;
	int manufacture_day;
	int manufacture_month;
	int manufacture_year;
	int auto_update;
	u8 reserved[156];
};

extern char fuelgauge_fw_version[];
extern int yft_fuelgauge_device_add(struct i2c_driver *driver, int used);
extern int yft_set_fuelgauge_device_used(char *name, int used);

u8 fg_sh366003_log = 1;
const char *device2str[] = {
	"sh366003",
};
struct sh_fg_chip *g_sm;
static u16 chipid;
static struct class *sh_fg_class;
static int online_val;


static int __fg_read_word(struct i2c_client *client, u8 reg, u16 *val)
{
	s32 ret;

	ret = i2c_smbus_read_word_data(client, reg);
	if (ret < 0) {























		sh_info("i2c read word fail: can't read from reg 0x%02X\n", reg);
		return ret;
	}
	*val = (u16)ret;
	return 0;
}

static int __fg_write_word(struct i2c_client *client, u8 reg, u16 val)
{
	s32 ret;

	ret = i2c_smbus_write_word_data(client, reg, val);
	if (ret < 0) {

		sh_info("i2c write word fail: can't write 0x%02X to reg 0x%02X\n", val, reg);
		return ret;
	}
	return 0;
}

#define TEMPER_OFFSET		2731
#define WRITE_BUF_MAX_LEN	160
#define BUF_MAX_LENGTH		512

#define OPERATE_READ		1
#define OPERATE_WRITE		2
#define OPERATE_COMPARE		3
#define OPERATE_WAIT		4

#define ERRORTYPE_NONE		0
#define ERRORTYPE_ALLOC		1
#define ERRORTYPE_LINE		2
#define ERRORTYPE_COMM		3
#define ERRORTYPE_COMPARE	4

#define INDEX_TYPE		0
#define INDEX_ADDR		1
#define INDEX_REG		2
#define INDEX_LENGTH		3
#define INDEX_DATA		4
#define INDEX_WAIT_LENGTH	1
#define INDEX_WAIT_HIGH		2
#define INDEX_WAIT_LOW		3
#define LINELEN_WAIT		4
#define LINELEN_READ		4
#define LINELEN_COMPARE		4
#define LINELEN_WRITE		4
#define FILEDECODE_STRLEN	96
#define COMPARE_RETRY_CNT	2
#define COMPARE_RETRY_WAIT	50

#define IIC_ADDR_OF_2_KERNEL(addr) ((u8)((u8)addr >> 1))

struct sh_decoder {
	u8 addr;
	u8 reg;
	u8 length;
	u8 buf_first_val;
};


static const u32 sh366003_regs[NUM_REGS] = {
	0x08000001, 0x08000000, 0x0100006E, 0x00000006,
	0x0000002C, 0x00000064, 0x00000008, 0x0000000C,
	0x0000001E, 0x00000006, 0x0000000C, 0x0000000E,
	0x88000041, 0x0000001A, 0x0000003C, 0x04000001,
};

#include "sinofs_afi_data.inc"

int sh_fg_get_soc(void)
{
	return (g_sm->fallback_flag == 1) ? g_sm->fallback_soc : g_sm->batt_soc;
}

int sh_fg_get_vbat(void)
{
	return (g_sm->fallback_flag == 1) ? g_sm->fallback_volt : g_sm->batt_volt;
}

int sh_fg_get_ibat(void)
{
	return (g_sm->fallback_flag == 1) ? g_sm->fallback_curr : g_sm->batt_curr;
}

int sh_fg_get_tbat(void)
{
	return (g_sm->fallback_flag == 1) ? g_sm->fallback_temp : g_sm->batt_temp;
}

static int __fg_read_buffer(struct i2c_client *client, u8 reg, u8 length, u8 *val)
{
	static struct i2c_msg msg[2];

	if (!client->adapter)
		return -ENODEV;
	msg[0].addr = client->addr;
	msg[0].flags = 0;
	msg[0].buf = &reg;
	msg[0].len = sizeof(u8);
	msg[1].addr = client->addr;
	msg[1].flags = I2C_M_RD;
	msg[1].buf = val;
	msg[1].len = length;

	return i2c_transfer(client->adapter, msg, ARRAY_SIZE(msg));
}

static int __fg_write_buffer(struct i2c_client *client, u8 reg, u8 length, u8 *val)
{
	static struct i2c_msg msg[1];
	static u8 write_buf[WRITE_BUF_MAX_LEN];
	int ret;

	if (!client->adapter)
		return -ENODEV;

	if ((length <= 0) || (length + 1 >= WRITE_BUF_MAX_LEN)) {
		sh_info("i2c write buffer fail: length invalid!");
		return -1;
	}

	memset(write_buf, 0, WRITE_BUF_MAX_LEN * sizeof(u8));
	write_buf[0] = reg;
	memcpy(&write_buf[1], val, length);

	msg[0].addr = client->addr;
	msg[0].flags = 0;
	msg[0].buf = write_buf;
	msg[0].len = sizeof(u8) * (length + 1);

	ret = i2c_transfer(client->adapter, msg, ARRAY_SIZE(msg));
	if (ret < 0) {





























































		sh_info("i2c write buffer fail: can't write reg 0x%02X\n", reg);
		return ret;
	}
	return 0;
}

static int fg_read_sbs_word(struct sh_fg_chip *sm, u32 reg, u16 *val)
{
	int ret = -1;

	mutex_lock(&sm->i2c_rw_lock);
	if ((reg & CMDMASK_ALTMAC_R) == CMDMASK_ALTMAC_R) {
		ret = __fg_write_word(sm->client, CMD_ALTMAC, (u16)reg);
		if (ret < 0)
			goto fg_read_sbs_word_end;
		msleep(3);
		ret = __fg_read_word(sm->client, CMD_ALTBLOCK, val);
	} else if ((reg & CMDMASK_CNTL_R) == CMDMASK_CNTL_R) {
		ret = __fg_write_word(sm->client, CMD_CNTL, (u16)reg);
		if (ret < 0)
			mdelay(10);
		ret = __fg_read_word(sm->client, CMD_CNTL, val);
	} else {
		ret = __fg_read_word(sm->client, (u8)reg, val);
	}

fg_read_sbs_word_end:
	mutex_unlock(&sm->i2c_rw_lock);
	return ret;
}

static int fg_read_block(struct sh_fg_chip *sm, u32 reg, u8 length, u8 *val)
{
	int ret;
	u16 temp = 0;
	u8 checksum;
	int i;

	mutex_lock(&sm->i2c_rw_lock);
	ret = __fg_write_word(sm->client, CMD_ALTMAC, (u16)reg);
	if (ret < 0)
		goto fg_read_block_end;
	msleep(3);

	ret = __fg_read_buffer(sm->client, CMD_ALTBLOCK, length, val);
	if (ret < 0)
		goto fg_read_block_end;
	msleep(3);

	ret = __fg_read_word(sm->client, CMD_ALTCHK, &temp);
	if (ret < 0)
		goto fg_read_block_end;

	if ((temp >> 8) <= 4) {
		ret = 0;
		goto fg_read_block_end;
	}

	i = (temp >> 8) - 4;
	checksum = (u8)reg;
	while (i--)
		checksum += val[i];
	checksum = ~checksum;
	ret = (checksum == (u8)temp) ? 0 : -1;

fg_read_block_end:
	mutex_unlock(&sm->i2c_rw_lock);
	return ret;
}

static void sh_fg_get_batt_info(struct sh_fg_chip *sm)
{
	int ret, i;
	u16 status[8] = { 0 };
	u8 buf[32] = { 0 };
	u16 cell1, cell2;

	for (i = 0; i < 8; i++) {
		ret = fg_read_sbs_word(sm, CMD_SAFETYALERT + i, &status[i]);
		if (ret < 0) {
















			sh_info("fail: could not read 0x0050, ret = %d, i=%d\n", ret, i);
			return;
		}
	}

	ret = fg_read_block(sm, CMD_DASTATUS1, 32, buf);
	if (ret < 0) {














		sh_info("sh366003_GaugeLog: fg_read_block could not read sh_da_status1, ret = %d\n", ret);
		return;
	}

	cell1 = buf[0] | (buf[1] << 8);
	cell2 = buf[2] | (buf[3] << 8);
	sh_info("SafetyAlert=0x%04X, SafetyStatus=0x%04X, PFAlert=0x%04X, PF=0x%04X, Operation=0x%04X, Charging=0x%04X, Gauging=0x%04X, Manufacturing=0x%04X, da_status1=[0x%04X(%d),0x%04X(%d)]\n", status[0], status[1], status[2], status[3], status[4], status[5], status[6], status[7], cell1, cell1, cell2, cell2);
}


static s32 fg_decode_iic_read(struct sh_fg_chip *sm, struct sh_decoder *decoder, u8 *pBuf)
{
	static struct i2c_msg msg[2];
	u8 addr = IIC_ADDR_OF_2_KERNEL(decoder->addr);
	s32 ret;

	if (!sm->client->adapter)
		return -ENODEV;

	mutex_lock(&sm->i2c_rw_lock);

	msg[0].addr = addr;
	msg[0].flags = 0;
	msg[0].buf = &(decoder->reg);
	msg[0].len = sizeof(u8);
	msg[1].addr = addr;
	msg[1].flags = I2C_M_RD;
	msg[1].buf = pBuf;
	msg[1].len = decoder->length;
	ret = (s32)i2c_transfer(sm->client->adapter, msg, ARRAY_SIZE(msg));

	mutex_unlock(&sm->i2c_rw_lock);
	return ret;
}

static s32 fg_decode_iic_write(struct sh_fg_chip *sm, struct sh_decoder *decoder)
{
	static struct i2c_msg msg[1];
	static u8 write_buf[WRITE_BUF_MAX_LEN];
	u8 addr = IIC_ADDR_OF_2_KERNEL(decoder->addr);
	u8 length = decoder->length;
	s32 ret;

	if (!sm->client->adapter)
		return -ENODEV;

	if ((length <= 0) || (length + 1 >= WRITE_BUF_MAX_LEN)) {












		sh_info("i2c write buffer fail: length invalid!");
		return -1;
	}

	mutex_lock(&sm->i2c_rw_lock);
	memset(write_buf, 0, WRITE_BUF_MAX_LEN * sizeof(u8));
	write_buf[0] = decoder->reg;
	memcpy(&write_buf[1], &(decoder->buf_first_val), length);

	msg[0].addr = addr;
	msg[0].flags = 0;
	msg[0].buf = write_buf;
	msg[0].len = sizeof(u8) * (length + 1);

	ret = i2c_transfer(sm->client->adapter, msg, ARRAY_SIZE(msg));
	if (ret < 0)
		sh_info("i2c write buffer fail: can't write reg 0x%02X\n", decoder->reg);

	mutex_unlock(&sm->i2c_rw_lock);
	return (ret < 0) ? ret : 0;
}

static int fg_read_word(struct sh_fg_chip *sm, u8 reg, u16 *val)
{
	int ret;

	mutex_lock(&sm->i2c_rw_lock);
	ret = __fg_read_word(sm->client, reg, val);
	mutex_unlock(&sm->i2c_rw_lock);
	return ret;
}

static int fg_read_SOC(struct sh_fg_chip *sm)
{
	int ret;
	u16 soc = 0;

	ret = fg_read_word(sm, CMD_SOC, &soc);
	if (ret < 0) {




















		sh_info("sh366003_GaugeLog: could not read CMD_SOC, ret = %d\n", ret);
		return ret;
	}

	mutex_lock(&sm->data_lock);
	sm->batt_soc = soc;
	mutex_unlock(&sm->data_lock);
	return 0;
}

static int fg_read_VCHG(struct sh_fg_chip *sm)
{
	int ret;
	u16 vchg = 0;

	ret = fg_read_word(sm, CMD_VCHG, &vchg);
	if (ret < 0) {





		sh_info("sh366003_GaugeLog: could not read CMD_VCHG, ret = %d\n", ret);
		return ret;
	}

	mutex_lock(&sm->data_lock);
	sm->batt_vchg = vchg;
	mutex_unlock(&sm->data_lock);
	return 0;
}

static int fg_read_ICHG(struct sh_fg_chip *sm)
{
	int ret;
	u16 ichg = 0;

	ret = fg_read_word(sm, CMD_ICHG, &ichg);
	if (ret < 0) {





		sh_info("sh366003_GaugeLog: could not read CMD_ICHG, ret = %d\n", ret);
		return ret;
	}

	mutex_lock(&sm->data_lock);
	sm->batt_ichg = ichg;
	mutex_unlock(&sm->data_lock);
	return 0;
}

static int fg_read_BatteryStatus(struct sh_fg_chip *sm)
{
	int ret;
	u16 status = 0;

	ret = fg_read_word(sm, CMD_BATTSTATUS, &status);
	if (ret < 0) {





		sh_info("sh366003_GaugeLog: could not read BatteryStatus, ret = %d\n", ret);
		return ret;
	}

	mutex_lock(&sm->data_lock);
	sm->batt_status = status;
	mutex_unlock(&sm->data_lock);
	return 0;
}

static int fg_read_Voltage(struct sh_fg_chip *sm)
{
	int ret;
	u16 volt = 0;

	ret = fg_read_word(sm, CMD_VOLTAGE, &volt);
	if (ret < 0) {












		sh_info("sh366003_GaugeLog: could not read CMD_Voltage, ret = %d\n", ret);
		return ret;
	}

	mutex_lock(&sm->data_lock);
	sm->batt_volt = volt;
	mutex_unlock(&sm->data_lock);
	return 0;
}

static int fg_read_Current(struct sh_fg_chip *sm)
{
	int ret;
	u16 curr = 0;

	ret = fg_read_word(sm, CMD_CURRENT, &curr);
	if (ret < 0) {












		sh_info("sh366003_GaugeLog: could not read CMD_Current, ret = %d\n", ret);
		return ret;
	}

	mutex_lock(&sm->data_lock);
	if ((s16)curr < 0)
		sm->batt_curr = -(s16)curr * 1000;
	else
		sm->batt_curr = (s16)curr * 1000;
	mutex_unlock(&sm->data_lock);
	return 0;
}

static int fg_read_ExtTemperature(struct sh_fg_chip *sm)
{
	int ret;
	u16 temp = 0;

	ret = fg_read_word(sm, CMD_TEMP, &temp);
	if (ret < 0) {





		sh_info("sh366003_GaugeLog: could not read CMD_ExtTemperature, ret = %d\n", ret);
		return ret;
	}

	sm->batt_temp = (s16)temp - TEMPER_OFFSET;
	return 0;
}

static int fg_read_IntTemperature(struct sh_fg_chip *sm)
{
	int ret;
	u16 temp = 0;

	ret = fg_read_word(sm, CMD_INTTEMP, &temp);
	if (ret < 0) {













		sh_info("sh366003_GaugeLog: could not read CMD_IntTemperature, ret = %d\n", ret);
		return ret;
	}

	return (s16)temp - TEMPER_OFFSET;
}

static int fg_read_soh(struct sh_fg_chip *sm)
{
	int ret;
	u16 soh = 0;

	ret = fg_read_word(sm, CMD_SOH, &soh);
	if (ret < 0) {





		sh_info("sh366003_GaugeLog: could not read fg_read_soh, ret = %d\n", ret);
		return ret;
	}

	sm->batt_soh = soh;
	return 0;
}

static int fg_read_cycnt(struct sh_fg_chip *sm)
{
	int ret;
	u16 cycnt = 0;

	ret = fg_read_word(sm, CMD_CYCLECOUNT, &cycnt);
	if (ret < 0) {




		sh_info("sh366003_GaugeLog: could not read fg_read_cycnt, ret = %d\n", ret);
		return ret;
	}

	sm->batt_cycle = cycnt;
	return 0;
}

static int fg_read_rc(struct sh_fg_chip *sm)
{
	int ret;
	u16 rc = 0;

	ret = fg_read_word(sm, CMD_RC, &rc);
	if (ret < 0) {




		sh_info("sh366003_GaugeLog: could not read fg_read_rc, ret = %d\n", ret);
		return ret;
	}

	sm->batt_rc = rc;
	return 0;
}

static int fg_read_fcc(struct sh_fg_chip *sm)
{
	int ret;
	u16 fcc = 0;

	ret = fg_read_word(sm, CMD_FCC, &fcc);
	if (ret < 0) {



		sh_info("sh366003_GaugeLog: could not read fg_read_fcc, ret = %d\n", ret);
		return ret;
	}

	sm->batt_fcc = fcc;
	return 0;
}

static int fg_write_word(struct sh_fg_chip *sm, u8 reg, u16 val)
{
	int ret;

	mutex_lock(&sm->i2c_rw_lock);
	ret = __fg_write_word(sm->client, reg, val);
	mutex_unlock(&sm->i2c_rw_lock);
	return ret;
}

static int fg_write_block(struct sh_fg_chip *sm, u8 reg, u8 *data, u8 len)
{
	int ret;

	mutex_lock(&sm->i2c_rw_lock);
	ret = __fg_write_buffer(sm->client, reg, len, data);
	mutex_unlock(&sm->i2c_rw_lock);
	return ret;
}

static int fg_get_device_id(struct i2c_client *client)
{
	struct sh_fg_chip *sm = i2c_get_clientdata(client);
	int ret;
	u16 data = 0;

	ret = fg_read_sbs_word(sm, sm->regs[SH_FG_REG_DEVICE_TYPE], &data);
	if (ret < 0) {





		sh_info("Failed to read DEVICE_ID, ret = %d\n", ret);
		return ret;
	}

	sh_info("device_id = 0x%04X\n", data);
	return 0;
}

static int fg_init(struct i2c_client *client)
{
	int ret;

	ret = fg_get_device_id(client);
	if (ret < 0) {
		sh_info("%s: fail to do i2c read(%d)\n", __func__, ret);
		return ret;
	}
	return 0;
}

static s32 fg_gauge_unseal(struct sh_fg_chip *sm)
{
	int ret;
	u16 op_status = 0;

	ret = fg_write_word(sm, CMD_CNTL, (u16)CMD_UNSEALKEY);
	if (ret < 0)
		return ret;
	msleep(3);

	ret = fg_write_word(sm, CMD_CNTL, (u16)(CMD_UNSEALKEY >> 16));
	if (ret < 0)
		return ret;
	msleep(3);

	ret = fg_write_word(sm, CMD_CNTL, (u16)CMD_FULLKEY);
	if (ret < 0)
		return ret;
	msleep(3);

	ret = fg_write_word(sm, CMD_CNTL, (u16)(CMD_FULLKEY >> 16));
	if (ret < 0)
		return ret;
	msleep(3);

	ret = fg_read_sbs_word(sm, CMD_OPERATION_STATUS, &op_status);
	if (ret < 0) {



		sh_info("read CMD_OPERATION_STATUS(0x0054) error.\n");
		return -1;
	}

	sh_info(" Chip Operation Status=0x%04X\n", op_status);

	if ((op_status & 0x0300) == 0) {
		sh_info("SH366003 unseal ok.\n");
		return 0;
	}

	sh_info("SH366003 unseal error.\n");
	return 0;
}

static s32 fg_gauge_seal(struct sh_fg_chip *sm)
{
	int ret;
	u16 op_status = 0;

	ret = fg_write_word(sm, CMD_ALTMAC, CMD_SEAL);
	ret = fg_read_sbs_word(sm, CMD_OPERATION_STATUS, &op_status);



	sh_info("gauge_seal read 0x0054=0x%04X\n", op_status);
	return ret;
}

static int fg_read_IntManufacturename(struct sh_fg_chip *sm)
{
	int ret;
	u8 buf[32] = { 0 };

	ret = fg_read_block(sm, CMD_MANUFACTURENAME, 32, buf);
	if (ret < 0) {


















		sh_info("could not read manufacturename, ret = %d\n", ret);
		return ret;
	}

	sh_info("manufacturename= [%c%c%c%c%c%c%c]\n", buf[0], buf[1], buf[2], buf[3], buf[4], buf[5], buf[6]);
	memcpy(sm->manufacturename, buf, 7);
	return 0;
}

static int fg_read_Intserialnum(struct sh_fg_chip *sm)
{
	int ret;
	u16 data = 0;

	ret = fg_read_sbs_word(sm, CMD_SERIALNUM, &data);
	if (ret < 0) {





		sh_info("sh366003_GaugeLog: could not read serialnum, ret = %d\n", ret);
		return ret;
	}

	sh_info("sh366003_GaugeLog: serialnum = %d\n", data);
	sm->serialnum = data;
	return 0;
}

static int fg_read_maxvoltage(struct sh_fg_chip *sm)
{
	int ret;
	u8 buf[32] = { 0 };
	int v1, v2;

	ret = fg_read_block(sm, CMD_MAXVOLTAGE, 32, buf);
	if (ret < 0) {



		sh_info("could not read maxvoltage, ret = %d\n", ret);
		return ret;
	}

	v1 = buf[0] | (buf[1] << 8);
	v2 = buf[2] | (buf[3] << 8);


	sh_info("maxvoltage= (%d)+(%d),[%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x]\n", v1, v2, buf[0], buf[1], buf[2], buf[3], buf[4], buf[5], buf[6], buf[7], buf[8], buf[9], buf[10], buf[11], buf[12], buf[13]);
	sm->maxvoltage = v1 + v2;
	return 0;
}

static void fg_read_IntManufacturedate(struct sh_fg_chip *sm)
{
	int ret;
	u8 buf[2] = { 0 };
	u16 date;

	ret = fg_read_block(sm, CMD_FWNO, 2, buf);
	if (ret < 0) {


		sh_info("could not read MANUFACTURE_DATE, ret = %d\n", ret);
		return;
	}

	date = buf[0] | (buf[1] << 8);

	sh_info("MANUFACTURE_DATE= 0x%02x,[%x,%x]\n", date, buf[0], buf[1]);
	sm->manufacture_date = date;
	sm->manufacture_day = date & 0x1f;
	sm->manufacture_month = (date >> 5) & 0x0f;
	sm->manufacture_year = (date >> 9) + 1980;
}

static void fg_write_IntManufactureTimedate(struct sh_fg_chip *sm, u8 *buf)
{
	int ret;
	int retry;




	sh_info("manufacturedate1= %x %x\n", buf[0], buf[1]);

	mutex_lock(&sm->wrblk_lock);
	if (sm->manufacture_date == 0)
		fg_read_IntManufacturedate(sm);

	if (sm->manufacture_date == 0) {
		fg_gauge_unseal(sm);
		retry = 5;
		while (retry--) {
			ret = fg_write_block(sm, CMD_MANUFACTURE_DATE, buf, 2);
			if (ret < 0) {


				sh_info("could not write manufacturedate, ret = %d\n", ret);
			} else {


				sh_info("manufacturedate= %x %x\n", buf[0], buf[1]);
				break;
			}
		}
		fg_gauge_seal(sm);
	} else {








		sh_info("manufacturedate HAS BEEN WRITED\n");
	}
	mutex_unlock(&sm->wrblk_lock);
}

static int fg_gauge_runstate_check(struct sh_fg_chip *sm)
{
	int ret = 0;
	int retry;
	u16 oem_flag = 0;
	u16 temp = 0;
	u8 buf[32] = { 0 };
	u32 soc_flag = 0, qen_flag = 0, lifetime_flag = 0;

	for (retry = 0; retry < 5; retry++) {
		ret = fg_read_SOC(sm);
		if (ret < 0)
			goto runstate_retry;
		msleep(3);
		ret = fg_read_Voltage(sm);
		if (ret < 0)
			goto runstate_retry;
		msleep(3);
		ret = fg_read_Current(sm);
		if (ret < 0)
			goto runstate_retry;
		msleep(3);
		ret = fg_read_sbs_word(sm, sm->regs[SH_FG_REG_TEMP], &temp);
		if (ret < 0)
			goto runstate_retry;
		temp -= TEMPER_OFFSET;
		ret = fg_read_sbs_word(sm, CMD_OEMFLAG, &oem_flag);
		if (ret < 0)
			goto runstate_retry;

		soc_flag = 0;
		if (sm->batt_curr <= 0)
			soc_flag = ((sm->batt_volt > 4000000) && (sm->batt_soc < 10)) |
				   ((sm->batt_volt > 3850000) && (sm->batt_soc < 3)) |
				   ((sm->batt_soc == 0) && ((sm->batt_volt - sm->term_volt) > 200000));

		if (soc_flag == 1) {
			ret = fg_gauge_unseal(sm);
			if (ret < 0)
				goto runstate_retry;
			ret = fg_write_word(sm, CMD_ALTMAC, CMD_RESET);
			if (ret < 0)
				goto runstate_retry;
			msleep(1000);
		}

		qen_flag = (oem_flag & 0x4000) ? 0 : 1;
		if (qen_flag) {














































































































































































































































































			sh_info("gauge disable \n");
			ret = fg_gauge_unseal(sm);
			if (ret < 0)
				goto runstate_retry;
			ret = fg_write_word(sm, CMD_ALTMAC, CMD_GAUGE_ENABLE);
			if (ret < 0)
				goto runstate_retry;
			msleep(1000);
		}

		lifetime_flag = (oem_flag & 0x8000) ? 0 : 1;
		if (lifetime_flag) {
			ret = fg_gauge_unseal(sm);
			if (ret < 0)
				goto runstate_retry;
			ret = fg_write_word(sm, CMD_ALTMAC, CMD_LIFETIME_ENABLE);
			if (ret < 0)
				goto runstate_retry;
			msleep(1000);
		}

		ret = fg_gauge_unseal(sm);
		if (ret < 0)
			goto runstate_retry;
		ret = fg_read_block(sm, CMD_RUNSTATE_BLOCK, 32, buf);
		if (ret >= 0)
			break;
runstate_retry:
		msleep(6);
	}












	sh_info("fg_gauge_runstate_check: soc=%d, volt=%d, termVolt=%d, OEMFlag=0x%04X, QEN_FLAG=%u, SOC_FLAG=%u, LifeTime_Flag=%u\n", sm->batt_soc, sm->batt_volt, sm->term_volt, oem_flag, qen_flag, soc_flag, lifetime_flag);
	fg_gauge_seal(sm);
	return ret;
}

static int Check_Chip_Version(struct sh_fg_chip *sm)
{
	int ret = 0;
	int retry;
	u16 temp1 = 0, temp2 = 0;
	bool afi_err = false;


	sh_info("%s %s %d\n", __FILE__, __func__, __LINE__);
	sh_info("Check_Chip_Version: new afi=0x%04X\n", AFI_NEW_STATIC_SUM);

	sh_info("start unseal, send 0x12345678:\n");
	if (fg_gauge_unseal(sm) < 0)


		sh_info("unseal error.\n");

	retry = 5;
	while (retry) {
		ret = fg_read_sbs_word(sm, CMD_AFI_STATIC_SUM, &temp1);
		if (ret < 0)




			sh_info("read CMD_AFI_STATIC_SUM(0x0046) error.ret=%dtemp1=0x%04X\n", ret, temp1);

		ret = fg_read_sbs_word(sm, CMD_FWNO, &temp2);
		if (ret >= 0) {
			ret = 0;
		} else {

			sh_info("read CMD_AFI_STATIC_SUM(0x004D) error.ret=%d,temp2=0X%04x\n", ret, temp2);
			ret = -1;
		}


		sh_info("Chip_Version: ic afi=0x%04X, fwno=0x%04X,retry:%d\n", temp1, temp2, retry);

		afi_err = (temp1 == 0) || (temp2 == 0);
		if (!afi_err)
			break;
		retry--;
		msleep(5);
	}

	fg_read_fcc(sm);


	sh_info("[0.0]Chip_Version: ic afi=0x%04X, fwno=0x%04X,FCC:%d,\n", temp1, temp2, sm->batt_fcc);

	if (afi_err) {
		sm->auto_update = -1;
	} else if ((temp2 != AFI_NEW_FWNO) || (sm->batt_fcc < AFI_FCC_MIN)) {
		sm->auto_update = 1;




		sh_info(" Chip_Version: ic afi=0x%04X(0x%04X), fwno=0x%04X(0x%04X),need update AFI!\n", temp1, AFI_NEW_STATIC_SUM, temp2, AFI_NEW_FWNO);
		ret = temp2;
	} else {
		sm->auto_update = 0;


		sh_info(" Chip_Version: ic afi=0x%04X(0x%04X), fwno=0x%04X(0x%04X),no need update AFI!\n", temp1, AFI_NEW_STATIC_SUM, temp2, AFI_NEW_FWNO);
		ret = 0;
	}

	fg_gauge_seal(sm);
	return ret;
}

int file_decode_process(struct sh_fg_chip *sm, char *profile_name)
{
	struct device *dev = &sm->client->dev;
	u8 *pBuf = NULL;
	u8 *pBuf_Read = NULL;
	char strDebug[FILEDECODE_STRLEN] = { 0 };
	int buflen;
	int wait_ms;
	int i, j;
	int line_length;
	int result = -1;
	int retry;
	int retry2 = 0;
	int i_bak = 0;
	int cnt = 1, cnt_bak = 0;
	struct sh_decoder *ptr_decoder;





	sh_info("%s %s %d\n", __FILE__, __func__, __LINE__);
	sh_info("file decode start:\n");

	if (strcmp("sinofs_afi_data", profile_name) == 0) {
		buflen = sizeof(sinofs_afi_data);
	} else {
		result = -1;
		goto main_process_error;
	}
	sh_info("ele_len=%d, key=%s\n", buflen, profile_name);

	pBuf = (u8 *)devm_kzalloc(dev, buflen, 0);
	pBuf_Read = (u8 *)devm_kzalloc(dev, BUF_MAX_LENGTH, 0);

	if ((pBuf == NULL) || (pBuf_Read == NULL)) {
		result = ERRORTYPE_ALLOC;
		sh_info(" kzalloc error");
		goto main_process_error;
	}

	if (strcmp("sinofs_afi_data", profile_name) == 0)
		memcpy(pBuf, sinofs_afi_data, buflen);



	sh_info("start unseal, send 0x80008000:\n");
	if (fg_gauge_unseal(sm) < 0)
		sh_info("unseal error.\n");

	if (fg_gauge_unseal(sm) < 0)
		sh_info("unseal error.\n");

	for (i = 0; i < 10; i++)

		sh_info("pBuf[%d] = 0x%x\n", i, pBuf[i]);

	snprintf(strDebug, 32, "%s", pBuf);


	sh_info("file_decode_process: first data=%s\n", strDebug);

	i = 0;
	j = 0;
frame_retry:
	while (i < buflen) {
		if (pBuf[i + INDEX_TYPE] == OPERATE_WAIT) {



			sh_info("OPERATE_WAIT\n");
			if (pBuf[i + INDEX_WAIT_LENGTH] == 2) {
				wait_ms = ((int)pBuf[i + INDEX_WAIT_HIGH] * 256) + pBuf[i + INDEX_WAIT_LOW];

				sh_info("[%s]wait_ms:%d\n", __func__, wait_ms);
				msleep(wait_ms);
				i += LINELEN_WAIT;
			} else {
				snprintf(strDebug, 32, "%s", &pBuf[i + INDEX_TYPE]);

				sh_info("file_decode_process wait error! index=%d, str=%s\n", i, strDebug);
				result = ERRORTYPE_LINE;
				goto main_process_error;
			}
		} else if (pBuf[i + INDEX_TYPE] == OPERATE_READ) {
			sh_info("OPERATE_READ\n");
			line_length = pBuf[i + INDEX_LENGTH];
			if (line_length <= 0) {
				result = ERRORTYPE_LINE;
				goto main_process_error;
			}

			if (fg_decode_iic_read(sm, (struct sh_decoder *)&pBuf[i + INDEX_ADDR], pBuf_Read) < 0) {
				snprintf(strDebug, 32, "%s", &pBuf[i + INDEX_TYPE]);



				sh_info("file_decode_process read error! index=%d, str=%s\n", i, strDebug);
				result = ERRORTYPE_COMM;
				goto main_process_error;
			}

			i += LINELEN_READ;
		} else if (pBuf[i + INDEX_TYPE] == OPERATE_COMPARE) {
			sh_info("OPERATE_COMPARE----本帧头数据下标[i_bak]=%d,运行第%d个03指令\n", i_bak, cnt);
			line_length = pBuf[i + INDEX_LENGTH];
			if (line_length <= 0) {
				result = ERRORTYPE_LINE;
				goto main_process_error;
			}

			ptr_decoder = (struct sh_decoder *)&pBuf[i + INDEX_ADDR];
			for (retry = 0; retry < COMPARE_RETRY_CNT; retry++) {
				if (fg_decode_iic_read(sm, ptr_decoder, pBuf_Read) < 0) {
					snprintf(strDebug, 32, "%s", &pBuf[i + INDEX_TYPE]);




					sh_info("file_decode_process compare_read error! index=%d, str=%s\n", i, strDebug);
					result = ERRORTYPE_COMM;
					goto file_decode_process_compare_loop_end;
				}

				snprintf(strDebug, line_length, "%s", pBuf_Read);



				sh_info("file_decode_process loop compare successfully: \n\n");

				result = 0;
				for (j = 0; j < line_length; j++) {
					if (pBuf[INDEX_DATA + i + j] != pBuf_Read[j]) {
						sh_info("file_decode_process [%x,%x] %x\n", pBuf[INDEX_DATA + i + j], pBuf_Read[j], pBuf_Read[j + 1]);
						result = ERRORTYPE_COMPARE;
						break;
					}
				}

				if (result == 0)
					break;

				snprintf(strDebug, 32, "%s", &pBuf[i + INDEX_TYPE]);


				sh_info("file_decode_process compare error! index=%d, retry=%d, host=%s\n", i, retry, strDebug);
				snprintf(strDebug, 32, "%s", pBuf_Read);

				sh_info("ic=%s\n\n", strDebug);

file_decode_process_compare_loop_end:
				msleep(COMPARE_RETRY_WAIT);
			}

			if (retry >= COMPARE_RETRY_CNT) {

				sh_info("OPERATE_COMPARE 重试:从本帧[i_bak=%d]处重新写入数据\n", i_bak);
				if (retry2 > 10) {
					result = ERRORTYPE_COMPARE;
					goto main_process_error;
				}
				retry2++;

				sh_info("retry2 = %d\n", retry2);
				i = i_bak;
				cnt = cnt_bak;
				goto frame_retry;
			}

			i += LINELEN_COMPARE + line_length;
			i_bak = i;
			retry2 = 0;
			cnt++;
			cnt_bak = cnt;
		} else if (pBuf[i + INDEX_TYPE] == OPERATE_WRITE) {
			sh_info("OPERATE_WRITE\n");
			line_length = pBuf[i + INDEX_LENGTH];
			if (line_length <= 0) {
				result = ERRORTYPE_LINE;
				goto main_process_error;
			}

			if ((line_length == 2) && (pBuf[i + INDEX_DATA] == 0x41) && (pBuf[i + INDEX_DATA + 1] == 0x00))






				sh_info("sh366003-------_______------start reset fg\n");

			ptr_decoder = (struct sh_decoder *)&pBuf[i + INDEX_ADDR];
			if (fg_decode_iic_write(sm, ptr_decoder) != 0) {
				snprintf(strDebug, 32, "%s", &pBuf[i + INDEX_TYPE]);









				sh_info("file_decode_process write error! index=%d, str=%s\n", i, strDebug);
				result = ERRORTYPE_COMM;
				goto main_process_error;
			}

			i += LINELEN_WRITE + line_length;
		} else {

			sh_info("OPERATE_ no active\n");
			result = ERRORTYPE_LINE;
			goto main_process_error;
		}
	}
	result = ERRORTYPE_NONE;

main_process_error:

	sh_info("file_decode_process end: result=%d\n", result);
	sh_info("end: result=%d\n", result);
	fg_gauge_seal(sm);
	return result;
}

static void fg_check_charge_type(struct sh_fg_chip *sm)
{
	union power_supply_propval val_ac = { 0 };
	int ret = 0;

	sm->adapter_status = 0;
	if (!sm->chg_psy)
		sm->chg_psy = power_supply_get_by_name("primary_chg");
	if (sm->chg_psy) {
		ret = power_supply_get_property(sm->chg_psy, POWER_SUPPLY_PROP_ONLINE, &val_ac);
		if (!ret && val_ac.intval)
			sm->adapter_status = 2;
	}

	if (online_val != val_ac.intval)
























		sh_info("[%s] ret=%d, val_ac.intval=%d\n", __func__, ret, val_ac.intval);
	online_val = val_ac.intval;
}

static void fg_monitor_workfunc(struct work_struct *work)
{
	struct sh_fg_chip *sm = container_of(work, struct sh_fg_chip, monitor_work.work);
	int ret;
	u16 data = 0;

	if (g_sm->fallback_flag == 1)
		goto monitor_end;

	fg_check_charge_type(sm);
	fg_read_SOC(sm);
	fg_read_VCHG(sm);
	fg_read_ICHG(sm);
	fg_read_BatteryStatus(sm);
	fg_read_Voltage(sm);
	fg_read_Current(sm);
	fg_read_IntTemperature(sm);
	fg_read_ExtTemperature(sm);
	fg_read_soh(sm);
	fg_read_cycnt(sm);
	fg_read_rc(sm);
	fg_read_fcc(sm);
	sh_fg_get_batt_info(sm);

	ret = fg_read_word(sm, CMD_CURRENT, &data);
	if (ret < 0)







		sh_info("sh366003_GaugeLog: could not read CMD_Current, ret = %d\n", ret);


	sh_info("RSOC=,%d, Volt=,%d, Curr=,%d,Temp=,%d,SoH:%d,cycnt:%d,Rc:%d,FCC:%d,Vchg:%d,Ichg=%d,BatS:0x%04x\n", sm->batt_soc, sm->batt_volt, (s16)data, sm->batt_temp, sm->batt_soh, sm->batt_cycle, sm->batt_rc, sm->batt_fcc, sm->batt_vchg, sm->batt_ichg, sm->batt_status);

monitor_end:
	queue_delayed_work(system_wq, &sm->monitor_work, msecs_to_jiffies(5000));
}

static char *sh_fg_supplied_from[] = {
	"usb",
	"charger",
	"ac",
};

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

static int sh_fg_battery_get_property(struct power_supply *psy, enum power_supply_property psp, union power_supply_propval *val)
{
	struct sh_fg_chip *sm = power_supply_get_drvdata(psy);

	switch (psp) {
	case POWER_SUPPLY_PROP_STATUS:
		if ((sm->adapter_status == 1) || (sm->adapter_status == 2)) {
			if (sm->batt_soc == 100)
				val->intval = POWER_SUPPLY_STATUS_FULL;
			else
				val->intval = POWER_SUPPLY_STATUS_CHARGING;
		} else {
			val->intval = POWER_SUPPLY_STATUS_DISCHARGING;
		}
		break;
	case POWER_SUPPLY_PROP_HEALTH:
	case POWER_SUPPLY_PROP_PRESENT:
		val->intval = 1;
		break;
	case POWER_SUPPLY_PROP_TECHNOLOGY:
		val->intval = POWER_SUPPLY_TECHNOLOGY_LION;
		break;
	case POWER_SUPPLY_PROP_CYCLE_COUNT:
		val->intval = sm->batt_cycle;
		break;
	case POWER_SUPPLY_PROP_VOLTAGE_NOW:
		val->intval = sm->batt_volt;
		break;
	case POWER_SUPPLY_PROP_CURRENT_NOW:
		val->intval = sm->batt_curr;
		break;
	case POWER_SUPPLY_PROP_CHARGE_FULL_DESIGN:
		val->intval = sm->batt_fcc;
		break;
	case POWER_SUPPLY_PROP_CAPACITY:
		val->intval = sm->batt_soc;
		break;
	case POWER_SUPPLY_PROP_TEMP:
		val->intval = sm->batt_temp;
		break;
	default:
		return -EINVAL;
	}
	return 0;
}

static void sh_fg_external_power_changed(struct power_supply *psy)
{
	struct sh_fg_chip *sm = power_supply_get_drvdata(psy);













	sh_info("enter\n");
	queue_delayed_work(system_wq, &sm->monitor_work, 0);
}

static int sh_fg_power_supply_init(struct sh_fg_chip *sm)
{
	sm->fg_psy_cfg.drv_data = sm;
	sm->fg_psy_d.name = "3rd-gauge";
	sm->fg_psy_d.type = POWER_SUPPLY_TYPE_BATTERY;
	sm->fg_psy_d.properties = sh_fg_battery_props;
	sm->fg_psy_d.num_properties = ARRAY_SIZE(sh_fg_battery_props);
	sm->fg_psy_d.get_property = sh_fg_battery_get_property;
	sm->fg_psy_d.external_power_changed = sh_fg_external_power_changed;

	sm->fg_psy = devm_power_supply_register(sm->dev, &sm->fg_psy_d, &sm->fg_psy_cfg);
	if (IS_ERR(sm->fg_psy)) {

		sh_info("fail: Couldn't register power supply\n");
		return PTR_ERR(sm->fg_psy);
	}
	sm->fg_psy->supplied_from = sh_fg_supplied_from;
	sm->fg_psy->num_supplies = ARRAY_SIZE(sh_fg_supplied_from);
	return 0;
}

bool hal_fg_init(struct i2c_client *client)
{
	struct sh_fg_chip *sm = i2c_get_clientdata(client);




	sh_info("sh366003 hal_fg_init...\n");
	mutex_lock(&sm->data_lock);
	if (fg_init(client) < 0)
		return false;
	mutex_unlock(&sm->data_lock);


	sh_info("hal fg init OK\n");
	return true;
}

static u16 fg_encode_manufacture_date(int year, int month, int day)
{
	return (day & 0x1f) | ((month & 0x0f) << 5) | ((year - 1980) << 9);
}

static ssize_t manufacturing_date_store(struct class *c, struct class_attribute *attr, const char *buf, size_t count)
{
	char date[10];
	char year[5];
	char month[3];
	char day[3];
	unsigned long y, m, d;
	u16 temp;
	u8 tmp_buffer[2];

	date[9] = 0;
	if (count < 8)
		return count;

	strncpy(date, buf, 9);
	strncpy(year, date, 4);
	year[4] = 0;
	y = simple_strtoul(year, NULL, 0);
	strncpy(month, date + 4, 2);
	month[2] = 0;
	m = simple_strtoul(month, NULL, 0);
	strncpy(day, date + 6, 2);
	day[2] = 0;
	d = simple_strtoul(day, NULL, 0);

















	pr_info("%s str  %s %s %s ul %lu %lu %lu\n", __func__, year, month, day, y, m, d);

	temp = fg_encode_manufacture_date(y, m, d);


	pr_info("%s str  %s %s %s ul %lu %lu %lu temp 0x%x\n", __func__, year, month, day, y, m, d, temp);

	tmp_buffer[0] = temp >> 8;
	tmp_buffer[1] = temp & 0xff;
	pr_info("%s temp 0x%x tmp_buffer %x %x\n", __func__, temp, tmp_buffer[0], tmp_buffer[1]);

	fg_write_IntManufactureTimedate(g_sm, tmp_buffer);
	return count;
}

static ssize_t chipid_show(struct class *c, struct class_attribute *attr, char *buf)
{
	return sprintf(buf, "%d\n", chipid);
}

static ssize_t chipid_store(struct class *c, struct class_attribute *attr, const char *buf, size_t count)
{
	return 0;
}

static ssize_t force_upgrade_show(struct class *c, struct class_attribute *attr, char *buf)
{
	return sprintf(buf, "%d", g_sm->force_upgrade);
}

static ssize_t force_upgrade_store(struct class *c, struct class_attribute *attr, const char *buf, size_t count)
{
	sscanf(buf, "%d", &g_sm->force_upgrade);
	schedule_delayed_work(&g_sm->update_work, msecs_to_jiffies(20));
	return count;
}

static ssize_t show_fw_version(struct class *c, struct class_attribute *attr, char *buf)
{
	return sprintf(buf, "%s\n", fuelgauge_fw_version);
}

static ssize_t manufacturing_date_show(struct class *c, struct class_attribute *attr, char *buf)
{
	return snprintf(buf, PAGE_SIZE, "%u\n", g_sm->manufacture_date);
}

static ssize_t manufacturing_year_show(struct class *c, struct class_attribute *attr, char *buf)
{
	return snprintf(buf, PAGE_SIZE, "%u\n", g_sm->manufacture_year);
}

static ssize_t manufacturing_month_show(struct class *c, struct class_attribute *attr, char *buf)
{
	return snprintf(buf, PAGE_SIZE, "%02u\n", g_sm->manufacture_month);
}

static ssize_t manufacturing_day_show(struct class *c, struct class_attribute *attr, char *buf)
{
	return snprintf(buf, PAGE_SIZE, "%02u\n", g_sm->manufacture_day);
}

static int get_sh366003_boot_mode_from_dts(void)
{
	struct device_node *np_chosen = NULL;
	struct tag_bootmode {
		u32 size;
		u32 tag;
		u32 bootmode;
		u32 boottype;
	} *tag = NULL;

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


	pr_notice("log_store: bootmode: 0x%x boottype: 0x%x.\n", tag->bootmode, tag->boottype);
	return tag->bootmode;
}

static void fg_update_workfunc(struct work_struct *work)
{
	struct sh_fg_chip *sm = container_of(work, struct sh_fg_chip, update_work.work);
	int boot_mode = get_sh366003_boot_mode_from_dts();
	int version;
	int ret;
	int i;

	if ((sm->adapter_status == 2) || (sm->batt_soc < 11) || (boot_mode == 8) || (boot_mode == 9)) {




		sh_info("not Update FW!! adapter_status=%d, soc=%d, boot_mode=%d\n", sm->adapter_status, sm->batt_soc, boot_mode);
		return;
	}

	version = ((g_sm->force_upgrade > 0) ? g_sm->force_upgrade : 0) | sm->auto_update;


	sh_info("upgrade wait\n");
	mutex_lock(&sm->upgrade_lock);
	sh_info("upgrade start\n");
	if (version == -1) {
		sh_info(" Check version error!\n");
	} else if (version == 0) {
		sh_info(" Check version ok!\n");
		goto update_end;
	} else {
		sh_info(" Check version update: %X , force_ugrade = %X\n", version, g_sm->force_upgrade);
		sm->fallback_flag = 1;
		sm->fallback_soc = sm->batt_soc;
		sm->fallback_volt = sm->batt_soc;
		sm->fallback_curr = sm->batt_soc;
		sm->fallback_temp = sm->batt_temp;



		sh_info(" AFI Update start\n");
		for (i = 0; i < 2; i++) {
			ret = file_decode_process(sm, "sinofs_afi_data");
			if (!ret)
				break;
			msleep(100);
		}
		if (ret == 0)
			sh_info(" AFI Update successfully!, ret=%d\n", ret);
		else
			sh_info(" AFI Update fail!, error! ret=%d\n", ret);
	}

	if (fg_gauge_runstate_check(sm) < 0) {



		sh_info("Failed to Enable Gauge\n");
		goto update_end;
	}

	if (!hal_fg_init(sm->client))
		sh_info("Failed to Initialize Fuelgauge\n");

update_end:

	sh_info("upgrade done\n");
	g_sm->force_upgrade = -1;
	sm->fallback_flag = 0;
	mutex_unlock(&sm->upgrade_lock);
}

static ssize_t manufacturename_show(struct class *c, struct class_attribute *attr, char *buf)
{
	return sprintf(buf, "%c%c%c%c%c%c%c\n", g_sm->manufacturename[0], g_sm->manufacturename[1], g_sm->manufacturename[2], g_sm->manufacturename[3], g_sm->manufacturename[4], g_sm->manufacturename[5], g_sm->manufacturename[6]);
}

static ssize_t serialnum_show(struct class *c, struct class_attribute *attr, char *buf)
{
	return sprintf(buf, "%04d\n", g_sm->serialnum);
}

static ssize_t soh_show(struct class *c, struct class_attribute *attr, char *buf)
{
	if ((g_sm->batt_cycle >= 0) && (g_sm->batt_cycle < 400))
		g_sm->display_soh -= g_sm->batt_cycle / 40;
	else if (g_sm->batt_cycle >= 400)
		g_sm->display_soh -= ((g_sm->batt_cycle - 400) / 60 + 10);

	return sprintf(buf, "%d\n", g_sm->display_soh);
}

static struct class_attribute class_attr_sh_fg[] = {
	__ATTR(chipid, 0664, chipid_show, chipid_store),
	__ATTR(force_upgrade, 0664, force_upgrade_show, force_upgrade_store),
	__ATTR(fw_version, 0664, show_fw_version, NULL),
	__ATTR(manufacturing_date, 0664, manufacturing_date_show, manufacturing_date_store),
	__ATTR(manufacturing_year, 0444, manufacturing_year_show, NULL),
	__ATTR(manufacturing_month, 0444, manufacturing_month_show, NULL),
	__ATTR(manufacturing_day, 0444, manufacturing_day_show, NULL),
	__ATTR(manufacturename, 0444, manufacturename_show, NULL),
	__ATTR(serialnum, 0444, serialnum_show, NULL),
	__ATTR(soh, 0444, soh_show, NULL),
	__ATTR_NULL,
};

static int sh_fg_probe(struct i2c_client *client, const struct i2c_device_id *id)
{
	struct sh_fg_chip *sm;
	int ret;
	int i;
	u16 sh_manuf_ret = 0;
	char sh_manuf_ascii[5] = "0000";











	sh_info("2022.10.17 %s: start,i2c addr is 0x%02x\n", __func__, client->addr);


	sh_info("enter ,  i2c addr is 0x%02x\n", client->addr);

	sm = devm_kzalloc(&client->dev, sizeof(*sm), GFP_KERNEL);
	if (!sm)
		return -ENOMEM;

	sm->dev = &client->dev;
	sm->client = client;
	sm->chip = id->driver_data;
	sm->batt_soc = -ENODATA;
	sm->batt_volt = -ENODATA;
	sm->batt_curr = -ENODATA;
	sm->force_upgrade = -1;
	memcpy(sm->regs, sh366003_regs, NUM_REGS * sizeof(u32));
	i2c_set_clientdata(client, sm);

	mutex_init(&sm->i2c_rw_lock);
	mutex_init(&sm->data_lock);
	mutex_init(&sm->cali_lock);
	mutex_init(&sm->upgrade_lock);
	mutex_init(&sm->wrblk_lock);

	fg_read_sbs_word(sm, sm->regs[SH_FG_REG_CHIPID], &chipid);








	sh_info("sh366003 read chipid = 0x%02x\n", chipid);
	if (chipid != SH366003_DEVICE_ID)
		return -ENOMEM;

	sh_fg_class = class_create(THIS_MODULE, "3rd-gauge");
	if (IS_ERR(sh_fg_class)) {
		ret = PTR_ERR(sh_fg_class);



		sh_info("create class, err = %d\n", ret);
		return ret;
	}
	for (i = 0; class_attr_sh_fg[i].attr.name; i++) {
		ret = class_create_file(sh_fg_class, &class_attr_sh_fg[i]);
		if (ret) {
			sh_info("Fail class_create_file\n");
			return ret;
		}
	}

	fg_read_sbs_word(sm, CMD_MANUF_ASCII, &sh_manuf_ret);
	sh_manuf_ascii[0] = sh_manuf_ret & 0xff;
	sh_manuf_ascii[1] = sh_manuf_ret >> 8;
	sh_manuf_ascii[4] = 0;
	sh_info("read sh_manuf_ret = 0x%04x, ASCII=%s,[%c,%c,%c]\n", sh_manuf_ret, sh_manuf_ascii, sh_manuf_ascii[0], sh_manuf_ascii[1], sh_manuf_ascii[2]);

	fg_read_SOC(sm);
	fg_read_Voltage(sm);
	fg_read_Current(sm);
	fg_read_ExtTemperature(sm);
	fg_read_IntTemperature(sm);
	fg_read_IntManufacturedate(sm);
	fg_read_IntManufacturename(sm);
	fg_read_Intserialnum(sm);
	fg_read_maxvoltage(sm);
	sh_info(" sh366003 read manufacturedate = 0x%02x [y=%d,m=%d,d=%d]\n", sm->manufacture_date, sm->manufacture_year, sm->manufacture_month, sm->manufacture_day);
	sprintf(fuelgauge_fw_version, "Vno:0x%02x-%s(%02d%02d)\n", sm->manufacture_date, sh_manuf_ascii, sm->manufacture_month, sm->manufacture_day);

	sm->fallback_flag = 0;
	g_sm = sm;
	ret = Check_Chip_Version(sm);
	if (ret == -1) {


		sh_info("Probe: Check version error!\n");
	} else if (ret == 0) {
		sh_info("Probe: Check version ok!\n");
	} else if ((sm->batt_soc == 0) && (sm->batt_volt == 0)) {

		sh_info("maybe upgrade failed ,force set soc == 0 \n");
		sm->batt_soc = 4;
		sm->batt_volt = 3600;
		sm->batt_temp = 256;
		sm->fallback_soc = 4;
		sm->fallback_temp = 256;
		sm->fallback_flag = 1;
		sm->fallback_volt = 3600;
	}

	INIT_DELAYED_WORK(&sm->monitor_work, fg_monitor_workfunc);
	queue_delayed_work(system_wq, &sm->monitor_work, msecs_to_jiffies(10000));
	INIT_DELAYED_WORK(&sm->update_work, fg_update_workfunc);
	queue_delayed_work(system_wq, &sm->update_work, msecs_to_jiffies(12000));

	yft_set_fuelgauge_device_used("sh366003", 1);








	sh_info("sh fuel gauge probe successfully, %s\n", device2str[sm->chip]);
	sh_info("2022.10.17 %s: end\n", __func__);

	sh_fg_power_supply_init(sm);
	g_sm->display_soh = 100;
	return 0;
}

static void sh_fg_remove(struct i2c_client *client)
{
}

static void sh_fg_shutdown(struct i2c_client *client)
{













	sh_info("sm fuel gauge driver shutdown!\n");
}

static const struct of_device_id sh_fg_match_table[] = {
	{ .compatible = "sh,sh366003", },
	{},
};
MODULE_DEVICE_TABLE(of, sh_fg_match_table);

static const struct i2c_device_id sh_fg_id[] = {
	{ "sh366003", 0 },
	{},
};
MODULE_DEVICE_TABLE(i2c, sh_fg_id);

static struct i2c_driver sh_fg_driver = {
	.driver = {
		.name = "sh366003",
		.owner = THIS_MODULE,
		.of_match_table = sh_fg_match_table,
	},
	.id_table = sh_fg_id,
	.probe = sh_fg_probe,
	.remove = sh_fg_remove,
	.shutdown = sh_fg_shutdown,
};

static int __init sh366003_driver_init(void)
{
	int ret;




	pr_info(" start\n");
	yft_fuelgauge_device_add(&sh_fg_driver, 0);
	ret = i2c_add_driver(&sh_fg_driver);
	if (ret) {





		pr_info("sh366003  driver init failed!");
		return -1;
	}

	pr_info(" end\n");
	return 0;
}

static void __exit sh366003_driver_exit(void)
{






	pr_info(" start\n");
	i2c_del_driver(&sh_fg_driver);
	pr_info(" end\n");
}

module_init(sh366003_driver_init);
module_exit(sh366003_driver_exit);

MODULE_DESCRIPTION("SH SH366003 Gauge Driver");
MODULE_LICENSE("GPL v2");
MODULE_AUTHOR("Sinowealth");
