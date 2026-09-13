/* SPDX-License-Identifier: GPL-2.0 */
/*
 * tkcore.ko provider ABI as consumed by tkcore_drv.ko.
 *
 * TrustKernel never published the tkcore headers, so the struct layouts below
 * were recovered from the stock binaries themselves:
 *
 *   tkcore.ko      sha256 03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226
 *   tkcore_drv.ko  sha256 c13503baf7c13828d0d666cbd364d8cadaa7d1282442405c72d28073bd51235d
 *
 * Every offset asserted here is proven by instruction evidence, e.g.
 *   tee_core_alloc():  devm_kmalloc(dev, priv_len + 0x138)      -> sizeof(struct tee)
 *                      snprintf(tee + 0x20, 64, "%s", name)     -> name[64] @0x20
 *                      str w23,[x20,#0x60]                      -> id @0x60
 *                      str x8,[x20,#0x88] (x8 = tee + 0x138)    -> priv @0x88
 *                      stp x22,x19,[x20,#0x90]                  -> ops @0x90, dev @0x98
 *   tee_tz_new():      stp x23,x8,[x26,#0x70]; str w24,[x26,#0x80]
 *                                                               -> log buf/size/irq
 *                      str w1,[x23,#0x64] ... [x23,#0x6c]       -> os version triple
 *   tz_start():        ldrb w8,[x0,#0x130]; tbnz w8,#0          -> conf @0x130, bit0
 *   tz_alloc():        devm_kmalloc(dev, 0x68) + field stores   -> struct tee_shm
 *
 * Member *names* are ours; only the layout is stock.  Nothing here is an
 * exported ABI of this module, so genksyms never sees these definitions.
 */
#ifndef TKCORE_DRV_TKCORE_ABI_H
#define TKCORE_DRV_TKCORE_ABI_H

#include <linux/device.h>
#include <linux/list.h>
#include <linux/types.h>

struct tk_tee;
struct tk_tee_shm;
struct tk_tee_session;
struct tk_tee_cmd;

/* tkcore enum tee_state values, from tkcore's tee_state_string table. */
#define TK_TEE_OFFLINE		0
#define TK_TEE_ONLINE		1
#define TK_TEE_SUSPENDED	2
#define TK_TEE_RUNNING		3
#define TK_TEE_CRASHED		4

/* tkcore struct tee conf bits (tz_start()/tz_stop() test bit 0). */
#define TK_TEE_CONF_FW_NOT_CAPABLE	0x00000001

/* tkcore shm flags, from tz_alloc(): flags |= 0x20000000 when the pool is cached */
#define TK_TEE_SHM_MAPPED		0x01000000
#define TK_TEE_SHM_TEMP			0x02000000
#define TK_TEE_SHM_FROM_RPC		0x04000000
#define TK_TEE_SHM_REGISTERED		0x08000000
#define TK_TEE_SHM_MEMREF		0x10000000
#define TK_TEE_SHM_CACHED		0x20000000

/**
 * struct tk_tee_ops - backend operation table handed to tee_core_alloc()
 *
 * 88 bytes, 11 slots.  Slot order proven by the stock .rodata image of
 * tee_tz_fops (.rodata+0x70) and its relocations:
 *   +0x00 __this_module  +0x08 "tz"     +0x10 tz_start  +0x18 tz_stop
 *   +0x20 tz_open        +0x28 tz_close +0x30 tz_invoke +0x38 tz_cancel
 *   +0x40 tz_alloc       +0x48 tz_free  +0x50 tz_shm_inc_ref
 * tkcore's tee_core_alloc() rejects the table unless slots +0x20, +0x28,
 * +0x40 and +0x48 are non-NULL.
 */
struct tk_tee_ops {
	struct module *owner;
	const char *type;
	int (*start)(struct tk_tee *tee);
	int (*stop)(struct tk_tee *tee);
	int (*open)(struct tk_tee_session *sess, struct tk_tee_cmd *cmd);
	int (*close)(struct tk_tee_session *sess);
	int (*invoke)(struct tk_tee_session *sess, struct tk_tee_cmd *cmd);
	int (*cancel)(struct tk_tee_session *sess, struct tk_tee_cmd *cmd);
	struct tk_tee_shm *(*alloc)(struct tk_tee *tee, size_t size, u32 flags);
	void (*free)(struct tk_tee_shm *shm);
	int (*shm_inc_ref)(struct tk_tee_shm *shm);
};

/**
 * struct tk_tee - tkcore's struct tee (312 bytes), as far as tkcore_drv uses it
 *
 * tkcore owns this object; tkcore_drv only reads/writes the members below.
 * The opaque runs are tkcore-private (klist node, misc device list, stats,
 * context/shm lists, mutex) and are never touched by this module.
 */
struct tk_tee {
	u8 tkcore_node[0x20];			/* 0x000 klist_node */
	char name[64];				/* 0x020 */
	int id;					/* 0x060 */
	u32 os_version[3];			/* 0x064 major, minor, patch */
	void *log_buf;				/* 0x070 */
	size_t log_size;			/* 0x078 */
	u32 log_irq;				/* 0x080 */
	u32 tkcore_pad084;			/* 0x084 */
	void *priv;				/* 0x088 backend private area */
	const struct tk_tee_ops *ops;		/* 0x090 */
	struct device *dev;			/* 0x098 */
	u8 tkcore_private[0x130 - 0xa0];	/* 0x0a0 lists/stats/mutex */
	u32 conf;				/* 0x130 */
	u32 test;				/* 0x134 */
};

