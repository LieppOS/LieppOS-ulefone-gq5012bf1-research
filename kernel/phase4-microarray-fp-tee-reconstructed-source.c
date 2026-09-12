// SPDX-License-Identifier: GPL-2.0
/*
 * MicroArray fingerprint SPI/TEE driver - clean-room reconstruction of the
 * Ulefone Armor 29 Pro Thermal (GQ5012BF1, MT6878) stock microarray_fp_tee.ko.
 *
 * Reconstructed from the frozen stock oracle
 *   sha256 8e1449cea5d07ef663d368ce5eea27e8c879a9cd70d39f8fc2b5b25445c2cf33
 * by relocation-aware disassembly of .text/.init.text/.exit.text plus the
 * frozen .data/.rodata images, the stock device tree, and the stock userspace
 * consumers /vendor/lib64/libfprint-x64.so and
 * /vendor/lib64/hw/microarray.fingerprint.default.so.
 *
 * No donor source exists for this module (see the project EMPTY-SOURCE RED
 * report).  Every behaviour below is taken from the stock binary; nothing
 * about the secure world is invented here.
 *
 * Provider graph (unchanged from stock):
 *   fingerprint.ko  - yft_waite_for_finger_dts_paser, yft_finger_set_reset,
 *                     yft_finger_set_spi_mode, yft_finger_set_irq
 *   spi-mt65xx.ko   - mt_spi_enable_master_clk, mt_spi_disable_master_clk
 *   tkcore.ko       - tee_spi_transfer   (TrustKernel; never replaced by a
 *                     generic TEE call or by a direct SPI transfer)
 */

#include <linux/cdev.h>
#include <linux/delay.h>
#include <linux/device.h>
#include <linux/fs.h>
#include <linux/input.h>
#include <linux/interrupt.h>
#include <linux/io.h>
#include <linux/irq.h>
#include <linux/kernel.h>
#include <linux/mm.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/of.h>
#include <linux/of_irq.h>
#include <linux/platform_device.h>
#include <linux/pm_wakeup.h>
#include <linux/regulator/consumer.h>
#include <linux/sched.h>
#include <linux/slab.h>
#include <linux/spi/spi.h>
#include <linux/sysfs.h>
#include <linux/uaccess.h>
#include <linux/wait.h>
#include <linux/workqueue.h>

/* ------------------------------------------------------------------ */
/* Stock intermodule ABI (never replaced, never reimplemented)         */
/* ------------------------------------------------------------------ */

/* fingerprint.ko */
extern void yft_waite_for_finger_dts_paser(void);
extern int yft_finger_set_reset(int enable);
extern int yft_finger_set_spi_mode(int enable);
extern int yft_finger_set_irq(int enable);

/* spi-mt65xx.ko */
extern void mt_spi_enable_master_clk(struct spi_device *spidev);
extern void mt_spi_disable_master_clk(struct spi_device *spidev);

/* tkcore.ko (TrustKernel) */
extern int tee_spi_transfer(void *conf, int conf_size, const char *txbuf,
			    char *rxbuf, int len);

/* ------------------------------------------------------------------ */
/* Stock log vocabulary                                               */
/* ------------------------------------------------------------------ */

#define MA_TAG		"MAFP_"

#define ma_debug(fn, msg) \
	printk(KERN_DEBUG "%s%s: debug log! %s!\n", MA_TAG, fn, msg)
#define ma_warn(fn, msg, r) \
	printk(KERN_WARNING "%s%s: warning log! the function %s's ret = %d\n", \
	       MA_TAG, fn, msg, (r))
#define ma_err(fn, msg, r) \
	printk(KERN_ERR "%s%s: error log! the function %s is failed, ret = %d\n", \
	       MA_TAG, fn, msg, (r))

/* ------------------------------------------------------------------ */
/* Device tree / platform constants recovered from the stock module    */
/* ------------------------------------------------------------------ */

#define MA_DEV_NAME		"madev"
#define MA_NODE_NAME		"madev0"
#define MA_COMPATIBLE		"mediatek,madev_finger"
#define MA_EINT_COMPATIBLE	"mediatek,yft_finger"
#define MA_IRQ_NAME		"mediatek,finger_print-eint"
#define MA_WQ_NAME		"mas_workqueue"
#define MA_WAKELOCK_NAME	"microarray_process_wakelock"
#define MA_REGULATOR_ID		"vfp"

