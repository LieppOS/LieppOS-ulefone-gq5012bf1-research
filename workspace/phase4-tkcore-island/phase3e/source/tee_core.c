/*
 * Copyright (c) 2014, STMicroelectronics International N.V.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License Version 2 as
 * published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 */
/* #define DEBUG */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/types.h>
#include <linux/slab.h>
#include <linux/cdev.h>
#include <linux/idr.h>
#include <linux/platform_device.h>
#include <linux/device.h>
#include <linux/compat.h>
#include <linux/fs.h>
#include <linux/file.h>
#include <linux/uaccess.h>
#include <asm-generic/ioctl.h>
#include <linux/sched.h>
#include <linux/cpumask.h>
#include <linux/arch_topology.h>

#include <trustkernel/tee_core.h>
#include "tee_ioc.h"

#include "tee_core_priv.h"

#include "tee_sysfs.h"
#include "tee_shm.h"
#include "tee_supp_com.h"
#include "tee_lifecycle_prereq.h"

#define _TEE_CORE_FW_VER "1:0.1"

/* Store the class misc reference */
static struct class *misc_class;

/*
 * Opaque handle table.
 *
 * Stock does NOT cast a kernel pointer into the 32-bit fd/handle field of
 * TEEC_Context / TEEC_Session (the donor did, and its own comment admitted
 * that breaks on 64-bit).  It keeps an IDR and hands out small positive ids.
 */
static DEFINE_IDR(tee_idr);
static DEFINE_SPINLOCK(tee_idr_lock);

int tee_core_alloc_uuid(void *ptr)
{
	int rv;

	idr_preload(GFP_KERNEL);
	spin_lock(&tee_idr_lock);
	rv = idr_alloc(&tee_idr, ptr, 1, 0, GFP_NOWAIT);
	if (rv < 0)
		pr_err("Bad alloc tee_uuid. rv: %d\n", rv);
	spin_unlock(&tee_idr_lock);
	idr_preload_end();

	return rv;
}

void *tee_core_uuid2ptr(int uuid)
{
	return idr_find(&tee_idr, uuid);
}

void tee_core_free_uuid(int uuid)
{
	idr_remove(&tee_idr, uuid);
}

/*
 * 32-bit userspace uses native-sized ABI records.  A compat pointer or
 * size_t occupies the low word of an eight-byte slot and the high word is
 * cleared in place before native command handling consumes the record.
 *
 * Keep these as put_user() operations rather than open-coding the arm64
 * access sequence: the stock converter is built from this exact-GKI uaccess
 * machinery, including its locally materialised TTBR0 helpers.
 */
#define tee_compat_clear_high(slot) \
	put_user(0, ((uint32_t __user *)&(slot)) + 1)

int convert_compat_tee_cmd(struct tee_cmd_io __user *u_cmd)
{
	TEEC_Operation __user *op;
	TEEC_SharedMemory __user *parent;
	uint32_t param_types;
	unsigned int n;

	if (!u_cmd)
		return -EINVAL;

	if (tee_compat_clear_high(u_cmd->padding_uuid) ||
	    tee_compat_clear_high(u_cmd->padding_data) ||
	    tee_compat_clear_high(u_cmd->padding_op))
		return -EFAULT;

	if (copy_from_user(&op, &u_cmd->padding_op, sizeof(op)))
		return -EFAULT;
	if (!op)
		return -EINVAL;

	if (get_user(param_types, &op->paramTypes) ||
	    tee_compat_clear_high(op->padding_ptr))
		return -EFAULT;

	for (n = 0; n < TEEC_CONFIG_PAYLOAD_REF_COUNT; n++) {
		switch (TEEC_PARAM_TYPE_GET(param_types, n)) {
		case TEEC_NONE:
		case TEEC_VALUE_INPUT:
		case TEEC_VALUE_OUTPUT:
		case TEEC_VALUE_INOUT:
			break;
		case TEEC_MEMREF_TEMP_INPUT:
		case TEEC_MEMREF_TEMP_OUTPUT:
		case TEEC_MEMREF_TEMP_INOUT:
			if (tee_compat_clear_high(
					op->params[n].tmpref.padding_ptr) ||
			    tee_compat_clear_high(
					op->params[n].tmpref.padding_sz))
				return -EFAULT;
			break;
		case TEEC_MEMREF_WHOLE:
		case TEEC_MEMREF_PARTIAL_INPUT:
		case TEEC_MEMREF_PARTIAL_OUTPUT:
		case TEEC_MEMREF_PARTIAL_INOUT:
			if (tee_compat_clear_high(
					op->params[n].memref.padding_ptr) ||
			    tee_compat_clear_high(
					op->params[n].memref.padding_sz) ||
			    tee_compat_clear_high(
					op->params[n].memref.padding_off))
				return -EFAULT;

			if (copy_from_user(&parent,
					   &op->params[n].memref.padding_ptr,
					   sizeof(parent)))
				return -EFAULT;
			if (!parent)
				break;

			if (tee_compat_clear_high(parent->padding_ptr) ||
			    tee_compat_clear_high(parent->padding_sz) ||
			    tee_compat_clear_high(parent->d.padding_d))
				return -EFAULT;
			break;
		default:
			pr_err("bad param %u\n", n);
			return -EFAULT;
		}
	}

	return 0;
}

