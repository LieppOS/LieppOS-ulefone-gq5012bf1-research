/* SPDX-License-Identifier: GPL-2.0 */
/* Phase-3F declaration-only compatibility view over the common authority. */
#ifndef TKCORE_DRV_PHASE3F_ABI_H
#define TKCORE_DRV_PHASE3F_ABI_H

#include <trustkernel/tee_core.h>
#include <trustkernel/tee_clkmgr.h>
#include <trustkernel/tee_shm.h>
#include <trustkernel/tee_supp.h>
#include <trustkernel/tee_wait_queue.h>

/* Frozen source spellings mapped to the same proven offsets. */
#define log_buf log_shm
#define log_size log_shm_len

#define TK_TEE_OFFLINE TEE_OFFLINE
#define TK_TEE_ONLINE TEE_ONLINE
#define TK_TEE_SUSPENDED TEE_SUSPENDED
#define TK_TEE_RUNNING TEE_RUNNING
#define TK_TEE_CRASHED TEE_CRASHED
#define TK_TEE_CONF_FW_NOT_CAPABLE TEE_CONF_FW_NOT_CAPABLE
#define TK_TEE_SHM_MAPPED TEE_SHM_MAPPED
#define TK_TEE_SHM_TEMP TEE_SHM_TEMP
#define TK_TEE_SHM_FROM_RPC TEE_SHM_FROM_RPC
#define TK_TEE_SHM_REGISTERED TEE_SHM_REGISTERED
#define TK_TEE_SHM_MEMREF TEE_SHM_MEMREF
#define TK_TEE_SHM_CACHED TEE_SHM_CACHED

#define TK_TEE_RPC_ICMD_ALLOCATE TEE_RPC_ICMD_ALLOCATE
#define TK_TEE_RPC_ICMD_FREE TEE_RPC_ICMD_FREE
#define TK_TEE_RPC_ICMD_INVOKE TEE_RPC_ICMD_INVOKE

#endif /* TKCORE_DRV_PHASE3F_ABI_H */
