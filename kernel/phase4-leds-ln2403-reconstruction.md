# Phase 4 — `leds_ln2403` reconstruction

# Final classification

`NO_PUBLIC_SOURCE_FOUND / STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`
Disposition: `SOURCE_RECONSTRUCTED / SOURCE_NOW`.

# FROZEN status

**FROZEN FOR RE: YES.** Every hardware-significant stock interface, constant,
transition, timing, dependency, userspace ABI, error class and retained defect
is accounted. Runtime validation remains a separate integration phase.

# Stock oracle

Canonical `vendor_dlkm/lib/modules/leds-ln2403.ko`: SHA256
`211bda35ee3476c107d7e495a0463c27bbef114a031a6b81b8bb718bbe54ee94`,
39,344 bytes, Build ID `589cce1de2565302414117d6e650f26aa98c4a46`.
It is normal-load zero-based index 192 and absent recovery. Two available
physical copies are byte-identical, so there is one unique oracle.

# Source provenance

No public/local target driver was found. The consumer is a clean-room stock-ELF
reconstruction. The separate genuine MT6878 PWM provider comes from local
Nothing device-modules commit `957dac185efe46cbf6336b0fff9516d84c8cd78f`;
the exact provider source used for the build is committed in
`kernel/phase4-mtk-pwm-provider/`.

# RED

Mandatory pre-edit baseline: `NO_PUBLIC_DONOR_FOUND`; empty source produced
0/16 functions, no ABI, no DT binding and no hardware/sysfs behavior. Generic
PWM/LED drivers were rejected as false lineage.

# Function inventory

All 16 named stock functions are inventoried with section, offset, size and
KCFI/preword evidence in `phase4-leds-ln2403-functions.tsv`. Init/exit, three
show/store pairs, GPIO/PWM helpers, both timer callbacks, probe/remove and GPIO
lookup are all present in the reconstruction with no extra function.

# Import ABI

32/32 imports are shared and all 32 MODVERSION CRCs match: 30 GKI/kernel imports
plus 2 real `mtk-pwm` imports. Stock and reconstruction export zero symbols.

# MTK PWM provider ABI

`mt_pwm_disable` CRC `0xd602ce35`, prototype
`void mt_pwm_disable(u32,u8)`, is called `(3,0)`; its 160 provider bytes match.
`pwm_set_spec_config` CRC `0xa54c8591`, prototype
`s32 pwm_set_spec_config(struct pwm_spec_config *)`, receives the exact 56-byte
legacy config and its ignored return; its 744 provider bytes match. The genuine
provider source build emitted both CRCs naturally—no fake symvers or patching.

# Device-tree contract

Exact path `/yft_camplight`, compatible `mediatek,yft_camplight`, status okay.
The module consumes five zero-flag GPIO properties and three explicit pinctrl
states. It consumes no PWM phandle/period or brightness/default-mode property.

# Hardware topology

Raw active-high GPIOs: LN2403 power 74, LN2403 enable 91, warning common power
153, red 20, blue 21. GPIO22 is the dimming signal. The module changes raw
values but never calls a GPIO direction API; board/pinctrl direction is a
precondition. Red/blue outputs do not use PWM.

# Pinctrl contract

`default` maps to an empty group and is not explicitly looked up. The consumed
states are `ln2403_pwmoff_high` (GPIO22 mux0/high), `ln2403_pwmoff_low`
(GPIO22 mux0/low), and `ln2403_pwmon` (GPIO22 mux1/PWM_3/high); all specify
slew-rate 1. Probe selects low. PWM shutdown selects high; explicit OFF then
selects low.

# PWM contract

No generic PWM framework or DT specifier is used. Legacy channel 3 uses
`PWM_MODE_OLD`, `CLK_DIV1`, `PWM_CLK_OLD_MODE_BLOCK`, PMIC pad 0, and all other
OLD fields zero. Fixed modes use width 17 and threshold `floor(P×17/100)` for
P=97/73/11, yielding 16/12/1. Provider returns are ignored.

