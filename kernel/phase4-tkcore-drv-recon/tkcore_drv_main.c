// SPDX-License-Identifier: GPL-2.0
/*
 * TrustKernel TKCore TZ driver (tkcore_drv.ko) - reconstruction of the
 * Ulefone Armor 29 Pro Thermal (GQ5012BF1, MT6878/MT6878T) stock module.
 *
 * Stock oracle:
 *   sha256 c13503baf7c13828d0d666cbd364d8cadaa7d1282442405c72d28073bd51235d
 *   size 63480, vermagic 6.1.115-android14-11-g945dff7bc1bf,
 *   srcversion 0A6E96ED7F723D4F0883C3D, depends=tkcore,ffa_v10,
 *   build path ../kernel_device_modules-6.1/drivers/tee/tkcore/armtz/tee_tz_drv.c
 *
 * Role: tkcore.ko provides the Linux-side TEE core (devices, contexts,
 * sessions, shared memory, supplicant); this module is the *backend* that
 * carries those requests into the TrustKernel secure OS over either FF-A
 * direct messaging (partition 8bf0ccc3-42a3-5271-860d-66580469479c) or a raw
 * SMC (DT node trustkernel,tzdrv).  Both transports share one implementation;
 * only the ->invoke_tee()/->build_mem_share_handle() pair differs.
 *
 * Reconstruction scope: the Linux side only.  Secure-monitor/secure-OS
 * behaviour behind the call ids is deliberately NOT modelled or invented.
 */
#define pr_fmt(fmt) "tkcore_drv: " fmt

#include <linux/arm-smccc.h>
#include <linux/arm_ffa.h>
#include <linux/device.h>
#include <linux/err.h>
#include <linux/gfp.h>
#include <linux/io.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/of_address.h>
#include <linux/of_irq.h>
#include <linux/of_reserved_mem.h>
#include <linux/platform_device.h>
#include <linux/slab.h>
#include <linux/types.h>

#include "handle.h"
#include "tee_mem.h"
#include "tkcore_abi.h"
#include "tkcore_drv.h"

/* Backend name handed to tee_core_alloc(); stock string at .rodata.str1.1+0x386. */
#define TKCORE_BACKEND_NAME	"tkcoredrv"
/* struct tee_ops.type; stock string "tz". */
#define TKCORE_BACKEND_TYPE	"tz"
/* ffa_driver.name and the platform driver name. */
#define TKCORE_FFA_DRV_NAME	"tkcore"
#define TKCORE_SMC_DRV_NAME	"tzdrv"

static struct reserved_mem *tee_shared_mem;
static int ffa_abi_rc;
static int smc_abi_rc;

/* ------------------------------------------------------------------ */
/* Transport backends                                                  */
/* ------------------------------------------------------------------ */

/*
 * FF-A transport: one synchronous direct request per secure call.  Note that
 * memory is *not* shared through FFA_MEM_SHARE: build_mem_share_handle_ffa()
 * and build_mem_share_handle_smc() are byte-identical in stock and simply hand
 * the physical address to the secure world.
 */
static int invoke_tee_ffa(struct tee_tz *ptee, u32 func_id, u64 a1, u64 a2,
			  u64 a3, struct smc_param *res)
{
	struct ffa_send_direct_data data = {
		.data0 = func_id,
		.data1 = a1,
		.data2 = a2,
		.data3 = a3,
		.data4 = 0,
	};
	struct ffa_device *ffa_dev;
	int ret;

	ffa_dev = container_of(ptee->tee->dev, struct ffa_device, dev);

	ret = ffa_dev->ops->msg_ops->sync_send_receive(ffa_dev, &data);
	if (ret) {
		pr_err("Unexpected error %d\n", ret);
		return ret;
	}

	res->a0 = data.data0;
	res->a1 = data.data1;
	res->a2 = data.data2;
	res->a3 = data.data3;

	return 0;
}