#define MA_REGULATOR_UV		2800000		/* 0x2ab980 */
#define MA_SPI_SPEED_HZ		6000000		/* 0x5b8d80 */
#define MA_XFER_MAX		0xc000		/* read/write clamp */
#define MA_MMAP_SIZE		0x11000		/* mmap backing buffer */
#define MA_KEY_CODE		249
#define MA_WAKE_MS		5000

/* ------------------------------------------------------------------ */
/* ioctl ABI (magic 'M' = 0x4d), recovered from the stock dispatcher   */
/* ------------------------------------------------------------------ */

#define MA_IOC_MAGIC		'M'

/* plain _IO() commands, 0x4d01 .. 0x4d2d */
#define MA_IOC_WAKELOCK		_IO(MA_IOC_MAGIC, 0x01)	/* 0x4d01 */
#define MA_IOC_WAIT_INT		_IO(MA_IOC_MAGIC, 0x02)	/* 0x4d02 */
#define MA_IOC_WAKE_INT		_IO(MA_IOC_MAGIC, 0x03)	/* 0x4d03 */
#define MA_IOC_NOP_04		_IO(MA_IOC_MAGIC, 0x04)	/* 0x4d04 */
#define MA_IOC_NOP_05		_IO(MA_IOC_MAGIC, 0x05)	/* 0x4d05 */
#define MA_IOC_IRQ_ENABLE	_IO(MA_IOC_MAGIC, 0x06)	/* 0x4d06 */
#define MA_IOC_IRQ_DISABLE	_IO(MA_IOC_MAGIC, 0x07)	/* 0x4d07 */
#define MA_IOC_KEY_DOWN		_IO(MA_IOC_MAGIC, 0x08)	/* 0x4d08 */
#define MA_IOC_KEY_UP		_IO(MA_IOC_MAGIC, 0x09)	/* 0x4d09 */
#define MA_IOC_KEY_CLICK	_IO(MA_IOC_MAGIC, 0x0b)	/* 0x4d0b */
#define MA_IOC_NOP_0D		_IO(MA_IOC_MAGIC, 0x0d)	/* 0x4d0d */
#define MA_IOC_POWER_OFF	_IO(MA_IOC_MAGIC, 0x24)	/* 0x4d24 */
#define MA_IOC_POWER_ON		_IO(MA_IOC_MAGIC, 0x25)	/* 0x4d25 */
#define MA_IOC_WAIT_U2		_IO(MA_IOC_MAGIC, 0x27)	/* 0x4d27 */
#define MA_IOC_WAKE_U2		_IO(MA_IOC_MAGIC, 0x28)	/* 0x4d28 */
#define MA_IOC_POWER_RESET	_IO(MA_IOC_MAGIC, 0x2d)	/* 0x4d2d */

/* _IOW(..., u32) commands */
#define MA_IOC_SET_REG		_IOW(MA_IOC_MAGIC, 0x21, u32)	/* 0x40044d21 */
#define MA_IOC_SET_SPEED	_IOW(MA_IOC_MAGIC, 0x26, u32)	/* 0x40044d26 */
#define MA_IOC_SET_REG_WAKE_U1	_IOW(MA_IOC_MAGIC, 0x2a, u32)	/* 0x40044d2a */

/* _IOR(..., u32) commands */
#define MA_IOC_GET_REG		_IOR(MA_IOC_MAGIC, 0x22, u32)	/* 0x80044d22 */
#define MA_IOC_GET_VERSION	_IOR(MA_IOC_MAGIC, 0x23, u32)	/* 0x80044d23 */
#define MA_IOC_WAIT_U1_GET_REG	_IOR(MA_IOC_MAGIC, 0x29, u32)	/* 0x80044d29 */
#define MA_IOC_GET_SCREEN_STATE	_IOR(MA_IOC_MAGIC, 0x2b, u32)	/* 0x80044d2b */

/* ------------------------------------------------------------------ */
/* Private state                                                      */
/* ------------------------------------------------------------------ */

/*
 * Layout mirrors the stock kmalloc(0x248) private object.  Offsets shown in
 * the comments are the stock offsets the disassembly proves.
 */
