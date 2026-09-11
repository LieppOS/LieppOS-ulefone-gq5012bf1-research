# Hynitron mandatory RED

## Frozen donor

Strongest available structural donor: LineageOS
`android_kernel_ayn_qcs8550-modules`, commit
`a552fac8fae2c65b7e2e1f3a42e4580732659a6c`, path
`qcom/opensource/touch-drivers/hynitron`. Frozen verbatim under
`workspace/phase4-hynitron/source-search/ayn-a552fac-hynitron/` with
`PROVENANCE.txt`.

Only the external-module Makefile and `BUILD.bazel` harness were replaced in
the exact-GKI RED copy. No donor C/header behavior was edited.

## Unchanged exact-GKI build

Target: `//lieppos/hynitron-recon/donor-red:donor_red`, kernel build
`//common:kernel_aarch64`.

Result: **BUILD_RC=1**. Clang fails at donor `hynitron_core.c:2160`: donor
`.remove = hyn_remove` has type `int (struct i2c_client *)`, while Linux 6.1.115
expects `void (*)(struct i2c_client *)`. Full log:
`workspace/phase4-hynitron/red/donor-build.log`.

## Stock-versus-donor RED

| Surface | Stock oracle | Unchanged donor | RED |
|---|---|---|---|
| Parsed function population | 65 ELF functions | 194 conservatively parsed C definitions | mismatch |
| Name overlap | authoritative 65 | 60 stock names are definitions; module wrappers and `hyn_remove` parser form aside | structural only |
| KCFI/function sizes | 65 IDs/sizes frozen | no final ELF; build fails | mismatch/unavailable |
| Imports/MODVERSIONs | 54 = 51 kernel/loader + 3 stock yft_devinfo | no final ELF; no YFT integration | mismatch |
| Exports | two `tiny_tp_*_contorl` symbols | neither exists | mismatch |
| Export CRC/KCFI | `0x4e4b7919`, `0xfcc94fc7`; both KCFI `0x019c0cac` | absent | mismatch |
| DT identity | `hynitron,hyn_ts`, I2C0/0x15, Ulefone GPIO properties | generic donor values/defaults, no GQ5012BF1 node | mismatch |
| Probe/GPIO | raw MTK GPIO API and YFT registration | different platform assumptions; incompatible remove callback | mismatch |
| Touch | one contact, 340x340 on fitted DT | donor configured CST148, 600x1024 defaults, up to five points | mismatch |
| Firmware | two embedded 15.4-KiB CST816D/T images | no stock images/config entries | mismatch |
| Gesture/PM | stock compiled gesture state machine and tiny-LCD callback | broader generic gesture/PM implementation; no tiny-LCD coordination | mismatch |
| Sysfs | stock compiled five debug/update/factory nodes plus gesture nodes | donor config disables main sysfs and enables a different feature matrix | mismatch |

## RED verdict

The donor is **STRUCTURAL_DONOR_ONLY**. Finding it does not close the module.
Behavioral reconstruction must be driven by relocation-aware stock ELF evidence,
with donor code used only where stock instruction/constant/call evidence agrees.
