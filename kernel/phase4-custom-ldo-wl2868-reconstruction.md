# Phase 4 — `custom_ldo_wl2868.ko` closure

# Final classification

**`STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`**

**RE disposition: FROZEN FOR RE.** All hardware-affecting stock behavior visible in the frozen ELF has been recovered and represented in source. Instruction-byte identity is not claimed or required: 6/15 functions are byte-identical and 10/15 are size-identical, while every function has the stock KCFI ID, external/internal call multiset, hardware constants, and established branch semantics.

This report supersedes the earlier `STRUCTURAL_AND_BEHAVIORAL_APPROXIMATION` status. The earlier evidence remains useful historical material, but this file is authoritative.

# Closure summary

Closure established the facts that removed the former material residuals:

- Stock has a 112-byte static singleton, not an allocated private object and not a regulator-framework model.
- Probe never reads chip ID register 0x00. It overwrites `client->addr` with 0x2f and hardcodes software chip byte 0x82.
- Probe does no default register writes. Seven apparent initialization operations reduce to seven `ldo_vout=0` logs and no I2C transfer.
- Exact GPIO order, failure behavior, descriptor release, voltage arithmetic, enable RMW, raw-I2C topology, misc ABI, and lifecycle are closed.
- The reconstructed module has the exact 15-function set, exact 27-entry import/MODVERSION map, exact KCFI map, exact export CRCs, and exact per-function call multisets.
- Exact-GKI provider and downstream `custom_ldo` builds are clean; the fail-closed verifier passes 50/50 checks.

# Stock oracle

Canonical extracted binary:

`workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/custom-ldo-wl2868.ko`

Preserved copy:

`workspace/phase4-custom-ldo-wl2868/stock-custom-ldo-wl2868.ko`

| Property | Frozen value |
|---|---|
| SHA-256 | `dab36e3d2593546d72b4fa7257b4a303c65c0ad4c507bbd1fbb50e1578111d48` |
| Size | 35,544 bytes |
| BuildID | `176a9559028840aba4b47e9b8db1fb12c9dde79e` |
| ELF | ELF64 little-endian AArch64 relocatable, not stripped, PAC property |
| Compiler | Android clang 17.0.2 build 10087095, PGO+BOLT+LTO, revision `d9f89f4d16663d5012e5c09495f3b30ece3d2362` |
| Vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| Name | `custom_ldo_wl2868` |
| Description | `WL2864 & WL2868 Power IC Driver` |
| License / author | `GPL v2` / absent |
| Depends / aliases / parameters / srcversion | empty / none / none / absent |
| Placement | vendor_dlkm only |
| modules.load | one-based line 102; zero-based index 101 |
| modules.dep | provider has no dependency; `custom-ldo.ko` directly depends on it; imgsensor line includes it transitively |

The preserved and proprietary-blob copies have the same hash. It does **not** disagree with the earlier canonical oracle; the one-character hash typo in the superseded report was documentary, not an oracle replacement. Full metadata and section ledger: `phase4-custom-ldo-wl2868-stock-oracle.txt`.

Clean stock inventory: 15 functions, 25 named object/data symbols, 27 kernel imports, 2 exports, 27 MODVERSION records, 433 relocations, and 47 strings. The inventories are the `phase4-custom-ldo-wl2868-{functions,objects,imports,exports,modversions,relocations,strings}.tsv` files.

# Source provenance

Final bounded search result: **`NO_PUBLIC_SOURCE_FOUND`**. Exact description, exports, compatible, misc name, helper names, typo logs, and probe strings were searched across general/GitHub/Gitee indexes and NothingOSS, Sony, Motorola, OnePlus/OPPO/realme, MiCode, Transsion, and MediaTek mirrors. No candidate has the combined stock ABI.

Sony, OnePlus, MiCode, Motorola, and Nothing artifacts remain `STRUCTURAL_DONOR_ONLY` or hardware/DT references. None supplied unproven semantics. The Sony RED remains a genuine incompatible donor failure. Details and frozen hashes: `phase4-custom-ldo-wl2868-source-candidates.md` and `workspace/phase4-custom-ldo-wl2868/donors/`.

# Struct layout

Stock `wl2864c_data` is one exact 0x70-byte `.bss` object:

| Offset | Size | Proven field |
|---:|---:|---|
| 0x00 | 8 | `struct i2c_client *client` |
| 0x08–0x2f | 40 | `UNKNOWN` zeroed, never accessed |
| 0x30 | 8 | reset GPIO descriptor |
| 0x38 | 8 | VIN1 GPIO descriptor |
| 0x40 | 4 | VIN2 integer GPIO number |
| 0x44 | 1 | software chip-dispatch byte |
| 0x45–0x67 | 35 | `UNKNOWN` zeroed, never accessed |
| 0x68 | 4 | global misc register cursor |
| 0x6c | 1 | probe-ready flag |
| 0x6d–0x6f | 3 | `UNKNOWN/PADDING` |