static int invoke_tee_smc(struct tee_tz *ptee, u32 func_id, u64 a1, u64 a2,
			  u64 a3, struct smc_param *res)
{
	struct arm_smccc_res smccc_res;

	arm_smccc_smc(func_id, a1, a2, a3, 0, 0, 0, 0, &smccc_res);

	res->a0 = smccc_res.a0;
	res->a1 = smccc_res.a1;
	res->a2 = smccc_res.a2;
	res->a3 = smccc_res.a3;

	return 0;
}

static int build_mem_share_handle_ffa(struct tee_tz *ptee, void *vaddr,
				      size_t size, u32 flags, u64 *handle,
				      u32 *out_flags)
{
	*handle = virt_to_phys(vaddr);
	*out_flags = flags & 1;

	return 0;
}

static int build_mem_share_handle_smc(struct tee_tz *ptee, void *vaddr,
				      size_t size, u32 flags, u64 *handle,
				      u32 *out_flags)
{
	*handle = virt_to_phys(vaddr);
	*out_flags = flags & 1;

	return 0;
}

/* ------------------------------------------------------------------ */
/* Secure call helpers                                                 */
/* ------------------------------------------------------------------ */

static void tee_smc_call(struct tee_tz *ptee, struct smc_param *param)
{
	struct tee_affinity aff = {
		.ops = &default_affinity_operations,
		.arg = NULL,
	};

	run_tee_task(ptee, param, &aff);
}

/**
 * call_tee() - issue one secure call and service its RPC requests
 *
 * The secure world answers either with a terminal status or with an RPC
 * request encoded in the low 16 bits of a0.  The requests reproduced here are
 * exactly the ones the stock switch handles.
 */
static void call_tee(struct tee_tz *ptee, unsigned long parg,
		     void *arg_vaddr, u32 func_id, u32 cmd_id)
{
	struct tee *tee = ptee->tee;
	struct smc_param param = { 0 };
	unsigned long rpc_paddr = parg;
	void *rpc_vaddr = arg_vaddr;
	struct tee_shm *supp_shm = NULL;
	u32 *msg;
	int handle;

	param.a0 = func_id;
	param.a1 = cmd_id;

	tee_smc_call(ptee, &param);

	while (TKCORE_SMC_RETURN_IS_RPC(param.a0)) {
		u32 rpc_func = (u32)param.a0 & 0xffff;

		switch (rpc_func) {
		case TKCORE_RPC_FUNC_ALLOC:
			/* Secure world needs a normal-world buffer. */
			rpc_paddr = tkcore_shm_pool_alloc(tee->dev,
							  ptee->shm_pool,
							  param.a1, 8);
			break;
		case TKCORE_RPC_FUNC_FREE_ARG:
			rpc_vaddr = NULL;
			break;
		case TKCORE_RPC_FUNC_FREE:
			tkcore_shm_pool_free(tee->dev, ptee->shm_pool,
					     rpc_paddr, NULL);
			break;
		case TKCORE_RPC_FUNC_IRQ:
			/* Nothing to do: the call is simply resumed. */
			break;
		case TKCORE_RPC_FUNC_SUPP_ALLOC: {
			struct tee_rpc_alloc alloc = { 0 };

			alloc.size = (u32)rpc_paddr;
			tee_supp_cmd(tee, TK_TEE_RPC_ICMD_ALLOCATE, &alloc,
				     sizeof(alloc));
			supp_shm = alloc.shm;
			if (!supp_shm || IS_ERR(supp_shm)) {
				rpc_paddr = 0;
				break;
			}
			handle = handle_get(&ptee->handle_db, supp_shm);
			if (handle < 0) {
				struct tee_rpc_free free_arg = {
					.shm = supp_shm,
				};

				tee_supp_cmd(tee, TK_TEE_RPC_ICMD_FREE,
					     &free_arg, sizeof(free_arg));
				rpc_paddr = 0;
				break;
			}
			rpc_paddr = (unsigned long)supp_shm->paddr;
			break;
		}
		case TKCORE_RPC_FUNC_SUPP_FREE: {
			struct tee_shm *shm;

			shm = handle_put(&ptee->handle_db, (int)rpc_paddr);
			if (shm) {
				struct tee_rpc_free free_arg = { .shm = shm };

				tee_supp_cmd(tee, TK_TEE_RPC_ICMD_FREE,
					     &free_arg, sizeof(free_arg));
			}
			break;
		}
		case TKCORE_RPC_FUNC_CMD:
			msg = tee_shm_pool_p2v(tee->dev, ptee->shm_pool,
					       rpc_paddr);
			if (!msg)
				break;

			switch (msg[0]) {
			case TKCORE_RPC_CMD_WAIT_QUEUE_SLEEP:
				tee_wait_queue_sleep(tee->dev,
						     &ptee->wait_queue,
						     msg[14]);
				break;
			case TKCORE_RPC_CMD_WAIT_QUEUE_WAKEUP:
				tee_wait_queue_wakeup(tee->dev,
						      &ptee->wait_queue,
						      msg[14]);
				break;
			case TKCORE_RPC_CMD_CLKMGR:
				tee_clkmgr_handle(msg[14], msg[16]);
				break;
			case TKCORE_RPC_CMD_SUPPLICANT:
				tee_supp_cmd(tee, TK_TEE_RPC_ICMD_INVOKE, msg,
					     0x88);
				break;
			default:
				pr_warn("Unknown RPC func 0x%lx\n",
					(unsigned long)msg[0]);
				break;
			}
			break;
		default:
			pr_warn("Unknown RPC func 0x%lx\n",
				(unsigned long)param.a0);
			break;
		}

		param.a0 = (func_id & TKCORE_SMC_32_64_MASK) |
			   (TKCORE_SMC_STD_CALL_PREFIX |
			    TKCORE_SMC_FUNC_RETURN_FROM_RPC);
		param.a1 = rpc_paddr;
		tee_smc_call(ptee, &param);
	}
}

