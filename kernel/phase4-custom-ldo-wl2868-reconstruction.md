# Phase 4 — `custom_ldo_wl2868.ko` reconstruction

## 1. Final classification

`STRUCTURAL_AND_BEHAVIORAL_APPROXIMATION` — **PRECISELY BLOCKED for an exact reconstruction claim**. The provider ABI is exact at the export-CRC level and the module builds against the requested GKI, but no exact source exists and the voltage-unit interpretation, some probe data layout, and byte/function parity are not proven. No live validation is permitted.

## 2. Stock oracle

Frozen oracle: `kernel/phase4-custom-ldo-wl2868-stock-oracle.txt`; raw copy and evidence are under `workspace/phase4-custom-ldo-wl2868/`. SHA-256 is `dab36e3d2593546d72b4fa7257b4a303c65c0ad4c507bbd50e1578111d48`, size 35,544 bytes, BuildID `176a9559028840aba4b47e9b8db1fb12c9dde79e`. It is the byte-identical vendor_dlkm/proprietary-blob copy; absent from recovery/system_dlkm/odm_dlkm. Metadata: name `custom_ldo_wl2868`, GPL v2, description `WL2864 & WL2868 Power IC Driver`, no dependencies/aliases/parameters, stock vermagic `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`.

## 3. Complete ELF inventory

The stock counts are 15 functions, 25 objects, 27 imports, 2 exports, 27 MODVERSIONS records, 433 relocations, and 47 strings. See `phase4-custom-ldo-wl2868-stock-inventory.md` and the required TSVs. Named functions include the four chip helpers, two exported dispatchers, `wl2864c_vin2_power`, probe/remove, misc fops, and module init/exit.

## 4. Source search and provenance

No exact local/public source was found. Sony, OnePlus, MiCode, Motorola, and Nothing artifacts are frozen under `workspace/phase4-custom-ldo-wl2868/donors/`. The closest architecture is the MiCode/OnePlus raw camera-LDO family, while Sony and Motorola are register/framework references only. Full classification is in `phase4-custom-ldo-wl2868-source-candidates.md`.

## 5. Mandatory RED

The untouched Sony donor at `7e42db1690b5…` is `STRUCTURAL_DONOR_ONLY`. Its regulator-framework/regmap implementation has the wrong compatible, no misc device, no raw custom chardev ABI, and no `will_ldo_*` exports. The RED harness and source are in the GKI workspace under `lieppos/custom-ldo-wl2868-recon/donor-red/`; the final RED build stops on the donor's incompatible legacy probe prototype (`int (*)(client,id)` versus `int (client)`). Logs: `sony-donor-red-build-final.log`, with the earlier temporary-directory attempts also retained.

## 6. Hardware contract

The fitted device is a seven-channel WL2864C/WL2868C-family camera PMU at I2C bus 11, 7-bit address 0x29. Chip identity is read at register 0x00; dispatch accepts WL2864C byte 0x01 and WL2868C byte 0x82. VOUT registers are 0x03–0x09 and enable is 0x0e. Details: `phase4-custom-ldo-wl2868-hardware-contract.md`.

## 7. Device-tree contract

Stock OF compatible is exactly `will,wl2864c_pmu`; I2C ID/driver string is `wl2864c`. Probe requests GPIO consumers `reset` and `vin1_en`; the internal vin2 path uses an integer GPIO converted with `gpio_to_desc`. No regulator child-node framework is present. Details: `phase4-custom-ldo-wl2868-dt-contract.md`.

## 8. Critical export ABI

The consumer chain is `imgsensor → custom_ldo → custom_ldo_wl2868`. Stock exports exactly:

| Symbol | Prototype recovered from call/KCFI/consumer | Stock CRC | Rebuild CRC |
|---|---|---:|---:|
| `will_ldo_vout` | `int (int ldo_num, int value)` | `0x23ec3223` | `0x23ec3223` |
| `will_ldo_en` | `int (int ldo_num, int enable)` | `0xdd9b9ea1` | `0xdd9b9ea1` |

No CRC patching or hand-written `Module.symvers` was used.

## 9. Register map

`phase4-custom-ldo-wl2868-register-map.tsv` records register 0x00 identity, 0x03–0x09 per-LDO VOUT, and 0x0e enable bitmap. All accesses are raw `i2c_transfer`; the stock module imports no regmap or regulator-framework symbol.

## 10. Voltage contract