struct mas_struct {
	void		*unused0;	/* 0x000 */
	u8		pad0;		/* 0x008 -> flag_int lives at 0x008 */
	u8		flag_u1;	/* 0x009 */
	u8		flag_u2;	/* 0x00a */
	u8		pad1[5];
	struct spi_device *spi;		/* 0x010 */
	struct list_head list;		/* 0x018 */
	struct spi_message msg;		/* 0x028 */
	struct spi_transfer xfer;	/* 0x0a0 */
	struct input_dev *input;	/* 0x138 */
	u8		reserved[0x108];
};

/* the gWaitq condition byte is stock offset 0x008 */
#define flag_int	pad0

struct mas_dev_node {
	dev_t		devno;		/* 0x00 */
	void		*pad;		/* 0x08 */
	struct cdev	*cdev;		/* 0x10 */
	struct class	*cls;		/* 0x18 */
	struct device	*dev;		/* 0x20 */
};

static int ret;					/* .bss+0x2c */
static struct regulator *fp_mt6373_ldo;		/* .bss+0x08 */
struct device_node *node;			/* .bss+0x10, stock leaves it unused */
static struct mas_struct *smas;			/* .bss+0x18 */
void *kernel_memaddr;				/* .bss+0x20 */
static u16 chip_id;				/* .bss+0x28 */
static bool compatible;				/* .bss+0x30 */
struct wakeup_source *gProcessWakeLock;		/* .bss+0x38 */
struct work_struct gWork;			/* .bss+0x40 */
struct workqueue_struct *gWorkq;		/* .bss+0x70 */
static struct mas_dev_node *sdev;		/* .bss+0x78 */
static u8 *srxb;				/* .bss+0x80 */
static u8 *stxb;				/* .bss+0x88 */
static int irq;					/* .bss+0x90 */
static u32 ma_drv_reg;				/* .bss+0x98 */
static u32 ma_speed;				/* .bss+0x9c */
static int is_screen_on;			/* .bss+0xa0 */

static DEFINE_MUTEX(dev_lock);			/* .data+0x128 */
static DECLARE_WAIT_QUEUE_HEAD(gWaitq);		/* .data+0x1d0 */
static DEFINE_MUTEX(ioctl_lock);		/* .data+0x1e8 */
static int MA_DRV_VERSION = 0x4006;		/* .data+0x218 */
static DECLARE_WAIT_QUEUE_HEAD(U2_Waitq);	/* .data+0x220 */
static DECLARE_WAIT_QUEUE_HEAD(U1_Waitq);	/* .data+0x238 */

int mas_probe(struct spi_device *spi);
void mas_remove(struct spi_device *spi);
extern struct spi_driver sdrv;

/* ------------------------------------------------------------------ */
/* Transfer helpers                                                   */
/* ------------------------------------------------------------------ */

/*
 * Both of these are empty in the stock module; they are retained so the
 * reconstructed call graph and the stock call graph agree exactly.
 */
void mas_select_transfer(struct spi_device *spi, int len)
{
}

void ma_spi_change(struct spi_device *spi, u32 speed, int mode)
{
}

int mas_remove_platform(void)
{
	driver_unregister(&sdrv.driver);
	return 0;
}

/* ------------------------------------------------------------------ */
/* Power                                                              */
/* ------------------------------------------------------------------ */

int mas_switch_power(int on)
{
	static int ret;

	ret = 0;
	printk(KERN_ERR "yftwang %s: regulator_enable enable mt6377_ldo start!!\n",
	       __func__);

	if (on) {
		ret = regulator_enable(fp_mt6373_ldo);
		if (ret < 0) {
			printk(KERN_ERR
			       "yftwang %s: regulator_enable enable mt6377_ldo fail!!\n",
			       __func__);
			return -1;
		}
	} else {
		ret = regulator_disable(fp_mt6373_ldo);
		if (ret < 0) {
			printk(KERN_ERR
			       "yftwang %s: regulator_disable disable mt6377_ldo fail!!\n",
			       __func__);
			return -1;
		}
	}

	return 0;
}

/*
 * The stock implementation ignores its second argument entirely: it always
 * acquires "vfp", programs 2.8 V, enables it, and then drives the three YFT
 * glue setters with 1.  Their return values are deliberately not checked.
 */
