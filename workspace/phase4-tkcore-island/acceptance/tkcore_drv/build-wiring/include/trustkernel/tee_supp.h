/* SPDX-License-Identifier: GPL-2.0 */
/*
 * TrustKernel TKCore - supplicant / RPC island header.
 *
 * tee_supp_cmd is exported and consumed by tkcore_drv.  Its historical CRC is
 * blocked only because the prototype names struct tee, whose private member
 * spellings are unrecoverable; the prototype shape itself is PROVEN_EXACT
 * from tkcore_drv's call site.
 */
#ifndef __TRUSTKERNEL_TEE_SUPP_H__
#define __TRUSTKERNEL_TEE_SUPP_H__

#include <linux/completion.h>
#include <linux/list.h>
#include <linux/mutex.h>
#include <linux/types.h>

struct tee;

/* Direction of one supplicant transfer. */
#define TEE_RPC_ICMD_ALLOCATE	0x1001
#define TEE_RPC_ICMD_FREE	0x1002
#define TEE_RPC_ICMD_INVOKE	0x1003

#define TEE_RPC_BUFFER		0x00000001
#define TEE_RPC_VALUE		0x00000002
#define TEE_RPC_LOAD_TA		0x10000001

#define TEE_RPC_NBR_BUFF	1
#define TEE_RPC_DATA_SIZE	(64)
#define TEE_RPC_BUFFER_NUMBER	5

#define TEE_RPC_STATE_IDLE	0x00
#define TEE_RPC_STATE_ACTIVE	0x01

/* One RPC parameter slot exchanged with the supplicant. */
struct tee_rpc_bf {
	uint32_t type;
	void *data;
};

#ifdef __GENKSYMS__
struct tee_rpc_alloc {
	size_t size;
	void *data;
	void *shm;
};

struct tee_rpc_free {
	void *shm;
};
#else
/* Compiler-only frozen tkcore_drv view; offsets and total sizes are identical. */
struct tee_rpc_alloc {
	u32 size;
	u32 pad;
	void *data;
	struct tee_shm *shm;
};

struct tee_rpc_free {
	struct tee_shm *shm;
};
#endif

struct tee_rpc_cmd {
	union {
		void *buffer;
		uint64_t padding_buf;
	};
	uint32_t size;
	uint32_t type;
	uint32_t reserved;
	uint32_t pad_reserved;
};

struct tee_rpc_invoke {
	uint32_t cmd;
	uint32_t res;
	uint32_t nbr_bf;
	uint32_t pad_nbr;
	struct tee_rpc_cmd cmds[TEE_RPC_BUFFER_NUMBER];
};

/*
 * struct tee_rpc - supplicant channel state hanging off struct tee.
 *
 * PROVEN_SEMANTICS: read/write/poll pairing, one in-flight request at a time,
 * completion-based handshake.  Member spellings SYNTHETIC_ISLAND_NAME.
 */
struct tee_rpc {
	struct tee_rpc_invoke commToUser;
	struct tee_rpc_invoke commFromUser;
	struct mutex thrd_mutex;
	struct mutex outsync;
	struct mutex insync;
	struct mutex reqsync;
	struct completion comp;
	int used;
	int state;
	atomic_t used_slots;
};

/*
 * Deliver one secure-world RPC to the waiting supplicant and block for its
 * answer.  Exported; consumed by tkcore_drv.
 * Prototype shape PROVEN_EXACT from the tkcore_drv call site.
 */
int tee_supp_cmd(struct tee *tee, uint32_t funcid, void *cmd, size_t cmd_size);

int tee_supp_init(struct tee *tee);
void tee_supp_deinit(struct tee *tee);

#endif /* __TRUSTKERNEL_TEE_SUPP_H__ */