There is no allocation, mutex, embedded miscdevice, separate device pointer, clientdata, cache, channel state, or enable state. Probe zeros the entire object and stores only the client initially. Source has exact `sizeof`/`offsetof` assertions. Full evidence: `phase4-custom-ldo-wl2868-struct-layout.md`.

# Probe contract

Exact stock order:

1. Replace the 112-byte global with zeroed state plus client pointer.
2. Print probe and `wl2864c_power_on` entry logs.
3. Get consumer `"vin1"` with `GPIOD_OUT_HIGH`; failure is logged as `vin1_en` but ignored. On success log, explicitly set logical 1, then immediately `devm_gpiod_put`.
4. Get consumer `"reset"` with `GPIOD_OUT_HIGH`. Normal error-pointer return is logged twice and returned without further cleanup.
5. On success drive logical 1, 0, 1, each followed by `usleep_range(10000,11000)`, then immediately put the descriptor.
6. `msleep(1)`.
7. Store 0x2f into `client->addr`; store 0x82 into state chip byte.
8. Emit seven `wl2864c_ldo_vout: ldo_vout=0` logs. There is no I2C access.
9. Register the miscdevice. Negative error is returned raw with no additional cleanup.
10. Log success, set ready=1, return 0.

There is no chip read, supported-ID decision, VIN2 setup, register initialization, regulator setup, clientdata assignment, or mutex setup. The branch-by-branch ownership/error ledger is in `phase4-custom-ldo-wl2868-probe-contract.md`.

# GPIO contract

The merged board DT exposes active-high `reset-gpios`; it does not expose `vin1-gpios` or a VIN2 property consumed here. Stock nevertheless requests `"vin1"` and deliberately tolerates failure. Both successful devm acquisitions are explicitly put in probe, so remove owns no GPIO. Reset is logical high-low-high with three 10–11 ms waits. VIN2 is a separate exported/global helper path: state+0x40 → `gpio_to_desc` → `gpiod_set_raw_value(!!power)`, with no request, validation, or free; normal probe leaves the integer zero.

No polarity or lifecycle semantics were copied from Sony. Full contract: `phase4-custom-ldo-wl2868-gpio-contract.md`.

# Chip variant

The code contains both families:

- state ID 0x01 → WL2864C voltage/enable helpers;
- state ID 0x82 → WL2868C voltage/enable helpers;
- any other byte → public dispatcher returns -1.

Both have seven channels at 0x03–0x09. They differ in voltage formula and bit-7 enable handling. Probe always sets 0x82 and never reads register 0x00; therefore the 0x01 branch is normally unreachable.

Board evidence is I2C bus 11, DT node address 0x29, compatible `will,wl2864c_pmu`, ID metadata `(reg 0x00,value 0x01/0x82)`, a live-bound `11-0029` snapshot, and stock's hardcoded WL2868C selector. This proves **WL2868C-intended family behavior**, not a physical-die register observation. Exact physical identity remains “not independently read,” because safety forbids a new read and the stock driver itself does not perform one. This is an evidence boundary, not an unresolved stock behavior. See `phase4-custom-ldo-wl2868-chip-variant-contract.md`.

# Voltage contract

Public input `value` is already proven microvolts by stock imgsensor call sites. Valid channels are 1–7 and map to register `0x02+ldo_num`. Let `q=trunc_toward_zero(value/100)`; if `q==0`, return without I2C. Otherwise:

| Variant | Channels | Register | nominal min/max | Step | Code before u8 truncation | Actual stock zero threshold |
|---|---|---|---|---:|---|---:|
| WL2864C | 1–2 | 0x03–0x04 | 600,000–3,787,500 uV | 12,500 uV | `(q-6000)/125` | 60,000 uV |
| WL2864C | 3–7 | 0x05–0x09 | 1,200,000–4,387,500 uV | 12,500 uV | `(q-12000)/125` | 120,000 uV |
| WL2868C | 1–2 | 0x03–0x04 | 496,000–2,536,000 uV | 8,000 uV | `(q-4960)/80` | 49,600 uV |
| WL2868C | 3–7 | 0x05–0x09 | 1,504,000–3,544,000 uV | 8,000 uV | `(q-15040)/80` | 150,400 uV |

There is no upper clamp. Above-range values and the region between the factor-ten-low guard and nominal base can wrap through low-byte truncation. Invalid helper channel returns -1. Write error is returned raw by the helper; readback always runs and its error is ignored for return. The public dispatcher discards every supported helper return and returns 0.