int mas_finger_set_gpio_info(struct device *dev, int on)
{
	ret = 0;
	printk(KERN_ERR "yftwang %s: regulator_enable enable mt6377_ldo start!!\n",
	       __func__);

	fp_mt6373_ldo = regulator_get(dev, MA_REGULATOR_ID);
	if (IS_ERR(fp_mt6373_ldo)) {
		ret = (int)(long)fp_mt6373_ldo;
		printk(KERN_ERR "yftwang %s: regulator_get mt6377_ldo fail=%d!!\n",
		       __func__, ret);
		goto set_gpio;
	}

	ret = regulator_set_voltage(fp_mt6373_ldo, MA_REGULATOR_UV,
				    MA_REGULATOR_UV);
	if (ret < 0) {
		printk(KERN_ERR
		       "yftwang %s: regulator_set_voltage mt6377_ldo fail!!\n",
		       __func__);
		return -1;
	}

	ret = regulator_enable(fp_mt6373_ldo);
	if (ret < 0) {
		printk(KERN_ERR
		       "yftwang %s: regulator_enable enable mt6377_ldo fail!!\n",
		       __func__);
		return -1;
	}

	printk(KERN_ERR
	       "yftwang %s: regulator_enable enable mt6377_ldo success!!\n",
	       __func__);

set_gpio:
	yft_finger_set_reset(1);
	yft_finger_set_spi_mode(1);
	yft_finger_set_irq(1);

	return ret;
}

void mas_enable_spi_clock(struct spi_device *spi)
{
	mt_spi_enable_master_clk(spi);
}

void mas_disable_spi_clock(struct spi_device *spi)
{
	mt_spi_disable_master_clk(spi);
}

int mas_get_irq(void)
{
	struct device_node *np;

	np = of_find_compatible_node(NULL, NULL, MA_EINT_COMPATIBLE);
	return irq_of_parse_and_map(np, 0);
}

/* ------------------------------------------------------------------ */
/* Normal-world SPI data path                                         */
/* ------------------------------------------------------------------ */

int mas_sync(const u8 *tx, u8 *rx, int len)
{
	int status;

	mas_select_transfer(smas->spi, len);

	smas->xfer.tx_buf = tx;
	smas->xfer.rx_buf = rx;
	smas->xfer.len = len;
	smas->xfer.bits_per_word = 8;
	smas->xfer.tx_nbits = SPI_NBITS_SINGLE;
	smas->xfer.rx_nbits = SPI_NBITS_SINGLE;
	smas->xfer.delay.value = 1;
	smas->xfer.delay.unit = SPI_DELAY_UNIT_USECS;
	smas->xfer.speed_hz = smas->spi->max_speed_hz;

	spi_message_init(&smas->msg);
	spi_message_add_tail(&smas->xfer, &smas->msg);

	yft_finger_set_spi_mode(1);

	mutex_lock(&dev_lock);
	status = spi_sync(smas->spi, &smas->msg);
	mutex_unlock(&dev_lock);

	return status;
}

/* ------------------------------------------------------------------ */
/* mmap                                                               */
/* ------------------------------------------------------------------ */

int mas_mmap(struct file *filp, struct vm_area_struct *vma)
{
	if (!kernel_memaddr) {
		kernel_memaddr = kmalloc(MA_MMAP_SIZE, GFP_KERNEL);
		if (!kernel_memaddr)
			return -1;
	}

	vma->vm_page_prot = pgprot_noncached(vma->vm_page_prot);

	if (remap_pfn_range(vma, vma->vm_start,
			    virt_to_phys(kernel_memaddr) >> PAGE_SHIFT,
			    vma->vm_end - vma->vm_start, vma->vm_page_prot))
		return -1;

	return 0;
}

/* ------------------------------------------------------------------ */
/* TrustKernel chip identification                                    */
/* ------------------------------------------------------------------ */

/*
 * 80-byte configuration blob handed verbatim to the TrustKernel SPI proxy TA
 * as MEMREF_TEMP_INPUT.  The field semantics live in the secure world and are
 * NOT recovered; only the exact byte image is reproduced here, matching stock
 * .data+0x158 byte for byte.
 */
struct mas_tee_spi_conf {
	u32 word[20];
};