/* ------------------------------------------------------------------ */
/* struct tee_ops backend                                              */
/* ------------------------------------------------------------------ */

static int tz_start(struct tee *tee)
{
	struct tee_tz *ptee;
	struct device_node *np;
	struct smc_param param = { 0 };
	unsigned long paddr = 0;
	void *vaddr = NULL;
	unsigned long pages = 0;
	size_t size = 0;
	bool reserved = false;
	int ret;

	if (WARN_ON(!tee) || WARN_ON(!tee->priv))
		return -EINVAL;

	if (tee->conf & TK_TEE_CONF_FW_NOT_CAPABLE) {
		pr_err("tee not capable\n");
		return -EBUSY;
	}

	ptee = tee->priv;
	WARN_ON(ptee->started);
	ptee->started = true;

	np = of_find_compatible_node(NULL, NULL, TKCORE_DT_SHARED_MEM);
	if (!np) {
		pr_err("no node for reserved memory\n");
	} else {
		tee_shared_mem = of_reserved_mem_lookup(np);
		if (!tee_shared_mem)
			pr_err("cannot lookup reserved memory\n");
	}

	if (tee_shared_mem) {
		paddr = tee_shared_mem->base;
		size = tee_shared_mem->size;
		pr_info("use reserved shared memory: [ 0x%lx 0x%lx ]\n",
			paddr, (unsigned long)size);
		ptee->shm_cached = true;
		ptee->shm_paddr = paddr;
		vaddr = tee_map_cached_shm(paddr, size);
		ptee->shm_vaddr = vaddr;
		if (!vaddr) {
			pr_warn("map shared mem failed\n");
			ret = -ENOMEM;
			goto err;
		}
		reserved = true;
	} else {
		pr_info("use allocated shared memory\n");
		pages = __get_free_pages(GFP_KERNEL | __GFP_ZERO,
					 TKCORE_SHM_FALLBACK_ORDER);
		if (!pages) {
			ret = -ENOMEM;
			goto err;
		}
		size = TKCORE_SHM_FALLBACK_SIZE;
		vaddr = (void *)pages;
		paddr = virt_to_phys(vaddr);
		ptee->shm_cached = true;
		ptee->shm_paddr = paddr;
		ptee->shm_vaddr = vaddr;
	}

	ptee->shm_pool = tee_shm_pool_create(tee->dev, size, vaddr, paddr);
	if (!ptee->shm_pool) {
		pr_warn("create shm pool failed (%zu)\n", size);
		ret = -EINVAL;
		goto err_free;
	}

	if (ptee->shm_cached)
		tee_shm_pool_set_cached(ptee->shm_pool);

	ret = ptee->invoke_tee(ptee, TKCORE_SMC_REGISTER_SHM, ptee->shm_paddr,
			       size, 1, &param);
	if (!ret)
		ret = (int)param.a0;
	if (ret) {
		pr_err("register shm failed: %d\n", ret);
		goto err_free;
	}

	return 0;

err_free:
	if (!reserved && pages)
		free_pages(pages, TKCORE_SHM_FALLBACK_ORDER);
	ret = -EINVAL;
err:
	ptee->started = false;

	return ret;
}

