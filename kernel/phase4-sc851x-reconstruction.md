# GQ5012BF1 SC851x reconstruction

## Outcome

`sc851x_charger.ko` is reconstructed as exact-GKI-buildable GPL-2.0 source.
The board selects **SC8510 at I2C address `0x69`**. The misleading DT directory
suffix `@6f` is stale; `reg=<0x69>` and live `6-0069` agree.

The driver is a leaf regmap configuration/debug/IRQ shim for SouthChip's SC8510
2S switched-capacitor converter. It is not the SC8571 charger-class policy
driver and is **not connected to uSmart in the stock software/control graph**.

Status:

```text
CLASSIFICATION = SOURCE_RECONSTRUCTION_EXACT_GKI
PRIOR_SOURCE_STATUS = NO_USEFUL_SOURCE
BUILD_RC = 0
COMPILER_WARNINGS = 0
UNRESOLVED_SYMBOLS = 0
STRUCTURAL_PARITY = PASS
RUNTIME_HARDWARE_TEST = NOT_PERFORMED_SAFETY_BOUNDARY
```

## Artifacts

| artifact | purpose |
|---|---|
| `phase4-sc851x-stock-oracle.txt` | complete behavioral oracle |
| `phase4-sc851x-source-candidates.md` | local/public source audit |
| `phase4-sc851x-RED.md` | mandatory no-public-source RED |
| `phase4-sc851x-hardware-contract.md` | DT/live address and hardware boundary |
| `phase4-sc851x-reconstructed-source.c` | review copy of source |
| `phase4-sc851x-register-fields.tsv` | all 50 register fields and 35 DT values |
| `phase4-sc851x-functions.tsv` | function inventory |
| `phase4-sc851x-objects.tsv` | object inventory |
| `phase4-sc851x-imports.tsv` | 30 imports/provider classes in stock order |
| `phase4-sc851x-modversions.tsv` | exact 30 name/CRC records |
| `phase4-sc851x-exports.tsv` | explicit zero-export ledger |
| `phase4-sc851x-relocations.tsv` | all 254 relocations |
| `phase4-sc851x-strings.tsv` | metadata/driver string inventory |
| `usmart/usmart-sc851x-power-path.md` | uSmart VBUS/control-path conclusion |
| `usmart/usmart-software-evidence.md` | DT/module/init/APK evidence ledger |
| `workspace/phase4-sc851x/` | frozen module, raw sections, disassembly, scripts, build/verification evidence |

Build source of record:

```text
/home/armol/kernel-work/gki-12901745-workspace/lieppos/sc851x-recon/
  BUILD.bazel
  Makefile
  sc851x_charger.c
```

A commit-contained mirror is at
`workspace/phase4-sc851x/reconstruction/`.

## Oracle identity

```text
module = sc851x_charger.ko
sha256 = b5e5f08bcfe37ac8c81525b0d4fe514902b552cc45b7f99fbeda8b80f6c2aa0c
size = 28488
build-id = d7daa55c413b8e593c2062b79b6bbaa9d19a68cc
vermagic = 6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64
description = SC SC851X Driver
author = South Chip <Aiden-yu@southchip.com>
license = GPL v2
depends = (empty)
imports = 30
exports = 0
parameters = 0
aliases = 0
```

It is explicitly loaded from the platform vendor ramdisk at normal
`modules.load` line 147 / zero-based index 146. Explicit loading is necessary
because stock omitted `MODULE_DEVICE_TABLE` aliases.

## Source recovery method

1. Freeze and hash the stock module.
2. Inventory ELF header, sections, symbols, objects, strings, notes,
   MODVERSION entries and every relocation.
3. Disassemble AArch64 with relocations (`llvm-objdump -dr`) so calls and scalar
   table references are not guessed from raw opcode immediates.
