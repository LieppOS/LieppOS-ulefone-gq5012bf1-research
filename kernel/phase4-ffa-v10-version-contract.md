# ffa_v10 protocol-version contract

**Advertised/required version: FF-A v1.0, hard-coded — this is the entire
reason the module is named `ffa_v10`.**

```c
#define FFA_DRIVER_VERSION	FFA_VERSION_1_0
#define FFA_MIN_VERSION		FFA_VERSION_1_0
```

## Negotiation (`ffa_version_check`, called once from `ffa_init`)

```c
ffa_value_t ver = invoke_ffa_fn({ .a0 = FFA_VERSION, .a1 = FFA_DRIVER_VERSION });
if ((s32)ver.a0 < 0) return -EOPNOTSUPP;
if (ver.a0 < FFA_MIN_VERSION) { pr_info("Incompatible v%d.%d! ..."); return -EINVAL; }
if (ver.a0 > FFA_DRIVER_VERSION) {
	pr_info("Firmware version higher than driver version, downgrading\n");
	ver.a0 = FFA_DRIVER_VERSION;   /* downgrade to what THIS driver understands */
}
pr_info("Driver version %d.%d\n", 1, 0);
pr_info("Firmware version %d.%d found\n", major, minor);
drv_info->version = ver.a0;
```

So the driver always caps its own operation at v1.0 semantics even if the
secure firmware advertises a newer FF-A version - it never negotiates upward.

## Feature discovery

`ffa_features()` wraps the raw `FFA_FEATURES` SMC (used only internally, by
`ffa_set_up_mem_ops_native_flag()` to probe native SMC64 memory-op support -
see memory-contract.md). No consumer on this device calls it directly.

## Partition-info behaviour

`__ffa_partition_info_get()` issues `FFA_PARTITION_INFO_GET`; because the
driver is capped at v1.0, `ffa_partition_info_get()` always assumes the v1.0
response format (fixed-size `struct ffa_partition_info` without the v1.1
`uuid` field) - the `drv_info->version > FFA_VERSION_1_0` check that would
switch response parsing never fires on this device, since `drv_info->version`
is itself clamped to `FFA_VERSION_1_0` by the downgrade path above.

## Direct-message support

Full support, both v1.0 32-bit (`FFA_MSG_SEND_DIRECT_REQ`) and 64-bit
(`FFA_FN64_MSG_SEND_DIRECT_REQ`) - see message-contract.md. `mode_32bit` is
what stock always sets true for every registered partition, because the
`drv_info->version > FFA_VERSION_1_0` guard in `ffa_mode_32bit_set()` never
passes (same v1.0 clamp), so `tkcore_drv`'s FF-A calls are always encoded
32-bit on this device.

## Memory-op support

Present but unused on this device - see memory-contract.md.

## Do not infer from the name alone

The name is confirmed, not assumed: `FFA_DRIVER_VERSION`/`FFA_MIN_VERSION`
are both literally `FFA_VERSION_1_0` in the compiled-in constants, and the
version-check/downgrade logic above is what actually enforces v1.0-only
behaviour at runtime, independent of what secure firmware advertises.
