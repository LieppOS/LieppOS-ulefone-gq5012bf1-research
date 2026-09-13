# ffa_v10 message transport ABI

`tkcore_drv` calls `ffa_dev->ops->msg_ops->sync_send_receive(ffa_dev, &data)`.
Full contract, proven from stock source + kCFI:

```c
struct ffa_msg_ops {
	void (*mode_32bit_set)(struct ffa_device *dev);
	int (*sync_send_receive)(struct ffa_device *dev,
				 struct ffa_send_direct_data *data);
};

static int ffa_sync_send_receive(struct ffa_device *dev,
				 struct ffa_send_direct_data *data)
{
	return ffa_msg_send_direct_req(drv_info->vm_id, dev->vm_id,
				       dev->mode_32bit, data);
}

struct ffa_send_direct_data {
	unsigned long data0;   /* -> w3/x3 */
	unsigned long data1;   /* -> w4/x4 */
	unsigned long data2;   /* -> w5/x5 */
	unsigned long data3;   /* -> w6/x6 */
	unsigned long data4;   /* -> w7/x7 */
};
```

## `ffa_msg_send_direct_req` (the real transport call)

```c
static int ffa_msg_send_direct_req(u16 src_id, u16 dst_id, bool mode_32bit,
				   struct ffa_send_direct_data *data)
{
	ffa_value_t ret, args = {
		.a0 = mode_32bit ? FFA_MSG_SEND_DIRECT_REQ : FFA_FN64_MSG_SEND_DIRECT_REQ,
		.a1 = PACK_TARGET_INFO(src_id, dst_id),
		.a2 = 0,
		.a3 = data->data0, .a4 = data->data1,
		.a5 = data->data2, .a6 = data->data3, .a7 = data->data4,
	};

	invoke_ffa_fn(args, &ret);

	while (ret.a0 == FFA_INTERRUPT)
		invoke_ffa_fn((ffa_value_t){ .a0 = FFA_RUN, .a1 = ret.a1 }, &ret);

	if (ret.a0 == FFA_ERROR)
		return ffa_to_linux_errno((int)ret.a2);

	if (ret.a0 == FFA_MSG_SEND_DIRECT_RESP ||
	    ret.a0 == FFA_FN64_MSG_SEND_DIRECT_RESP) {
		data->data0 = ret.a3; data->data1 = ret.a4;
		data->data2 = ret.a5; data->data3 = ret.a6; data->data4 = ret.a7;
		return 0;
	}
	return -EINVAL;
}
```

## 32/64-bit behaviour

`dev->mode_32bit` selects `FFA_MSG_SEND_DIRECT_REQ` (SMC32 encoding,
`FFA_SMC_32(0x6F)`) vs `FFA_FN64_MSG_SEND_DIRECT_REQ` (SMC64,
`FFA_SMC_64(0x6F)`). `ffa_mode_32bit_set()` sets this per stock (v1.0-only)
semantics - see version-contract.md.

## Error translation (`ffa_to_linux_errno`)

FF-A `FFA_ERROR` codes are mapped to negative `errno` values
(`NOT_SUPPORTED -> -EOPNOTSUPP`, `INVALID_PARAMETERS -> -EINVAL`,
`NO_MEMORY -> -ENOMEM`, `BUSY -> -EBUSY`, `DENIED -> -EACCES`,
`RETRY -> -EAGAIN`, `ABORTED -> -ECANCELED`, unknown -> `-EINVAL`) before the
caller (tkcore_drv's `invoke_tee_ffa`) ever sees it.

## Interrupt handling

`FFA_INTERRUPT` responses are resumed transparently with `FFA_RUN` inside
`ffa_msg_send_direct_req` itself - the caller (tkcore_drv) never sees a
partial/preempted direct-message result, only the final response or error.
This is a **different** preemption path than tkcore_drv's own SMC resume loop
(`do_smc()`'s `0xffff0004`), which applies to the *SMC transport*, not FF-A.

## Proof

`ffa_sync_send_receive` kCFI `0xccb1e6c8` matches stock exactly (function
parity table). `mode_32bit` field offset is invariant across the RED-vs-vendor
delta (same struct in both).