int init_connect(void)
{
	static struct mas_tee_spi_conf smt_conf = {
		.word = {
			10, 10, 10, 10, 10,
			0, 0, 0, 0, 0,
			1, 1, 0, 0, 0,
			1, 0, 0, 0, 0,
		},
	};
	u8 tx_reset[4] = { 0x8c, 0xff, 0xff, 0xff };
	u8 tx_rdid[4]  = { 0x00, 0xff, 0xff, 0xff };
	u8 outid[4] = { 0 };
	u8 tx_a[5] = { 0x70, 0x00, 0x00, 0x00, 0x00 };
	u8 tx_b[5] = { 0x90, 0x08, 0x00, 0x00, 0x00 };
	u8 tx_c[5] = { 0x90, 0x0b, 0x00, 0x00, 0x00 };
	u8 inid[5] = { 0 };

	/* 1: soft reset, tx and rx share one buffer exactly like stock */
	if (tee_spi_transfer(&smt_conf, sizeof(smt_conf),
			     tx_reset, tx_reset, sizeof(tx_reset))) {
		printk("TEE RESET SPI transfer failed\n");
		return -1;
	}
	msleep(100);

	/* 2: read id */
	if (tee_spi_transfer(&smt_conf, sizeof(smt_conf),
			     tx_rdid, outid, sizeof(tx_rdid)))
		goto xfer_failed;

	printk("[MAFP] outid[3]=[0x%x, 0x%x,0x%x,0x%x]\n",
	       outid[0], outid[1], outid[2], outid[3]);

	if ((outid[3] & ~0x04) == 0x41) {
		printk("[MAFP] chip is ok1\n");
		chip_id = outid[3];
		return chip_id;
	}

	/* 3+4: second identification sequence */
	if (tee_spi_transfer(&smt_conf, sizeof(smt_conf),
			     tx_a, inid, sizeof(tx_a)))
		goto xfer_failed;
	msleep(3);
	if (tee_spi_transfer(&smt_conf, sizeof(smt_conf),
			     tx_b, inid, sizeof(tx_b)))
		goto xfer_failed;

	if (inid[3] == 0x20 || inid[3] == 0x1a) {
		printk("[MAFP] chip is ok2\n");
		chip_id = inid[3];
		return chip_id;
	}

	/* 5: third identification sequence */
	if (tee_spi_transfer(&smt_conf, sizeof(smt_conf),
			     tx_c, inid, sizeof(tx_c)))
		goto xfer_failed;

	if (inid[3] == 0x4a) {
		printk("[MAFP] chip is ok3\n");
		chip_id = inid[3];
		return chip_id;
	}

	printk("[%s], chip_id is 0x%x\n", __func__, chip_id);
	return chip_id;

xfer_failed:
	printk("TEE SPI transfer failed\n");
	return -1;
}

int deinit_connect(void)
{
	return 0;
}

/* ------------------------------------------------------------------ */
/* Unused platform hooks retained from stock                          */
/* ------------------------------------------------------------------ */

int mas_plat_probe(struct platform_device *pdev)
{
	ret = mas_finger_set_gpio_info(&pdev->dev, 1);
	if (ret)
		ma_err(__func__, "mas_plat_probe do mas_finger_set_gpio_info",
		       ret);
	return ret;
}

int mas_plat_remove(struct platform_device *pdev)
{
	mas_finger_set_gpio_info(&pdev->dev, 0);
	return 0;
}

/* ------------------------------------------------------------------ */
/* Input, IRQ, work                                                   */
/* ------------------------------------------------------------------ */

static void mas_set_input(void)
{
	struct input_dev *idev;

	idev = input_allocate_device();
	if (!idev) {
		ma_warn(__func__, "input_allocate_device failed.", ret);
		return;
	}

	__set_bit(EV_KEY, idev->evbit);
	__set_bit(MA_KEY_CODE, idev->keybit);
	__set_bit(KEY_POWER, idev->keybit);
	idev->id.bustype = BUS_SPI;
	idev->name = MA_DEV_NAME;

	ret = input_register_device(idev);
	if (ret) {
		input_free_device(idev);
		ma_warn(__func__, "failed to register input device.", ret);
		return;
	}

	smas->input = idev;
}

