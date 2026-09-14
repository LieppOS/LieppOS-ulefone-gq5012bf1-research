# GQ5012BF1 — extcon-mtk-usb reconstruction (authoritative report)

Device: Ulefone Armor 29 Pro Thermal · Board GQ5012BF1 · SoC MT6878/MT6878T
Kernel: 6.1.115-android14-11, Android CI ab/12901745,
common `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`.

**Static / offline only. No device was touched at any point.**

## 1. Classification

**`SOURCE_DELTA_RECONSTRUCTION_EXACT`**

**FROZEN FOR RE: YES**

Justification: all 22 stock functions are accounted for; the import,
MODVERSION-symbol and MODVERSION-**CRC** contracts are exact (63/63 and 64/64);
KCFI type-ids are identical; DT, GPIO, USB-role, Type-C, `yft_usb_flag`,
power-supply, regulator and sysfs/procfs behaviour are closed against the stock
binary; the build is clean against exact GKI; provider ABI is compatible with
the **stock** `tcpc_class` and `mt6375-charger`; the fail-closed verifier passes
with no unexplained Linux-visible residual.

## 2. Stock oracle (frozen)

```
sha256      9e6adf23de6729f9983f680be75c8aca9eabe22aa6efcaafe7704257b37cb2bf
size        46864
build-id    bdfe8ed88c1df7083329acd2e2999c3c2b043796
vermagic    6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64
name        extcon_mtk_usb          description  MediaTek Extcon USB Driver
license     GPL                     srcversion   (absent)
depends     tcpc_class,mt6375-charger
alias       of:N*T*Cmediatek,extcon-usb   of:N*T*Cmediatek,extcon-usbC*
compiler    Android clang 17.0.2 (r487747c), +pgo +bolt +lto
```

Exactly **one** physical stock ELF exists; every located copy is byte-identical.
Load placement: `modules.load` 153/184, `modules.load.recovery` 151/189,
`modules.dep:57 → mt6375-charger.ko tcpc_class.ko pd_dbg_info.ko charger_class.ko`.

Details: `phase4-extcon-mtk-usb-stock-oracle.txt`.

## 3. Source search → donor

The device's own UsMart source drop (`Fibo_Fone_P3226`) ships **no extcon driver
at all**. Closure therefore came from a donor plus the binary.

```
donor tree      kernel-research/nothing-mt6878
device_modules  957dac185efe46cbf6336b0fff9516d84c8cd78f   (matches pinned rev)
kernel_modules  5f75a3b13e8135d45b4b0b70ec893345144f70df   (matches pinned rev)
donor file      drivers/misc/mediatek/extcon/extcon-mtk-usb.c   758 lines
donor sha256    ad7a82001ff8f8820582ed2af2f02c7a7cdc9f50f6b2f990380b06e4c0fcc16f
```

See `phase4-extcon-mtk-usb-source-candidates.md`.

## 4. RED (performed before any behaviour change)

The unmodified donor was built against exact GKI. It **compiles clean but
modpost-fails** on `get_charger_by_name` and `charger_dev_enable_vac_otgovp` —
two symbols the stock Ulefone build does not contain.

| axis | stock | unmodified donor |
|---|---|---|
| functions | 22 | 19 (17 shared, 6/17 size-identical) |
| imports | 63 | 53 (13 stock-only, 2 donor-only) |

Full delta: `phase4-extcon-mtk-usb-RED.md`.

## 5. GREEN — final parity

| axis | stock | rebuilt | result |
|---|---|---|---|
| functions | 22 | 25 | **22/22 present, 0 missing** |
| objects | 28 | 27 | 27 shared, 25 size-identical |
| imports | 63 | 63 | **exact** (0 missing / 0 extra) |
| MODVERSION symbols | 64 | 64 | **exact** |
| MODVERSION CRCs | 64 | 64 | **64/64 identical** |
| KCFI type-ids | 4 | 4 | **identical set** |
| exports | 0 | 0 | exact |
| log literals | 70 | 70 | **0 stock-only** |

Residuals, each explained and none Linux-visible:

