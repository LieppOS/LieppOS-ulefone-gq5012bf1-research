/* SPDX-License-Identifier: GPL-2.0 */
/*
 * TrustKernel TKCore - common island core types (LieppOS reconstruction).
 *
 * GQ5012BF1 / MT6878T.  This header defines the private TrustKernel type
 * graph shared by every source-built module of the TrustKernel ABI island:
 *
 *     tkcore  tkcore_drv  tmem_ffa  microarray_fp_tee
 *
 * PROVENANCE OF EVERY DEFINITION
 * ------------------------------
 * Layout anchors (offsets and total sizes) are recovered from the stock
 * tkcore.ko / tkcore_drv.ko ELFs and corroborated by tmem_ffa.  Those are
 * marked PROVEN_*.  MEMBER NAMES ARE NOT RECOVERABLE from a stripped .ko:
 * genksyms hashes member spellings, and an exhaustive search over millions of
 * candidate spellings failed to reproduce the historical CRCs.  Names below
 * that could not be recovered are therefore SYNTHETIC_ISLAND_NAME: chosen
 * once, here, and used identically by every island module.
 *
 * Consequence, stated plainly: the 11 historically PROVIDER_ABI_BLOCKED
 * exports get island CRCs that differ from the historical Ulefone CRCs.  That
 * is deliberate and is documented in
 * kernel/phase4-tkcore-historical-vs-island-crc.md.  No CRC is injected,
 * patched or faked anywhere.
 *
 * Structural donor: OP-TEE optee_linuxdriver (BSD-2), reworked by TrustKernel.
 */
#ifndef __TRUSTKERNEL_TEE_CORE_H__
#define __TRUSTKERNEL_TEE_CORE_H__

#include <linux/atomic.h>
#include <linux/device.h>
#include <linux/klist.h>
#include <linux/kref.h>
#include <linux/list.h>
#include <linux/miscdevice.h>
#include <linux/mutex.h>
#include <linux/scatterlist.h>
#include <linux/types.h>

#include <trustkernel/tee_client_api.h>

struct tee_cmd_io;
struct tee_shm_io;
struct tee_rpc;
struct tee_ops;

/* PROVEN_SEMANTICS: state machine observed in tkcore sysfs "state" output. */
enum tee_state {
	TEE_OFFLINE = 0,
	TEE_ONLINE = 1,
	TEE_SUSPENDED = 2,
	TEE_RUNNING = 3,
	TEE_CRASHED = 4,
	TEE_LAST = 5,
};

#define TEE_CONF_TEST_MODE		0x01000000
#define TEE_CONF_FW_NOT_CAPABLE		0x00000001

/* PROVEN_EXACT layout: two ints, three entries, reached by tee_inc_stats. */
struct tee_stats_entry {
	int count;
	int max;
};

#define TEE_STATS_CONTEXT_IDX	0
#define TEE_STATS_SESSION_IDX	1
#define TEE_STATS_SHM_IDX	2

#define TEE_MAX_TEE_DEV_NAME	(64)

/**
 * struct tee - one TrustKernel TEE device instance.
 *
 * Total size PROVEN_EXACT: 0x138 (312) bytes.
 *
 * Proven offset anchors (from stock tkcore/tkcore_drv code):
 *   node        @0x000   klist_node
 *   name        @0x020   char[64]
 *   id          @0x060   int
 *   version     @0x064   three u32 components used by /proc/tkcore_os_version
 *   log_shm     @0x070   shared secure-log header/ring mapping
 *   log_shm_len @0x078
 *   log_irq     @0x080
 *   priv        @0x088
 *   ops         @0x090
 *   dev         @0x098
 *   list_misc   @0x0a0   TrustKernel replaced OP-TEE's inline struct
 *                        miscdevice with a LIST of misc devices, because one
 *                        tee instance backs tkcore_admin/tkcore_client/
 *                        tkcore_fp.
 *   rpc         @0x0b0
 *   refcount    @0x0b8
 *   max_refcount@0x0bc
 *   stats       @0x0c0
 *   list_ctx    @0x0d8
 *   list_rpc_shm@0x0e8
 *   lock        @0x0f8   mutex
 *   state       @0x128
 *   shm_flags   @0x12c
 *
 * Members occupying the gaps between those anchors are
 * PROVEN_SEMANTICS_OFFSETS_ONLY: their presence and role are inferred from
 * stock call sites (statistics, refcount, rpc, debugfs) and they are placed
 * so that every proven anchor above lands on its proven offset.  Their
 * spellings are SYNTHETIC_ISLAND_NAME.
 */
