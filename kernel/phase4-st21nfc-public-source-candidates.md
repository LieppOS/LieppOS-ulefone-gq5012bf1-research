# ST21 NFC public source candidates

## Exact GQ5012BF1 target

Stock Ulefone module metadata:

- driver: st21nfc
- version: 2.2.0.19
- srcversion: B6AF553DA6B3CC90D31F110

Stock binary analysis identifies additional/newer behavior including:

- st21nfc_ping()
- CORE_RESET_NTF probing/recovery
- st,pidle_active_low
- explicit wakeup_source lifecycle
- expanded probe cleanup
- expanded remove cleanup
- explicit GPIO release
- workqueue destruction

## NothingOSS MT6878 donor

NothingOSS source/rebuild:

- version: 2.2.0.15
- srcversion: 9CDF386295E0F7F1306D932

This source builds successfully against the exact GQ5012BF1 GKI.

47 kernel imports are shared with stock and all 47 CONFIG_MODVERSIONS CRCs
match exactly.

Therefore it remains the primary MT6878 source donor, but it is not the exact
Ulefone ST21 revision.

## Google NFC source candidate

Repository:

  https://android.googlesource.com/kernel/google-modules/nfc

Commit:

  b96ab17cff5ce99738430e7eae0fa73de3f05d92

Public commit date:

  2025-06-07

The commit was used by Android 16 release tags including android-16.0.0_r0.8.

Its ST21 source reports:

  DRIVER_VERSION "2.0.1A"

Therefore it is not the exact Ulefone 2.2.0.19 source.

However it is a useful second source-lineage donor because its source contains
features also fingerprinted in the Ulefone binary, including:

- st,pidle_active_low
- pidle power-state handling
- st_pstate_work workqueue
- related GPIO/power-stat infrastructure

Use this tree as a comparative donor, not as an exact replacement.

## Current reconstruction strategy

Use a three-way comparison:

1. NothingOSS ST21 2.2.0.15
   - primary MT6878-compilable source donor

2. Google ST21 2.0.1A lineage
   - additional public implementation reference

3. Ulefone unstripped ST21 2.2.0.19 binary
   - exact behavioral and ABI target

Only functionality absent from both public source donors should require
binary-assisted reconstruction.


## Stock module debug metadata

The stock GQ5012BF1 st21nfc.ko was inspected for recoverable debug/type
metadata.

Present:

- .symtab
- .strtab
- .rodata
- .rodata.str1.1

Absent:

- .BTF
- all .debug_* DWARF sections

Therefore automatic C type reconstruction through BTF or DWARF is not
available.

However the module is not symbol-stripped. Local function names remain
available in .symtab, including:

- st21nfc_probe
- st21nfc_remove
- st21nfc_ping
- st21nfc_dev_irq_handler
- st21nfc_suspend
- st21nfc_resume
- other internal ST21 functions

This significantly improves binary-assisted source reconstruction despite
the absence of BTF/DWARF.


## st21nfc_ping behavioral reconstruction

The stock 2.2.0.19 st21nfc_ping function has now been reconstructed to a
high-confidence behavioral model from its unstripped symbol, relocations,
assembly and exact rodata strings.

Important findings:

- The function checks the ST21 device_open state first and returns -EBUSY if
  the character device is already open.

- All i2c_transfer_buffer_flags calls pass flags=1. Linux defines I2C_M_RD
  as exactly 0x0001, therefore these operations are I2C reads.

- Before checking for CORE_RESET_NTF the function executes the ST21 double
  reset pulse sequence used by public ST21 sources to exit Quick Boot mode:

    reset low
    msleep(20)
    reset high
    usleep_range(10000, 11000)
    reset low
    msleep(20)
    reset high

- It then performs up to four NCI message-read attempts.

- Each attempt checks IRQ and reads a 3-byte NCI header.

- Leading NFC idle bytes 0x7e are explicitly handled:

    7e XX YY
      -> shift XX YY and read one more header byte

    7e 7e XX
      -> shift XX and read two more header bytes

    7e 7e 7e
      -> treat as stuck-high IRQ / failure

- Payload size comes from the third NCI header byte.

- The function reads exactly that payload length and logs the beginning of
  the complete message.

- Success is detected when the first two NCI header bytes are:

    0x60 0x00

  corresponding to CORE_RESET_NTF.

The probe performs up to three ST21 recovery procedures between ping
attempts, followed by a final ping validation. If that validation still
fails it reports:

  Did not get CORE_RESET_NTF, hardware issue?

The recovery procedure closely matches publicly available ST21NFC_RECOVERY
source and therefore does not need to be reconstructed instruction by
instruction.

Additional stock DT behavior recovered from probe:

  st,pidle_active_low
  i2c-retry

The observed stock-only kernel imports can now be mapped to concrete source
features with high confidence.

Next step:

  construct an isolated 2.2.0.19 reconstruction tree from NothingOSS
  2.2.0.15 and add source deltas incrementally, using the stock module's
  MODVERSIONS import contract as the validation oracle.


## Reconstruction workspace

An isolated ST21 2.2.0.19 reconstruction workspace was created at:

  lieppos/st21nfc-2.2.0.19-recon

Its initial source is byte-identical to the NothingOSS 2.2.0.15 donor.

Initial st21nfc.c SHA256:

  5a9dee31d3c69dae50a0b93f3aff1a06395cfa6749b7cac81386db758062522f

The reconstruction will proceed incrementally.

Planned stages:

  R0  untouched NothingOSS baseline
  R1  ping + probe recovery
  R2  pidle_active_low + i2c-retry
  R3  wakeup_source lifecycle
  R4  cleanup/lifetime differences
  R5  remaining sysfs/API delta

Each stage must:

1. compile against exact GKI 12901745
2. pass modpost
3. retain exact CRCs for shared imports
4. be compared against stock st21nfc.ko
5. reduce or explain the remaining import/function delta

