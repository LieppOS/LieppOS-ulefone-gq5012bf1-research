/* SPDX-License-Identifier: GPL-2.0 */
#ifndef TK_TEE_WAIT_QUEUE_H
#define TK_TEE_WAIT_QUEUE_H
#include <linux/mutex.h>
#include <linux/list.h>
struct device;
struct tee_wait_queue_private {
	struct mutex mu;
	struct list_head db;
};
#endif
