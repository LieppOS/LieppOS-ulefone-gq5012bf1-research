// SPDX-License-Identifier: GPL-2.0
/*
 * TrustKernel TKCore lifecycle prerequisites reconstructed from the stripped
 * GQ5012BF1 stock tkcore.ko.  Scope is deliberately limited to proc/log
 * registration and platform clock registration/teardown.
 */
#include <linux/clk.h>
#include <linux/err.h>
#include <linux/fs.h>
#include <linux/interrupt.h>
#include <linux/kernel.h>
#include <linux/kthread.h>
#include <linux/list.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/of.h>
#include <linux/proc_fs.h>
#include <linux/slab.h>
#include <linux/uaccess.h>
#include <linux/wait.h>

#include <trustkernel/tee_clkmgr.h>
#include <trustkernel/tee_core.h>

#include "tee_lifecycle_prereq.h"

#define TKCORE_LOG_HEADER_SIZE	0x100
#define TKCORE_LOG_WAIT_TICKS	125
#define TKCORE_LOG_LINE_SIZE	128
#define TKCORE_MAX_SPI_CLOCKS	20

struct tkcore_log_header {
	u32 magic;
	u32 size;
	u8 reserved0[0x10];
	u32 readers;
	u32 write_pos;
	u32 logd_pos;
	u8 reserved1[0xdc];
};

struct tkcore_log_state {
	struct tkcore_log_header *header;
	char *data;
	u32 size;
	u8 wrapped;
	u8 padding[3];
	wait_queue_head_t wq;
	struct task_struct *task;
	u64 reserved;
};

struct tkcore_log_reader {
	u32 pos;
	u32 padding;
	const char *pending;
	struct tkcore_log_state *log;
};

static_assert(sizeof(struct tkcore_log_header) == TKCORE_LOG_HEADER_SIZE);
static_assert(offsetof(struct tkcore_log_header, readers) == 0x18);
static_assert(offsetof(struct tkcore_log_header, write_pos) == 0x1c);
static_assert(offsetof(struct tkcore_log_header, logd_pos) == 0x20);
static_assert(sizeof(struct tkcore_log_state) == 0x40);
static_assert(offsetof(struct tkcore_log_state, wq) == 0x18);
static_assert(offsetof(struct tkcore_log_state, task) == 0x30);
static_assert(sizeof(struct tkcore_log_reader) == 0x18);

struct proc_dir_entry *tee_proc_dir;
struct proc_dir_entry *tee_proc_log_file;
struct proc_dir_entry *tee_proc_drv_version;
struct proc_dir_entry *tee_proc_tee_version;
struct proc_dir_entry *tee_proc_teed_version;
char teed_version[51] = "unknown\n";

static struct tkcore_log_state klog;
static int klog_irq;

static const char log_beginning[] = "------ beginning of tee\n";
static const char log_interrupted[] = "------ interrupted\n";
static const char logd_interrupted[] = "---- interrupted";
static const char drv_version[] = "6:1.1-k6.6";

static noinline ssize_t copy_to_user_str(char __user *buffer, size_t count,
					loff_t *ppos, const char *string)
{
	size_t length = strlen(string) + 1;
	size_t amount;
	size_t not_copied;

	if (*ppos > length) {
		pr_warn("tkcore: invalid pos: %lld len: %zu\n", *ppos,
			length - 1);
		return -EINVAL;
	}

	amount = min_t(size_t, count, length - *ppos);
	not_copied = copy_to_user(buffer, string + *ppos, amount);
	amount -= not_copied;
	*ppos += amount;
	return amount;
}

static ssize_t drv_version_read(struct file *file, char __user *buffer,
				size_t count, loff_t *ppos)
{
	if (!buffer || !ppos)
		return -EINVAL;
	return copy_to_user_str(buffer, count, ppos, drv_version);
}

static ssize_t tee_version_read(struct file *file, char __user *buffer,
				size_t count, loff_t *ppos)
{
	struct tee *tee;
	char version[32] = { 0 };

	if (!buffer || !ppos)
		return -EINVAL;

	tee = pde_data(file_inode(file));
	snprintf(version, sizeof(version), "%u.%u.%u-gp\n",
		 tee->version_major, tee->version_minor, tee->version_patch);
	return copy_to_user_str(buffer, count, ppos, version);
}

static ssize_t teed_version_read(struct file *file, char __user *buffer,
				 size_t count, loff_t *ppos)
{
	if (!buffer || !ppos)
		return -EINVAL;
	return copy_to_user_str(buffer, count, ppos, teed_version);
}