struct tee {
	struct klist_node node;			/* 0x000 PROVEN_EXACT */
	char name[TEE_MAX_TEE_DEV_NAME];	/* 0x020 PROVEN_EXACT */
	int id;					/* 0x060 PROVEN_EXACT */
	u32 version_major;			/* 0x064 PROVEN_EXACT */
	u32 version_minor;			/* 0x068 PROVEN_EXACT */
	u32 version_patch;			/* 0x06c PROVEN_EXACT */
	void *log_shm;				/* 0x070 PROVEN_EXACT */
	size_t log_shm_len;			/* 0x078 PROVEN_EXACT */
	int log_irq;				/* 0x080 PROVEN_EXACT */
	u32 pad_log_irq;			/* 0x084 alignment */
	void *priv;				/* 0x088 PROVEN_EXACT */
	const struct tee_ops *ops;		/* 0x090 PROVEN_EXACT */
	struct device *dev;			/* 0x098 PROVEN_EXACT */
	struct list_head list_misc;		/* 0x0a0 PROVEN_EXACT */
	struct tee_rpc *rpc;			/* 0x0b0 PROVEN_EXACT */
	atomic_t refcount;			/* 0x0b8 PROVEN_EXACT */
	int max_refcount;			/* 0x0bc PROVEN_EXACT */
	struct tee_stats_entry stats[3];	/* 0x0c0 PROVEN_EXACT */
	struct list_head list_ctx;		/* 0x0d8 PROVEN_EXACT */
	struct list_head list_rpc_shm;		/* 0x0e8 PROVEN_EXACT */
	struct mutex lock;			/* 0x0f8 PROVEN_EXACT, 0x30 B */
	unsigned int state;			/* 0x128 PROVEN_EXACT */
	u32 shm_flags;				/* 0x12c PROVEN_EXACT */
	u32 conf;				/* 0x130 SYNTHETIC */
	u32 test;				/* 0x134 SYNTHETIC */
};						/* 0x138 PROVEN_EXACT total */

/*
 * Misc-device record.
 *
 * The OP-TEE donor embedded a single `struct miscdevice` directly inside
 * `struct tee` and recovered the owning tee with
 *   container_of(filp->private_data, struct tee, miscdev)
 *
 * TrustKernel does NOT do that: `struct tee` carries a list_head at the
 * PROVEN offset 0x0a0, and GQ5012BF1 exposes three device nodes
 * (/dev/tkcore_admin, /dev/tkcore_client, /dev/tkcore_fp) backed by the TEE.
 * A list of misc devices is therefore the only structure consistent with the
 * stock evidence.
 *
 * This record is what `struct tee.list_misc` links together.  It is an
 * island-private helper type: it does NOT appear in any exported prototype,
 * so it cannot perturb any export CRC, and it does NOT change the layout of
 * `struct tee`.
 */
struct tee_misc_dev {
	struct list_head node;		/* link into struct tee.list_misc */
	struct miscdevice miscdev;
	struct tee *tee;		/* owning TEE */
};

/*
 * Device used for logging and for DMA attribution.
 *
 * Donor:  #define _DEV(tee) (tee->miscdev.this_device)
 *
 * The island resolves this through the PROVEN `struct tee.dev` member at
 * 0x098 instead, which holds the parent device passed to tee_core_alloc().
 *
 * `tee->dev` deliberately keeps holding the PARENT device and is NOT
 * reassigned to this_device, because tee_core_free() calls
 * devm_kfree(tee->dev, tee) and devm accounting must stay attached to the
 * device the allocation was made against.
 *
 * Divergence from the donor is therefore limited to which device name
 * prefixes a dev_*() log line, and to the device recorded on an exported
 * dma_buf.  The misc device's this_device remains reachable through the
 * matching struct tee_misc_dev for the cases that genuinely require it
 * (drvdata, class registration, device naming).
 */
#define _DEV(tee) ((tee)->dev)

/**
 * tee_primary_misc() - first misc-device record registered for @tee
 *
 * Replaces the donor's direct `&tee->miscdev` access.  Returns NULL when no
 * misc device has been attached yet.
 */
struct tee_misc_dev *tee_primary_misc(struct tee *tee);

#define TEE_MAX_CLIENT_NAME	(128)

/**
 * struct tee_context - one open client connection to a struct tee.
 *
 * Total size PROVEN_EXACT: 0xd0 (208) bytes.
 *
 * Proven offset anchors:
 *   tee        @0x00
 *   name       @0x08   char[128]
 *   tgid       @0x88
 *   usr_client @0x8c
 *   entry      @0x90
 *   list_sess  @0xa0
 *   list_shm   @0xb0
 *   refcount   @0xc0   kref
 *   (extra ptr)@0xc8   TrustKernel addition over the OP-TEE donor
 */
