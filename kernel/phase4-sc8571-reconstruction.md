# GQ5012BF1 SC8571 reconstruction

## Outcome

The stock `sc8571_charger.ko` contract was reconstructed as GPL-2.0 source and
built in the exact GKI ab/12901745 workspace. It is the board's dual-role
SouthChip charge-pump leaf: one driver binds the master at `11-0066` and slave
at `6-0067`, exposing `primary_dvchg` and `secondary_dvchg` through MediaTek
`charger_class`.

```text
CLASSIFICATION = SOURCE_RECONSTRUCTION_EXACT_GKI
PRIOR_SOURCE_STATUS = NO_USEFUL_SOURCE
BUILD_RC = 0
COMPILER_WARNINGS = 0
UNRESOLVED_SYMBOLS = 0
ABI_AND_BEHAVIORAL_CONTRACT_PARITY = PASS
BINARY_IDENTITY = NO
RUNTIME_HARDWARE_TEST = NOT_PERFORMED_SAFETY_BOUNDARY
```

`PASS` means the frozen static verifier's ABI and observable code/data contract
checks pass. It does not mean the ELF is byte-identical or that reconstructed
code was activated on hardware.

## Artifacts

| artifact | purpose |
|---|---|
| `phase4-sc8571-stock-oracle.txt` | canonical stock identity/load/provider oracle |
| `phase4-sc8571-source-candidates.md` | public/local source audit and donor classification |
| `phase4-sc8571-RED.md` | mandatory unchanged-donor RED |
| `phase4-sc8571-hardware-contract.md` | topology, DT, registers, callbacks, ADC, IRQ, watchdog, PM and PD boundary |
| `phase4-sc8571-provider-abi.md` | exact charger_class consumer/provider ABI |
| `phase4-sc8571-build-verification.md` | exact-GKI build and parity measurements |
| `phase4-sc8571-recon/` | buildable source, ABI header, stock CRC oracle, Makefile and Kleaf target |
| `phase4-sc8571-reconstructed-source.c` | single-file review mirror |
| `phase4-sc8571-dt-contract.tsv` | all 40 required scalar properties plus GPIO/name |
| `phase4-sc8571-register-fields.tsv` | all 58 regmap fields |
| `phase4-sc8571-{functions,objects,imports,exports,modversions,relocations,strings}.tsv` | complete stock ELF ledgers |
| `scripts/phase4_sc8571_verify_recon.py` | bounded relocation-aware verifier |
| `workspace/phase4-sc8571/` | frozen ELF/raw evidence/donor/build output (local analysis workspace) |

Build source of record:

```text
/home/armol/kernel-work/gki-12901745-workspace/lieppos/sc8571-recon/
```

## Oracle and method

Stock oracle:

```text
sha256=790065853b875213ee7906bb4c41a5f272106b24a537034a886f12f0153d1d0b
size=49,768
BuildID=25748028cf538204ae8d7b387f51a89e3c93bf9f
vermagic=6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64
depends=charger_class
functions=34 objects=34 modversions=42 relocations=608 exports=0
```

Recovery used section/symbol inventories, every relocation, AArch64 disassembly,
raw data-table decoding, the committed DT snapshot, stock provider ELF/source
type evidence and the exact 6.1 headers. The unrelated OPLUS SC8571 code was
accepted only as a register-name/scale donor after stock evidence independently
fixed coordinates. Its unchanged RED fails on missing OPLUS framework headers;
no stubs were created.

## Recovered architecture

The private object is exactly 872 bytes. It owns device/client/regmap pointers,
58 `regmap_field` pointers, 40 u32 configuration values, IRQ GPIO/IRQ, role,
power-supply descriptor/config/cache state and charger-device pointer. One OF
match table handles standalone/master/slave roles; this board instantiates only
master and slave.

Probe validates device ID `0x41`, parses every required property, resets and
programs the chip, applies the slave-only VBUS-in-range-disable override,
registers a MAINS power supply, requests a falling-edge oneshot IRQ, registers
the charger-class endpoint and creates the stock `fastcharge_N/chipid` class.
Stock quirks—including ignored sysfs return, continuing initialization after
individual write failures, alarm-reset no-ops, PRESENT listed but unimplemented,
and imperfect cleanup/error paths—are preserved rather than improved.

The hardware and framework details are deliberately centralized in
`phase4-sc8571-hardware-contract.md` and
`phase4-sc8571-provider-abi.md` rather than duplicated here.

## PD/PPS and watchdog conclusions

The module contains no PD/PPS negotiation or charger-policy state machine. It
imports no TCPM, TCPC, adapter, USB-PD, PPS or charger-algorithm symbol. Policy
selects the master/slave charger devices through `charger_class`; SC8571 only
programs thresholds/enable and returns telemetry.

The DT selects watchdog timeout code 0 but sets watchdog disable to 1. Both
charger-class watchdog callback slots are NULL. There is no periodic kick.

## Build and parity

```sh
cd /home/armol/kernel-work/gki-12901745-workspace
tools/bazel build //lieppos/sc8571-recon:sc8571_recon
```

The build succeeds with zero compiler warnings and no unresolved symbols. The
rebuilt module preserves the exact metadata except local SCM vermagic, exact
function/object sets, exact KCFI words, byte-identical `__versions` and
`.rodata`, exact string multiset, exact external-call multiset per function,
all fourteen charger callback slots and the exact provider CRC.

It is not byte-identical. The bounded residual is two compensating function
sizes (probe -4 bytes, IBAT setter +4), two extra relocation records from probe
layout, local data placement/padding, BuildID and SCM token. Full numbers and
the verifier's fail-closed allowed residuals are in the build report.

## Safety boundary

No live charge cycle, I2C/register write, sysfs write, module insertion,
I2C-driver bind/unbind, PD/PPS request, reboot, flash or slot mutation was
performed. Existing read-only snapshots identify stock topology only. Runtime
validation of reconstructed power-converter code remains intentionally deferred.