static ssize_t teed_version_write(struct file *file,
				  const char __user *buffer,
				  size_t count, loff_t *ppos)
{
	size_t not_copied;

	if (count > 50)
		return -ENOMEM;

	not_copied = copy_from_user(teed_version, buffer, count);
	if (not_copied)
		memset(teed_version + count - not_copied, 0, not_copied);

	/*
	 * Stock terminates at index count + 1, which is an out-of-bounds
	 * store for count == 50 and is guarded there by a fortify trap.
	 * DOCUMENTED DIVERGENCE: the island clamps to the last in-bounds
	 * index instead of reproducing an out-of-bounds write.
	 */
	teed_version[min_t(size_t, count + 1, sizeof(teed_version) - 1)] = '\0';
	return count;
}

int tee_log_open(struct inode *inode, struct file *file)
{
	struct tkcore_log_reader *reader;
	int ret;

	reader = kzalloc(sizeof(*reader), GFP_KERNEL);
	if (!reader)
		return -ENOMEM;
	if (!klog.header)
		return -EIO;

	reader->pending = log_beginning;
	reader->log = &klog;
	ret = nonseekable_open(inode, file);
	if (ret) {
		kfree(reader);
		pr_warn("tkcore: open file failed with %d\n", ret);
		return ret;
	}
	file->private_data = reader;
	return 0;
}

int tee_log_release(struct inode *inode, struct file *file)
{
	kfree(file->private_data);
	return 0;
}

static ssize_t tee_log_read(struct file *file, char __user *buffer,
			    size_t count, loff_t *ppos)
{
	struct tkcore_log_reader *reader;
	struct tkcore_log_state *log;
	struct tkcore_log_header *header;
	size_t total = 0;
	long wait_ret;

	if (!file || !buffer || !ppos)
		return -EINVAL;
	reader = file->private_data;
	if (!reader) {
		pr_warn("tkcore: file not open correctly\n");
		return -EINVAL;
	}
	if (file->f_flags & O_NONBLOCK)
		return -EAGAIN;

	log = reader->log;
	header = log->header;
	while (!reader->pending && reader->pos == READ_ONCE(header->write_pos)) {
		wait_ret = wait_event_interruptible_timeout(log->wq,
			reader->pos != READ_ONCE(header->write_pos),
			TKCORE_LOG_WAIT_TICKS);
		if (wait_ret < 0)
			return -EINTR;
	}

	while (total < count) {
		u32 write_pos = READ_ONCE(header->write_pos);
		u32 available;
		size_t amount;
		size_t not_copied;
		size_t copied;

		if (reader->pending) {
			if (*reader->pending) {
				amount = min_t(size_t, strlen(reader->pending),
					       count - total);
				not_copied = copy_to_user(buffer + total,
							  reader->pending, amount);
				copied = amount - not_copied;
				reader->pending += copied;
				total += copied;
				if (!copied) {
					pr_warn("tkcore: failed to copy flag to user\n");
					break;
				}
				continue;
			}

			reader->pending = NULL;
			if (write_pos < log->size && !log->wrapped)
				reader->pos = 0;
			else
				reader->pos = write_pos - log->size;
		}

		available = write_pos - reader->pos;
		if (!available)
			break;
		if (available > log->size) {
			reader->pending = log_interrupted;
			continue;
		}

		amount = min_t(size_t, available, count - total);
		amount = min_t(size_t, amount,
			       log->size - (reader->pos % log->size));
		not_copied = copy_to_user(buffer + total,
					  log->data + (reader->pos % log->size),
					  amount);
		copied = amount - not_copied;
		if (!copied) {
			pr_warn("tkcore: failed to copy klog to user\n");
			break;
		}
		reader->pos += copied;
		total += copied;
	}

	*ppos += total;
	return total;
}

static int logd(void *data)
{
	struct tkcore_log_state *log = data;
	struct tkcore_log_header *header = log->header;

	header->readers++;
	while (!kthread_should_stop()) {
		const char *line;
		char buf[TKCORE_LOG_LINE_SIZE] = { 0 };
		u32 write_pos;
		u32 pos;
		size_t len;

		if (READ_ONCE(header->logd_pos) ==
		    READ_ONCE(header->write_pos)) {
			long ret;

			ret = wait_event_interruptible_timeout(log->wq,
				READ_ONCE(header->logd_pos) !=
				READ_ONCE(header->write_pos),
				TKCORE_LOG_WAIT_TICKS);
			if (ret < 1)
				continue;
		}

		pos = READ_ONCE(header->logd_pos);
		write_pos = READ_ONCE(header->write_pos);
		len = 0;
		line = buf;

		while (pos != write_pos) {
			char ch;

			if (write_pos - pos > log->size) {
				line = logd_interrupted;
				pos = write_pos - log->size;
				break;
			}
			ch = log->data[pos % log->size];
			pos++;
			if (!ch || ch == '\n')
				break;
			if (len >= TKCORE_LOG_LINE_SIZE - 2)
				break;
			buf[len++] = ch;
		}
		buf[len] = '\0';
		pr_info("tkcore: %s\n", line);
		WRITE_ONCE(header->logd_pos, pos);
		if (write_pos >= log->size)
			log->wrapped = 1;
	}
	header->readers--;
	return 0;
}

