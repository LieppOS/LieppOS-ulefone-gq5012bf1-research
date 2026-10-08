# Normal-world source-to-userspace and firmware contract

This describes the byte-proven stock kernel implementation. It distinguishes a compiled/exposed interface from evidence that Android successfully exercised it.

## Load and probe

Both modules are in `vendor_dlkm/lib/modules`; stock `modules.load` places `apu_top.ko` at 179 and `apusys.ko` at 180 (one-based), so power support precedes the monolith. `modules.dep` has a direct `apusys -> apu_top` edge; cross-partition depmod adds stock providers `aee_aed`, `mtk_slbc`, `mtk_qos`, `mtk_peak_power_budget`, `mrdump`, and `iommu_debug` plus their transitive dependencies.

`apu_top.ko` supplies APUSYS power/RPC/regulator/OPP/DVFS state and exports the callbacks consumed by `apusys.ko`. `apusys.ko` combines middleware, remoteproc/RPMsg, APUMMU/reviser, EDMA, MDLA, VPU, MVPU, APS, MNOC, logging, exception/recovery, and secure-memory glue. Compiled support for multiple SoC/IP generations is not proof that every path probes on MT6878.

## Main Android ABI

The middleware registers misc device **`/dev/apusys`** (`MDW_NAME="apusys"`). Open allocates a per-file `mdw_fpriv`, initializes its memory/command lists and creates firmware/device sessions. Close marks it inactive, aborts/releases commands, destroys its command-buffer pool and drops the session. Native and compat calls use the same fixed-width-layout handler; there is no middleware `mmap` or `poll` fop.

Four `_IOWR('A', nr, ...)` commands are accepted; other numbers return `-ENOTTY`:

| nr | macro | input/output role |
|---:|---|---|
| 32 | `APU_MDW_IOCTL_HANDSHAKE` | report middleware version, device and memory bitmasks; query per-device count/meta and memory regions |
| 33 | `APU_MDW_IOCTL_MEM` | allocate/free/map/unmap/flush/invalidate MAIN, VLM, LOCAL, SYSTEM/ISP/APU memory; handles are dma-buf FDs and map results include device VA |
| 34 | `APU_MDW_IOCTL_CMD` | run/run-stale/delete/enqueue a graph of subcommands; supplies dma-buf command buffers, adjacency/link data, priority/time/power policy and returns command/fence IDs and execution status |
| 35 | `APU_MDW_IOCTL_UTIL` | power control, user command, and utility information |

The handler allocates `_IOC_SIZE(cmd)`, copies `IOC_IN`, dispatches the exact command value, then copies `IOC_OUT`; copy failures return `-EFAULT`. Fixed `uint32_t`/`uint64_t` members allow the native handler to be the compat handler, but this is a source/layout fact, not a runtime 32-bit-app test.

### Buffer and command lifetime

1. MEM allocation creates an `mdw_mem`, takes a file-private reference, allocates a dma-buf-backed MAIN or ARAM/VLM/local buffer, optionally returns an FD, and tracks it in both device and per-file lists.
2. Import/map resolves the dma-buf FD, creates APUMMU/device mappings, and returns device VA/IOVA. Flush/invalidate are bounded cache operations on that object.
3. CMD copies graph/subcommand descriptors and command-buffer metadata from userspace, validates type/size/direction, pins/maps the referenced buffers, creates a DMA fence, and serializes an MDW message/shared command structure.
4. The RPMsg endpoint submits to APU RV. Handshake selects command protocol v2, v3, or v4 from firmware-reported version and discovers device/memory capabilities; that negotiation is why static source cannot assume one firmware protocol solely from compiled code.
5. Callback/completion updates per-subcommand and command execution info, signals the fence, copies bidirectional/output buffers back, and releases maps/references. Timeout/error paths mark failure and invoke device/firmware recovery; close removes outstanding commands before freeing the file context.

## Auxiliary kernel interfaces

Compiled code can create `edma`, MDLA control, `apusys_apummu`, and `apusys_reviser` character devices plus sysfs/debugfs/proc nodes when their matching platform devices initialize. They are engineering or lower-level IP interfaces; their compiled presence is not evidence shipped Android opens them. The full stock symbol/string ledgers preserve their exact handlers. Debug nodes are not a stable production ABI.

## DT/hardware topology actually present

The merged stock DT has 29 owned declarations, recorded property-for-property in `dt-nodes.tsv`. Device-specific evidence includes:

* APU RV complex `apusys-rv@190e1000` and power controller `apu-top-3@1c000000`;
* `mediatek, apu_mdw`, `mediatek,apu-mdw-rpmsg`, code/data shared-memory nodes;
* APUMMU and APU IOMMU bank references;
* one MDLA core (`/mdla`, `core-num=1`, version `0x68780305`), plus MVPU/EDMA/RPMsg declarations;
* clocks, power, mailbox/interrupt and reserved-memory references resolved in `dt-providers.tsv` where the DT supplies them.

`status=okay` or implicit enablement proves configuration, not successful probe, IRQ servicing, power sequencing or inference.

## Firmware/security boundary

The normal-world driver boots/coordinates an APU RISC-V remote processor, establishes RPMsg endpoints, maps reserved/shared memory, exchanges handshake/command/completion messages, and handles watchdog/exception/coredump/recovery paths. Stock carries `firmware/apusys.img` (SHA-256 `f2c65a3754ffb901d7bc449d857d3a0326c59a79eb128d4834ac0efad32e17d8`, 1,186,192 bytes). Its signed code, model execution algorithms, secure-world services and signing keys are retained binaries outside this source reconstruction. `sapu.ko` remains owned by `GZ-TZ-SYSTEM`.

## Android evidence and unproved runtime

Stock declares APUware services and contains APUware/NeuroPilot/neuron/NNAPI consumers (see `userspace-consumers.tsv`). Together with load lists and DT, this establishes reachability and an intended client stack, **not** a recorded successful probe or inference.

Later authorized hardware testing must capture, without changing firmware or calibration:

1. `dmesg`/uevent evidence that both modules load, all required providers resolve, `apu_top` and MT6878 APU RV probe, firmware authentication/boot and RPMsg handshake succeed;
2. `/dev/apusys` ownership/SELinux label and HAL open, handshake results, negotiated protocol version/device masks, and memory-region report;
3. one known model through the shipped NNAPI/APUware path, with command enqueue, fence completion, result comparison and proof the MDLA/MVPU device—not CPU fallback—executed it;
4. timeout/cancel/process-death cleanup, suspend/resume and controlled recovery evidence;
5. regulator/clock/power-domain transitions, thermal/power-budget interaction and idle return, with no fault/IOMMU/secure-world errors;
6. only after those pass, throughput/power measurements against stock.

No such live action was performed in this offline task.