Stock examples: channels 1–2 use 1,100,000/1,200,000 uV; channels 3–6 use 2,800,000 uV; channel 7 uses 1,800,000 uV. Full per-channel table and encoded values: `phase4-custom-ldo-wl2868-voltage-contract.md`.

# Enable contract

Both helpers read-modify-write register 0x0e. Channel N maps to bit N−1. `enable==0` clears; any nonzero integer sets. Invalid helper channel returns 0 without I2C. Read failure maps to `-ENODEV`; write failure is returned raw.

WL2864C writes the modified read byte and returns the original `enable` on success. WL2868C computes `write_value = intermediate ? (intermediate|0x80) : 0` and returns 0 on success. The condition includes the previously read bit 7, so disabling the final low bit can still write 0x80 if bit 7 was already set. Public `will_ldo_en` discards helper results and returns 0 for supported IDs. There is no register cache or internal voltage/enable sequencing. Details: `phase4-custom-ldo-wl2868-enable-contract.md`.

# I2C contract

Only raw `i2c_transfer` is used. Read is one register-address write message followed by one one-byte read message in a single two-message transfer. Write is one two-byte `{register,value}` message. Address and adapter are read from the stored client; after probe the address is 0x2f. There is one attempt, no retry, no mutex/lock, no SMBus/regmap, and no delay inside helpers. Any nonnegative result—including short transfer—is considered success; negative results receive the exact dev-info log. Caller-specific error mapping is frozen in `phase4-custom-ldo-wl2868-i2c-contract.md`.

# Misc-device ABI

`/dev/wl2864c` uses fixed minor **250**, not dynamic minor 255. The exact 272-byte fops has only owner, llseek, read, write, and open; no release/ioctl/compat/poll/mmap.

- `open`: require ready byte, else `-ENODEV`; reset global cursor to zero.
- `llseek`: SEEK_CUR adds low 32 bits of offset to global cursor; every other whence resets it. Return existing `file->f_pos` unchanged.
- `read`: allocate 128 before validating; reject count>20; read count registers from global cursor; emit uppercase `RR VV ` (6 bytes each); ignore `copy_to_user` failure; return register count; do not advance cursor or ppos.
- `write`: reject count>128; `memdup_user`; parse positions 0/1 and 3/4 of each six-byte record with permissive nibble conversion; perform arbitrary one-byte register writes; return count. A non-multiple-of-six nonzero count can read beyond the duplicated buffer. I2C failure maps to `-ENODEV`.

The raw writer is dangerous and was not exercised. No safety gate was added because oracle-compatible behavior is retained. Full ABI: `phase4-custom-ldo-wl2868-miscdev-contract.md`.

# Lifecycle

`init_module` logs, calls `i2c_register_driver`, truncates its return to u8, logs by that byte, and returns it. Remove only deregisters misc, clears ready, and logs. It does not disable rails, modify reset/VIN, free GPIOs, clear client/chip/cursor, or clear global state. There is no shutdown callback. `cleanup_module` only calls `i2c_del_driver`; driver-core removal supplies misc cleanup. See `phase4-custom-ldo-wl2868-lifecycle-contract.md`.

# Function parity

| Metric | Result |
|---|---:|
| Function set | exact 15/15 |
| KCFI map | exact 15/15 |
| External/internal call multisets | exact 15/15 |
| Hardware constants and branch semantics | exact 15/15 |
| Size-identical | 10/15 |
| Byte-identical | 6/15 |

Byte-identical functions are `wl2864c_vin2_power`, `wl2864c_llseek`, `wl2864c_remove`, `wl2864c_open`, `init_module`, and `cleanup_module`. The nine others differ only in compiler/source-expression layout after their hardware and error semantics were recovered. Exact row ledger: `phase4-custom-ldo-wl2868-function-parity.tsv`.

# Object parity

The 25 stock named object/data symbols and four anonymous voltage arrays are all explained. Twenty-eight of 29 parity rows are byte-identical (with relocation targets normalized where needed). The sole non-identical row is generated vermagic text. Particularly:

- 112-byte state, 280-byte `i2c_driver`, 80-byte miscdevice, 400-byte OF table, 64-byte I2C ID table, and 272-byte fops are exact-sized and byte-identical;
- `.data` and important string sections are exactly identical;
- all four 28-byte voltage tables are content-identical;
- the complete 1,728-byte `__versions` section is byte-identical;
- export CRC/name/namespace/symbol entries are exact.

See `phase4-custom-ldo-wl2868-object-parity.tsv`. No hardware-significant object is unresolved.

# Exact-GKI build

Workspace: `/home/armol/kernel-work/gki-12901745-workspace`

Kernel: Linux 6.1.115-android14-11, Android GKI ab/12901745, common commit `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`.