static irqreturn_t tkcore_log_irq_handler(int irq, void *data)
{
	wake_up(&klog.wq);
	return IRQ_HANDLED;
}

static const struct proc_ops tee_log_ops = {
	.proc_open = tee_log_open,
	.proc_read = tee_log_read,
	.proc_release = tee_log_release,
};

static const struct proc_ops drv_version_ops = {
	.proc_read = drv_version_read,
};

static const struct proc_ops tee_version_ops = {
	.proc_read = tee_version_read,
};

static const struct proc_ops teed_version_ops = {
	.proc_read = teed_version_read,
	.proc_write = teed_version_write,
};

static void remove_proc_surface(void)
{
	proc_remove(tee_proc_dir);
	tee_proc_dir = NULL;
	tee_proc_log_file = NULL;
	tee_proc_drv_version = NULL;
	tee_proc_tee_version = NULL;
	tee_proc_teed_version = NULL;
}

int tee_init_procfs(struct tee *tee)
{
	struct tkcore_log_header *header;
	int ret;

	BUG_ON(!tee || !tee->priv);

	tee_proc_dir = proc_mkdir("tkcore", NULL);
	if (!tee_proc_dir) {
		pr_err("tkcore: proc_mkdir tkcore failed\n");
		return -1;
	}
	tee_proc_log_file = proc_create_data("tkcore_log", 0444,
		tee_proc_dir, &tee_log_ops, tee);
	if (!tee_proc_log_file) {
		pr_err("tkcore: proc_create failed\n");
		goto err_proc;
	}
	tee_proc_drv_version = proc_create_data("tkcore_drv_version", 0444,
		tee_proc_dir, &drv_version_ops, tee);
	if (!tee_proc_drv_version) {
		pr_err("tkcore: proc_create tkcore_drv_version failed\n");
		goto err_proc;
	}
	tee_proc_tee_version = proc_create_data("tkcore_os_version", 0444,
		tee_proc_dir, &tee_version_ops, tee);
	if (!tee_proc_tee_version) {
		pr_err("tkcore: proc_create tkcore_os_version failed\n");
		goto err_proc;
	}
	tee_proc_teed_version = proc_create_data("tkcore_teed_version", 0666,
		tee_proc_dir, &teed_version_ops, tee);
	if (!tee_proc_teed_version) {
		pr_err("tkcore: proc_create tkcore_teed_version failed\n");
		goto err_proc;
	}

	memset(&klog, 0, sizeof(klog));
	if (!tee->log_shm || !tee->log_shm_len)
		return 0;
	if (tee->log_shm_len <= TKCORE_LOG_HEADER_SIZE) {
		pr_err("tkcore: init_klog_shm: shm_len %zu too small\n",
		       tee->log_shm_len);
		goto err_remove;
	}

	header = tee->log_shm;
	if (tee->log_shm_len - TKCORE_LOG_HEADER_SIZE != header->size) {
		pr_err("tkcore: Unexpected shm length: %u\n", header->size);
		goto err_remove;
	}
	klog.header = header;
	klog.data = (char *)header + TKCORE_LOG_HEADER_SIZE;
	klog.size = header->size;
	klog.wrapped = 0;
	header->readers = 0;
	init_waitqueue_head(&klog.wq);

	if (!tee->log_irq) {
		pr_warn("tkcore: unknown tee log irq\n");
	} else {
		pr_info("tkcore: tee log irq = %d\n", tee->log_irq);
		ret = request_threaded_irq(tee->log_irq,
			tkcore_log_irq_handler, NULL, IRQF_TRIGGER_RISING,
			"tee_log_irq", NULL);
		if (ret) {
			pr_err("tkcore: failed to register klog_irq with %d\n",
			       ret);
			goto err_log;
		}
		klog_irq = tee->log_irq;
	}

	klog.task = kthread_create(logd, &klog, "tee-log");
	if (IS_ERR_OR_NULL(klog.task)) {
		pr_err("tkcore: Failed to create kthread\n");
		klog.task = NULL;
		goto err_log;
	}
	wake_up_process(klog.task);
	return 0;

err_log:
	if (klog_irq > 0) {
		free_irq(klog_irq, NULL);
		klog_irq = 0;
	}
	memset(&klog, 0, sizeof(klog));
err_remove:
err_proc:
	remove_proc_surface();
	return -1;
}