# Camping-light modes

`camplight_mode` table: 0 OFF; 1 LOW; 2 NORMAL; 3 HIGH; 4 BLINK; 5 SOS.
Transitions first stop gate timing/PWM and clear gates. Fixed modes program PWM,
assert EN then POWER. BLINK/SOS select GPIO22 low, start EN gating, then assert
POWER. Nonzero modes hold the camping wake source; 0 relaxes it. The signed
range check rejects >=6 but accepts negative modes; those follow the default
path, assert POWER, are cached, and make a later show reach the bounds trap.

# Brightness ABI

Signed decimal parser. Zero turns EN/POWER/PWM off and selects GPIO22 low.
Nonzero computes `capped=(N<94)?N:94`, internal duty `100-capped`, width 100 and
threshold equal to internal duty, then programs PWM and asserts POWER before EN.
There is no lower clamp; negative values can wrap the 16-bit provider field.
Brightness neither updates camping mode nor cancels a gate timer.

# Red/blue LED ABI

`leds_ctl`: 0 all off; 1 red; 2 blue; 3 both; 4 red flash; 5 blue flash;
6 alternating red/off/blue/off. Direct GPIO triplets are fully mapped. Every
store cancels the prior timer and resets phase; invalid values retain their
cached state without output cleanup. Only 0 relaxes the warning wake source.

# Timer/work behavior

Two CLOCK_MONOTONIC relative hrtimers and no work structs exist. Warning flashes
forward every 40 ms. BLINK gates EN 50/50 ms. SOS preserves stock transition
counter boundaries 6, 12 and 17 with 200/50/500/1000-ms interval changes.
`ln2403_pwm_work` is synchronous despite its name. Camping start/cancel alone is
mutex-protected.

# Private state layout

The exact 280-byte allocation has mutex at 0, intervals 0x30/0x38, SOS count
0x40, gate GPIO 0x44, camping mode 0x48, five GPIO integers 0x4c–0x5c,
warning state/mode 0x60/0x64, red/blue hrtimer 0x68, wake pointer 0xb0,
flags 0xb8/0xb9, current interval 0xc0, camping hrtimer 0xc8 and wake pointer
0x110. All semantic offsets are stock-access evidenced.

# Probe

Probe allocates 0x118 bytes; finds the exact compatible; requests EN, LN power,
warning power, red and blue GPIOs in that order; acquires/lookups pinctrl; creates
three sysfs files; initializes state, one timer and two wake sources; sets five
raw values and GPIO22 low. Allocation/missing-node/GPIO/pinctrl/sysfs failure
classes and reverse sysfs rollback—including removal of the current failed
attribute—are preserved. GPIO requests and other late resources intentionally
leak on failure as in stock.

# Sysfs ABI

Canonical files are
`/sys/devices/platform/yft_camplight/{camplight_mode,leds_ctl,camplight_set_brightness}`.
All are `DEVICE_ATTR` 0644 and stock init chmods all three 0777. Stock
`vendor_file_contexts` labels them `u:object_r:sysfs_yft_file:s0`. Shows emit
exact names/integer plus newline; stores use `%d` and return count even on parse
or range failure. A separate `soc:gftk_camplight` chmod is legacy/stale.

# Userspace contract

`com.yft.lamp` maps SOS→5, SUPER→4, ALWAYS→2 and seekbar values to brightness;
shutdown/timeout writes both controls 0. It offers 5/10/20/30-minute and
indefinite durations. `com.yft.redbluelight` writes every `leds_ctl` value 0..6
with exact service action mapping. `YftPowerSavingSwitchService` reads both
camping files and forces active values to 0 in power saving.

# Safety behavior

Kernel behavior includes normal brightness cap 94, explicit off sequencing and
separate wake holds. It has no thermal/current/battery sensor, timeout,
low-battery restriction, charging restriction or boot-mode cap. App auto-off,
10-minute cooldown for repeated >90 use, warnings and power-save closure are
userspace-only and bypassable by another sysfs writer.