int convert_compat_tee_shm_io(struct tee_shm_io __user *u_shm)
{
	if (!u_shm)
		return -EINVAL;
	if (tee_compat_clear_high(u_shm->padding_buf))
		return -EFAULT;
	return 0;
}

int convert_compat_tee_spta_inst(struct tee_spta_inst_desc __user *u_inst)
{
	if (!u_inst)
		return -EINVAL;
	if (tee_compat_clear_high(u_inst->padding_ptr0) ||
	    tee_compat_clear_high(u_inst->padding_ptr16))
		return -EFAULT;
	return 0;
}

/* Compiler-enforced native-sized compat overlay graph recovered from stock. */
static_assert(sizeof(struct tee_cmd_io) == 0x30);
static_assert(offsetof(struct tee_cmd_io, uuid) == 0x10);
static_assert(offsetof(struct tee_cmd_io, data) == 0x18);
static_assert(offsetof(struct tee_cmd_io, op) == 0x20);
static_assert(offsetof(struct tee_cmd_io, data_size) == 0x28);
static_assert(sizeof(struct tee_shm_io) == 0x18);
static_assert(offsetof(struct tee_shm_io, buffer) == 0x00);
static_assert(offsetof(struct tee_shm_io, size) == 0x08);
static_assert(offsetof(struct tee_shm_io, flags) == 0x0c);
static_assert(offsetof(struct tee_shm_io, fd_shm) == 0x10);
static_assert(offsetof(struct tee_shm_io, registered) == 0x14);
static_assert(sizeof(struct tee_spta_inst_desc) == 0x18);
static_assert(offsetof(struct tee_spta_inst_desc, ptr0) == 0x00);
static_assert(offsetof(struct tee_spta_inst_desc, opaque8) == 0x08);
static_assert(offsetof(struct tee_spta_inst_desc, ptr16) == 0x10);
static_assert(sizeof(TEEC_TempMemoryReference) == 0x10);
static_assert(offsetof(TEEC_TempMemoryReference, size) == 0x08);
static_assert(sizeof(TEEC_RegisteredMemoryReference) == 0x18);
static_assert(offsetof(TEEC_RegisteredMemoryReference, size) == 0x08);
static_assert(offsetof(TEEC_RegisteredMemoryReference, offset) == 0x10);
static_assert(sizeof(TEEC_Parameter) == 0x18);
static_assert(sizeof(TEEC_Operation) == 0x118);
static_assert(offsetof(TEEC_Operation, paramTypes) == 0x04);
static_assert(offsetof(TEEC_Operation, params) == 0x08);
static_assert(offsetof(TEEC_Operation, session) == 0x68);
static_assert(offsetof(TEEC_Operation, memRefs) == 0x70);
static_assert(offsetof(TEEC_Operation, flags) == 0x110);
static_assert(sizeof(TEEC_SharedMemory) == 0x28);
static_assert(offsetof(TEEC_SharedMemory, buffer) == 0x00);
static_assert(offsetof(TEEC_SharedMemory, size) == 0x08);
static_assert(offsetof(TEEC_SharedMemory, flags) == 0x10);
static_assert(offsetof(TEEC_SharedMemory, d) == 0x18);
static_assert(offsetof(TEEC_SharedMemory, registered) == 0x20);

