/*
 * Copyright (c) 2014, STMicroelectronics International N.V.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License Version 2 as
 * published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 */
#include <linux/module.h>
#include <linux/device.h>
#include <linux/miscdevice.h>
#include <linux/io.h>
#include <linux/vmalloc.h>

#include <trustkernel/tee_client_api.h>
#include <trustkernel/tee_core.h>
#include "tee_ioc.h"

#include "tee_core_priv.h"
#include "tee_shm.h"
#include "tee_supp_com.h"

/*
 * Stock default device node for a NULL context name.  The donor used
 * "opteearmtz00"; tkcore registers tkcore_admin / tkcore_client / tkcore_fp
 * and only the client node is resolvable by name.
 */
#define TEE_TZ_DEVICE_NAME	"tkcore_client"

/*
 * Map an internal negative errno onto a GlobalPlatform result.
 *
 * @verbose reproduces a stock asymmetry: TEEC_InitializeContext() logs the
 * -EINVAL case, TEEC_OpenSession() maps the identical value silently.
 */
static TEEC_Result teec_result_from_errno(int err, bool verbose)
{
	switch (err) {
	case -ENOSPC:
	case -ENOMEM:
		return TEEC_ERROR_OUT_OF_MEMORY;
	case -EINVAL:
		if (verbose)
			pr_err("context->fd is invalid\n");
		return TEEC_ERROR_BAD_PARAMETERS;
	default:
		return TEEC_ERROR_GENERIC;
	}
}

static void reset_tee_cmd(struct tee_cmd_io *cmd)
{
	memset(cmd, 0, sizeof(struct tee_cmd_io));
	cmd->fd_sess = -1;
	cmd->cmd = 0;
	cmd->uuid = NULL;
	cmd->origin = TEEC_ORIGIN_API;
	cmd->err = TEEC_SUCCESS;
	cmd->data = NULL;
	cmd->data_size = 0;
	cmd->op = NULL;
}

TEEC_Result TEEC_InitializeContext(const char *name, TEEC_Context *context)
{
	struct tee *tee;
	struct tee_context *ctx;
	int id;

	if (!context)
		return TEEC_ERROR_BAD_PARAMETERS;

	context->fd = 0;

	strncpy(context->devname, name ? name : TEE_TZ_DEVICE_NAME,
		sizeof(context->devname));

	tee = tee_get_tee(context->devname);
	if (!tee) {
		pr_err("can't get device [%s]\n", name);
		return TEEC_ERROR_ITEM_NOT_FOUND;
	}

	ctx = tee_context_create(tee);
	if (IS_ERR_OR_NULL(ctx)) {
		pr_err("ctx is NULL\n");
		return TEEC_ERROR_BAD_PARAMETERS;
	}

	ctx->usr_client = 0;
	ctx->ctx_priv = NULL;

	/*
	 * The 32-bit identifier is an IDR handle, never a truncated kernel
	 * pointer.  Stock stores the raw allocator result - including a
	 * negative one - before deciding what to report.
	 */
	id = tee_core_alloc_uuid(ctx);
	context->fd = id;
	if (id < 0)
		return teec_result_from_errno(id, true);

	return TEEC_SUCCESS;
}
EXPORT_SYMBOL(TEEC_InitializeContext);

void TEEC_FinalizeContext(TEEC_Context *context)
{
	struct tee_context *ctx;
	size_t len;

	if (!context || !context->fd) {
		/*
		 * Stock formats the context name on this path even when
		 * @context is NULL, which faults.  The island keeps the same
		 * single diagnostic but refuses to dereference NULL:
		 * DOCUMENTED DIVERGENCE.
		 */
		const char *nm = "";

		if (context) {
			len = strnlen(context->devname,
				      sizeof(context->devname));
			nm = (len == sizeof(context->devname))
				     ? "[invalid]" : context->devname;
		}
		pr_err("can't release context %p:[%s]\n", context, nm);
		return;
	}

	ctx = tee_core_uuid2ptr(context->fd);
	if (!ctx) {
		pr_err("bad context->fd %d provided\n", context->fd);
		return;
	}

	tee_core_free_uuid(context->fd);
	tee_context_destroy(ctx);
}
EXPORT_SYMBOL(TEEC_FinalizeContext);

TEEC_Result TEEC_OpenSession(TEEC_Context *context,
			     TEEC_Session *session,
			     const TEEC_UUID *destination,
			     uint32_t connectionMethod,
			     const void *connectionData,
			     TEEC_Operation *operation,
			     uint32_t *return_origin)
{
	TEEC_Operation dummy_op;
	struct tee_cmd_io cmd;
	struct tee_session *sess;
	struct tee_context *ctx;
	uint32_t origin;
	int id;

	if (!operation) {
		/*
		 * The code here exist because Global Platform API states that
		 * it is allowed to give operation as a NULL pointer.
		 * In kernel and secure world we in most cases don't want
		 * this to be NULL, hence we use this dummy operation when
		 * a client doesn't provide any operation.
		 */
		memset(&dummy_op, 0, sizeof(TEEC_Operation));
		operation = &dummy_op;
	}

	if (!context || !session || !destination)
		return TEEC_ERROR_BAD_PARAMETERS;

	session->fd = 0;

	ctx = tee_core_uuid2ptr(context->fd);
	if (!ctx) {
		pr_err("bad context_fd %d provided\n", context->fd);
		if (return_origin)
			*return_origin = TEEC_ORIGIN_COMMS;
		return TEEC_ERROR_BAD_PARAMETERS;
	}

	reset_tee_cmd(&cmd);
	cmd.op = operation;
	cmd.uuid = (TEEC_UUID *) destination;

	sess = tee_session_create_and_open(ctx, &cmd);
	if (IS_ERR_OR_NULL(sess)) {
		if (return_origin)
			*return_origin = cmd.origin ? cmd.origin
						    : TEEC_ORIGIN_COMMS;
		return cmd.err ? cmd.err : TEEC_ERROR_COMMUNICATION;
	}

	origin = cmd.origin;
	id = tee_core_alloc_uuid(sess);
	session->fd = id;
	if (id < 0) {
		tee_session_close_and_destroy(sess);
		if (return_origin)
			*return_origin = TEEC_ORIGIN_COMMS;
		return teec_result_from_errno(id, false);
	}

	if (return_origin)
		*return_origin = origin;

	return cmd.err;
}
EXPORT_SYMBOL(TEEC_OpenSession);