static int tz_stop(struct tee *tee)
{
	struct tee_tz *ptee;

	if (WARN_ON(!tee) || WARN_ON(!tee->priv))
		return -EINVAL;

	if (tee->conf & TK_TEE_CONF_FW_NOT_CAPABLE) {
		pr_err("tee: bad state\n");
		return -EBUSY;
	}

	ptee = tee->priv;
	tee_shm_pool_destroy(tee->dev, ptee->shm_pool);
	iounmap(ptee->shm_vaddr);
	ptee->started = false;

	return 0;
}

static void set_params(struct tee_tz *ptee, struct tee_data *data,
		       u32 *msg_params)
{
	/*
	 * Translate the tkcore parameter block into the secure-world message
	 * layout.  Value parameters are copied verbatim; memory references are
	 * translated to the physical address inside the shared window.
	 */
	unsigned int n;

	for (n = 0; n < 4; n++) {
		u32 type = (data->type >> (n * 4)) & 0xf;

		switch (type) {
		case 0:
			break;
		case 1:
		case 2:
		case 3:
			msg_params[n * 2] = data->params[n].value.a;
			msg_params[n * 2 + 1] = data->params[n].value.b;
			break;
		default:
			if (data->params[n].shm)
				msg_params[n * 2] =
					(u32)data->params[n].shm->paddr;
			break;
		}
	}
}

static int tz_open(struct tee_session *sess, struct tee_cmd *cmd)
{
	struct tee *tee;
	struct tee_tz *ptee;
	unsigned long parg;
	void *arg;

	if (WARN_ON(!sess->ctx) || WARN_ON(!sess->ctx->tee))
		return -EINVAL;

	tee = sess->ctx->tee;
	ptee = tee->priv;
	if (WARN_ON(!ptee))
		return -EINVAL;

	parg = tkcore_shm_pool_alloc(tee->dev, ptee->shm_pool, 0x88, 8);
	if (!parg)
		return -ENOMEM;

	arg = tee_shm_pool_p2v(tee->dev, ptee->shm_pool, parg);
	if (!arg) {
		tkcore_shm_pool_free(tee->dev, ptee->shm_pool, parg, NULL);
		return -EINVAL;
	}

	memset(arg, 0, 0x88);
	set_params(ptee, &cmd->param, (u32 *)arg + 8);

	call_tee(ptee, parg, arg, TKCORE_SMC_STD_CALL_PREFIX, 0);

	tkcore_shm_pool_free(tee->dev, ptee->shm_pool, parg, NULL);

	return 0;
}

