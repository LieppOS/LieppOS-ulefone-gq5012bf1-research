# GQ5012BF1 — AW36518 userspace / camera contract (Phase 4)

Scan of the stock `vendor`, `system`, `system_ext`, `product` and `odm` trees
for `aw36518`, `flashlight`, `torch`, `strobe`, `duty`, `current`.

## Nothing in userspace names the driver

The only stock files containing the literal `aw36518` are kernel-side:
`vendor_dlkm/lib/modules/{aw36518.ko, aw36518_v2.ko, flashlight.ko,
modules.alias, modules.dep, modules.load}`.  No HAL, no XML/JSON, no property
and no init script references the module, the chip or the sub-device name.
Userspace therefore has **no direct dependency on the module name** — but it
does depend on the flashlight-core device identity the module registers
(`type/ct/part` and the name string, see below).

## Path 1 — MediaTek flashlight character device (the one in use)

* `vendor/etc/init/hw/init.mt6878.rc`:
  `chmod 0660 /dev/flashlight`, `chown system camera /dev/flashlight`.
* `vendor/etc/selinux/vendor_file_contexts`:
  `/dev/flashlight(/.*)?  u:object_r:flashlight_device:s0`.
* `vendor/lib64/mt6878/libcam.hal3a.v3.strobe.so` (and the non-SoC copy) opens
  `/dev/flashlight` from
  `…/aaa/peripheraldriver/strobe/strobe_drv_flashlight.cpp` and
  `strobe_drv_flashlight_fops.cpp`, using the classic MediaTek strobe API:
  `getStrobeHandle(type, ct)`, `setDuty()`, `setTimeOutTime()`,
  `setOnOff(type, enable, scenario, duty, dutylt)`, `setTorchOnOff()`,
  `getCurrentByDuty()`, `getMaxDuty()`, `getTorchLevel()`, `hasFlashHw()`.
* The HAL addresses devices by `(mTypeId, mCtId, mPartId)` — exactly the triple
  the kernel driver takes from the DT child (`0, 0, 1` for AW36518).  The
  duty→current table lives in userspace
  (`libcameracustom.flashlight.so` / `lib3a.flash.so`), which is why the kernel
  side only ever receives absolute µA values or the fixed 250 000 µA torch
  point.
* `vendor/bin/factory` also opens `/dev/flashlight` (factory flash test).

Consequence: the ABI userspace really depends on is
`flashlight_dev_register_by_device_id()` with `type=0, ct=0, part=1,
channel=0, decouple=0`, plus the `FLASH_IOC_SET_ONOFF` handler.  Renaming the
module or changing those DT-derived IDs would break the camera HAL; the
reconstruction preserves all of them.

## Path 2 — Ulefone `yft` torch sysfs

`vendor/etc/init/hw/init.yft.rc`:

```
# flashlight
chmod 0777 sys/devices/virtual/flashlight_core/flashlight/flashlight_contrl
chown system radio sys/devices/virtual/flashlight_core/flashlight/flashlight_contrl
```

`vendor/etc/selinux/vendor_file_contexts` / `vendor_sepolicy.cil` additionally
label `…/flashlight_core/flashlight/flashlight_strobe`,
`…/flashlight_core/flashlight/flashlight_torch` and
`/class/flashlight_core/flashlight_sw_ctrl` as `sysfs_yft_file`.

All of those nodes are created by **`flashlight.ko`**, not by `aw36518.ko`
(`dev_attr_flashlight_torch`, `flashlight_strobe_store`,
`class_attr_flashlight_sw_ctrl` are symbols of `flashlight.ko`).  They reach the
AW36518 through `flashlight_operations.flashlight_strobe_store` /
`flashlight_ioctl`.

The Ulefone-specific coupling is inside the core: `fl_enable()` in
`flashlight.ko` compares the registered device name against
`"aw36518-led0"` (12 chars) and `"aw36518_v2-led0"` (15 chars) and bypasses the
low-battery / over-current disable for them.  **The sub-device name string is
therefore part of the userspace-visible behaviour** and must remain exactly
`aw36518-led0`.

## The driver's own sysfs

`aw36518.ko` creates exactly one attribute on the I²C device:

```
/sys/bus/i2c/devices/8-0063/reg      (0644)
  read  -> "reg0x00 = 0x..\n" … "reg0x0D = 0x..\n" then "\r\n"
  write -> "<reg_hex> <val_hex>"  (sscanf "%x %x") -> regmap_write
```

It is not labelled by the stock SELinux policy and is not used by any stock
userspace component: it is a vendor debug hatch.  It is reproduced because it is
part of the stock ABI (`dev_attr_reg` is byte-identical in the rebuild), and it
is a raw register write path — it must stay root-only in any LieppOS policy.

No debugfs and no procfs entry is created.