void TEEC_CloseSession(TEEC_Session *session)
{
	struct tee_session *sess;

	if (!session || !session->fd)
		return;

	sess = tee_core_uuid2ptr(session->fd);
	if (!sess) {
		pr_err("bad session_id %d provided\n", session->fd);
		return;
	}

	tee_core_free_uuid(session->fd);
	tee_session_close_and_destroy(sess);
}
EXPORT_SYMBOL(TEEC_CloseSession);

TEEC_Result TEEC_InvokeCommand(TEEC_Session *session,
			       uint32_t commandID,
			       TEEC_Operation *operation,
			       uint32_t *return_origin)
{
	int ret = 0;
	struct tee_cmd_io cmd;
	struct tee_session *sess;

	if (!session || !operation || !return_origin || !session->fd)
		return TEEC_ERROR_BAD_PARAMETERS;

	/*
	 * Handle resolution only.  The command path itself is NOT part of
	 * Phase 3A-R; this keeps the identifier type consistent with the IDR
	 * handles now issued by TEEC_OpenSession().
	 */
	sess = tee_core_uuid2ptr(session->fd);
	if (!sess)
		return TEEC_ERROR_BAD_PARAMETERS;
	reset_tee_cmd(&cmd);
	cmd.cmd = commandID;
	cmd.op = operation;

	ret = tee_session_invoke_be(sess, &cmd);
	if (ret) {
		if (cmd.origin)
			*return_origin = cmd.origin;
		else
			*return_origin = TEEC_ORIGIN_COMMS;
		if (cmd.err)
			return cmd.err;
		else
			return TEEC_ERROR_COMMUNICATION;
	} else {
		*return_origin = cmd.origin;
		return cmd.err;
	}
}
EXPORT_SYMBOL(TEEC_InvokeCommand);

TEEC_Result TEEC_RegisterSharedMemory(TEEC_Context *context,
				      TEEC_SharedMemory *sharedMem)
{
	if (!sharedMem)
		return TEEC_ERROR_BAD_PARAMETERS;

	sharedMem->registered = 1;
	return TEEC_SUCCESS;
}
EXPORT_SYMBOL(TEEC_RegisterSharedMemory);

TEEC_Result TEEC_AllocateSharedMemory(TEEC_Context *context,
				      TEEC_SharedMemory *shared_memory)
{
	struct tee_shm_io shm_io;
	struct tee_context *ctx;
	int ret;
	struct tee_shm *shm;

	if (!context || !context->fd || !shared_memory)
		return TEEC_ERROR_BAD_PARAMETERS;

	/* Handle resolution only; shared memory itself is out of scope. */
	ctx = tee_core_uuid2ptr(context->fd);
	if (!ctx)
		return TEEC_ERROR_BAD_PARAMETERS;

	shm_io.size = shared_memory->size;
	shm_io.flags = shared_memory->flags | TEEC_MEM_KAPI;
	ret = tee_shm_alloc_io(ctx, &shm_io);
	if (ret) {
		pr_err("%s: tee_shm_alloc_io(%zd) failed\n", __func__,
		       shared_memory->size);
		return TEEC_ERROR_OUT_OF_MEMORY;
	}

	shared_memory->registered = 0;
	shared_memory->flags = shm_io.flags;
	shared_memory->d.fd = shm_io.fd_shm;

	shm = (struct tee_shm *)(long)shm_io.fd_shm;
	shared_memory->buffer = shm->kaddr;

	pr_debug("%s(%d) => fd=%d, kaddr=%p\n", __func__,
		 shm_io.size, shm_io.fd_shm, (void *)shared_memory->buffer);

	return TEEC_SUCCESS;
}
EXPORT_SYMBOL(TEEC_AllocateSharedMemory);

void TEEC_ReleaseSharedMemory(TEEC_SharedMemory *shared_memory)
{
	struct tee_shm *shm;

	if (!shared_memory || shared_memory->registered)
		return;

	pr_debug("%s (vaddr = %p)\n", __func__, shared_memory->buffer);

	shm = (struct tee_shm *)(long)shared_memory->d.fd;
	tee_shm_free_io(shm);

	shared_memory->buffer = NULL;
	shared_memory->d.fd = 0;
}
EXPORT_SYMBOL(TEEC_ReleaseSharedMemory);
