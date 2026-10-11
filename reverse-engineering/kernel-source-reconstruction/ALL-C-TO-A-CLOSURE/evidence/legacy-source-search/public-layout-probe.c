/* SPDX-License-Identifier: GPL-2.0-only
 * Read-only layout probe of the pinned public TKCore header; never a module.
 */
#include <linux/tee_core.h>
#include <linux/stddef.h>
const unsigned long tkcore_public_layout[] = {
 sizeof(struct tee), offsetof(struct tee, priv), offsetof(struct tee, ops),
 offsetof(struct tee, dev), offsetof(struct tee, miscdev), offsetof(struct tee, rpc),
 offsetof(struct tee, lock), offsetof(struct tee, state), offsetof(struct tee, shm_flags),
 sizeof(struct tee_context), offsetof(struct tee_context, refcount),
 sizeof(struct tee_session), offsetof(struct tee_session, sessid), offsetof(struct tee_session, priv),
 sizeof(struct tee_shm), sizeof(struct tee_ops)
};