1. **3 extra functions** — `mtk_usb_extcon_set_vbus`,
   `mtk_usb_extcon_procfs_init`, `yft_tiny2c_mode_work`. Stock's clang inlined
   the first two into their callers; the arithmetic closes (stock notifier
   0x832 vs 0x476 here ≈ the 348-byte `set_vbus` body plus call sites, with
   `probe` moving −224 bytes the other way).
2. **`mtk_usb_extcon_of_match` local symbol** — the 400-byte table is present
   and identical in size; stock retains both the local symbol and the
   `__mod_of__…_device_table` alias, this build retains only the alias.
3. **Module size** (46864 vs 443624) — build provenance only: the stock module
   is stripped and LTO/BOLT/PGO-optimised, this one is not.

Per-symbol evidence: `phase4-extcon-mtk-usb-function-parity.tsv`,
`-object-parity.tsv`, `-modversion-parity.tsv`.

## 6. Provider / ABI

- `yft_usb_flag` CRC **0x398e9c8b — matches stock exactly**. Ownership is
  unchanged: `mt6375-charger` is the single real provider, `extcon-mtk-usb`
  reads, `yft_tiny2c_usb` writes. No duplicate provider was created and
  `yft_tiny2c_usb` was not modified.
- The three `tcpc_class` CRCs initially **differed** (the LieppOS tcpc-class
  reconstruction has its own ABI), which would have caused a modprobe rejection
  against stock `tcpc_class.ko`. Closed with a declared **non-shippable
  stock-provider witness** whose CRCs were extracted provider-side from the
  stock `tcpc_class.ko` `__ksymtab`/`__kcrctab`; both directions independently
  agree.

Full analysis incl. the `CONFIG_TCPC_CLASS` stub-inline trap:
`phase4-extcon-mtk-usb-provider-abi.md`.

## 7. Behaviour closure

`phase4-extcon-mtk-usb-dt-contract.md` (DT/GPIO/regulator, all strings verified
1:1 in both ELFs, including the stock misspelling `mediatek,bypss-typec-sink`)
and `phase4-extcon-mtk-usb-usmart-contract.md` (accessory insert/remove, probe
with accessory present, the `yft_usb_flag` gate, USB role, Type-C/VBUS,
power-supply, `vbus_limit_cur`, procfs, shutdown) with strict
PROVEN_EXACT / PROVEN_STRUCTURE / PROVEN_HIGH_LEVEL / UNKNOWN grading.

The `yft_usb_flag == 1` stale-state quirk is **preserved, not fixed**, and
documented as a stock quirk.

## 8. Build

```
target    M= module build against //common:kernel_aarch64 (ab/12901745),
          NOT the historically broken prebuilt kernel_filegroup route
BUILD_RC              0
compiler warnings     0
modpost warnings      0
unresolved symbols    0
KBUILD_MODPOST_WARN   not used
fake CRCs             none        ELF patching      none
copied __versions     none        exports added     none
```

Final source: `/home/armol/kernel-work/gki-12901745-workspace/lieppos/extcon-mtk-usb/`.
Module identity is preserved on both axes: the file is shipped as
`extcon-mtk-usb.ko` (hyphen, as in `modules.dep`) while `.modinfo` keeps
`name=extcon_mtk_usb` (underscore), exactly as stock does.

Two build-environment gotchas are recorded in
`workspace/phase4-extcon-mtk-usb/verification.txt` §1: an aborted
`modules_prepare` wipes `scripts/module.lds` (regenerate by preprocessing
`module.lds.S`), and the tree intermittently loses `include/config/auto.conf`
and must be re-prepared.

## 9. Verifier

`kernel/scripts/phase4_extcon_mtk_usb_verify.py` — fail-closed: a missing
artifact, changed byte, lost symbol, CRC delta, dropped literal or a
`KBUILD_MODPOST_WARN` in any build log is a FAIL. It never passes by default.

## 10. Remaining unknowns (explicitly not claimed)

Physical uSmart connector pinout and pin numbers; whether uSmart can charge the
phone; reverse-power acceptance; external mux/load-switch IC identity; accessory
current/inrush limits; USB descriptor matrix; a second USB controller; SC851x
ownership; `reverse_charging_level`. Runtime notify-type coverage of the
Type-C notifier is **UNKNOWN** and needs a device — it is the only open item.