static int tz_close(struct tee_session *sess)
{
	struct tee *tee;
	struct tee_tz *ptee;
	unsigned long parg;
	void *arg;

	if (WARN_ON(!sess->ctx) || WARN_ON(!sess->ctx->tee))
		return -EINVAL;

	tee = sess->ctx->tee;
	ptee = tee->priv;

	parg = tkcore_shm_pool_alloc(tee->dev, ptee->shm_pool, 0x88, 8);
	if (!parg)
		return -ENOMEM;

	arg = tee_shm_pool_p2v(tee->dev, ptee->shm_pool, parg);
	if (!arg) {
		tkcore_shm_pool_free(tee->dev, ptee->shm_pool, parg, NULL);
		return -EINVAL;
	}

	memset(arg, 0, 0x88);
	((u32 *)arg)[2] = sess->sessid;

	call_tee(ptee, parg, arg, TKCORE_SMC_STD_CALL_PREFIX, 0);

	tkcore_shm_pool_free(tee->dev, ptee->shm_pool, parg, NULL);

	return 0;
}

static int tz_invoke(struct tee_session *sess, struct tee_cmd *cmd)
{
	struct tee *tee;
	struct tee_tz *ptee;
	unsigned long parg;
	void *arg;

	if (WARN_ON(!sess->ctx) || WARN_ON(!sess->ctx->tee))
		return -EINVAL;

	tee = sess->ctx->tee;
	ptee = tee->priv;

	parg = tkcore_shm_pool_alloc(tee->dev, ptee->shm_pool, 0x88, 8);
	if (!parg)
		return -ENOMEM;

	arg = tee_shm_pool_p2v(tee->dev, ptee->shm_pool, parg);
	if (!arg) {
		tkcore_shm_pool_free(tee->dev, ptee->shm_pool, parg, NULL);
		return -EINVAL;
	}

	memset(arg, 0, 0x88);
	((u32 *)arg)[1] = cmd->cmd;
	((u32 *)arg)[2] = sess->sessid;
	set_params(ptee, &cmd->param, (u32 *)arg + 8);

	call_tee(ptee, parg, arg, TKCORE_SMC_STD_CALL_PREFIX, 0);

	tkcore_shm_pool_free(tee->dev, ptee->shm_pool, parg, NULL);

	return 0;
}

static int tz_cancel(struct tee_session *sess, struct tee_cmd *cmd)
{
	struct tee *tee;
	struct tee_tz *ptee;
	unsigned long parg;
	void *arg;

	if (WARN_ON(!sess->ctx) || WARN_ON(!sess->ctx->tee))
		return -EINVAL;

	tee = sess->ctx->tee;
	ptee = tee->priv;

	parg = tkcore_shm_pool_alloc(tee->dev, ptee->shm_pool, 0x88, 8);
	if (!parg)
		return -ENOMEM;

	arg = tee_shm_pool_p2v(tee->dev, ptee->shm_pool, parg);
	if (!arg) {
		tkcore_shm_pool_free(tee->dev, ptee->shm_pool, parg, NULL);
		return -EINVAL;
	}

	memset(arg, 0, 0x88);
	((u32 *)arg)[2] = sess->sessid;

	call_tee(ptee, parg, arg, TKCORE_SMC_STD_CALL_PREFIX, 0);

	tkcore_shm_pool_free(tee->dev, ptee->shm_pool, parg, NULL);

	return 0;
}

static struct tee_shm *tz_alloc(struct tee *tee, size_t size, u32 flags)
{
	struct tee_tz *ptee = tee->priv;
	struct tee_shm *shm;
	size_t alloc_size;

	if (WARN_ON(!ptee))
		return NULL;

	alloc_size = (size & PAGE_MASK) + PAGE_SIZE;
	if (!alloc_size) {
		pr_err("requested size too big\n");
		return NULL;
	}

	shm = devm_kzalloc(tee->dev, sizeof(*shm), GFP_KERNEL);
	if (!shm)
		return ERR_PTR(-ENOMEM);

	shm->size_req = size;
	shm->size_alloc = alloc_size;
	shm->paddr = tkcore_shm_pool_alloc(tee->dev, ptee->shm_pool,
					   alloc_size, PAGE_SIZE);
	if (!shm->paddr) {
		pr_err("tz_alloc: cannot alloc memory, size 0x%lx\n",
		       (unsigned long)alloc_size);
		devm_kfree(tee->dev, shm);
		return ERR_PTR(-ENOMEM);
	}

