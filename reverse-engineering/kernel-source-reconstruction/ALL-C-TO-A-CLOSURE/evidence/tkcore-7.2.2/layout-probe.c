/* SPDX-License-Identifier: GPL-2.0-only */
/* Read-only layout probe of unchanged TrustKernel 7:2.2 header; never a module. */
#include <linux/tee_tkcore.h>
#include <linux/stddef.h>
const unsigned long tk72_layout[] = {
 sizeof(struct tee), offsetof(struct tee, name), offsetof(struct tee, id),
 offsetof(struct tee, version), offsetof(struct tee, log),
 offsetof(struct tee, priv), offsetof(struct tee, ops), offsetof(struct tee, dev),
 offsetof(struct tee, udevs), offsetof(struct tee, rpc), offsetof(struct tee, refcount),
 offsetof(struct tee, stats), offsetof(struct tee, list_ctx), offsetof(struct tee, list_rpc_shm),
 offsetof(struct tee, lock), offsetof(struct tee, state), offsetof(struct tee, shm_flags),
 offsetof(struct tee, conf),
 sizeof(struct tee_context), offsetof(struct tee_context, refcount), offsetof(struct tee_context, config),
 sizeof(struct tee_session), sizeof(struct tee_shm), sizeof(struct tee_ops)
};