# Lifecycle / PM

Init/exit register/unregister `yft_camplight`. Remove only logs and returns 0:
it performs no sysfs, timer, PWM, GPIO, wake-source, GPIO-request, heap or global
cleanup. There is no shutdown, suspend, resume or PM table. These stock defects
are preserved and make unload while active unsafe.

# Exact-GKI build

Target `//lieppos/leds-ln2403-recon:leds_ln2403_recon` against pinned
`//common:kernel_aarch64` and genuine source-built provider: BUILD_RC 0,
compiler warnings 0, modpost warnings 0, unresolved symbols 0. Rebuilt SHA256
`9ba9d6fef5d1e364aae07692169cde076eb4c3db509d9032c1265e78351db526`,
36,976 bytes, Build ID `eff0083a51ae66750cdc35f57c4340d83f06a9d3`.

# Function parity

Stock/rebuilt/shared 16/16/16; stock-only 0; rebuilt-only 0; size-identical
8/16; byte-identical 7/16. All 12 applicable indirect/address-taken KCFI IDs
match. The four other pre-function words are adjacent direct-call instructions,
not KCFI identifiers. Every non-byte row has a bounded semantic explanation.

# Object parity

Exact bytes include both mode string tables, all three attributes, OF table,
platform driver, duty, null-terminated sysfs pointer array and core metadata.
Pointers/state globals and `__versions` are relocation-equivalent. No
hardware-significant object is unresolved.

# Behavioral verifier

`kernel/scripts/phase4_leds_ln2403_verify_recon.py` is fail-closed and reports
**50/50 CHECKS PASSED**, covering oracle/build hashes, function/KCFI/import CRCs,
provider bytes, DT/GPIO/pinctrl/PWM/modes/timers/sysfs/lifecycle/source sync and
clean-build gates.

# Residuals

Only compiler control-flow/source factoring, diagnostic placement, local
`maybe-dirty` vermagic, source paths, Build ID, symbol/string placement and link
metadata differ. None changes ABI,
hardware state, timing, userspace output or failure class.

# Runtime-validation status

Not performed and not required for static RE closure. Future integration may
validate on/off/brightness/waveforms thermally and electrically under a separate
approved safety procedure; it does not reopen this RE result absent contrary
stock evidence.

# Safety

All work was static/offline. No module was inserted/removed; no sysfs write,
GPIO/PWM programming, bind/unbind, flash, reboot or slot change occurred.

# Evidence index

Oracle/RED/search: `phase4-leds-ln2403-stock-oracle.txt`, `*-RED.md`,
`*-source-candidates.md`. Inventories: `*-functions.tsv`, `*-objects.tsv`,
`*-imports.tsv`, `*-modversions.tsv`, `*-relocations.tsv`, `*-strings.tsv`.
Contracts: `*-provider-abi.md`, `*-dt-contract.md`, `*-hardware-contract.md`,
`*-pwm-contract.md`, `*-camplight-mode-contract.md`, `*-brightness-contract.md`,
`*-redblue-contract.md`, `*-async-contract.md`, `*-struct-layout.md`,
`*-probe-contract.md`, `*-sysfs-contract.md`, `*-userspace-contract.md`,
`*-safety-contract.md`, `*-lifecycle-contract.md`. Parity/build:
`*-function-parity.tsv`, `*-object-parity.tsv`, `*-import-delta.tsv`,
`*-build-parity.md`. Source snapshots: `kernel/phase4-leds-ln2403-recon/` and
`kernel/phase4-mtk-pwm-provider/`.

# Final verdict

`leds_ln2403.ko` is source-reconstructed, `SOURCE_NOW`, and **FROZEN FOR RE**.
The stock transition blob is removed from the active ZERO-BLOB RE queue. No
other module's status is changed by this closure.