	shm->kaddr = tee_shm_pool_p2v(tee->dev, ptee->shm_pool, shm->paddr);
	if (!shm->kaddr) {
		pr_err("tz_alloc: p2v(%p)=0\n", (void *)(uintptr_t)shm->paddr);
		tkcore_shm_pool_free(tee->dev, ptee->shm_pool, shm->paddr,
				     NULL);
		devm_kfree(tee->dev, shm);
		return ERR_PTR(-EFAULT);
	}

	shm->flags = flags;
	if (ptee->shm_cached)
		shm->flags |= TK_TEE_SHM_CACHED;

	return shm;
}

static void tz_free(struct tee_shm *shm)
{
	struct tee *tee = shm->tee;
	struct tee_tz *ptee;
	size_t size = 0;

	if (WARN_ON(!tee) || WARN_ON(!tee->priv))
		return;

	ptee = tee->priv;
	if (!tkcore_shm_pool_free(tee->dev, ptee->shm_pool, shm->paddr, &size))
		devm_kfree(tee->dev, shm);
}

static int tz_shm_inc_ref(struct tee_shm *shm)
{
	struct tee *tee = shm->tee;
	struct tee_tz *ptee;

	if (WARN_ON(!tee) || WARN_ON(!tee->priv))
		return -EINVAL;

	ptee = tee->priv;

	return tee_shm_pool_incref(tee->dev, ptee->shm_pool, shm->paddr);
}

static const struct tee_ops tee_tz_fops = {
	.owner = THIS_MODULE,
	.type = TKCORE_BACKEND_TYPE,
	.start = tz_start,
	.stop = tz_stop,
	.open = tz_open,
	.close = tz_close,
	.invoke = tz_invoke,
	.cancel = tz_cancel,
	.alloc = tz_alloc,
	.free = tz_free,
	.shm_inc_ref = tz_shm_inc_ref,
};

/* ------------------------------------------------------------------ */
/* Backend registration                                                */
/* ------------------------------------------------------------------ */

/**
 * tee_tz_new() - build the backend and hand it to tkcore
 *
 * Order (stock):
 *   tee_init_task()                 - per-CPU workers + hotplug listener
 *   tee_core_alloc(dev, "tkcoredrv", id, &tee_tz_fops, 0xa0)
 *   ptee init + tee_wait_queue_init()
 *   invoke(GET_OS_REVISION)         - first secure call, fills tee->os_version
 *   of_find_compatible_node("trustkernel,tkcore") + irq_of_parse_and_map()
 *   __get_free_pages(order 5)       - 128 KiB secure log ring
 *   build_mem_share_handle() + invoke(SETUP_LOG_BUF)
 *   tee_core_add() then __tee_get()
 */
static int tee_tz_new(struct device *dev, int id,
		      int (*invoke_tee)(struct tee_tz *, u32, u64, u64, u64,
					struct smc_param *),
		      int (*build_mem_share_handle)(struct tee_tz *, void *,
						    size_t, u32, u64 *, u32 *),
		      struct tee **tee_out)
{
	struct smc_param param = { 0 };
	struct device_node *np;
	struct tee_tz *ptee;
	struct tee *tee;
	unsigned long log_buf;
	u32 log_flags = 0;
	u64 log_handle = 0;
	u32 ver[3] = { 0 };
	int log_irq = 0;
	int ret;

	ret = tee_init_task();
	if (ret < 0)
		return ret;

	tee = tee_core_alloc(dev, TKCORE_BACKEND_NAME, id, &tee_tz_fops,
			     sizeof(struct tee_tz));
	if (!tee) {
		tee_exit_task();
		return -ENOMEM;
	}

	ptee = tee->priv;
	ptee->started = false;
	ptee->tee = tee;
	ptee->shm_paddr = 0;
	ptee->shm_vaddr = NULL;
	ptee->shm_cached = false;
	ptee->shm_pool = NULL;
	ptee->reserved30 = 0;
	ptee->reserved38 = 0;
	ptee->invoke_tee = invoke_tee;
	ptee->build_mem_share_handle = build_mem_share_handle;
	tee_wait_queue_init(&ptee->wait_queue);
	ptee->handle_db.ptrs = NULL;
	ptee->handle_db.max_ptrs = 0;