Valid LDO numbers are 1–7 and map to `ldo_num+2`; invalid numbers return -1. Static arithmetic recovered from the AArch64 constants is signed `value/100`, addition of the per-chip/per-LDO offset table, then division by 125, with a limit comparison selecting zero on the failing branch. Tables are recorded in `phase4-custom-ldo-wl2868-voltage-enable-contract.md`. The public unit convention remains unresolved; assigning donor uV semantics would be speculation.

## 11. Enable and GPIO contract

Enable reads 0x0e, modifies bit `ldo_num-1`, writes the result, and returns I2C errors. WL2868C preserves bit7 when the resulting low-seven-bit bitmap is zero. Probe statically shows reset high, vin1_en high/low/high with two 10–11 ms waits, then a 1 ms sleep. These actions were not executed.

## 12. Userspace/chardev ABI

A misc device named `wl2864c` supplies `open`, `llseek`, `read`, and `write`. Open is single-owner; llseek handles SEEK_CUR and otherwise resets position; read caps count at 20 and formats six bytes per register (`RR VV `); write caps count at 128, uses `memdup_user`, parses six-byte records, and performs raw register writes. No ioctl/sysfs write ABI was found. Details: `phase4-custom-ldo-wl2868-userspace-contract.md`.

## 13. Camera/sensor power mapping

The stock binary proves seven camera/sensor LDO channels and the transitive consumer chain, but no local sensor power-table source recovers named rail-to-LDO assignments or call-site voltage units. Unrelated Nothing DT rail names are explicitly not attributed to Ulefone. The exact evidence boundary is in `phase4-custom-ldo-wl2868-consumer-contract.md`.

## 14. Consumer pre-analysis

`stock-custom-ldo.ko` was only disassembled and symbol-scanned. Its two wrappers directly CALL26 the two provider exports and carry no additional logic. It was not rebuilt, inserted, removed, or otherwise executed; work stops before the custom_ldo phase as required.

## 15. Reconstruction tree

Reconstruction source/build glue is in `/home/armol/kernel-work/gki-12901745-workspace/lieppos/custom-ldo-wl2868-recon/recon/`. A repository copy is `phase4-custom-ldo-wl2868-reconstructed-source.c`. The implementation intentionally uses raw I2C, the stock compatible, GPIO names, misc name, seven-register map, provider exports, and no regulator framework.

## 16. Exact-GKI build

Target: `//lieppos/custom-ldo-wl2868-recon/recon:custom_ldo_wl2868_recon`; kernel target `//common:kernel_aarch64`; workspace common commit `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`, Linux 6.1.115 Android 14 / ab/12901745. Final `BUILD_RC=0`, check-no-remaining present, modpost unresolved symbols 0, and the 27-symbol stock kernel import surface is reproduced. Build log: `workspace/phase4-custom-ldo-wl2868/recon-build.log`.

Kleaf emits two OpenSSL/sign-file diagnostics because the local workspace has no `common/certs/signing_key.pem`; these are signing-provenance diagnostics, not compiler warnings or unresolved module symbols. The rebuilt vermagic is `…-maybe-dirty` rather than the frozen vendor suffix. No device or rail operation occurred.

## 17. Structural, behavioral, and CRC verification

Static verification is in `workspace/phase4-custom-ldo-wl2868/verify-recon-vs-stock.txt`. Results: all 27 stock kernel imports are present (the `module_layout` record is MODVERSION-only), no extra imports, both export CRCs match exactly, and the check-no-remaining artifact exists. Named function/control-flow shape, exact data layout, voltage units, and byte identity do not match sufficiently to claim exact behavioral parity. The raw rebuilt module is `workspace/phase4-custom-ldo-wl2868/recon-custom_ldo_wl2868.ko`.

## 18. Safety, runtime status, evidence, and final verdict

Hard safety boundary held: no device I2C writes, GPIO toggles, rail changes, chardev/ioctl/sysfs writes, bind/unbind, module insertion/removal, DT changes, flashing, slot switching, or camera opening. Runtime validation is therefore `NOT PERFORMED BY POLICY`.

Authoritative evidence index: stock oracle; seven inventory TSVs; raw ELF sections/disassembly/bytes; source candidates; RED; hardware/DT/register/voltage-enable/userspace/consumer contracts; provider/consumer boundary TSVs; reconstruction source/build glue; build logs; and static verification output.

**Final verdict: PRECISELY BLOCKED for COMPLETE exact source reconstruction.** The safe deliverable is a built structural/behavioral approximation with exact consumer export CRCs, not a claim that it is drop-in hardware-equivalent. Keep the stock module/provider chain until exact consumer call-site voltage semantics and permitted non-live evidence resolve the residuals.