4. Resolve Linux 6.1 structure offsets against the exact GKI tree.
5. Decode the 50-entry `struct reg_field` table directly from `.rodata`.
6. Recover the inlined 35-property parse table and 35-entry initialization
   table from stack stores, string/data relocations and target member offsets.
7. Recover error-flow, sysfs, IRQ, PM, shutdown and I2C callback contracts.
8. Perform no-public-source RED; reject related SouthChip charger drivers as
   structurally incompatible donors.
9. Build against exact GKI and iterate only where stock-oracle evidence
   justified a change.
10. Compare rebuilt ELF with a relocation-aware script.

No decompiler pseudocode was accepted without relocation/disassembly support.

## Recovered architecture

### Private object

The exact allocation is 576 bytes:

```c
struct sc851x_chip {
        struct device *dev;                       /* 0x000 */
        struct i2c_client *client;                /* 0x008 */
        struct regmap *regmap;                    /* 0x010 */
        struct regmap_field *rmap_fields[50];     /* 0x018 */
        struct sc851x_cfg cfg;                    /* 0x1a8, 35 u32 */
        int irq_gpio;                             /* 0x234 */
        int irq;                                  /* 0x238 */
};                                                /* sizeof 0x240 */
```

### Register model

- registers and values are 8-bit;
- maximum register is `0x15`;
- 50 fields cover selected bits in `0x00..0x08`, `0x12..0x15`;
- registers `0x0c..0x0e` are read as raw IRQ flags;
- 35 fields receive required DT values;
- `0x06[3]` is `REG_RST` and receives 1 at probe;
- `0x06[2]` is `AUDIO_EN`, receives DT value 1 at probe and 0 at shutdown;
- 14 allocated fields are never read or written by stock and remain
  intentionally `RSVD_*` in source.

The stock module does not decode physical thresholds to millivolts/amps; DT
contains raw bitfield encodings. Reconstruction preserves those raw encodings.

### Probe

Probe allocates state, initializes regmap/fields, creates raw-register sysfs,
requires all DT properties, resets and configures the chip, dumps all 22
registers, requests a falling-edge oneshot threaded IRQ, and enables IRQ wake.

Important stock quirks preserved:

- version/success/dump messages use `dev_err`;
- `device_create_file` return is ignored;
- property writes log errors but the init loop does not propagate each error;
- register-dump return is only the final register-read status;
- later probe failures do not explicitly remove sysfs or free legacy GPIO;
- remove only `devm_kfree`s the state;
- raw register sysfs remains mode 0660 and writable.

### IRQ

The handler only reads and logs raw FLAG1/2/3 (`0x0c..0x0e`). There is no fault
state machine, explicit clear write, charger notification, power-supply update,
or converter-mode change.

### PM/shutdown

Suspend/resume reproduce the stock IRQ wake and disable/enable order. Shutdown
clears only `AUDIO_EN` and prints the stock message.

## Charging and converter-role conclusion

SouthChip describes SC8510 as a 99.5%-efficiency dual-cell switched-capacitor
device with:

- 10-A battery discharging, forward 2:1 conversion;
- 4-A charging, reverse 1:2 conversion;
- load-switch/reset/shipping-mode capability;
- use between a 2S pack and 1S-equivalent system architecture.

That is the silicon's capability. The recovered stock Linux module does not
implement charging policy or expose conversion direction/enable to another
module. It only supplies static field programming, debug access, raw fault
logging, PM IRQ handling, and shutdown `AUDIO_EN` clearing.

The board's separate `sc8571@67` path depends on `charger_class`; SC851x does
not. During the available normal-charging snapshot SC8571 was active while no
SC851x IRQ/event was captured. This supports, but is not needed for, the
software-boundary conclusion.

Do not describe SC851x as the main PD/PPS charger, an OTG/uSmart switch, or an
audio-amplifier supply controller without a schematic or additional evidence.
The exact board nets and detailed `AUDIO_EN` silicon semantics remain unknown.

## I2C identity resolution

