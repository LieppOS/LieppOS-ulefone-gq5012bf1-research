# Hynitron rear-touch reconstruction

# Final classification

**STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE**

# FROZEN status

**FROZEN FOR RE: YES**. Static stock-oracle reconstruction, exact-GKI build,
stock-provider ABI, downstream-consumer ABI and fail-closed verifier are closed.
Runtime testing remains separate integration validation.

# Stock oracle

Canonical `vendor_dlkm/lib/modules/hynitron.ko`, 142,528 bytes, SHA256
`860f28409fdd59458640cd067fec6eb83f3e5ec00ca12782c0e152323a351fb6`,
Build ID `2defd559d61e657b6f1bd9712d48c6f403e8514d`, Android clang 17.0.2
(build 10087095), vermagic
`6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`.
The sole extracted copy is frozen at
`workspace/phase4-hynitron/oracle/hynitron.stock.ko`; placement/config evidence
is in `phase4-hynitron-stock-oracle.txt`.

# Source provenance

No exact Ulefone/YFT source was found. The strongest public source is LineageOS
AYN qcs8550 modules commit `a552fac8fae2c65b7e2e1f3a42e4580732659a6c`,
which shares 63/65 identifiers but has a different Qualcomm framework/config
and no Ulefone exports. It remains **STRUCTURAL_DONOR_ONLY**. Final source is a
stock-oracle clean-room reconstruction at
`workspace/phase4-hynitron/reconstruction-source/` and mirrored to
`/home/armol/kernel-work/gki-12901745-workspace/lieppos/hynitron-recon/`.

# RED

Unmodified donor plus harness failed exact-GKI compilation on obsolete remove
callback/API assumptions before producing a module. The pre-edit mismatch,
source/function deltas and feature differences are frozen in
`phase4-hynitron-RED.md`; no behavioral source edit preceded RED.

# Function inventory

Stock and rebuild each define **65 functions**; sets are 65 shared, zero
stock-only and zero rebuild-only. Nine are size-identical and eight are byte-identical; 63/63
applicable KCFI IDs are exact. The two local direct-only functions do not emit a
KCFI preamble and are N/A. Full stock inventory and row parity are
`phase4-hynitron-functions.tsv` and `phase4-hynitron-function-parity.tsv`.

# Import ABI

All **54** imported symbol/CRC pairs are exact: 51 kernel/loader edges plus
three stock yft_devinfo edges. There are no extra imports, missing imports or
CRC mismatches. See `phase4-hynitron-imports.tsv` and modversions TSV.

# yft_devinfo provider ABI

The final build uses the frozen real-stock provider witness, never reconstructed
yft_devinfo: `second_touch_fw_version` `0x7198d58d`,
`yft_touchpanel_device_add` `0xf5ba4446`, and
`yft_set_touch_device_used` `0x0a0f3b69`. Calls, types, KCFI and lifecycle are
closed in `phase4-hynitron-yft-devinfo-provider-abi.md`.

# Export / consumer ABI

Natural genksyms exports are exact:

- `tiny_tp_gesture_contorl`: `0x4e4b7919`
- `tiny_tp_power_contorl`: `0xfcc94fc7`

Both are `void(int)` with KCFI `0x019c0cac`. Stock
`spi_tiny_co5300_lcd.ko` requires exactly those CRCs, so 2/2 consumer edges
accept the rebuilt provider without modification. See export parity and
stock-consumer verification.

# Device-tree contract

Live path `/soc/i2c@11c20000/hynitron@15`, compatible
`hynitron,hyn_ts`, status okay, reg 0x15, bus 400 kHz. Consumed custom
properties are GPIOs, 340x340 coordinates and one contact; absent generic donor
properties are not invented. Full present-vs-consumed separation is in the DT
contract.

# Controller identity

The configured/fitted device is **CST820**, chip type `0x00b7`, CST8xx series
800 at 0x15. Embedded selection also supports CST816D `0xb6` and CST816T
`0xb5`; generic tables contain legacy families but do not prove those fitted.
Runtime A6 fields remain read values rather than invented constants.

# I2C/register contract

Stock send-then-receive framing, short-transfer behavior, legacy two-retry
helpers, endianness and all observed registers are closed in the I2C contract
and register-map TSV. Hardware-significant CST820 registers are 0x00 touch,
0xe5 sleep, 0xa6 firmware info, 0xa001/0xa003 ROM-presence handshake, 0xd3
gesture and 0xec gesture mode. No live operation was executed.

# Hardware topology

Rear touch is I2C0/0x15 paired with the SPI CO5300 rear mini display. GPIO 11
is interrupt, GPIO 32 reset and GPIO 119 VDD enable. Hynitron owns these GPIOs;
LCD coordination uses the two exported calls.

# Touch/input ABI

`hyn_ts`, BUS_I2C, direct type-A MT, one contact, X/Y 0..340,
tracking 0..1, touch-major 0..255, width-major 0..200, BTN_TOUCH. Exact nine-byte
CST820 decoding and input-event ordering are in `phase4-hynitron-input-contract.md`
and corroborated by the live InputReader snapshot.

# IRQ contract

GPIO11 resolves to live IRQ56. Stock requests a falling-edge ONESHOT threaded
IRQ named `Hynitron Touch Int`; the thread disables IRQ and queues one work item.
Work reads/reports then reenables. Probe enables IRQ wake once; gesture mode
uses type flags `0x4002` (falling plus NO_SUSPEND), and normal mode restores the
DT/request flags. Exact transitions are closed in the IRQ contract.

# GPIO/reset/power contract

All GPIO numbers, active-high flags, direction, low-reset/high-run sequence and
20/40 ms delays are documented. The export does not drive VDD or LCD GPIOs.
Late stock failures may free an asserted VDD GPIO without first driving low;
this quirk is preserved.