	/*
	 * Secure OS revision handshake.  A secure world that answers with a
	 * fourth word reports (major, minor, patch) in a0..a2; otherwise the
	 * triple is shifted and the major number is 0.
	 */
	ret = ptee->invoke_tee(ptee, TKCORE_SMC_GET_OS_REVISION, 0, 0, 0,
			       &param);
	if (!ret) {
		if (param.a3 == 0) {
			ver[0] = 0;
			ver[1] = (u32)param.a0;
			ver[2] = (u32)param.a1;
		} else {
			ver[0] = (u32)param.a0;
			ver[1] = (u32)param.a1;
			ver[2] = (u32)param.a2;
		}
		tee->os_version[0] = ver[0];
		tee->os_version[1] = ver[1];
		tee->os_version[2] = ver[2];
	} else {
		ver[0] = tee->os_version[0];
		ver[1] = tee->os_version[1];
		ver[2] = tee->os_version[2];
	}
	pr_info("tkcoreos-rev: %d.%d.%d-gp\n", ver[0], ver[1], ver[2]);

	/* Secure log ring: IRQ number from DT, buffer from the page allocator. */
	np = of_find_compatible_node(NULL, NULL, TKCORE_DT_TKCORE);
	if (!np)
		pr_err("device node not found\n");
	else
		log_irq = irq_of_parse_and_map(np, 0);

	log_buf = __get_free_pages(GFP_KERNEL | __GFP_ZERO,
				   TKCORE_LOG_BUF_ORDER);
	if (!log_buf) {
		pr_warn("alloc log buffer failed\n");
		ret = -ENOMEM;
		goto log_failed;
	}

	ret = ptee->build_mem_share_handle(ptee, (void *)log_buf,
					   TKCORE_LOG_BUF_SIZE, 1, &log_handle,
					   &log_flags);
	if (ret)
		goto log_free;

	ret = ptee->invoke_tee(ptee, TKCORE_SMC_SETUP_LOG_BUF, log_handle,
			       TKCORE_LOG_BUF_SIZE, log_flags, &param);
	if (ret) {
		pr_err("setup tee log buffer failed with 0x%x\n", ret);
		goto log_free;
	}

	ret = (int)param.a0;
	if (ret)
		goto log_free;

	tee->log_buf = (void *)log_buf;
	tee->log_size = TKCORE_LOG_BUF_SIZE;
	tee->log_irq = log_irq;
	goto add;

log_free:
	free_pages(log_buf, TKCORE_LOG_BUF_ORDER);
log_failed:
	tee->log_buf = NULL;
	tee->log_size = 0;
	tee->log_irq = 0;
	pr_warn("init log buffer failed: %d\n", ret);

add:
	ret = tee_core_add(tee);
	if (!ret)
		ret = __tee_get(tee);
	if (ret) {
		if (!(ptee->tee->conf & TK_TEE_CONF_FW_NOT_CAPABLE))
			tee_wait_queue_exit(&ptee->wait_queue);
		tee_core_del(tee);
		tee_exit_task();
		return ret;
	}

	*tee_out = tee;

	return 0;
}

static void tee_tz_destroy(struct tee *tee)
{
	struct tee_tz *ptee = tee->priv;

	if (!(ptee->tee->conf & TK_TEE_CONF_FW_NOT_CAPABLE))
		tee_wait_queue_exit(&ptee->wait_queue);

	tee_core_del(ptee->tee);
	tee_exit_task();
}

/* ------------------------------------------------------------------ */
/* FF-A driver                                                         */
/* ------------------------------------------------------------------ */

static const struct ffa_device_id tkcore_ffa_device_id[] = {
	/* 8bf0ccc3-42a3-5271-860d-66580469479c */
	{ UUID_INIT(0x8bf0ccc3, 0x42a3, 0x5271,
		    0x86, 0x0d, 0x66, 0x58, 0x04, 0x69, 0x47, 0x9c) },
	{}
};