/*
 * For the kernel api.
 * Get a reference on a device tee from the device node name.
 *
 * Stock matches against the MISC DEVICE name (tkcore_admin / tkcore_client /
 * tkcore_fp), not against tee->name, and only descriptors flagged for name
 * lookup may be resolved this way - which is why TEEC_InitializeContext()
 * defaults to "tkcore_client".
 */
struct tee *tee_get_tee(const char *devname)
{
	struct device *device;
	struct tee_misc_dev *tmd;

	if (!devname)
		return NULL;

	device = class_find_device(misc_class, NULL, devname,
				   device_match_name);
	if (!device) {
		pr_err("can't find device [%s]\n", devname);
		return NULL;
	}

	tmd = dev_get_drvdata(device);
	if (!tmd->desc->name_lookup)
		return NULL;

	return dev_get_drvdata(device->parent);
}

void tee_inc_stats(struct tee_stats_entry *entry)
{
	entry->count++;
	if (entry->count > entry->max)
		entry->max = entry->count;
}

void tee_dec_stats(struct tee_stats_entry *entry)
{
	entry->count--;
}

/**
 * tee_get - increases refcount of the tee
 * @tee:	[in]	tee to increase refcount of
 *
 * @note: If tee.ops.start() callback function is available,
 * it is called when refcount is equal at 1.
 */
int tee_get(struct tee *tee)
{
	int count;

	if (!tee) {
		BUG();
		return -EINVAL;
	}

	count = atomic_inc_return(&tee->refcount);

	/*
	 * Reaching 1 here means the provider reference was never taken with
	 * __tee_get(); stock treats that as a hard programming error rather
	 * than silently starting the backend from a client path.
	 */
	BUG_ON(count == 1);

	if (count > tee->max_refcount)
		tee->max_refcount = count;

	return 0;
}

/**
 * __tee_get - take the provider reference and start the backend
 *
 * EXPORTED.  This is the entry the provider (tkcore_drv) uses once, right
 * after tee_core_add().  It is the only path that may take the 0 -> 1
 * transition.
 */
int __tee_get(struct tee *tee)
{
	int ret;

	if (!tee) {
		BUG();
		return -EINVAL;
	}

	if (atomic_inc_return(&tee->refcount) != 1) {
		/*
		 * Stock deliberately does NOT undo the increment on this
		 * misuse path.  Reproduced as-is.
		 */
		dev_warn(tee->dev, "tee->refcount is not 1\n");
		return -1;
	}

	BUG_ON(!try_module_get(tee->ops->owner));
	get_device(tee->dev);

	if (!tee->ops->start)
		return 0;

	ret = tee->ops->start(tee);
	if (ret) {
		pr_err("%s::start() failed, err=%d\n", tee->name, ret);
		put_device(tee->dev);
		module_put(tee->ops->owner);
		atomic_dec(&tee->refcount);
		return ret;
	}

	return 0;
}
EXPORT_SYMBOL(__tee_get);

/**
 * tee_put - decreases refcount of the tee
 * @tee:	[in]	tee to reduce refcount of
 */
int tee_put(struct tee *tee)
{
	if (!tee) {
		BUG();
		return -EINVAL;
	}

	/*
	 * Reaching 0 here would drop the provider reference from a client
	 * path; stock BUGs instead of calling the backend stop hook.
	 */
	BUG_ON(atomic_dec_return(&tee->refcount) == 0);

	return 0;
}

/*
 * Resolve the misc record installed by tee_core_add() and the owning TEE.
 *
 * misc_open() puts the struct miscdevice into file->private_data, and the
 * record embeds it at offset 0, so the record IS that pointer.  The owner is
 * reached through the parent device's driver data, exactly as stock does.
 */