# Gesture export contract

`tiny_tp_gesture_contorl` is a binary cached policy toggle with no immediate
hardware access. Display-off power-control uses it to choose deep sleep versus
0xec gesture mode/wake IRQ. IDs, 0xd3 packet and key mappings are fully listed
in the gesture contract.

# Power export contract

`tiny_tp_power_contorl` is a void, idempotent binary transition guarded by the
singleton/suspended cache. Off selects reset+deep-sleep+IRQ-off or gesture scan;
on resets, releases touch and restores normal IRQ. Exact ordering and consumer
calls are closed in the power-export/consumer documents.

# Private state

Stock allocation is 584 bytes; all proven offsets, three globals and UNKNOWN
gaps are in `phase4-hynitron-struct-layout.md`. The private binary layout is not
an external ABI; reconstruction uses a semantic structure.

# Probe contract

Allocation/publication, DT, GPIO/rail/reset, normal identity with bootloader-only fallback, input, workqueue, IRQ, non-fatal identity/table re-read, sysfs/gesture, final reset and YFT-used order are closed.
Failure labels, errno propagation, resource state and stock quirks are recorded
in `phase4-hynitron-probe-contract.md`.

# Firmware/update engine

Two exact embedded objects are preserved: 15,419-byte CST816D-family image
SHA256 `0566ea7799d6f8bbce026639d9dbb89f0e629ab533d1d90e4901c81d5611e1d8`
and 15,410-byte CST816T image SHA256
`0d02fde67223c1e7aa6c4ce1d1e522bcbe79d4d58decf1aa79b865cb2e504de3`.
Static call/relocation proof shows this stock ELF has sysfs-triggered image selection and fallback bootloader detection but **no linked erase/program/status/checksum programming routine**. Therefore no donor programmer is invented. Full negative proof,
metadata and selection are in the firmware report.

# YFT registry behavior

Candidate-add occurs at module init with used=0; successful probe marks
`"hyn_ts"` used=1. A6 fields format `second_touch_fw_version` as
`Vno: fw. checksum. module. project.`. Return values are ignored; removal does
not clear registry.

# Userspace ABI

`/sys/hynitron_debug` contains seven 0644 attributes: firmware version/update,
raw-register, app-upgrade, factory, gesture mode and gesture buffer. Base and
gesture groups, formats/parsers and side effects are inventoried. No procfs,
debugfs, misc or ioctl ABI exists.

# Userspace/factory consumers

No dedicated Hynitron app/service/overlay/SELinux/IDC consumer was found.
`init.touch.rc` is the on-demand load edge; Android generic InputReader consumes
`hyn_ts`. Kernel exports are consumed only by the stock tiny-LCD module.

# PM / wake

There are no stock I2C `dev_pm_ops` or display-notifier callbacks. Tiny-LCD
exports coordinate active, deep-sleep and gesture-wake states. Resume does not
redetect or update firmware.

# Async behavior

One workqueue/work item services the threaded IRQ. No delayed work, timer,
hrtimer, kthread, completion or firmware worker exists. Scheduling,
cancellation and IRQ interaction are in the async contract.

# Lifecycle

Module init/exit, probe/remove, work/IRQ/input/sysfs/GPIO cleanup and absent
shutdown callback are closed in the lifecycle report. YFT state and firmware
string are not cleared on remove, matching stock.

# Exact-GKI build

`./tools/bazel build //lieppos/hynitron-recon:hynitron_recon` against
`//common:kernel_aarch64`: BUILD_RC 0, compiler warnings 0, modpost warnings 0,
unresolved symbols 0. Rebuild SHA256 is
`26522dc090fc6a57cf45ed841755a8ef267c83f43f511433439f1392e2ba438a`.

# Function parity

65/65 names; nine size-identical and eight byte-identical; 63/63 applicable
KCFI exact. Nonidentical rows are semantic clean-room codegen differences, not
unexplained hardware residuals.

# Object parity

Firmware arrays are byte-identical. I2C/OF/ID tables, attributes, gesture/input
metadata, state and module sections are byte-, relocation-, or
semantic-equivalent as classified in `phase4-hynitron-object-parity.tsv`.
No hardware-significant object is UNRESOLVED.

# Stock-consumer verification

Stock `spi_tiny_co5300_lcd.ko` requires and accepts both rebuilt export CRCs.
That module remains the next separate target and is not marked done.

# Behavioral verifier

`kernel/scripts/phase4_hynitron_verify_recon.py` fails closed and reports
**34/34 CHECKS PASSED**.

# Residuals

No unexplained hardware-significant residual. Binary/CFG differences in 57
functions are documented semantic reconstruction differences. Exact running A6
version bytes are runtime values, not reconstruction residuals.

# Runtime-validation status

Not performed; explicitly separate integration validation. All research was
static/offline and made no on-device writes, resets, power/IRQ changes, binding,
module load, flash, reboot, DT or NVRAM changes.

# Safety

`HYNITRON_ALLOW_FW_PROGRAMMING=0` is default in both source and exact build.
There is no programmer to invoke; opt-in returns `-ENOSYS`. Firmware images and
selection remain preserved rather than deleted.

# Evidence index

Stock inventories, disassemblies and sections are under
`workspace/phase4-hynitron/{oracle,raw}/`; firmware, donor RED, rebuild and
source are under sibling directories. All named `kernel/phase4-hynitron-*`
contracts and parity TSVs are authoritative indices.

# Final verdict

The Hynitron rear-touch module is source-reconstructed, exact on stock import
and downstream export ABI, behaviorally closed for GQ5012BF1, clean-built
against exact GKI, verifier-passing, and **FROZEN FOR RE**. Only stock runtime
integration validation remains; `spi_tiny_co5300_lcd` itself is not done.