static void mas_work(struct work_struct *work)
{
	smas->flag_int = 1;
	wake_up_interruptible(&gWaitq);
}

static irqreturn_t mas_interrupt(int irqno, void *dev_id)
{
	queue_work(gWorkq, &gWork);
	return IRQ_HANDLED;
}

/* ------------------------------------------------------------------ */
/* Character device operations                                        */
/* ------------------------------------------------------------------ */

static ssize_t mas_read(struct file *filp, char __user *buf, size_t count,
			loff_t *ppos)
{
	int status;

	if (count > MA_XFER_MAX) {
		ma_warn(__func__, "data too long", 0);
		return -1;
	}

	status = mas_sync(stxb, srxb, count);
	if (status) {
		ma_warn(__func__, "mas_sync failed.", status);
		return -2;
	}

	if (copy_to_user(buf, srxb, count)) {
		ma_warn(__func__, "copy_to_user failed.", ret);
		return -3;
	}

	return count;
}

static ssize_t mas_write(struct file *filp, const char __user *buf,
			 size_t count, loff_t *ppos)
{
	unsigned long left;
	u8 cmd[6] = { 0 };

	if (count == 6) {
		ret = copy_from_user(cmd, buf, sizeof(cmd));
		return 0;
	}

	if (count > MA_XFER_MAX) {
		ma_warn(__func__, "write data too long", ret);
		return -1;
	}

	memset(stxb, 0, MA_XFER_MAX);

	left = copy_from_user(stxb, buf, count);
	ret = left;
	if (left) {
		ma_warn(__func__, "copy form user failed", (int)left);
		return -2;
	}

	ret = 0;
	return count;
}

static long mas_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)
{
	void __user *argp = (void __user *)arg;
	long rc = 0;

	switch (cmd) {
	case MA_IOC_WAKELOCK:
		__pm_wakeup_event(gProcessWakeLock, MA_WAKE_MS);
		break;

	case MA_IOC_WAIT_INT:
		smas->flag_int = 0;
		rc = wait_event_interruptible(gWaitq, smas->flag_int);
		break;

	case MA_IOC_WAKE_INT:
		smas->flag_int = 1;
		wake_up_interruptible(&gWaitq);
		break;

	case MA_IOC_NOP_04:
	case MA_IOC_NOP_05:
	case MA_IOC_NOP_0D:
		break;

	case MA_IOC_IRQ_ENABLE:
		enable_irq(irq);
		break;

	case MA_IOC_IRQ_DISABLE:
		disable_irq(irq);
		break;

	case MA_IOC_KEY_DOWN:
		input_event(smas->input, EV_KEY, MA_KEY_CODE, 1);
		input_event(smas->input, EV_SYN, SYN_REPORT, 0);
		break;

	case MA_IOC_KEY_UP:
		input_event(smas->input, EV_KEY, MA_KEY_CODE, 0);
		input_event(smas->input, EV_SYN, SYN_REPORT, 0);
		break;

	case MA_IOC_KEY_CLICK:
		input_event(smas->input, EV_KEY, MA_KEY_CODE, 1);
		input_event(smas->input, EV_SYN, SYN_REPORT, 0);
		input_event(smas->input, EV_KEY, MA_KEY_CODE, 0);
		input_event(smas->input, EV_SYN, SYN_REPORT, 0);
		break;

	case MA_IOC_POWER_OFF:
		mas_switch_power(0);
		break;

	case MA_IOC_POWER_ON:
		mas_switch_power(1);
		break;

	case MA_IOC_POWER_RESET:
		mas_switch_power(0);
		msleep(5);
		mas_switch_power(1);
		break;

	case MA_IOC_WAIT_U2:
		smas->flag_u2 = 0;
		wait_event_interruptible(U2_Waitq, smas->flag_u2);
		break;

	case MA_IOC_WAKE_U2:
		smas->flag_u2 = 1;
		wake_up_interruptible(&U2_Waitq);
		break;

	case MA_IOC_SET_REG:
		mutex_lock(&ioctl_lock);
		rc = copy_from_user(&ma_drv_reg, argp, sizeof(ma_drv_reg));
		mutex_unlock(&ioctl_lock);
		break;

	case MA_IOC_SET_REG_WAKE_U1:
		mutex_lock(&ioctl_lock);
		rc = copy_from_user(&ma_drv_reg, argp, sizeof(ma_drv_reg));
		mutex_unlock(&ioctl_lock);
		msleep(4);
		smas->flag_u1 = 1;
		wake_up_interruptible(&U1_Waitq);
		break;

	case MA_IOC_SET_SPEED:
		rc = copy_from_user(&ma_speed, argp, sizeof(ma_speed));
		if (rc)
			break;
		ma_spi_change(smas->spi, ma_speed, 0);
		break;

	case MA_IOC_GET_REG:
		mutex_lock(&ioctl_lock);
		rc = copy_to_user(argp, &ma_drv_reg, sizeof(ma_drv_reg));
		mutex_unlock(&ioctl_lock);
		break;

	case MA_IOC_GET_VERSION:
		mutex_lock(&ioctl_lock);
		rc = copy_to_user(argp, &MA_DRV_VERSION, sizeof(MA_DRV_VERSION));
		mutex_unlock(&ioctl_lock);
		break;

	case MA_IOC_WAIT_U1_GET_REG:
		smas->flag_u1 = 0;
		wait_event_interruptible(U1_Waitq, smas->flag_u1);
		mutex_lock(&ioctl_lock);
		rc = copy_to_user(argp, &ma_drv_reg, sizeof(ma_drv_reg));
		mutex_unlock(&ioctl_lock);
		break;

	case MA_IOC_GET_SCREEN_STATE:
		mutex_lock(&ioctl_lock);
		rc = copy_to_user(argp, &is_screen_on, sizeof(is_screen_on));
		mutex_unlock(&ioctl_lock);
		break;

	default:
		ma_warn(__func__, "mas_ioctl no such cmd", ret);
		rc = -EINVAL;
		break;
	}

	return rc;
}