static int tkcore_ffa_probe(struct ffa_device *ffa_dev)
{
	struct tee *tee = NULL;
	int ret;

	ret = tee_tz_new(&ffa_dev->dev, ffa_dev->id, invoke_tee_ffa,
			 build_mem_share_handle_ffa, &tee);
	if (ret)
		return ret;

	dev_set_drvdata(&ffa_dev->dev, tee);
	pr_info("ffa: initialized driver\n");

	return 0;
}

static void tkcore_ffa_remove(struct ffa_device *ffa_dev)
{
	struct tee *tee = dev_get_drvdata(&ffa_dev->dev);

	tee_tz_destroy(tee);
}

static struct ffa_driver tkcore_ffa_driver = {
	.name = TKCORE_FFA_DRV_NAME,
	.probe = tkcore_ffa_probe,
	.remove = tkcore_ffa_remove,
	.id_table = tkcore_ffa_device_id,
};

/* ------------------------------------------------------------------ */
/* SMC (platform) driver                                               */
/* ------------------------------------------------------------------ */

static const struct of_device_id tkcore_smc_device_id[] = {
	{ .compatible = TKCORE_DT_TZDRV },
	{}
};
MODULE_DEVICE_TABLE(of, tkcore_smc_device_id);

static int tkcore_smc_probe(struct platform_device *pdev)
{
	struct tee *tee = NULL;
	int ret;

	ret = tee_tz_new(&pdev->dev, pdev->id, invoke_tee_smc,
			 build_mem_share_handle_smc, &tee);
	if (!ret)
		platform_set_drvdata(pdev, tee);

	return ret;
}

static int tkcore_smc_remove(struct platform_device *pdev)
{
	struct tee *tee = platform_get_drvdata(pdev);

	tee_tz_destroy(tee);

	return 0;
}

static struct platform_driver tkcore_smc_driver = {
	.probe = tkcore_smc_probe,
	.remove = tkcore_smc_remove,
	.driver = {
		.name = TKCORE_SMC_DRV_NAME,
		.owner = THIS_MODULE,
		.of_match_table = tkcore_smc_device_id,
	},
};

/* ------------------------------------------------------------------ */
/* Module lifecycle                                                    */
/* ------------------------------------------------------------------ */

static int __init tkcore_drv_init(void)
{
	pr_info("TrustKernel TEE Driver initialization\n");

	/*
	 * Both transports are registered unconditionally; whichever one the
	 * platform actually provides will probe.  The module only fails to
	 * load when *both* registrations fail, and it then returns 1 rather
	 * than a negative errno - preserved stock behaviour.
	 */
	ffa_abi_rc = ffa_driver_register(&tkcore_ffa_driver, THIS_MODULE,
					 KBUILD_MODNAME);
	smc_abi_rc = __platform_driver_register(&tkcore_smc_driver,
						THIS_MODULE);

	return (ffa_abi_rc && smc_abi_rc) ? 1 : 0;
}

static void __exit tkcore_drv_exit(void)
{
	pr_info("TrustKernel TEE Driver Release\n");

	/*
	 * Stock quirk, preserved verbatim: the unregister calls are guarded by
	 * the *non-zero* (i.e. failed) registration return codes, so a module
	 * that registered successfully is never unregistered here.  The stock
	 * module is never unloaded on this device (no dependents, vendor
	 * ramdisk load list), so the asymmetry is unobservable in practice.
	 */
	if (ffa_abi_rc)
		ffa_driver_unregister(&tkcore_ffa_driver);
	if (smc_abi_rc)
		platform_driver_unregister(&tkcore_smc_driver);
}

module_init(tkcore_drv_init);
module_exit(tkcore_drv_exit);

MODULE_AUTHOR("TrustKernel");
MODULE_DESCRIPTION("TrustKernel TKCore TZ driver");
MODULE_VERSION("1.0");
MODULE_LICENSE("GPL");