static struct tee_context *tee_node_open(struct inode *inode,
					 struct file *filp,
					 struct tee_misc_dev **record)
{
	struct tee_misc_dev *tmd = filp->private_data;
	struct tee_context *ctx;
	struct tee *tee;

	BUG_ON(tmd->miscdev.minor != iminor(inode));

	tee = dev_get_drvdata(tmd->miscdev.parent);
	BUG_ON(!tee);

	ctx = tee_context_create(tee);
	if (IS_ERR_OR_NULL(ctx))
		return NULL;

	ctx->usr_client = 1;
	ctx->ctx_priv = (void *)tmd->desc;
	*record = tmd;

	return ctx;
}

static int tee_ctx_open(struct inode *inode, struct file *filp)
{
	struct tee_misc_dev *tmd;
	struct tee_context *ctx;

	ctx = tee_node_open(inode, filp, &tmd);
	if (!ctx)
		return -1;

	filp->private_data = ctx;
	return 0;
}

static int tee_ctx_release(struct inode *inode, struct file *filp)
{
	struct tee_context *ctx = filp->private_data;

	if (!ctx) {
		BUG();
		return -EINVAL;
	}
	if (!ctx->tee) {
		BUG();
		return -EINVAL;
	}

	tee_context_destroy(ctx);
	return 0;
}

/*
 * /dev/tkcore_admin carries the supplicant.  Only one daemon may hold it at
 * a time; the counter lives in the RPC lifecycle object initialised by
 * tee_supp_init().
 */
static int tee_supp_open(struct inode *inode, struct file *filp)
{
	struct tee_misc_dev *tmd;
	struct tee_context *ctx;
	struct tee *tee;

	ctx = tee_node_open(inode, filp, &tmd);
	if (!ctx)
		return -1;

	tee = ctx->tee;
	BUG_ON(!tee->rpc);

	if (atomic_inc_return(&tee->rpc->used) >= 2) {
		pr_warn("Only one daemon is allowed\n");
		atomic_dec(&tee->rpc->used);
		tee_context_destroy(ctx);
		return -EBUSY;
	}

	filp->private_data = ctx;
	return 0;
}

static int tee_supp_release(struct inode *inode, struct file *filp)
{
	struct tee_context *ctx = filp->private_data;
	struct tee *tee;

	if (!ctx) {
		BUG();
		return -EINVAL;
	}

	tee = ctx->tee;
	if (!tee) {
		BUG();
		return -EINVAL;
	}

	tee_context_destroy(ctx);

	if (!tee->rpc) {
		BUG();
		return -1;
	}

	atomic_dec(&tee->rpc->used);
	return 0;
}

static int tee_do_create_session(struct tee_context *ctx,
				 struct tee_cmd_io __user *u_cmd)
{
	int ret = -EINVAL;
	struct tee_cmd_io k_cmd;
	struct tee *tee;

	tee = ctx->tee;
	BUG_ON(!ctx->usr_client);

	dev_dbg(_DEV(tee), "%s: >\n", __func__);

	if (copy_from_user(&k_cmd, (void *)u_cmd, sizeof(struct tee_cmd_io))) {
		dev_err(_DEV(tee), "%s: copy_from_user failed\n", __func__);
		goto exit;
	}

	if (k_cmd.fd_sess > 0) {
		dev_err(_DEV(tee), "%s: invalid fd_sess %d\n", __func__,
			k_cmd.fd_sess);
		goto exit;
	}

	if ((k_cmd.op == NULL) || (k_cmd.uuid == NULL) ||
	    ((k_cmd.data != NULL) && (k_cmd.data_size == 0)) ||
	    ((k_cmd.data == NULL) && (k_cmd.data_size != 0))) {
		dev_err(_DEV(tee),
			"%s: op or/and data parameters are not valid\n",
			__func__);
		goto exit;
	}

	ret = tee_session_create_fd(ctx, &k_cmd);
	put_user(k_cmd.err, &u_cmd->err);
	put_user(k_cmd.origin, &u_cmd->origin);
	if (ret)
		goto exit;