static long mas_compat_ioctl(struct file *filp, unsigned int cmd,
			     unsigned long arg)
{
	return filp->f_op->unlocked_ioctl(filp, cmd, arg);
}

static const struct file_operations sfops = {
	.owner		= THIS_MODULE,
	.read		= mas_read,
	.write		= mas_write,
	.unlocked_ioctl	= mas_ioctl,
	.compat_ioctl	= mas_compat_ioctl,
	.mmap		= mas_mmap,
};

/* ------------------------------------------------------------------ */
/* sysfs                                                              */
/* ------------------------------------------------------------------ */

static ssize_t chip_id_show(struct device *dev, struct device_attribute *attr,
			    char *buf)
{
	ma_debug(__func__, "start");
	return snprintf(buf, PAGE_SIZE, "chip_id:0x%04x\n", chip_id);
}

static DEVICE_ATTR_RO(chip_id);

static struct attribute *madev_attrs[] = {
	&dev_attr_chip_id.attr,
	NULL,
};

static const struct attribute_group madev_attrs_group = {
	.attrs = madev_attrs,
};

/* ------------------------------------------------------------------ */
/* Driver registration data                                           */
/* ------------------------------------------------------------------ */

struct spi_device_id sdev_id[] = {
	{ MA_DEV_NAME, 0 },
	{ }
};

static const struct of_device_id madev_dt_ids[] = {
	{ .compatible = MA_COMPATIBLE },
	{ }
};
MODULE_DEVICE_TABLE(of, madev_dt_ids);

struct spi_driver sdrv = {
	.id_table	= sdev_id,
	.probe		= mas_probe,
	.remove		= mas_remove,
	.driver = {
		.name		= MA_DEV_NAME,
		.bus		= &spi_bus_type,
		.owner		= THIS_MODULE,
		.of_match_table	= madev_dt_ids,
	},
};

/* ------------------------------------------------------------------ */
/* Probe / remove                                                     */
/* ------------------------------------------------------------------ */