```text
DT_ADDRESS = 0x69
LIVE_ADDRESS = 0x69
DRIVER_EXPECTED_ADDRESS = 0x69
DISCREPANCY_RESOLVED = YES
EXPLANATION = DT node suffix @6f is stale; the reg cell is <0x69>, the I2C core
              creates client 6-0069, and the driver uses that client without a
              hard-coded address.
```

## uSmart determination

```text
USMART_CLASSIFICATION = PROVEN_UNRELATED
CAN_STOCK_USMART_CHARGE_PHONE = NO_SOFTWARE_SUPPORT_FOUND
```

The stock uSmart/UVC path is implemented by `extcon-mtk-usb.ko`, USB1/xHCI,
UVC switch/VBUS GPIOs, and MT6375's `usb-otg-vbus` regulator. SC851x has no DT
edge, symbol edge, userspace reference or applicable framework object. Details
and the distinct internal `yft_tiny2c_usb` thermal-camera path are documented
under `kernel/usmart/`.

## Exact-GKI build

Workspace/kernel:

```text
/home/armol/kernel-work/gki-12901745-workspace
Linux 6.1.115-android14-11
GKI ab/12901745
commit 6b18f0b574ab3267615ae6ce642d5a7c3c21ac09
```

Command:

```sh
cd /home/armol/kernel-work/gki-12901745-workspace
tools/bazel build //lieppos/sc851x-recon:sc851x_recon
```

Result from `workspace/phase4-sc851x/recon-build.log`:

```text
BUILD_RC=0
compiler warnings=0
unresolved symbols=0
```

The log contains the workspace's expected `sign-file` missing private-key SSL
notices; Bazel still completes successfully. This is not a compiler warning or
an unresolved symbol, and no key/module-signature fabrication was attempted.
The generated `*.check_no_remaining` file is empty.

## Structural comparison

`verify_recon.py` reports:

- exact 11-function key set and sizes;
- exact KCFI type-id word for every function;
- 8 of 9 behavioral `.text` functions byte-identical;
- `probe` exactly 1924 bytes in each;
- byte-identical `.init.text`, `.exit.text`, `.rodata`, `.data`,
  `.rodata.str1.1`, `__versions`, and `.comment`;
- exact 30 MODVERSION records, byte-for-byte and in stock order;
- exact relocation section sets and counts;
- exact relocation target/type sequence in every section, including all 215
  `.rela.text` entries;
- exact `.rela.data`, `.rela.rodata`, init/exit and module relocations;
- only modinfo delta: local workspace SCM suffix in `vermagic`.

Residual code bytes are honestly bounded:

- inlined probe has compiler-local stack/register allocation scheduling while
  preserving exact size and relocation/call target sequence;
- IRQ-registration has a 3-byte encoding delta between equivalent unsigned GPIO
  bounds checks (`cmp #0x1ff; b.hi` versus `cmp #0x200; b.hs`).

No source contortion, fake symvers, CRC editing, binary patching, or behavior
addition was used to erase those semantically null differences.

## Runtime validation boundary

The source was compiled and statically compared only. It was not loaded on
hardware. Inserting a reconstructed power-converter module or exercising its
writable register sysfs would cross the agreed safety boundary. Existing stock
snapshots prove that the stock driver binds at `6-0069` and registers
`irq/57-sc851x-irq`; they do not substitute for unsafe reconstructed-driver
activation.

## Final status

SC851x moves from `RE_REQUIRED / P1_CORE_HARDWARE / NO_USEFUL_SOURCE` to:

```text
SOURCE_RECONSTRUCTION_EXACT_GKI
BUILD_PASS
STATIC_ORACLE_PARITY_PASS_WITH_REPORTED_NONOBSERVABLE_TEXT_DELTA
LEAF_NO_INTERMODULE_DEPENDENCIES
HARDWARE_RUNTIME_VALIDATION_DEFERRED_BY_SAFETY_POLICY
```