	put_user(k_cmd.fd_sess, &u_cmd->fd_sess);

exit:
	dev_dbg(_DEV(tee), "%s: < ret=%d, sessfd=%d\n", __func__, ret,
		k_cmd.fd_sess);
	return ret;
}

static int tee_do_shm_alloc(struct tee_context *ctx,
			    struct tee_shm_io __user *u_shm)
{
	int ret = -EINVAL;
	struct tee_shm_io k_shm;
	struct tee *tee = ctx->tee;

	BUG_ON(!ctx->usr_client);

	dev_dbg(_DEV(tee), "%s: >\n", __func__);

	if (copy_from_user(&k_shm, (void *)u_shm, sizeof(struct tee_shm_io))) {
		dev_err(_DEV(tee), "%s: copy_from_user failed\n", __func__);
		goto exit;
	}

	if ((k_shm.buffer != NULL) || (k_shm.fd_shm != 0) ||
	    /*(k_shm.flags & ~(tee->shm_flags)) ||*/
	    ((k_shm.flags & tee->shm_flags) == 0) || (k_shm.registered != 0)) {
		dev_err(_DEV(tee),
			"%s: shm parameters are not valid %p %d %08x %08x %d\n",
			__func__, (void *)k_shm.buffer, k_shm.fd_shm,
			(unsigned int)k_shm.flags, (unsigned int)tee->shm_flags,
			k_shm.registered);
		goto exit;
	}

	ret = tee_shm_alloc_io(ctx, &k_shm);
	if (ret)
		goto exit;

	put_user(k_shm.fd_shm, &u_shm->fd_shm);
	put_user(k_shm.flags, &u_shm->flags);

exit:
	dev_dbg(_DEV(tee), "%s: < ret=%d, shmfd=%d\n", __func__, ret,
		k_shm.fd_shm);
	return ret;
}

static int tee_do_get_fd_for_rpc_shm(struct tee_context *ctx,
				     struct tee_shm_io __user *u_shm)
{
	int ret = -EINVAL;
	struct tee_shm_io k_shm;
	struct tee *tee = ctx->tee;

	dev_dbg(_DEV(tee), "%s: >\n", __func__);
	BUG_ON(!ctx->usr_client);

	if (copy_from_user(&k_shm, (void *)u_shm, sizeof(struct tee_shm_io))) {
		dev_err(_DEV(tee), "%s: copy_from_user failed\n", __func__);
		goto exit;
	}

	if ((k_shm.buffer == NULL) || (k_shm.size == 0) || (k_shm.fd_shm != 0)
	    || (k_shm.flags & ~(tee->shm_flags))
	    || ((k_shm.flags & tee->shm_flags) == 0)
	    || (k_shm.registered != 0)) {
		dev_err(_DEV(tee), "%s: shm parameters are not valid\n",
			__func__);
		goto exit;
	}

	ret = tee_shm_fd_for_rpc(ctx, &k_shm);
	if (ret)
		goto exit;

	put_user(k_shm.fd_shm, &u_shm->fd_shm);

exit:
	dev_dbg(_DEV(tee), "%s: < ret=%d, shmfd=%d\n", __func__, ret,
		k_shm.fd_shm);
	return ret;
}

static uint32_t nsdrv_feature_flags;

static long tee_internal_ioctl(struct tee_context *ctx, unsigned int cmd,
			       unsigned long arg)
{
	int ret = -EINVAL;
	void __user *u_arg = (void __user *)arg;
	const struct tee_device_desc *desc;

	BUG_ON(!ctx);
	BUG_ON(!ctx->tee);

	switch (cmd) {
	case TEE_OPEN_SESSION_IOC:
		ret = tee_do_create_session(ctx,
				(struct tee_cmd_io __user *)u_arg);
		break;
	case TEE_ALLOC_SHM_IOC:
		ret = tee_do_shm_alloc(ctx, (struct tee_shm_io __user *)u_arg);
		break;
	case TEE_GET_FD_FOR_RPC_SHM_IOC:
		desc = ctx->ctx_priv;
		if (!desc || !desc->supplicant)
			break;
		ret = tee_do_get_fd_for_rpc_shm(ctx,
				 (struct tee_shm_io __user *)u_arg);
		break;
	case TEE_GET_NSDRV_FEATURE_FLAGS_IOC:
		if (!u_arg)
			break;
		ret = copy_to_user(u_arg, &nsdrv_feature_flags,
				   sizeof(nsdrv_feature_flags)) ? -EFAULT : 0;
		break;
	default:
		pr_err("internal_ioctl: Unknown command: %u\n", cmd);
		break;
	}

	return ret;
}