int mas_probe(struct spi_device *spi)
{
	ma_debug(__func__, "start");

	spi->mode = 0;

	yft_waite_for_finger_dts_paser();

	ret = mas_finger_set_gpio_info(&spi->dev, 1);
	if (ret)
		ma_err(__func__, "mas_plat_probe do mas_finger_set_gpio_info",
		       ret);

	/* init_vars */
	sdev = kmalloc(sizeof(*sdev), GFP_KERNEL);
	smas = kmalloc(sizeof(*smas), GFP_KERNEL);
	srxb = kmalloc(MA_XFER_MAX, GFP_KERNEL);
	stxb = kmalloc(MA_XFER_MAX, GFP_KERNEL);
	if (!sdev || !smas || !srxb || !stxb) {
		ma_warn("init_vars", "smas kmalloc failed.", ret);
		kfree(sdev);
		kfree(smas);
		kfree(stxb);
		kfree(srxb);
		ret = -ENOMEM;
		goto err_free;
	}

	gProcessWakeLock = wakeup_source_register(NULL, MA_WAKELOCK_NAME);
	INIT_WORK(&gWork, mas_work);

	gWorkq = create_singlethread_workqueue(MA_WQ_NAME);
	if (!gWorkq) {
		ma_warn("init_vars", "create_single_workqueue error!", ret);
		ret = -ENOMEM;
		goto err_free;
	}

	/* init_interrupt */
	ret = 0;
	irq = mas_get_irq();
	if (!irq) {
		ma_err("init_interrupt", "mas_get_irq", 0);
		ret = 0;
	}

	ret = request_threaded_irq(irq, mas_interrupt, NULL,
				   IRQF_TRIGGER_RISING, MA_IRQ_NAME, NULL);
	if (ret) {
		ma_err("init_interrupt", "request_irq", ret);
		goto err_irq;
	}
	irq_set_irq_wake(irq, 1);
	if (ret)
		goto err_irq;

	smas->spi = spi;
	spi->max_speed_hz = MA_SPI_SPEED_HZ;
	spi_setup(spi);
	INIT_LIST_HEAD(&smas->list);

	ret = 0;
	init_connect();

	/* init_file_node */
	ret = 1;
	ret = alloc_chrdev_region(&sdev->devno, 0, 1, MA_DEV_NAME);
	if (ret < 0) {
		ma_warn("init_file_node", "alloc_chrdev_region error!", ret);
		goto err_node;
	}

	sdev->cdev = cdev_alloc();
	if (!sdev->cdev) {
		ma_warn("init_file_node", "cdev_alloc error!", ret);
		goto err_node;
	}
	sdev->cdev->owner = THIS_MODULE;
	sdev->cdev->ops = &sfops;
	cdev_add(sdev->cdev, sdev->devno, 1);

	sdev->cls = class_create(THIS_MODULE, MA_DEV_NAME);
	if (IS_ERR(sdev->cls)) {
		ma_err("init_file_node", "class_create", ret);
		goto err_node;
	}

	sdev->dev = device_create(sdev->cls, NULL, sdev->devno, NULL,
				  MA_NODE_NAME);
	if (IS_ERR(sdev->dev) || !sdev->dev)
		ma_err("init_file_node", "device_create", (int)(long)sdev->dev);

	ret = 0;
	ret = sysfs_create_group(&spi->dev.kobj, &madev_attrs_group);

	mas_set_input();

	ma_debug(__func__, "end");
	ret = 0;
	is_screen_on = 1;
	return 0;

err_node:
	ret = -1;
	cdev_del(sdev->cdev);
	smas->spi = NULL;
err_irq:
	disable_irq(irq);
	free_irq(irq, NULL);
err_free:
	destroy_workqueue(gWorkq);
	if (compatible)
		return -ret;
	return -ENODEV;
}

void mas_remove(struct spi_device *spi)
{
	cdev_del(sdev->cdev);
	disable_irq(irq);
	free_irq(irq, NULL);
	destroy_workqueue(gWorkq);
}

/* ------------------------------------------------------------------ */
/* Module init / exit                                                 */
/* ------------------------------------------------------------------ */

int __init mas_get_platform(void)
{
	ret = spi_register_driver(&sdrv);
	if (ret)
		ma_err(__func__, "spi_register_driver", ret);
	return ret;
}

static int __init mas_init(void)
{
	int status;

	ma_debug("mas_init", "start");

	compatible = true;

	status = mas_get_platform();
	if (status)
		ma_err("mas_init", "mas_get_platform", status);

	return status;
}

static void __exit mas_exit(void)
{
}

module_init(mas_init);
module_exit(mas_exit);

MODULE_AUTHOR("Microarray");
MODULE_DESCRIPTION("Driver for microarray fingerprint sensor");
MODULE_LICENSE("GPL");