/**
 * struct tk_tee_shm - tkcore's struct tee_shm (104 bytes)
 *
 * tz_alloc() allocates it with devm_kmalloc(dev, 0x68, GFP_KERNEL) and fills
 * size_req/size_alloc/flags/kaddr/paddr; tz_free() reads tee and paddr.
 */
struct tk_tee_shm {
	struct list_head entry;			/* 0x00 */
	void *ctx;				/* 0x10 struct tee_context * */
	struct tk_tee *tee;			/* 0x18 */
	struct device *dev;			/* 0x20 */
	size_t size_req;			/* 0x28 */
	size_t size_alloc;			/* 0x30 */
	u32 flags;				/* 0x38 */
	u32 tkcore_pad03c;			/* 0x3c */
	void *kaddr;				/* 0x40 */
	dma_addr_t paddr;			/* 0x48 */
	u8 tkcore_private[0x68 - 0x50];		/* 0x50 sgt/dma-buf state */
};

/** struct tk_tee_context - tkcore's struct tee_context, first member only */
struct tk_tee_context {
	struct tk_tee *tee;			/* 0x00 */
};

/** struct tk_tee_session - tkcore's struct tee_session (tz_open/tz_close) */
struct tk_tee_session {
	struct list_head entry;			/* 0x00 */
	struct tk_tee_context *ctx;		/* 0x10 */
	u32 sessid;				/* 0x18 */
	u32 tkcore_pad01c;			/* 0x1c */
	void *priv;				/* 0x20 */
};

/**
 * struct tk_tee_data / struct tk_tee_cmd - tkcore's command payload
 *
 * tz_open()/tz_invoke() read cmd->uuid (0x10), cmd->ta (0x18) and write the
 * four parameter slots at 0xc8/0xd0/0xd8/0xe0 plus the value pairs; that
 * places struct tee_data at 0x20 with the classic
 * {type, type_original, TEEC_SharedMemory c_shm[4], params[4]} layout.
 */
struct tk_teec_shared_memory {
	void *buffer;
	size_t size;
	u32 flags;
	u32 reserved;
	union {
		int fd;
		void *ptr;
		u64 padding_d;
	} d;
	u64 registered;
};

struct tk_teec_value {
	u32 a;
	u32 b;
};

struct tk_tee_data {
	u32 type;					/* +0x00 */
	u32 type_original;				/* +0x04 */
	struct tk_teec_shared_memory c_shm[4];		/* +0x08 */
	union {
		struct tk_tee_shm *shm;
		struct tk_teec_value value;
	} params[4];					/* +0xa8 */
};

struct tk_tee_cmd {
	u32 err;				/* 0x00 */
	u32 origin;				/* 0x04 */
	u32 cmd;				/* 0x08 */
	u32 tkcore_pad00c;			/* 0x0c */
	struct tk_tee_shm *uuid;		/* 0x10 */
	struct tk_tee_shm *ta;			/* 0x18 */
	struct tk_tee_data param;		/* 0x20 */
};

/*
 * tkcore exported API consumed by this module (11 edges).
 *
 * Prototypes for the six scalar/opaque edges are the ones whose genksyms type
 * graph is fully recovered (see kernel/phase4-tkcore-provider-abi.md); the
 * five struct-tee edges cannot be regenerated naturally and are resolved from
 * the stock provider record in the stock-compatible build.
 */
void *tee_map_cached_shm(unsigned long paddr, size_t size);
void tee_unmap_cached_shm(void *vaddr);

struct tee_wait_queue_private {
	struct mutex mu;
	struct list_head db;
};

void tee_wait_queue_init(struct tee_wait_queue_private *priv);
void tee_wait_queue_exit(struct tee_wait_queue_private *priv);
void tee_wait_queue_sleep(struct device *dev,
			  struct tee_wait_queue_private *priv, u32 key);
void tee_wait_queue_wakeup(struct device *dev,
			   struct tee_wait_queue_private *priv, u32 key);

int tee_clkmgr_handle(uint32_t id, uint32_t command);

struct tk_tee *tee_core_alloc(struct device *dev, char *name, int id,
			      const struct tk_tee_ops *ops, size_t len);
int tee_core_add(struct tk_tee *tee);
int tee_core_del(struct tk_tee *tee);
int __tee_get(struct tk_tee *tee);

/* tkcore supplicant RPC ids, from the stock tee_supp_cmd() call sites. */
#define TK_TEE_RPC_ICMD_ALLOCATE	0x1001
#define TK_TEE_RPC_ICMD_FREE		0x1002
#define TK_TEE_RPC_ICMD_INVOKE		0x1003

enum tk_teec_rpc_result {
	TK_TEEC_RPC_OK,
	TK_TEEC_RPC_FAIL,
};

enum tk_teec_rpc_result tee_supp_cmd(struct tk_tee *tee, u32 id, void *data,
				     size_t datalen);

/* tkcore RPC buffer descriptor used with TK_TEE_RPC_ICMD_ALLOCATE/FREE. */
struct tk_tee_rpc_alloc {
	u32 size;
	u32 pad;
	void *data;
	struct tk_tee_shm *shm;
};

struct tk_tee_rpc_free {
	struct tk_tee_shm *shm;
};

#endif /* TKCORE_DRV_TKCORE_ABI_H */