static long tee_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)
{
	struct tee_context *ctx = filp->private_data;

	BUG_ON(!ctx);
	BUG_ON(!ctx->tee);
	return tee_internal_ioctl(ctx, cmd, arg);
}

#ifdef CONFIG_COMPAT
static long tee_compat_ioctl(struct file *filp, unsigned int cmd,
			     unsigned long arg)
{
	struct tee_context *ctx = filp->private_data;
	void __user *u_arg = compat_ptr(arg);
	int ret = 0;

	BUG_ON(!ctx);
	BUG_ON(!ctx->tee);

	switch (cmd) {
	case TEE_ALLOC_SHM_IOC:
	case TEE_GET_FD_FOR_RPC_SHM_IOC:
		ret = convert_compat_tee_shm_io(
				(struct tee_shm_io __user *)u_arg);
		break;
	case TEE_OPEN_SESSION_IOC:
		ret = convert_compat_tee_cmd(
				(struct tee_cmd_io __user *)u_arg);
		break;
	case TEE_COMPAT_SPTA_CONVERSION_IOC:
		ret = convert_compat_tee_spta_inst(
				(struct tee_spta_inst_desc __user *)u_arg);
		break;
	default:
		break;
	}

	if (ret)
		return -EFAULT;
	return tee_internal_ioctl(ctx, cmd, (unsigned long)u_arg);
}
#endif

/*
 * Two distinct misc-node file_operations, plus stock's dedicated compat
 * callback.  Every field not listed here remains NULL exactly as stock.
 */
const struct file_operations tee_client_fops = {
	.owner = THIS_MODULE,
	.unlocked_ioctl = tee_ioctl,
#ifdef CONFIG_COMPAT
	.compat_ioctl = tee_compat_ioctl,
#endif
	.open = tee_ctx_open,
	.release = tee_ctx_release,
};

const struct file_operations tee_admin_fops = {
	.owner = THIS_MODULE,
	.read = tee_supp_read,
	.write = tee_supp_write,
	.unlocked_ioctl = tee_ioctl,
#ifdef CONFIG_COMPAT
	.compat_ioctl = tee_compat_ioctl,
#endif
	.open = tee_supp_open,
	.release = tee_supp_release,
};

/*
 * Stock classifies a CPU as big when its arm64 topology cluster_id equals
 * the greatest cluster_id observed over the possible-CPU mask.  No capacity,
 * MPIDR, DT, online-mask or hard-coded CPU-number policy is involved.
 */
static int large_cluster_id = -1;

noinline bool plat_cpu_is_big(int cpu)
{
	if (large_cluster_id == -1)
		return false;

	return cpu_topology[cpu].cluster_id == large_cluster_id;
}

int plat_tee_init(void)
{
	int max_cluster_id = -1;
	int cpu;

	for_each_possible_cpu(cpu) {
		if (cpu_topology[cpu].cluster_id > max_cluster_id)
			max_cluster_id = cpu_topology[cpu].cluster_id;
	}

	large_cluster_id = max_cluster_id;
	pr_info("tkcore: tkcore: big cluster_id = %d\n", large_cluster_id);
	return 0;
}

/*
 * The private stock affinity ABI is fully recovered from its KCFI ids:
 * bool(void *), bool(void *, int), int(void *).  The context is unused by
 * this policy.  These callbacks are retained by the const operations object;
 * stock contains no executable callback callsite on GQ5012BF1.
 */
struct tee_affinity_operations {
	bool (*need_bind_cpu)(void *context);
	bool (*match_cpu)(void *context, int cpu);
	int (*get_candidate_cpu)(void *context);
};

