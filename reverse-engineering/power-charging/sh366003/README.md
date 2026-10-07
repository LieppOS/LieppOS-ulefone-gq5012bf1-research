# SH366003 pack fuel gauge ("3rd-gauge"): DONE (static)

`sh366003_fg.ko` is reconstructed to binary equivalence: 38/39 functions byte-identical, the
39th (`sh_fg_probe`) differing only by a proven register-allocation permutation; all data,
strings, imports, modversion CRCs, KCFI, modinfo and relocations (except 4 order-only addend
swaps from the same permutation) equal stock; B1 == B2. See `STATUS.md` and `parity/residuals.md`.

## Stock module identity

| item | value |
|---|---|
| file | `vendor_boot` platform ramdisk `/lib/modules/sh366003_fg.ko` — the **only** SH366003 module in any stock partition |
| load | first stage; `modules.load` line 134, `modules.load.recovery` line 132; resolved insertion 146 (after `yft_devinfo` 145) |
| sha256 / size | `527bddb4ddb11e94ed85e6969a10f807178cbb3f0fd326c8509824800a3d61a7` / 85 968 B |
| build-id | `ca3844234cba145f85adf483b0232095881ffa6e` |
| vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| srcversion | none (not emitted) |
| modinfo | license `GPL v2`, author `Sinowealth`, name `sh366003_fg`, depends `yft_devinfo`, aliases `of:N*T*Csh,sh366003`, `of:N*T*Csh,sh366003C*`, `i2c:sh366003` |
| imports | 35 (+ `module_layout`) — 32 kernel, 3 yft_devinfo; CRCs in `parity/abi-parity.tsv` / `kernel/phase4-sh366003-modversions.tsv` |
| exports | 0 |
| functions / data | 39 FUNC (28 with KCFI preamble) / 42 OBJECT |
| sections / relocations | 37 / 1513 |
| strings | `.rodata.str1.1` 194, `.rodata` 829 entries (incl. the 2142-B AFI) |
| compiler | Android clang 17.0.2 (r487747c) |

## Answers

| topic | file |
|---|---|
| hardware identity, bus, address, IRQ, topology | `hardware-topology.md` |
| DT contract | `dt-properties.tsv` |
| register / MAC map | `register-map.tsv` |
| profile, calibration, storage | `battery-profile.md` |
| power_supply + class sysfs | `power-supply-interface.tsv` |
| charging stack relationship | `charging-boundary.md` |
| YFT-DEVINFO dependency | `yft-devinfo-boundary.md` |
| lineage | `source-lineage.md` |
| board/YFT deltas and stock bugs | `yft-sh366003-deltas.md` |
| parity | `parity/` (`function-`, `data-`, `abi-`, `relocation-`, `kcfi-parity.tsv`, `residuals.md`, tool outputs) |
| source | `source/sh366003_fg.src.c` (annotated) → `source/sh366003_fg.c` (line-padded, compiled); `source/Makefile`, `source/stock-yft-devinfo.symvers` |
| scripts | `scripts/build_sh366003.sh`, `pad_lines.py`, `kcfi_preamble_parity.py`, `probe_residual_check.py` |

Earlier per-topic notes remain in `../../../kernel/phase4-sh366003-*.md`.

## Behaviour summary

- Probe: control 0x0001 must be 0x0603; create class `3rd-gauge` + 10 attributes; read
  manufacturer tag (MAC 0x40D9), SOC/V/I/T, date, name, serial, max cell voltages; format
  `fuelgauge_fw_version`; `Check_Chip_Version` (unseal, ≤5 reads of MAC 0x0046/0x004D, FCC,
  decide auto-update, seal); schedule monitor (10 s, then every 5 s) and update work (12 s);
  register psy `3rd-gauge`.
- Monitor: `primary_chg` ONLINE, SOC, VCHG, ICHG, BatteryStatus, V, I, int/ext temperature,
  SOH, cycles, RC, FCC, 8 status words + DAStatus1, one log line. Skipped while `fallback_flag`.
- Update work: gate (charger offline, SOC ≥ 11, boot mode ∉ {8,9}, trigger ≠ 0); up to two AFI
  program runs; run-state check (OEMFlag 0x00C1 → MAC 0x0021 / 0x0067, block 0x00C5); `hal_fg_init`.
- AFI interpreter: record types 1/2/3/4; COMPARE retried 2× (50 ms), then the frame is
  re-sent from the last good offset, at most 10 restarts; READ/WRITE errors abort.

## Firmware / NVM boundary

| layer | status |
|---|---|
| gauge ROM firmware (SH366003 internal MCU code) | not accessible, never read or written; outside the kernel scope |
| data flash 0x4000–0x47B8 (battery model/profile) | written only by the embedded AFI program when the gate opens; image documented by hash/structure (`battery-profile.md`) |
| calibration, learned FCC, cycle/lifetime data | gauge flash; driver reads results only (FCC, cycles, SOH); no backup/restore |
| OTP / external flash / NVRAM / firmware file | none used |
| one-time writes | manufacture date (raw reg 0x4D) via sysfs when zero |

## Corrections to earlier notes

| earlier claim | correction |
|---|---|
| "matches 2/39 functions; exact parity not closed" | 38/39 byte-identical + 1 register-allocation permutation |
| bus "400 kHz" (this README, `../hardware/charge-pump-topology.md`) | child `clock-frequency` unconsumed; adapter default 100 kHz |
| auto-update when "FCC ≤ 3500" / acceptance "FCC > 3500" (`kernel/phase4-sh366003-afi-contract.md`, `…-hardware-contract.md`) | update when FCC **< 3500** (accept ≥ 3500) |
| probe "waits 10 ms" before reading control (`…-hardware-contract.md`) | 10 ms only if the subcommand write failed |
| AFI "transfer failures get one retry after 50 ms; compare failure is fatal" (`…-afi-contract.md`) | read/write failures abort; compare is retried 2× at 50 ms, then the frame restarts (≤ 10), and update work re-runs the whole program once after 100 ms |
| PARTIAL folder "Still required: runtime firmware/AFI values and board calibration validation"; "stock `sh366003_battery.ko` … `/sys/class/power_supply/Battery*`" | AFI values are static and documented; module is `sh366003_fg.ko`, psy `3rd-gauge`; calibration validation is runtime-only |
| reset path MAC 0x0041 "when the stock V/I/termVolt test fails" | condition is unreachable with mV/\|µA\| caches (`yft-sh366003-deltas.md` D7) |

No runtime access was used; all results are offline static analysis plus earlier captures.
