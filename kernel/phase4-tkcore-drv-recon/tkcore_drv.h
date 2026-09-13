/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Private types and secure-monitor call identifiers for the GQ5012BF1
 * TrustKernel backend driver (tkcore_drv.ko) reconstruction.
 *
 * Every identifier below is read out of the stock binary; none is invented.
 * Secure-world *behaviour* behind these ids is deliberately not modelled.
 */
#ifndef TKCORE_DRV_H
#define TKCORE_DRV_H

#include <linux/completion.h>
#include <linux/list.h>
#include <linux/mutex.h>
#include <linux/sched.h>
#include <linux/spinlock.h>
#include <linux/types.h>
#include <linux/wait.h>

#include "handle.h"
#include "tkcore_abi.h"

struct shm_pool;

/*
 * Secure call identifiers.
 *
 * The stock module builds them as <prefix> | <function>, where the prefix
 * carries the SMC 32/64 calling-convention bit in bit 31:
 *   0x72000000  standard (yielding) call
 *   0xf2000000  fast call
 * Evidence:
 *   tee_tz_new():  mov w1,#1     ; movk w1,#0xf200,lsl#16 -> 0xf2000001
 *   tee_tz_new():  mov w1,#0x5705; movk w1,#0xf200,lsl#16 -> 0xf2005705
 *   tz_start():    mov w1,#0x5704; movk w1,#0xf200,lsl#16 -> 0xf2005704
 *   do_smc():      (a0 & 0x80000000) | 0x72000003          -> return-from-RPC
 */
#define TKCORE_SMC_STD_CALL_PREFIX	0x72000000u
#define TKCORE_SMC_FAST_CALL_PREFIX	0xf2000000u
#define TKCORE_SMC_32_64_MASK		0x80000000u

#define TKCORE_SMC_FUNC_GET_OS_REVISION	0x0001u
#define TKCORE_SMC_FUNC_RETURN_FROM_RPC	0x0003u
#define TKCORE_SMC_FUNC_REGISTER_SHM	0x5704u
#define TKCORE_SMC_FUNC_SETUP_LOG_BUF	0x5705u

#define TKCORE_SMC_GET_OS_REVISION \
	(TKCORE_SMC_FAST_CALL_PREFIX | TKCORE_SMC_FUNC_GET_OS_REVISION)
#define TKCORE_SMC_REGISTER_SHM \
	(TKCORE_SMC_FAST_CALL_PREFIX | TKCORE_SMC_FUNC_REGISTER_SHM)
#define TKCORE_SMC_SETUP_LOG_BUF \
	(TKCORE_SMC_FAST_CALL_PREFIX | TKCORE_SMC_FUNC_SETUP_LOG_BUF)

/* Secure-world return values observed in do_smc()/run_tee_task(). */
#define TKCORE_SMC_RETURN_BUSY		0x00000001u	/* retry after wait   */
#define TKCORE_SMC_RETURN_BIND_CPU	0x00000006u	/* rebind then resume */
#define TKCORE_SMC_RETURN_RPC_PREFIX	0xffff0000u
#define TKCORE_SMC_RETURN_RPC_IRQ	0xffff0004u	/* preempted by IRQ   */
#define TKCORE_SMC_RETURN_RPC_BIND_CPU	0xffff5702u
#define TKCORE_SMC_RETURN_IS_RPC(a0)	\
	((((u32)(a0)) & TKCORE_SMC_RETURN_RPC_PREFIX) == TKCORE_SMC_RETURN_RPC_PREFIX)

/* RPC function selectors, low 16 bits of a0 (call_tee() switch). */
#define TKCORE_RPC_FUNC_ALLOC		0x0000u
#define TKCORE_RPC_FUNC_FREE_ARG	0x0001u
#define TKCORE_RPC_FUNC_FREE		0x0002u
#define TKCORE_RPC_FUNC_IRQ		0x0003u
#define TKCORE_RPC_FUNC_CMD		0x0005u
#define TKCORE_RPC_FUNC_SUPP_ALLOC	0x5700u
#define TKCORE_RPC_FUNC_SUPP_FREE	0x5701u

/* RPC command ids inside the shared-memory message (call_tee() CMD path). */
#define TKCORE_RPC_CMD_WAIT_QUEUE_SLEEP		0x20000001u
#define TKCORE_RPC_CMD_WAIT_QUEUE_WAKEUP	0x20000002u
#define TKCORE_RPC_CMD_SUPPLICANT		0x1000000au
#define TKCORE_RPC_CMD_CLKMGR			0x80000001u
#define TKCORE_RPC_CMD_SHM_ALLOC_LIMIT		0x2fffffffu
#define TKCORE_RPC_CMD_SHM_ALLOC		0x30000000u

/* Secure-world log ring: __get_free_pages(order 5) = 32 pages = 128 KiB. */
#define TKCORE_LOG_BUF_ORDER		5
#define TKCORE_LOG_BUF_SIZE		(PAGE_SIZE << TKCORE_LOG_BUF_ORDER)