struct tee_affinity {
	const struct tee_affinity_operations *operations;
	void *context;
};

static bool big_core_affinity_need_bind_cpu(void *context)
{
	return true;
}

static bool big_core_affinity_match_cpu(void *context, int cpu)
{
	return plat_cpu_is_big(cpu);
}

static int big_core_affinity_get_candidate_cpu(void *context)
{
	static int candidate_cpu = -1;
	int cpu;

	if (candidate_cpu >= 0)
		return candidate_cpu;

	for_each_possible_cpu(cpu) {
		if (plat_cpu_is_big(cpu)) {
			candidate_cpu = cpu;
			pr_info("tkcore: candidate big cpu set to %d\n", cpu);
			break;
		}
	}

	return candidate_cpu;
}

static const struct tee_affinity_operations big_core_affinity_operations = {
	.need_bind_cpu = big_core_affinity_need_bind_cpu,
	.match_cpu = big_core_affinity_match_cpu,
	.get_candidate_cpu = big_core_affinity_get_candidate_cpu,
};

static const struct tee_affinity big_core_affinity = {
	.operations = &big_core_affinity_operations,
};

/*
 * PROVEN_EXACT: stock tee_device_configs is 3 * 0x28 bytes with exactly this
 * content.  `available` is NULL for all three entries on GQ5012BF1.
 */
static struct tee_device_desc tee_device_configs[] = {
	{
		.name = "tkcore_admin",
		.fops = &tee_admin_fops,
		.supplicant = 1,
	},
	{
		.name = "tkcore_client",
		.fops = &tee_client_fops,
		.name_lookup = 1,
	},
	{
		.name = "tkcore_fp",
		.fops = &tee_client_fops,
		/* Stock carries this dormant policy only on the fingerprint node. */
		.affinity = &big_core_affinity,
	},
};

static void tee_plt_device_release(struct device *dev)
{
	pr_debug("%s: (dev=%p)....\n", __func__, dev);
}

struct tee *tee_core_alloc(struct device *dev, char *name, int id,
			   const struct tee_ops *ops, size_t len)
{
	struct tee *tee;

	if (!dev || !name || !ops ||
	    !ops->open || !ops->close || !ops->alloc || !ops->free)
		return NULL;

	tee = devm_kzalloc(dev, len + sizeof(struct tee), GFP_KERNEL);
	if (!tee) {
		pr_err("core_alloc: kzalloc failed\n");
		return NULL;
	}

	if (!dev->release)
		dev->release = tee_plt_device_release;

	tee->id = id;
	tee->priv = &tee[1];
	tee->ops = ops;
	tee->dev = dev;

	/*
	 * Stock copies the provider-supplied name verbatim ("%s").  The
	 * donor's "optee%s%02d" decoration is NOT what tkcore does, and it
	 * does not matter for device lookup either: the /dev nodes are named
	 * from tee_device_configs, not from tee->name.
	 */
	snprintf(tee->name, sizeof(tee->name), "%s", name);
	pr_info("TEE core: Alloc the misc device \"%s\" (id=%d)\n",
		tee->name, tee->id);

	mutex_init(&tee->lock);
	atomic_set(&tee->refcount, 0);
	INIT_LIST_HEAD(&tee->list_misc);
	INIT_LIST_HEAD(&tee->list_ctx);
	INIT_LIST_HEAD(&tee->list_rpc_shm);

	tee->state = TEE_OFFLINE;
	tee->shm_flags = TEEC_MEM_INPUT | TEEC_MEM_OUTPUT;

	if (tee_supp_init(tee)) {
		devm_kfree(dev, tee);
		return NULL;
	}

	return tee;
}
EXPORT_SYMBOL(tee_core_alloc);

int tee_core_free(struct tee *tee)
{
	if (tee) {
		tee_supp_deinit(tee);
		devm_kfree(tee->dev, tee);
	}
	return 0;
}
EXPORT_SYMBOL(tee_core_free);

