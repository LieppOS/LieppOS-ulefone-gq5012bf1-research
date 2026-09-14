/* SPDX-License-Identifier: GPL-2.0 */
#ifndef __TEE_LIFECYCLE_PREREQ_H__
#define __TEE_LIFECYCLE_PREREQ_H__

struct tee;

int tee_init_procfs(struct tee *tee);
void tee_exit_procfs(void);

int tee_peridev_init(void);
void tee_peridev_exit(void);

#endif /* __TEE_LIFECYCLE_PREREQ_H__ */