/* Fallback (non reserved-memory) shared pool: order 10 = 1024 pages = 4 MiB. */
#define TKCORE_SHM_FALLBACK_ORDER	10
#define TKCORE_SHM_FALLBACK_SIZE	(PAGE_SIZE << TKCORE_SHM_FALLBACK_ORDER)

/* Device-tree contract. */
#define TKCORE_DT_SHARED_MEM		"trustkernel,shared_mem"
#define TKCORE_DT_TKCORE		"trustkernel,tkcore"
#define TKCORE_DT_TZDRV			"trustkernel,tzdrv"

/* Long-call warning threshold used by do_smc(): 1,000,000 us. */
#define TKCORE_SMC_WARN_DURATION_US	1000000LL

/**
 * struct smc_param - normal/secure world register block
 *
 * Mirrors the stock 4x64-bit buffer that invoke_tee_smc()/invoke_tee_ffa()
 * fill from x0..x3 (respectively FF-A direct-response data0..data3).
 */
struct smc_param {
	u64 a0;
	u64 a1;
	u64 a2;
	u64 a3;
};

/**
 * struct tee_affinity_ops - CPU selection policy for one secure call
 *
 * Two instances exist in stock .rodata, each three slots wide:
 *   default_affinity_operations      (.rodata+0xc8)
 *   tee_bind_cpu_request_operations  (.rodata+0x290)
 */
struct tee_affinity_ops {
	bool (*need_bind_cpu)(void *arg);
	bool (*match_cpu)(void *arg, int cpu);
	int (*get_candidate_cpu)(void *arg);
};

/** struct tee_affinity - policy + policy argument for one secure call */
struct tee_affinity {
	const struct tee_affinity_ops *ops;
	void *arg;
};

/**
 * struct tee_task_req - one queued secure call
 *
 * Layout matches the stock stack frame consumed by tkcore_smc_task():
 *   ldp x0,x1,[node-0x18]; ldur x2,[node-0x8]; complete(node+0x10)
 */
struct tee_task_req {
	struct tee_tz *ptee;		/* -0x18 */
	struct smc_param *param;	/* -0x10 */
	struct smc_param *out;		/* -0x08 */
	struct list_head node;		/*  0x00 */
	struct completion done;		/*  0x18 */
};

/** struct tee_task - one per-CPU secure-call kthread (32 bytes in stock) */
struct tee_task {
	struct task_struct *task;
	wait_queue_head_t thread_wq;
};

/**
 * struct tee_task_ctl - global secure-call dispatcher state
 *
 * Stock object: tee_task_ctl in .bss+0x10, 152 bytes.  Offsets proven by
 * tee_init_task()/tkcore_smc_task()/run_tee_task()/do_smc().
 */
struct tee_task_ctl {
	struct mutex g_lock;		/* 0x00 serialises every secure call */
	int waiters;			/* 0x30 */
	struct completion wait_done;	/* 0x38 */
	u32 idle_mask;			/* 0x58 bit set while a CPU thread runs */
	struct list_head queue;		/* 0x60 */
	spinlock_t q_lock;		/* 0x70 */
	int cpuhp_state;		/* 0x74 */
	struct tee_task *threads;	/* 0x78 */
	int nr_threads;			/* 0x80 */
	s64 max_duration_us;		/* 0x88 */
	u64 reserved90;			/* 0x90 */
};

/**
 * struct tee_tz - backend private area (0xa0 bytes)
 *
 * tee_core_alloc(dev, "tkcoredrv", id, &tee_tz_fops, 0xa0) reserves it right
 * behind tkcore's struct tee; offsets below are the stock ones.
 */
struct tee_tz {
	bool started;					/* 0x00 */
	struct tee *tee;				/* 0x08 */
	unsigned long shm_paddr;			/* 0x10 */
	void *shm_vaddr;				/* 0x18 */
	bool shm_cached;				/* 0x20 */
	u8 pad21[7];
	struct shm_pool *shm_pool;			/* 0x28 */
	u64 reserved30;					/* 0x30 zeroed by tee_tz_new() */
	u64 reserved38;					/* 0x38 zeroed by tee_tz_new() */
	int (*invoke_tee)(struct tee_tz *ptee, u32 func_id, u64 a1, u64 a2,
			  u64 a3, struct smc_param *res);	/* 0x40 */
	int (*build_mem_share_handle)(struct tee_tz *ptee, void *vaddr,
				      size_t size, u32 flags, u64 *handle,
				      u32 *out_flags);		/* 0x48 */
	struct tee_wait_queue_private wait_queue;	/* 0x50 */
	struct handle_db handle_db;			/* 0x90 */
};

/* tee_task.c */
int tee_init_task(void);
void tee_exit_task(void);
void run_tee_task(struct tee_tz *ptee, struct smc_param *param,
		  struct tee_affinity *aff);
extern const struct tee_affinity_ops default_affinity_operations;
extern const struct tee_affinity_ops tee_bind_cpu_request_operations;

#endif /* TKCORE_DRV_H */