void tee_exit_procfs(void)
{
	remove_proc_surface();
	if (klog_irq > 0) {
		free_irq(klog_irq, NULL);
		klog_irq = 0;
	}
	if (klog.task) {
		kthread_stop(klog.task);
		klog.task = NULL;
	}
	wake_up(&klog.wq);
}

struct tee_clkmgr_record {
	u32 token;
	u32 padding;
	void *enable;
	void *disable;
	void *arg0;
	void *arg1;
	void *arg2;
	size_t argnum;
	struct list_head entry;
};

static_assert(sizeof(struct tee_clkmgr_record) == 0x48);
static_assert(offsetof(struct tee_clkmgr_record, enable) == 0x08);
static_assert(offsetof(struct tee_clkmgr_record, disable) == 0x10);
static_assert(offsetof(struct tee_clkmgr_record, arg0) == 0x18);
static_assert(offsetof(struct tee_clkmgr_record, argnum) == 0x30);
static_assert(offsetof(struct tee_clkmgr_record, entry) == 0x38);

static DEFINE_MUTEX(tee_clkmgr_lock);
static LIST_HEAD(tee_clkmgr_records);

int tee_clkmgr_register(const char *name, int index,
			void *enable, void *disable,
			void *arg0, void *arg1, void *arg2,
			size_t argnum)
{
	struct tee_clkmgr_record *record;
	struct tee_clkmgr_record *found;
	u32 class;
	u32 shifted;
	u32 token;

	pr_info("tkcore: clkname=%s id=%d\n", name, index);
	if (argnum > 3) {
		pr_err("tkcore: does not support argnum %zu\n", argnum);
		return -EINVAL;
	}
	if (!strcmp(name, "spi"))
		class = 0;
	else if (!strcmp(name, "i2c"))
		class = 0x10000;
	else if (!strcmp(name, "i2c-dma"))
		class = 0x20000;
	else {
		pr_err("tkcore: invalid clkname %s\n", name);
		return -EINVAL;
	}

	shifted = (u32)index << 1;
	if (shifted >= 0x10000) {
		pr_err("tkcore: %s-%d: invalid id\n", name, index);
		return -EINVAL;
	}
	token = class | shifted | 1;

	record = kzalloc(sizeof(*record), GFP_KERNEL);
	if (!record)
		return -ENOMEM;
	record->token = token;
	record->enable = enable;
	record->disable = disable;
	record->arg0 = arg0;
	record->arg1 = arg1;
	record->arg2 = arg2;
	record->argnum = argnum;

	mutex_lock(&tee_clkmgr_lock);
	list_for_each_entry(found, &tee_clkmgr_records, entry) {
		if (found->token != token)
			continue;
		found->enable = enable;
		found->disable = disable;
		found->arg0 = arg0;
		found->arg1 = arg1;
		found->arg2 = arg2;
		found->argnum = argnum;
		mutex_unlock(&tee_clkmgr_lock);
		kfree(record);
		return 0;
	}
	list_add(&record->entry, &tee_clkmgr_records);
	mutex_unlock(&tee_clkmgr_lock);
	return 0;
}
EXPORT_SYMBOL(tee_clkmgr_register);

static void mtk_enable_clk(void *data)
{
	struct clk *clk = data;
	int ret;

	ret = clk_prepare(clk);
	if (ret)
		return;
	ret = clk_enable(clk);
	if (ret)
		clk_unprepare(clk);
}

static void mtk_disable_clk(void *data)
{
	struct clk *clk = data;

	clk_disable(clk);
	clk_unprepare(clk);
}

int plat_register_spi_clk(void)
{
	char node_name[10] = { 0 };
	int index;

	pr_info("tkcore: register platform spi clk\n");
	for (index = 0; index < TKCORE_MAX_SPI_CLOCKS; index++) {
		struct device_node *node;
		struct clk *clk;

		sprintf(node_name, "spi%d", index);
		node = of_find_node_by_name(NULL, node_name);
		if (!node)
			break;
		clk = of_clk_get_by_name(node, "spi-clk");
		if (IS_ERR_OR_NULL(clk)) {
			pr_warn("tkcore: of_clk_get_by_name: failed with %ld\n",
				PTR_ERR(clk));
			continue;
		}
		tee_clkmgr_register("spi", index, mtk_enable_clk,
			mtk_disable_clk, clk, NULL, NULL, 1);
	}
	return 0;
}

int tee_peridev_init(void)
{
	return plat_register_spi_clk();
}

void tee_peridev_exit(void)
{
	struct tee_clkmgr_record *record;
	struct tee_clkmgr_record *next;

	mutex_lock(&tee_clkmgr_lock);
	list_for_each_entry_safe(record, next, &tee_clkmgr_records, entry) {
		list_del(&record->entry);
		kfree(record);
	}
	mutex_unlock(&tee_clkmgr_lock);
}