No reconstruction changes will be made directly to the pristine
NothingOSS donor tree.


## R1 first build attempt

The first R1 build did not reach semantic ST21 compilation.

Failure:

  missing terminating '"' character

Root cause:

The one-shot Python transformation used re.sub() with a replacement string
containing an escaped newline. Python regex replacement processing converted
the intended C sequence:

  \n

into a literal newline inside the C string:

  pr_info("%s Recovery Request
  ", __func__);

This was a source-generation/escaping defect, not an ST21 API, GKI, KMI, or
driver reconstruction failure.

The defect was corrected with a literal string replacement. No behavioral
R1 changes were made as part of the fix.

R1 semantic build status remains pending until the corrected source compiles.


## R1 reconstruction result

R1b successfully reconstructs the stock probe-time ST21 ping/recovery
behavior on top of the NothingOSS 2.2.0.15 source.

Build result:

  BUILD PASS

CONFIG_MODVERSIONS versus stock:

  stock symbols:   54
  reconstructed:   51
  common:          47
  stock-only:       7
  recon-only:       4
  CRC mismatches:   0

The import contract did not change during R1 because the reconstructed
ping/recovery logic uses kernel APIs that were already part of the
2.2.0.15 donor contract.

Important structural convergence:

  st21nfc_ping
    R1b:  0x294
    stock: 0x284
    delta: +0x10

  st21nfc_dev_ioctl
    R1b:  0x5a4
    stock: 0x5a0
    delta: +0x04

  st21nfc_probe
    R1b:  0x58c
    stock: 0x674
    delta: -0xe8

The temporary standalone st21nfc_recovery symbol introduced during R1a
was eliminated by reproducing the source-helper/inlining topology inferred
from stock.

Stock contains the literal string:

  st21nfc_recovery

but no standalone ELF symbol. This is consistent with a source-level
recovery helper that was inlined by the compiler.

R1 status:

  compile:          PASS
  modpost:          PASS
  shared KMI CRCs:  47/47 exact
  ping behavior:    reconstructed
  probe recovery:   reconstructed
  source topology:  strongly converged

The remaining large probe-size delta is expected to contain later revision
changes already identified from the stock binary:

- st,pidle_active_low
- i2c-retry
- dedicated wakeup_source lifecycle
- expanded GPIO/workqueue cleanup

Next stage:

  R2 = pidle_active_low + i2c-retry

Expected R2 ABI effect:

  recover device_property_present
  recover of_property_read_variable_u32_array


## R2a result — pidle polarity and i2c-retry

R2a was built from the frozen R1 source and added only strongly evidenced
ST21 2.2.0.19 revision features:

- st,pidle_active_low property support
- pidle_active_low state in struct st21nfc_device
- polarity-aware power-state interpretation
- i2c-retry DT property support

The stock suspend p_idle_last behavior was deliberately preserved because
direct stock disassembly proved st21nfc_suspend still calls gpiod_get_value.

R2a build result:

  BUILD PASS

ABI comparison:

  stock symbols:       54
  reconstructed:       53
  common:              49
  stock-only:           5
  reconstructed-only:   4
  CRC mismatches:       0

R2a recovered exactly the two predicted stock imports:

  0x94a3f9c7 of_property_read_variable_u32_array
  0xd4b590ed device_property_present

This provides strong binary ABI evidence for both reconstructed source
features:

  of_property_read_u32(..., "i2c-retry", ...)
    -> of_property_read_variable_u32_array

  device_property_read_bool(..., "st,pidle_active_low")
    -> device_property_present

No unexpected imports were introduced.

Remaining stock-only symbols:

  destroy_workqueue
  devm_gpiod_put
  pm_wakeup_ws_event
  wakeup_source_register
  wakeup_source_unregister

Remaining reconstructed-only symbols:

  device_set_wakeup_capable
  device_wakeup_enable
  pm_wakeup_dev_event
  sysfs_create_file_ns

R2a status:

  compile:              PASS
  modpost:              PASS
  shared KMI CRCs:      49/49 exact
  i2c-retry:            reconstructed
  pidle_active_low:     reconstructed
  suspend snapshot:     preserved pending exact R2b reconstruction


## R2b — exact suspend/resume delta

Direct stock-vs-R2a disassembly isolated the complete suspend/resume size
difference.

R2a sizes:

  st21nfc_suspend  0x70
  st21nfc_resume   0x98

Stock sizes:

  st21nfc_suspend  0x60
  st21nfc_resume   0x88

Each R2a function contained exactly four additional AArch64 instructions
before the stock-equivalent logic:

  device_may_wakeup(&client->dev)

Stock performs no device_may_wakeup() test.

Its effective conditions are:

  suspend:
    if (st21nfc_dev->irq_enabled)

  resume:
    if (st21nfc_dev->irq_wake_up)

The remainder of the stock pidle logic confirms that 2.2.0.19 still retains:

- p_idle_last
- suspend-time gpiod_get_value()
- resume-time gpiod_get_value()
- raw p_idle_last comparison
- ST21NFC_IDLE / ST21NFC_ACTIVE consistency checks
- queue_work() when reconciliation is required

Therefore stock 2.2.0.19 combines the newly recovered pidle_active_low
power-stat handling with the older suspend/resume snapshot mechanism.

This is a binary-proven divergence from the compared Google public ST21
source.


## R3 wakeup-source reconstruction evidence

Stock 2.2.0.19 uses a dedicated struct wakeup_source rather than the
device-level wakeup mechanism present in the older public ST21 lineage.

Binary evidence:

- wakeup-source pointer stored at struct offset 0x208
- probe calls:
    wakeup_source_register(NULL, "st21nfc")
- IRQ handler:
    checks wakeup-source pointer
    fires wake event for exactly 500 ms
    compiled import: pm_wakeup_ws_event
- remove:
    wakeup_source_unregister()
    then clears the pointer

The stock registration-name relocation points to the literal:

  st21nfc

Older public Google/ST21 source instead uses device_may_wakeup() plus
pm_wakeup_event(), so the dedicated wakeup-source lifecycle is a later
revision delta and is not inherited blindly from the public donor.


### R3 verified result

R3 build completed successfully.

MODVERSION comparison:

  stock symbols:        54
  reconstructed:        53
  common:               52
  stock-only:            2
  reconstructed-only:    1
  CRC mismatches:        0

Recovered stock wakeup imports:

  0x8be45c3b wakeup_source_register
  0xb511937b wakeup_source_unregister
  0x43b33a8d pm_wakeup_ws_event

Removed donor-only wakeup imports:

  device_set_wakeup_capable
  device_wakeup_enable
  pm_wakeup_dev_event

st21nfc_dev_irq_handler size:

  reconstructed: 0x8c
  stock:         0x8c

Remaining ABI delta:

  stock-only:
    destroy_workqueue
    devm_gpiod_put

  reconstructed-only:
    sysfs_create_file_ns


### R4a verified result

Removed the redundant standalone sysfs_create_file(power_stats) call.

The power_stats attribute remains in st21nfc_attrs and therefore continues
to be created through sysfs_create_group(), matching stock behavior.

Verified MODVERSION result:

  stock symbols:        54
  reconstructed:        52
  common:               52
  stock-only:            2
  reconstructed-only:    0
  CRC mismatches:        0

No reconstructed-only imports remain.

Remaining stock-only imports:

  destroy_workqueue
  devm_gpiod_put


## R4b — complete stock MODVERSION contract recovered

R4b reconstructed the remaining explicit cleanup behavior:

- destroy_workqueue()
- devm_gpiod_put() probe failure paths
- devm_gpiod_put() remove paths

Verified result:

  stock symbols:        54
  reconstructed:        54
  common:               54
  stock-only:            0
  reconstructed-only:    0
  CRC mismatches:        0

  MODVERSION CONTRACT: EXACT MATCH

Key function sizes:

  function                   reconstructed   stock
  st21nfc_dev_irq_handler     0x8c           0x8c
  st21nfc_pstate_wq           0x1ac          0x1ac
  st21nfc_remove              0xc0           0xc0
  st21nfc_suspend             0x60           0x60
  st21nfc_resume              0x88           0x88
  st21nfc_probe               0x654          0x674

Therefore the complete kernel-facing ABI/import contract of the stock
GQ5012BF1 ST21NFC 2.2.0.19 module has been reconstructed against the exact
stock Android 14-11 GKI ABI.

This does not yet prove complete source/behavioral equivalence. Structural
differences remain, most visibly a 0x20-byte probe size delta.


## R5a — release IRQ teardown recovered

Stock st21nfc_release() performs real IRQ teardown before clearing
device_open:

- checks irq_is_attached
- disables IRQ under irq_enabled_lock
- devm_free_irq()
- clears irq_is_attached
- clears device_open

After reconstruction:

  reconstructed release: 0x8c
  stock release:         0x8c

MODVERSION contract remains exact:

  54 / 54 common
  0 stock-only
  0 reconstructed-only
  0 CRC mismatches

The release disassembly also exposed the stock struct layout:

  irq_enabled      +0x204
  irq_wake_up      +0x205
  wake_source      +0x208
  irq_is_attached  +0x210
  device_open      +0x211
  irq_enabled_lock +0x214

The current reconstructed source has irq_is_attached/device_open before
wake_source, producing incorrect offsets. R5b corrects this field order.


## R5b — stock struct topology recovered

R5b reordered the IRQ/wakeup fields to match the stock binary layout.

Verified stock/reconstructed offsets:

  irq_enabled      +0x204
  irq_wake_up      +0x205
  wake_source      +0x208
  irq_is_attached  +0x210
  device_open      +0x211
  irq_enabled_lock +0x214

Evidence from reconstructed release():

  irq_is_attached  file-relative access => struct +0x210
  device_open      file-relative access => struct +0x211
  irq_enabled_lock file-relative access => struct +0x214

Evidence from reconstructed IRQ handler:

  wake_source      +0x208
  irq_enabled      +0x204
  irq_enabled_lock +0x214

The reconstructed release remains 0x8c, identical to stock.

MODVERSION contract remains exact:

  54 / 54 common
  0 stock-only
  0 reconstructed-only
  0 CRC mismatches

Remaining visible structural differences include:

  st21nfc_dev_ioctl:
    reconstructed 0x5a4
    stock         0x5a0

  st21nfc_ping:
    reconstructed 0x294
    stock         0x284

  st21nfc_probe:
    reconstructed 0x654
    stock         0x674

Stock also retains a standalone st21nfc_disable_irq symbol of size 0x60,
while the reconstructed build currently inlines all instances.


## R5c pre-build evidence — disable_irq call topology

Explicit-range disassembly proved that stock contains exactly one direct
call to the standalone st21nfc_disable_irq() function.

The direct call occurs in the ST21 recovery path in st21nfc_dev_ioctl(),
immediately after successful devm_request_irq() and setting
irq_is_attached=true.

Stock direct-call count:

  st21nfc_disable_irq: 1

Other disable-IRQ users compile as inline lock / disable_irq_nosync /
state-clear / unlock sequences.

R5c reconstructs this topology using an always-inline implementation for
those callers and a stock-named standalone helper used only by recovery.


## R5c — stock disable_irq call topology recovered

R5c reconstructed the stock st21nfc_disable_irq topology.

Verified:

  reconstructed st21nfc_disable_irq: 0x60
  stock st21nfc_disable_irq:         0x60

Exactly one direct call exists in both binaries. It occurs in the
ST21 recovery path inside st21nfc_dev_ioctl().

Other callers retain inline IRQ-disable logic.

Functions still exact after R5c:

  st21nfc_dev_irq_handler  0x8c
  st21nfc_release          0x8c
  st21nfc_poll             0xf4
  st21nfc_suspend          0x60
  st21nfc_resume           0x88

MODVERSION contract remains exact:

  54 / 54 common
  0 stock-only
  0 reconstructed-only
  0 CRC mismatches

R5c exposes a cleaner ioctl delta:

  reconstructed ioctl: 0x578
  stock ioctl:         0x5a0
  delta:               0x28 bytes

The stock direct disable_irq call occurs at ioctl +0x3f4.
The reconstructed direct call occurs at ioctl +0x3ec.

Therefore only 0x08 of the remaining delta is before the disable_irq call;
approximately 0x20 is after it. The remaining ioctl discrepancy is not
explained by disable_irq topology.


## R5d — ioctl residual-delta localization

After R5c:

  reconstructed ioctl: 0x578
  stock ioctl:         0x5a0
  residual delta:      0x28

Ordered external-call comparison identified four additional stock call
sites:

  _printk
  mutex_unlock
  _printk
  mutex_unlock

The first missing printk occurs inside the recovery sequence after reset
is driven high and before the following 20 ms delay.

Stock also contains a dedicated mutex_unlock call immediately after the
successful recovery IRQ re-request / st21nfc_disable_irq path, whereas
the reconstruction currently branches to a shared unlock tail.

This indicates that the remaining ioctl delta consists largely of missing
logging and source control-flow topology rather than additional kernel ABI
requirements.

MODVERSION contract remains 54/54 exact.


## R5d — ioctl-local recovery sequence reconstructed

Binary evidence showed that the stock userspace recovery path is compiled
inside st21nfc_dev_ioctl rather than sharing the reconstructed
st21nfc_recovery helper used for probe-time recovery.

R5d reconstructed that ioctl-local sequence, including:

- explicit IRQ teardown
- reset / IRQ pulse sequence
- "%s done Pulse Request" log
- continued IRQ restoration after gpiod_direction_input failure
- dedicated devm_request_irq failure handling
- branch-specific irq_dir_mutex unlocks
- direct st21nfc_disable_irq call on recovery success

Verified sizes:

  st21nfc_dev_ioctl:
    R5c   0x578
    R5d   0x588
    stock 0x5a0

  residual ioctl delta: 0x18

Still exact:

  st21nfc_disable_irq      0x60
  st21nfc_dev_irq_handler  0x8c
  st21nfc_release          0x8c

MODVERSION contract remains exact:

  stock:          54
  reconstructed:  54
  common:         54
  stock-only:      0
  recon-only:      0
  CRC mismatches:  0


## R5e evidence — ioctl request_irq failure return topology

R5d versus stock ordered-call comparison showed only two residual stock
calls:

  _printk
  mutex_unlock

The residual st21nfc_dev_ioctl size delta was exactly:

  R5d:  0x588
  stock: 0x5a0
  delta: 0x18

Disassembly localized these calls to the devm_request_irq failure path.

Stock does not funnel this failure through the normal switch-case ret/break
tail. Instead it performs:

  printk("%s : devm_request_irq failed", __func__)
  mutex_unlock(&st21nfc_dev->irq_dir_mutex)
  return -ENODEV

The stock block returns through the direct function-return path, while R5d
used:

  ret = -ENODEV
  break

Clang therefore tail-merged the R5d block with another error path, removing
exactly the dedicated printk/unlock code corresponding to the observed
0x18 residual size delta.

R5e changes only this failure path to a direct return.


## R5e — st21nfc_dev_ioctl structurally recovered

R5e changed the devm_request_irq failure path from:

  ret = -ENODEV;
  break;

to the stock direct-return topology:

  mutex_unlock(&st21nfc_dev->irq_dir_mutex);
  return -ENODEV;

Verified result:

  reconstructed st21nfc_dev_ioctl: 0x5a0
  stock st21nfc_dev_ioctl:         0x5a0

External call count:

  reconstructed: 39
  stock:         39

The ordered external-call sequence comparison is identical.

Previously recovered functions remain intact:

  st21nfc_disable_irq      0x60
  st21nfc_dev_irq_handler  0x8c
  st21nfc_release          0x8c
  st21nfc_poll             0xf4
  st21nfc_suspend          0x60
  st21nfc_resume           0x88

MODVERSION contract remains exact:

  stock symbols:          54
  reconstructed symbols:  54
  common symbols:          54
  stock-only:               0
  reconstructed-only:       0
  CRC mismatches:           0

At this point st21nfc_dev_ioctl is considered structurally recovered
against the stock GQ5012BF1 ST21 2.2.0.19 binary.


## R5f — st21nfc_loc_set_polaritymode structurally recovered

Stock-versus-reconstructed disassembly localized the complete
st21nfc_loc_set_polaritymode size delta to IRQ request flags.

Before R5f:

  reconstructed: 0xfc
  stock:         0xf8
  delta:         0x04

The donor-derived reconstruction passed:

  st21nfc_dev->polarity_mode | IRQF_NO_SUSPEND

to devm_request_irq().

The stock GQ5012BF1 ST21 2.2.0.19 binary passes polarity_mode directly
without IRQF_NO_SUSPEND.

The removed reconstructed instruction was the 0x4000 flag OR corresponding
to IRQF_NO_SUSPEND.

Verified after R5f:

  reconstructed st21nfc_loc_set_polaritymode: 0xf8
  stock st21nfc_loc_set_polaritymode:         0xf8

Disassembly confirms no OR of 0x4000 remains.

MODVERSION contract remains exact:

  stock symbols:          54
  reconstructed symbols:  54
  common symbols:          54
  stock-only:               0
  reconstructed-only:       0
  CRC mismatches:           0


## R5g — ping payload_len partial convergence

R5g removed the synthetic payload_len local from st21nfc_ping and used
buffer[2] directly for both the payload read length and returned-length
comparison.

Result:

  R5f reconstructed ping: 0x294
  R5g reconstructed ping: 0x290
  stock ping:              0x284

The change recovered 0x04 bytes of the previous 0x10 excess.

The ordered external-call sequence remains identical to stock.

MODVERSION contract remains exact:

  stock symbols:          54
  reconstructed symbols:  54
  common symbols:          54
  stock-only:               0
  reconstructed-only:       0
  CRC mismatches:           0

Therefore the remaining 0x0c ping delta is internal register/data-flow or
control-flow structure rather than missing external NFC operations.


## R5h pre-build evidence — ping residual 0x0c

R5g versus stock st21nfc_ping comparison disproved the hypothesis that
the residual 0x0c size difference is caused by additional callee-saved
register preservation.

Both functions:

- allocate a 0x60-byte stack frame
- save x19 through x28
- save x29/x30

The four-attempt loop is canonicalized differently:

  reconstructed:
    counter = 4
    subs counter, counter, #1
    b.ne

  stock:
    negative/wrapping induction form
    adds counter, counter, #1
    b.lo

The ordered external-call sequence remains identical.

The remaining difference is exactly three AArch64 instructions and is now
being localized between loop induction representation and shared printk
error-tail topology.


## R5h evidence — ping residual localized to payload error tail

Instruction-normalized comparison produced:

  reconstructed instructions: 164
  stock instructions:         161
  delta:                        3

The retry-loop induction form differs:

  reconstructed:
    mov  counter, 4
    subs counter, counter, 1
    b.ne

  stock:
    mov  counter, -4
    adds counter, counter, 1
    b.lo

but these forms have identical instruction counts and therefore do not
explain the residual size delta.

The complete three-instruction excess is localized to the
"Could not read payload" error path.

Reconstructed tail:

  load payload-error string
  load __func__
  move saved I2C result into printk argument register
  branch to shared printk

Stock tail:

  load payload-error string
  branch directly to the common printk argument/setup block

Therefore the residual 0x0c is caused by payload-read return-value
data flow / error-tail sharing, not the retry-loop implementation.


## R5h payload-result register data flow

Payload-read disassembly further localized the residual ping delta.

Immediately after the payload I2C read, stock performs:

  load buffer[2]
  mov w2, w0
  compare w0 with buffer[2]
  branch on mismatch

Thus the I2C result is placed directly into w2, the eventual printk
integer argument register, before control flow splits.

On success stock reuses it as:

  add w2, w2, #3

for the "Read message" length.

On payload-read failure, w2 already contains the read result, allowing
the error block to load only its format string and branch into a common
printk tail.

R5g instead preserves the I2C result in w5 and reconstructs the error
printk arguments later, requiring exactly three additional instructions.

The remaining 0x0c therefore appears to be caused by read-error
control-flow/tail-sharing rather than the retry loop or external
operations.


## R5h — stock ping fatal-read tail topology

Stock st21nfc_ping disassembly confirms three fatal read-error paths share
one common printk/return tail:

- rest-of-header after 7E7E failure
- payload-length read failure
- payload read failure

For the first two paths stock performs:

  mov w2, w0
  load error format into x0
  branch common tail

The payload-read path differs because the I2C result has already been
placed into w2 before the payload-length comparison. Its error block
therefore only loads the payload-error format and branches to the same
common tail.

On the success path stock reuses that same w2 value and performs:

  add w2, w2, #3

for the total message length passed to the "Read message" printk.

This fully accounts for the three-instruction / 0x0c residual delta seen
in R5g. R5h-a tests whether an in-place read_ret += 3 source expression
reconstructs this stock register/data-flow topology.


## R5h-a — negative experiment

R5h-a tested whether rewriting:

  read_ret + 3

as:

  read_ret += 3

would reproduce the stock payload-result register data flow.

Result:

  R5g ping:    0x290
  R5h-a ping:  0x290
  stock ping:  0x284

No structural convergence occurred.

The MODVERSION contract remained exact at 54/54 with zero CRC
mismatches.

Conclusion:

LLVM canonicalizes these source expressions equivalently in this build.
The remaining 0x0c ping delta is not recoverable through this syntax-level
rewrite. Further work must identify the actual source/control-flow
difference.


## R5h-b2 — shared fatal-read tail partial convergence

R5h-b2 replaced the invalid pr_warn(runtime_format, ...) experiment with
runtime-selected full KERN_WARNING strings and a common printk() tail.

Build result:

  R5g ping:     0x290
  R5h-b2 ping:  0x288
  stock ping:   0x284

Instruction counts:

  R5h-b2: 162
  stock:   161

Thus explicit shared fatal-read control flow recovered two of the three
remaining instructions.

The final reconstructed excess is caused by the runtime format selector:
the compiler retains read_error_msg in x23 and emits:

  mov x0, x23

before entering the common printk tail.

Stock instead reaches that tail with the selected format literal already
present in x0.

MODVERSION remained exact:

  stock:          54
  reconstructed:  54
  common:         54
  CRC mismatches:  0

R5h-c therefore returns to R5g and tests a different source-level
hypothesis: expressing the payload I2C assignment directly inside the
length-comparison condition.


## R5h-c — negative conditional-assignment experiment

R5h-c tested whether expressing the payload I2C read directly inside the
length-comparison condition would reproduce stock register allocation.

Result:

  R5g ping:    0x290
  R5h-c ping:  0x290
  stock ping:  0x284

The payload-read machine code remains materially unchanged:

  reconstructed:
    mov w5, w0
    cmp w0, payload_length

rather than stock:

  stock:
    mov w2, w0
    cmp w0, payload_length

MODVERSION remains exact:

  stock:          54
  reconstructed:  54
  common:         54
  CRC mismatches:  0

Combined R5g/R5h-a/R5h-b2/R5h-c evidence shows no missing external
operation in st21nfc_ping. The ordered external-call contract is identical
to stock, while the residual 0x0c difference is internal CFG/register
allocation associated with the fatal-read printk tail.

R5g is retained as the current behavioral ping reconstruction. Ping is
not claimed instruction-size exact.

Further syntax-level compiler coaxing is deferred unless new 2.2.0.19
source evidence appears.


## R5i pre-patch evidence — probe section isolation and i2c-retry ordering

Initial explicit-address st21nfc_probe disassembly was discovered to include
instructions from .init.text because .text and .init.text use overlapping
section-relative addresses in the relocatable module.

Evidence of contamination included i2c_register_driver appearing in the
supposed st21nfc_probe external-call list even though that call belongs to
init_module.

Therefore the initial 61-versus-64 probe call count and the contaminated
tail of that call-sequence diff must not be used for reconstruction.

Subsequent probe comparisons must constrain llvm-objdump to:

  --section=.text

One source-order difference is independently proven already.

Reconstructed R5g currently parses:

  "i2c-retry"

near the beginning of probe, before GPIO acquisition.

Stock GQ5012BF1 ST21 2.2.0.19 instead performs:

  client->irq = gpiod_to_irq(gpiod_irq)

before the of_property_read_* call for "i2c-retry".

Thus i2c-retry property parsing must eventually be moved later in probe,
but no source modification is made until the clean .text-only call and
control-flow comparison is complete.


## R5i-a — probe i2c-retry ordering convergence

R5i-a moved the i2c-retry property handling from the beginning of
st21nfc_probe to immediately after:

  client->irq = gpiod_to_irq(st21nfc_dev->gpiod_irq);

This matches the ordering observed in the stock GQ5012BF1 ST21 2.2.0.19
binary.

Result:

  R5g probe:    0x654
  R5i-a probe:  0x658
  stock probe:  0x674

The source-order correction recovered 0x04 bytes of the previous 0x20
probe delta.

Remaining probe delta:

  0x1c = 7 AArch64 instructions

The clean .text-only ordered external-call comparison now has matching
i2c-retry placement.

MODVERSION remains exact:

  stock:          54
  reconstructed:  54
  common:         54
  CRC mismatches:  0

R5i-a is retained as the current probe reconstruction checkpoint.


## R5i diagnostic correction and log-level evidence

R5i-a was frozen with:

  source SHA256:
  abe6f6400efaa66d6a1624c6267c923d6e4ddac7135bb332e388a708d6e719f5

  module SHA256:
  86a7f24f7303dfe489f584f2416138a5a040ad204316c51bdaf6906c1948379c

Two diagnostic-script issues were identified before making another source
change.

First, the initial rodata resolver required relocation offsets to exactly
equal string start offsets. Kernel printk relocations may point inside the
stored string, particularly around the encoded KERN_* log-level prefix.
The resolver therefore missed most probe strings.

Second, the initial recovery-region extractor searched for an
R_AARCH64_CALL26 relocation to st21nfc_ping. st21nfc_ping is a local
symbol, so the call is emitted directly as a local `bl <st21nfc_ping>`
without such a relocation. The resulting recovery slices were empty, and
their empty diff was not evidence of structural equality.

Both diagnostic methods are being corrected before the next source patch.

Raw .rodata comparison also proves log-level differences between the
reconstructed source and stock 2.2.0.19. Several corresponding failure
messages use level 6 in the reconstruction but level 3 in stock:

  gpiod_direction_input failed
  Did not get CORE_RESET_NTF, hardware issue?
  devm_request_irq for power stats idle failed
  sysfs_create_group failed
  misc_register failed

Kernel printk level 6 is KERN_INFO while level 3 is KERN_ERR.

These severity differences are real 2.2.0.19 source-behavior evidence,
although actual probe call-site ownership must still be verified before
changing the reconstructed source.


## R5i recovery-region call topology

The corrected recovery-region extraction produced a real ordered-call
difference.

Relative to R5i-a, stock probe recovery contains:

  + one _printk immediately before mutex_lock
  + one _printk during the GPIO reset/pulse sequence
  - the reconstructed _printk after gpiod_direction_input

Thus stock has a net one additional printk call in this region.

The second stock-only printk is now identified exactly.

Stock relocation:

  .rodata.str1.1+0xc75

corresponds to:

  KERN_INFO "%s done Pulse Request\n"

Although readelf -p displays the printable string at offset 0xc76, the
actual kernel printk string begins one byte earlier at 0xc75 because of
the non-printable SOH byte preceding the printk log-level digit.

The same rule explains other stock strings such as the level-3
CORE_RESET failure string displayed one byte after its actual relocation
start.

The first stock-only recovery printk is being traced next. The nearby
stock string table contains:

  KERN_INFO "%s Recovery Request\n"

with printable text at 0xc4e and expected actual string start at 0xc4d.

No R5i-b source change is made until the function-name/register topology
of these stock calls and the reconstructed st21nfc_recovery helper are
compared.


## R5i-b pre-patch — recovery helper ownership evidence

Further stock disassembly resolves the probe recovery logging topology.

The stock sequence after a failed ping is:

  probe CORE_RESET failure printk
  Recovery Request printk
  mutex_lock
  recovery GPIO sequence

The Recovery Request printk uses:

  format: KERN_INFO "%s Recovery Request\n"
  __func__: "st21nfc_recovery"

Therefore the printk belongs semantically to st21nfc_recovery, not
st21nfc_probe.

Because this printk executes before mutex_lock, while the current
reconstruction performs mutex_lock in probe before calling the inline
recovery helper, the stock source topology likely differs structurally:
st21nfc_recovery itself appears to own the irq_dir_mutex lock/unlock.

Stock also proves:

  KERN_INFO "%s done Pulse Request\n"

immediately after the first reset/pulse sequence.

The previously apparent absence of the stock
"gpiod_direction_input failed" printk was a call-site artifact.
Stock does contain the error message; on failure it branches to a shared
_printk block at 0x2ac and then performs mutex_unlock.

Thus the semantic recovery differences are not:

  +2 stock logs
  -1 stock direction-input log

Instead they are:

  + Recovery Request
  + done Pulse Request

plus different mutex/error-tail source topology.

Stock's gpiod_direction_input failure string also uses KERN_ERR while
the reconstruction currently uses KERN_INFO.

No R5i-b source modification is made until Nothing/Google public-source
recovery topology is compared against this stock evidence.


## R5i-b — public donor confirms recovery helper lineage

NothingOSS ST21 2.2.0.15 contains the recovery sequence that the stock
GQ5012BF1 ST21 2.2.0.19 probe binary exhibits.

The Nothing recovery ioctl case performs:

  KERN_INFO "%s Recovery Request\n"
  mutex_lock(irq_dir_mutex)
  reset GPIO low
  usleep_range(10000, 11000)
  gpiod_direction_output(irq, 1)
  IRQ GPIO high
  usleep_range(10000, 11000)
  reset GPIO high
  KERN_INFO "%s done Pulse Request\n"
  four 20 ms IRQ GPIO toggle/sleep steps
  KERN_INFO "%s Recovery procedure finished\n"
  gpiod_direction_input(irq)
  IRQ re-request/disable logic
  mutex_unlock(irq_dir_mutex)

Stock 2.2.0.19 probe disassembly independently shows the same ordering.

Stock additionally supplies "__func__" as the literal:

  st21nfc_recovery

for these recovery messages.

This strongly indicates that the later ST/Ulefone 2.2.0.19 source
refactored the older inline ioctl recovery sequence into a helper named
st21nfc_recovery, which is then compiler-inlined into probe.

Google public ST21 source independently preserves the same high-level
Recovery Request -> pulse -> pulse-complete -> Recovery procedure
finished -> direction-input sequence, though it does not provide the same
MTK mutex topology.

Therefore R5i-b should reconstruct recovery-helper ownership rather than
insert equivalent logging statements directly into st21nfc_probe.

The remaining pre-patch requirement is to inspect every exit path in the
current reconstructed st21nfc_recovery helper so irq_dir_mutex ownership
can be moved into the helper without introducing an unlock bug.


## R5i-b — recovery helper topology major convergence

R5i-b restored the recovery-helper topology supported independently by
NothingOSS ST21 2.2.0.15 source and the stock GQ5012BF1 ST21 2.2.0.19
binary.

Changes included:

- st21nfc_recovery logs "Recovery Request"
- st21nfc_recovery owns irq_dir_mutex lock/unlock
- probe no longer wraps the helper in mutex_lock/mutex_unlock
- "done Pulse Request" restored after the reset pulse
- GPIO direction failures use KERN_ERR
- helper early exits converge through a common unlock tail

The structural RED test initially failed all seven expected topology
checks. After R5i-b it passed all seven.

Build succeeded.

Probe convergence:

  R5g:    0x654
  R5i-a:  0x658
  R5i-b:  0x678
  stock:  0x674

R5i-b therefore reduced the remaining probe discrepancy to:

  +0x04 = one AArch64 instruction

MODVERSION remains exact:

  stock symbols:          54
  reconstructed symbols:  54
  common symbols:          54
  stock-only:               0
  reconstructed-only:       0
  CRC mismatches:           0

R5i-b is retained as a checkpoint. No further source change is made until
the final one-instruction probe delta is localized.


## R5i-c pre-patch — final probe instruction localized

R5i-b was frozen with:

  source SHA256:
  3c91cb07a9e0a18c72b39c5d36c8e19f4b28196b83da0fb67a0b3411a3ef9ce7

  module SHA256:
  bfff43ac0926cd45990cc6b82c5366504c113ce1510dc078b133e3d43bea9b78

Probe instruction counts are:

  R5i-b: 414
  stock:  413

Thus the remaining probe delta is exactly one AArch64 instruction.

The recovery-only external-call comparison localizes a structural
difference:

  reconstructed:
    ...
    Recovery procedure finished printk
    gpiod_direction_input
    direction-input failure printk
    ...

  stock:
    ...
    Recovery procedure finished printk
    gpiod_direction_input
    ...

This does not mean stock omits the direction-input failure message.
Previous stock disassembly and rodata evidence prove:

  KERN_ERR "%s : gpiod_direction_input failed\n"

Stock instead appears to tail-merge the direction-input and
direction-output failure paths through a single physical _printk call
site and common -ENODEV/mutex-unlock tail.

R5i-b currently emits a separate physical printk call for each direction
failure. This is the strongest candidate for the final +0x04 probe delta.

No cleanup or registration code is changed until this common recovery
error tail is confirmed against stock disassembly and the NothingOSS
donor source.


## R5i-c correction — recovery error tail already matches stock

Full stock and R5i-b disassembly disproved the previous hypothesis that
R5i-b retained a separate physical printk for gpiod_direction_input
failure.

Both stock and R5i-b already tail-merge the two GPIO direction failures.

Stock:

  gpiod_direction_output
  load output-error format into x0
  cbnz -> common error block

  gpiod_direction_input
  load input-error format into x0
  cbnz -> same common error block

Common block:

  x1 = "st21nfc_recovery"
  _printk
  result = -ENODEV
  mutex_unlock

R5i-b has the same topology.

Therefore the remaining probe difference:

  R5i-b: 0x678 / 414 instructions
  stock:  0x674 / 413 instructions

does NOT originate from a duplicate recovery error printk.

No R5i-c recovery source change is made. The final one-instruction delta
must be localized elsewhere in st21nfc_probe.


## R5i-c — final probe divergence localized after recovery

Instruction-index landmark comparison shows R5i-b and stock are exact
through the recovery sequence and final recovery ping:

  first st21nfc_ping:
    R5i-b 172
    stock 172

  mutex_lock:
    R5i-b 183
    stock 183

  gpiod_direction_output:
    R5i-b 196
    stock 196

  gpiod_direction_input:
    R5i-b 237
    stock 237

The first divergence occurs immediately after the final recovery ping.

R5i-b executes an _printk before __init_waitqueue_head:

  R5i-b __init_waitqueue_head index: 257
  stock  __init_waitqueue_head index: 252

The five-instruction shift is consistent with R5i-b's
"probing nfc i2c success" log being emitted at this point while stock
does not emit that log here.

After accounting for this early log, subsequent initialization landmarks
would realign exactly:

  misc_register
  sysfs_create_group
  wakeup_source_register

Stock contains the same "probing nfc i2c success" string, so the next
check is whether stock emits it later at the end of successful probe
initialization rather than immediately after recovery/ping success.

No source modification is made until the stock success-log callsite is
confirmed.


## R5i-c negative — success-log relocation exposes remaining CFG difference

Stock binary evidence proves that the
"probing nfc i2c success" message belongs to the successful end of
st21nfc_probe rather than immediately after recovery/ping.

R5i-c moved the existing success log from the post-ping location to after
irq_wake_up initialization.

The source topology check passed and the module built successfully.

Results:

  R5i-b probe: 0x678
  R5i-c probe: 0x688
  stock probe:  0x674

Thus the semantically justified source relocation increased the residual
from +0x04 to +0x14.

The kernel-facing ABI remained exact:

  stock symbols:   54
  rebuilt symbols: 54
  common symbols:  54
  stock-only:       0
  rebuilt-only:     0
  CRC mismatches:   0

Conclusion:

The success-log placement was a real source-order difference, but the
size regression indicates another probe control-flow/cleanup topology
difference interacts with compiler block placement.

R5i-c is retained only as a negative/diagnostic checkpoint.
R5i-b remains the active structural baseline until the success/cleanup
CFG is compared directly.


## Final verification — probe and ABI closed, init log remains

The R5i-c final candidate passed the kernel-facing behavioral checks.

Probe external-call multiset comparison against stock is empty: both
implementations contain exactly the same counts of externally observable
kernel calls.

MODVERSION contract remains exact:

  stock symbols:   54
  rebuilt symbols: 54
  common symbols:  54
  stock-only:       0
  rebuilt-only:     0
  CRC mismatches:   0

Function-size status:

  st21nfc_dev_open               exact
  st21nfc_dev_read               exact
  st21nfc_dev_write              exact
  st21nfc_release                exact
  st21nfc_poll                   exact
  st21nfc_dev_irq_handler        exact
  st21nfc_disable_irq            exact
  st21nfc_loc_set_polaritymode   exact
  st21nfc_dev_ioctl              exact
  st21nfc_pstate_wq              exact
  st21nfc_remove                 exact
  st21nfc_suspend                exact
  st21nfc_resume                 exact
  cleanup_module                 exact

Known non-size-exact behavioral reconstructions:

  st21nfc_ping:
    reconstructed 0x290
    stock         0x284
    residual +0x0c previously localized to compiler CFG/register
    allocation around the fatal payload-read logging tail.

  st21nfc_probe:
    reconstructed 0x688
    stock         0x674
    external-call multiset exact; successful initialization tail now
    matches stock source ordering. Remaining size difference is treated
    as internal CFG/basic-block placement unless contrary evidence is
    discovered.

One genuine source-level mismatch remains in init_module:

  reconstructed 0x38
  stock         0x40

Stock emits two additional instructions loading x1 before _printk.
Therefore the stock init message supplies an additional string argument
that the reconstructed source currently does not.

This init logging difference is the final source-semantic item to
reconstruct before closing ST21 NFC.


## R5j FINAL — ST21NFC 2.2.0.19 reconstruction closed

The GQ5012BF1 stock ST21 NFC module has been reconstructed to a
buildable source implementation against the exact Android GKI 12901745
kernel workspace.

Final semantic correction:

- DRIVER_VERSION changed from donor 2.2.0.15 to stock 2.2.0.19
- init log reconstructed as:
    pr_info("Loading st21nfc driver %s\n", DRIVER_VERSION);

Final validation:

  module version:
    reconstructed 2.2.0.19
    stock         2.2.0.19

  init_module:
    reconstructed 0x40
    stock         0x40

  init_module disassembly:
    structurally identical, excluding normal rodata relocation offsets

  MODVERSION:
    stock symbols:          54
    reconstructed symbols:  54
    common symbols:          54
    stock-only:               0
    reconstructed-only:       0
    CRC mismatches:           0

  MODVERSION CONTRACT: EXACT MATCH

The probe external-call multiset is also identical to stock.

Previously reconstructed and verified behavior includes:

- probe-time NFCC ping/recovery
- three-recovery + final-ping topology
- i2c-retry handling
- pidle polarity handling
- wakeup_source lifecycle
- IRQ setup/teardown
- release IRQ cleanup
- stock struct member topology
- standalone st21nfc_disable_irq call topology
- userspace ioctl-local recovery
- GPIO recovery error handling
- polarity IRQ flags
- suspend/resume
- remove cleanup
- power-state work handling
- stock success-log placement
- stock module version/init logging

Known non-byte-exact functions retained as behavioral reconstructions:

  st21nfc_ping:
    reconstructed 0x290
    stock         0x284

  st21nfc_probe:
    reconstructed 0x688
    stock         0x674

Their remaining differences were localized to compiler CFG/register
allocation/basic-block placement. No missing kernel-facing calls remain
in probe, and the full kernel MODVERSION contract is exact.

The reconstructed module has a different srcversion from stock because
the reconstructed C source is not byte-for-byte ST's unpublished
2.2.0.19 source. This is expected and is not treated as an ABI failure.

Status:

  ST21NFC RECONSTRUCTION: COMPLETE
  further byte-chasing: NOT JUSTIFIED