Target: `//lieppos/custom-ldo-wl2868-recon/recon:custom_ldo_wl2868_recon` against `//common:kernel_aarch64`.

Result: `BUILD_RC=0`, compiler warnings 0, modpost/check-no-remaining warnings 0, unresolved symbols 0. Provider exports arise naturally from source and generated symvers—no fake symvers, CRC editing, or ELF patching. Closure artifact: `workspace/phase4-custom-ldo-wl2868/recon-closure-custom_ldo_wl2868.ko`; log: `recon-build-closure.log`.

Local unstamped Kleaf vermagic uses `...-maybe-dirty` rather than stock's release suffix. That is a build-release-label/signing provenance delta, not a source or hardware-behavior delta; a deployable image must use its normal stamped/signing pipeline.

# Downstream custom_ldo verification

The already-complete `//lieppos/custom-ldo-recon:custom_ldo_recon` was rebuilt against this provider: `BUILD_RC=0`, warnings 0, unresolved 0. Its imports resolve as:

- `will_ldo_vout` `0x23ec3223`;
- `will_ldo_en` `0xdd9b9ea1`.

It still exports `custom_ldo_vout` `0xfda530e0` and `custom_ldo_en` `0x239d3df2`; both forwarding functions remain byte-identical to stock. Evidence: `custom-ldo-downstream-closure-build.log` and `recon-closure-custom_ldo.ko`.

# Behavioral verifier

`kernel/scripts/phase4_custom_ldo_wl2868_verify_recon.py` is fail-closed and verifies oracle hash/size, function sets, MODVERSIONs, KCFI, exports, function call multisets, key object sizes/bytes, strings, tables/formulas, probe/GPIO order, struct assertions, fops/misc quirks, raw-I2C topology, lifecycle, clean build logs, and downstream ABI/byte identity.

Result: **`50/50 CHECKS PASSED`**. Output: `workspace/phase4-custom-ldo-wl2868/verifier-closure.txt`.

# Residual differences

No hardware-significant or ABI-significant behavior remains unresolved. Bounded non-behavioral residuals are:

1. exact original vendor source is not public;
2. nine functions are not instruction-byte-identical and five are not size-identical due recovered-source/code-generation expression differences;
3. anonymous voltage arrays occupy a different source-order location although bytes and references are equivalent;
4. local unstamped vermagic/release label differs from the stock packaged module;
5. two unused zeroed state ranges retain `UNKNOWN` names rather than invented fields;
6. physical die identity was not independently read; stock itself hardcodes software ID 0x82.

These residuals do not alter stock-observable register, GPIO, misc, lifecycle, error, or consumer ABI behavior.

# Runtime validation status

**NOT PERFORMED BY POLICY.** Closure is static/offline. No module was inserted, removed, bound, or unbound, and no misc operation was executed.

# Safety

No WL2868 register was read or written on the phone; no rail voltage/enable, reset, VIN1, or VIN2 GPIO was changed; no camera was launched for stimulation; no flash or slot operation occurred. The misc raw-write path remains explicitly prohibited for development testing.

# Evidence index

- Oracle and inventory: `phase4-custom-ldo-wl2868-stock-oracle.txt`, `phase4-custom-ldo-wl2868-stock-inventory.md`, seven stock TSV ledgers.
- Closure contracts: `phase4-custom-ldo-wl2868-{struct-layout,probe-contract,gpio-contract,chip-variant-contract,voltage-contract,enable-contract,i2c-contract,miscdev-contract,lifecycle-contract}.md`.
- Parity: `phase4-custom-ldo-wl2868-function-parity.tsv`, `phase4-custom-ldo-wl2868-object-parity.tsv`.
- Proven consumer units/calls: `phase4-custom-ldo-imgsensor-consumer-analysis.md` and associated stage TSV.
- Source/provenance: `phase4-custom-ldo-wl2868-source-candidates.md`, `phase4-custom-ldo-wl2868-reconstructed-source.c`.
- Scripts: `kernel/scripts/phase4_custom_ldo_wl2868_verify_recon.py`, `phase4_custom_ldo_wl2868_generate_parity.py`.
- Raw disassembly, ELF dumps, rebuilt modules, logs, and verifier output: `workspace/phase4-custom-ldo-wl2868/`.
- Active source tree: `/home/armol/kernel-work/gki-12901745-workspace/lieppos/custom-ldo-wl2868-recon/`.

# Final verdict

`custom_ldo_wl2868` is promoted to **`STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`** and is **FROZEN FOR RE**. The camera-power provider chain `custom_ldo_wl2868 → custom_ldo` is source-ready with exact stock consumer ABI. Deployment still requires the normal target stamping/signing and device-level validation process; neither is a reason to reopen reverse engineering.