struct tee_context {
	struct tee *tee;			/* 0x00 PROVEN_EXACT */
	char name[TEE_MAX_CLIENT_NAME];		/* 0x08 PROVEN_EXACT */
	int tgid;				/* 0x88 PROVEN_EXACT */
	int usr_client;				/* 0x8c PROVEN_EXACT */
	struct list_head entry;			/* 0x90 PROVEN_EXACT */
	struct list_head list_sess;		/* 0xa0 PROVEN_EXACT */
	struct list_head list_shm;		/* 0xb0 PROVEN_EXACT */
	struct kref refcount;			/* 0xc0 PROVEN_EXACT */
	u32 pad_refcount;			/* 0xc4 alignment */
	void *ctx_priv;				/* 0xc8 SYNTHETIC name,
						 *      PROVEN offset/size
						 */
};						/* 0xd0 PROVEN_EXACT total */

/**
 * struct tee_session - one open session to a Trusted Application.
 *
 * Struct tag PROVEN_EXACT (recovered from tkcore_drv).  Member layout follows
 * the donor; TrustKernel did not change its observable size.
 */
struct tee_session {
	struct list_head entry;
	struct tee_context *ctx;
	u32 sessid;
	u32 pad_sessid;
	void *priv;
};

struct tee_shm_dma_buf {
	struct dma_buf_attachment *attach;
	struct sg_table *sgt;
	bool tee_allocated;
};

/**
 * struct tee_shm - one shared-memory object.
 *
 * Struct tag PROVEN_EXACT (recovered from tkcore_drv).  TrustKernel routes
 * these through its own dma-buf ops (__tee_shm_dma_buf_*), so the dma-buf
 * back-pointer is retained.
 */
struct tee_shm {
	struct list_head entry;
	struct tee_context *ctx;
	struct tee *tee;
	struct device *dev;
	size_t size_req;
	size_t size_alloc;
	u32 flags;
	u32 pad_flags;
	void *kaddr;
	dma_addr_t paddr;
	struct sg_table sgt;
	struct tee_shm_dma_buf *sdb;
};

#define TEE_SHM_MAPPED			0x01000000
#define TEE_SHM_TEMP			0x02000000
#define TEE_SHM_FROM_RPC		0x04000000
#define TEE_SHM_REGISTERED		0x08000000
#define TEE_SHM_MEMREF			0x10000000
#define TEE_SHM_CACHED			0x20000000
#define TEE_SHM_DRV_PRIV_MASK		0xFF000000

struct tee_data {
	u32 type;
	u32 type_original;
	TEEC_SharedMemory c_shm[TEEC_CONFIG_PAYLOAD_REF_COUNT];
	union {
		struct tee_shm *shm;
		TEEC_Value value;
	} params[TEEC_CONFIG_PAYLOAD_REF_COUNT];
};

/* Struct tag PROVEN_EXACT (recovered from tkcore_drv). */
struct tee_cmd {
	TEEC_Result err;
	u32 origin;
	u32 cmd;
	u32 pad_cmd;
	struct tee_shm *uuid;
	struct tee_shm *ta;
	struct tee_data param;
};

/**
 * struct tee_ops - the backend interface tkcore_drv implements for tkcore.
 *
 * Slot set and prototypes are PROVEN by tkcore_drv's stock backend object and
 * by tkcore's indirect call sites; see
 * kernel/phase4-trustkernel-backend-ops.md.
 */
struct tee_ops {
	struct module *owner;
	const char *type;

	int (*start)(struct tee *tee);
	int (*stop)(struct tee *tee);
	int (*open)(struct tee_session *sess, struct tee_cmd *cmd);
	int (*close)(struct tee_session *sess);
	int (*invoke)(struct tee_session *sess, struct tee_cmd *cmd);
	int (*cancel)(struct tee_session *sess, struct tee_cmd *cmd);
	struct tee_shm *(*alloc)(struct tee *tee, size_t size, u32 flags);
	void (*free)(struct tee_shm *shm);
	int (*shm_inc_ref)(struct tee_shm *shm);
};

/* ---- core lifecycle (exported) ------------------------------------- */
struct tee *tee_core_alloc(struct device *dev, char *name, int id,
			   const struct tee_ops *ops, size_t len);
int tee_core_free(struct tee *tee);
int tee_core_add(struct tee *tee);
int tee_core_del(struct tee *tee);
struct tee *__tee_get(struct tee *tee);

/* ---- rpc shared memory (exported to the backend) ------------------- */
struct tee_shm *tee_shm_alloc_from_rpc(struct tee *tee, size_t size);
void tee_shm_free_from_rpc(struct tee_shm *shm);

#endif /* __TRUSTKERNEL_TEE_CORE_H__ */