/*
 * Drop every misc record currently linked on @tee.
 *
 * Stock allocates the records with devm_kmalloc() but releases them with a
 * plain kfree() on both the add-failure and the delete path.  That asymmetry
 * is a stock quirk, reproduced here deliberately rather than silently
 * "corrected" to devm_kfree(), which would change the devres bookkeeping the
 * provider observes.
 */
static void tee_misc_unwind(struct tee *tee)
{
	struct tee_misc_dev *rec;
	struct tee_misc_dev *tmp;

	list_for_each_entry_safe(rec, tmp, &tee->list_misc, node) {
		misc_deregister(&rec->miscdev);
		list_del(&rec->node);
		kfree(rec);
	}
}

int tee_core_add(struct tee *tee)
{
	struct tee_misc_dev *rec;
	int i;
	int rc;

	if (!tee)
		return -EINVAL;

	for (i = 0; i < ARRAY_SIZE(tee_device_configs); i++) {
		const struct tee_device_desc *desc = &tee_device_configs[i];
		struct class *cls;

		if (desc->available && !desc->available())
			continue;

		rec = devm_kmalloc(tee->dev, sizeof(*rec),
				   GFP_KERNEL | __GFP_ZERO);
		if (!rec) {
			rc = -ENOMEM;
			goto err;
		}

		rec->desc = desc;
		rec->miscdev.minor = MISC_DYNAMIC_MINOR;
		rec->miscdev.name = desc->name;
		rec->miscdev.fops = desc->fops;
		rec->miscdev.parent = tee->dev;

		rc = misc_register(&rec->miscdev);
		if (rc) {
			pr_err("register misc device[%d] failed with %d\n",
			       i, rc);
			kfree(rec);
			goto err;
		}

		list_add_tail(&rec->node, &tee->list_misc);

		/*
		 * Keep a static reference on the misc class so that
		 * tee_get_tee() can resolve a node by name.  Every record
		 * must land in the same class.
		 */
		cls = rec->miscdev.this_device->class;
		if (!cls || (misc_class && misc_class != cls)) {
			BUG();
			rc = -ENOENT;
			goto err;
		}
		if (!misc_class)
			misc_class = cls;
	}

	rc = tee_init_procfs(tee);
	if (rc)
		goto err;

	rc = tee_init_sysfs(tee);
	if (rc) {
		tee_exit_procfs();
		goto err;
	}

	tee_peridev_init();

	list_for_each_entry(rec, &tee->list_misc, node)
		pr_info("TKCore misc: Register the misc device \"%s\" (id=%d,minor=%d)\n",
			dev_name(rec->miscdev.this_device), tee->id,
			rec->miscdev.minor);

	return 0;

err:
	tee_misc_unwind(tee);
	return rc;
}
EXPORT_SYMBOL(tee_core_add);

int tee_core_del(struct tee *tee)
{
	if (!tee)
		return 0;

	tee_peridev_exit();
	tee_cleanup_sysfs(tee);
	tee_misc_unwind(tee);
	tee_supp_deinit(tee);
	devm_kfree(tee->dev, tee);

	return 0;
}
EXPORT_SYMBOL(tee_core_del);

static int __init tee_core_init(void)
{
	spin_lock_init(&tee_idr_lock);
	idr_init(&tee_idr);
	plat_tee_init();

	return 0;
}

static void __exit tee_core_exit(void)
{
}

module_init(tee_core_init);
module_exit(tee_core_exit);

MODULE_AUTHOR("STMicroelectronics");
MODULE_DESCRIPTION("STM Secure TEE Framework/Core TEEC v1.0");
/*
 * MODULE_SUPPORTED_DEVICE() was removed from Linux in commit 6417f031 (v5.13);
 * it never emitted anything and has no ABI effect.
 */
MODULE_VERSION(_TEE_CORE_FW_VER);
MODULE_LICENSE("GPL");

/*
 * Stock GQ5012BF1 tkcore.ko declares import_ns=DMA_BUF in its .modinfo and
 * imports exactly the eight dma_buf symbols this module uses
 * (dma_buf_export/fd/get/attach/map_attachment/unmap_attachment/detach/put).
 * Declaring the namespace here reproduces the stock contract.
 */
MODULE_IMPORT_NS(DMA_BUF);
