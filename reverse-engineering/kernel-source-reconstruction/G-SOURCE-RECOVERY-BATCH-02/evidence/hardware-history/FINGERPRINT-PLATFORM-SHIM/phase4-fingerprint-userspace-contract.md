# Fingerprint userspace / HAL relation

## Layer boundary

```text
Android biometrics framework
  -> vendor AIDL fingerprint service / MicroArray HAL
  -> /dev/madev0 and TrustKernel client library/TA
  -> microarray_fp_tee.ko (sensor, character device, IRQ, SPI/TEE boundary)
  -> fingerprint.ko (YFT board pinctrl/DT provider only)
```

`fingerprint.ko` has no character-device, file-operation, SPI-transfer, TEE,
TrustKernel, ioctl, sysfs, regulator, or Android binder imports. It is not the
HAL-facing sensor driver and performs no secure-world operation.

## Stock selectors and artifacts

- `system/build.prop`:
  `persist.vendor.fingerprint.chip=microarray_tee_back`
- AIDL service binary:
  `/vendor/bin/hw/android.hardware.biometrics.fingerprint-service.example`
  contains `Fingerprint HAL started - Microarray`, `microarray.fingerprint`,
  and default-MicroArray AIDL source paths.
- HAL module:
  `/vendor/lib64/hw/microarray.fingerprint.default.so`
- vendor client/TEE library:
  `/vendor/lib64/libfprint-x64.so`; contains `/dev/madev0`, `TEEC_*`, and
  TrustKernel/MicroArray strings.
- TA artifact:
  `/vendor/app/t6/edcf9395-3518-9067-614cafae2909775b.ta`
- `init.fingerprint.rc` grants system access to `/dev/madev0` at boot and
  post-fs-data.
- `ro.yft_trustkernel_tee_support=1` is present in system properties.

The generic example VINTF manifest exposes
`android.hardware.biometrics.fingerprint.IFingerprint/virtual`; the matching
rc is disabled and contains a stale/mismatched start name. This is recorded as
stock packaging evidence, not proof that the example instance is the active
production service.

## YFT rc distinction

`init.yft.rc` imports `init.fingerprint.rc`. It also contains a generic UDFPS
permission line for `/sys/bus/platform/drivers/yft_finger/tplcd_pattern`, but
this stock `fingerprint.ko` exposes no sysfs group or `tplcd_pattern` symbol.
That line is variant-common/stale configuration and must not be attributed to
this module.

## Ownership of `/dev/madev0`

`microarray_fp_tee.ko`, not `fingerprint.ko`, implements the MicroArray device
boundary. Static analysis in this task did not open the device or invoke any
active path. All hardware/TEE statements above come from offline stock files.
