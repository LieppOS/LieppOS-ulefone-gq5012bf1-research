# GQ5012BF1 SH366003 fuel-gauge reconstruction

# Final classification

**BEHAVIORAL_RECONSTRUCTION_WITH_DOCUMENTED_RESIDUALS**

The ordinary telemetry path, power-supply ABI, monitor loop, YFT consumer ABI, embedded AFI image, AFI interpreter, update gates, update/recovery sequence, and exact-GKI build are statically accounted for. The result is not instruction/section/string identical and no live gauge programming was performed.

# Stock oracle

Canonical frozen oracle:

`workspace/phase4-sh366003/oracle/sh366003_fg.stock.ko`

- SHA256: `527bddb4ddb11e94ed85e6969a10f807178cbb3f0fd326c8509824800a3d61a7`
- size: 85,968 bytes
- module: `sh366003_fg`
- author: `Sinowealth`
- description: `SH SH366003 Gauge Driver`
- license: `GPL v2`
- depends: `yft_devinfo`
- vermagic: `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`
- aliases: `i2c:sh366003`, `of:N*T*Csh,sh366003`, `of:N*T*Csh,sh366003C*`
- normal vendor-boot load index: 133
- recovery load index: 131

Build ID, compiler, all source copies, module-list evidence, and hashes are in `kernel/phase4-sh366003-stock-oracle.txt`.

# Source provenance

No public exact or plausible same-driver donor was found after local NothingOSS/MiCode/vendor-tree searches and web/GitHub/Gitee-oriented searches. The only source-path provenance is the stock ELF string:

`../kernel_device_modules-6.1/drivers/power/supply/sh366003/sh366003_fg.c`

Result: `NO_PUBLIC_DONOR_FOUND`. Reconstruction is stock-oracle-led. See `kernel/phase4-sh366003-source-candidates.md`.

# RED

There was no donor to build unchanged. RED therefore records the absent-source baseline and stock requirements rather than fabricating a generic SBS donor. The stock module has 39 named functions, raw SMBus and `i2c_transfer` paths, ten `3rd-gauge` properties, two delayed works, class attributes, an embedded AFI image, and three YFT imports. See `kernel/phase4-sh366003-RED.md`.

# Hardware identity

- **CHIP = Sinowealth SH366003**
- **I2C_BUS = 9**
- **I2C_ADDRESS = 0x55**
- **DEVICE_ID_REGISTER = control register `0x00`, subcommand `0x0001`**
- **DEVICE_ID_VALUE = `0x0603`**
- **FW_VERSION = two bytes returned by MAC command `0x40d9`; captured runtime bytes unavailable**
- **AFI_VERSION = 16-bit MAC command `0x0046`; captured runtime value unavailable**
- **BATTERY_PROFILE_VERSION = MAC command `0x004d`, required value `0x5a93` (packed date 2025-04-19)**

The probe writes subcommand `0x0001` to register `0x00`, waits 10 ms, reads register `0x00`, and accepts only `0x0603`. Silicon revision is not separately exposed by the stock module. See `kernel/phase4-sh366003-hardware-contract.md`.

# DT contract

Live stock path:

`/soc/i2c@11c24000/sh366003@55`

Exact captured node properties are `compatible = "sh,sh366003"`, `reg = <0x55>`, `status = "okay"`, and `clock-frequency = <400000>`. The module consumes no gauge-specific DT tuning property. It uses OF matching and, in update work only, reads `/chosen` with `/chosen@0` fallback and `atag,boot` to block update in boot modes 8/9. See `kernel/phase4-sh366003-dt-contract.md`.

# yft_devinfo provider boundary

Stock `yft_devinfo` remains authoritative. The reconstruction is linked through ordinary `KBUILD_EXTRA_SYMBOLS`, not CRC patching, and naturally emits:

| Symbol | Stock CRC | Prototype/purpose |
|---|---:|---|
| `fuelgauge_fw_version` | `0x8c280260` | `extern char fuelgauge_fw_version[30]`; formatted probe version string |
| `yft_fuelgauge_device_add` | `0xf5752941` | `int (struct i2c_driver *, int)`; called at module init with `&sh_fg_driver, 0` |
| `yft_set_fuelgauge_device_used` | `0x82093a2e` | `int (char *, int)`; called after successful probe with `"sh366003", 1` |

Provider KCFI words are documented where applicable; direct consumer calls require no indirect CFI check. The rebuilt module is not coupled to the incomplete reconstructed YFT provider. See `kernel/phase4-sh366003-yft-devinfo-boundary.md`.

# Register map

The complete accessed-address table is `kernel/phase4-sh366003-register-map.tsv`. Core telemetry registers are:

| Register | Meaning | Access |
|---:|---|---|
| `0x00` | control/subcommand, unseal, activation | word R/W |
| `0x06` | external pack temperature | word read |
| `0x08` | pack voltage | word read |
| `0x0a` | battery status | word read |
| `0x0c` | signed pack current | word read |
| `0x10` | remaining capacity | word read |
| `0x12` | full-charge capacity | word read |
| `0x28` | internal temperature diagnostic | word read |
| `0x2a` | cycle count | word read |
| `0x2c` | relative SOC | word read |
| `0x2e` | gauge SOH diagnostic | word read |
| `0x30` | charging voltage | word read |
| `0x32` | charging current | word read |
| `0x3e` | MAC command/data-flash window | word/block R/W |
| `0x40` | MAC response data | block read |
| `0x60` | MAC checksum/length commit | block write |

The monitor also reads MAC commands `0x0050` through `0x0057` and block `0x0071`; update/recovery uses `0x0021`, `0x0030`, `0x0041`, `0x0045`, `0x0046`, `0x004c`, `0x004d`, `0x004e`, `0x0060`, `0x0067`, `0x00c1`, `0x00c5`, and `0x40d9`.

# Unit/scaling contract

Stock intentionally mixes standard and nonstandard power-supply units:

| Value | Gauge raw to cache/public value |
|---|---|
| RSOC | unsigned word unchanged; percent |
| Volt | unsigned word unchanged; **mV** (`8397`), although property is `VOLTAGE_NOW` |
| Curr | signed 16-bit word; stock stores `abs((s16)raw) * 1000` **uA**; monitor log divides by 1000 to mA and separately preserves raw sign for logging |
| Temp | register `0x06` in 0.1 K; subtract `2731`; **0.1 °C** (`375` = 37.5 °C) |
| SoH | register `0x2e` unchanged; percent in monitor diagnostics; not a power-supply property |
| cycnt | register `0x2a` unchanged; cycles |
| FCC | register `0x12` unchanged; **mAh** (`8594`), although exposed as `CHARGE_FULL_DESIGN` |
| remaining capacity | register `0x10` unchanged; mAh; monitor-only |

See `kernel/phase4-sh366003-units.md`.

# Power-supply ABI

`power_supply_desc.name = "3rd-gauge"`, type `Battery`. Exact ordered property list:

1. `POWER_SUPPLY_PROP_STATUS`
2. `POWER_SUPPLY_PROP_PRESENT`
3. `POWER_SUPPLY_PROP_VOLTAGE_NOW`
4. `POWER_SUPPLY_PROP_CURRENT_NOW`
5. `POWER_SUPPLY_PROP_CAPACITY`
6. `POWER_SUPPLY_PROP_TEMP`
7. `POWER_SUPPLY_PROP_CHARGE_FULL_DESIGN`
8. `POWER_SUPPLY_PROP_TECHNOLOGY`
9. `POWER_SUPPLY_PROP_CYCLE_COUNT`
10. `POWER_SUPPLY_PROP_HEALTH`

There is no `set_property` or writable power-supply property and no `power_supply_changed()` call. Error reads retain the prior cache. Status is charging while `primary_chg` ONLINE is true, full at SOC 100, otherwise discharging. See `kernel/phase4-sh366003-power-supply-contract.md`.

# Monitor loop

- first queue: 2,500 jiffies = 10 s at stock `HZ=250`
- recurrence: 1,250 jiffies = 5 s
- order: `primary_chg` ONLINE; SOC; `0x30`; `0x32`; `0x0a`; voltage; current; internal temperature; external temperature; SOH; cycle count; remaining capacity; FCC; MAC `0x0050..0x0057`; block `0x0071`; signed-current diagnostic; log; requeue
- cache updates occur only on successful reads
- `external_power_changed` queues the same monitor immediately

See `kernel/phase4-sh366003-monitor-contract.md`.

# Battery topology

Proven software chain:

`SH366003 @ i2c-9/0x55` → `3rd-gauge` → stock `mt6375-battery.ko`/charging modules via `power_supply_get_by_name("3rd-gauge")` → public `battery` power supply → Android battery framework.

The live `battery` node mirrors SH values with expected unit normalization (`8397` mV → `8397000` uV; `8594` mAh → `8594000` uAh). The MT6375/PMIC gauge remains present. An approximately 8.4 V pack strongly indicates a series multi-cell/2S pack, but physical wiring and division of coulomb-counting authority remain unproven without a schematic. See `kernel/phase4-sh366003-battery-topology.md`.

# Firmware / AFI assets

No external SH366003 `.bin`, `.hex`, `.afi`, `.fw`, `.cfg`, or `.dat` asset was found. The authoritative profile is embedded:

- ELF object: `sinofs_afi_data`
- preserved path: `workspace/phase4-sh366003/oracle/sinofs_afi_data.stock.bin`
- size: 2,142 bytes
- SHA256: `4888c5bc4b847ec6c118cd7bd334cbcffbf52c5fa2bf8f8660c3ac65e03359e1`
- exact decoded records: `kernel/phase4-sh366003-afi-records.tsv`

See `kernel/phase4-sh366003-firmware-assets.md`.

# AFI update state machine

Static recovery is complete at the transaction/state-machine level:

1. probe reads current MAC `0x0046`, profile/date `0x004d`, and FCC;
2. automatic update is requested when profile is not `0x5a93` or FCC is not above 3,500 mAh; all-zero version reads become error state `-1`;
3. update work starts after 3,000 jiffies (12 s);
4. it refuses update while `primary_chg` reports online, SOC is below 11%, or boot mode is 8/9;
5. current telemetry is copied to fallback cache and update mode is marked;
6. unseal/full-access sequence writes `0x5678`, `0x1234`, `0xcdef`, `0x90ab` to control register `0x00`, with stock delays/status checks;
7. `file_decode_process` interprets the embedded 2,142-byte image;
8. image records: 209 total = 104 writes, 104 waits, one compare;
9. all transfers address `0x55`; writes target `0x3e` (52), `0x60` (51), and `0x00` (one);
10. 51 monotonically increasing data-flash addresses span `0x4000..0x47b8`;
11. waits are 51×2 ms, 51×5 ms, and 2×1,500 ms (3,357 ms encoded total);
12. block commit values carried by the `0x60` records are the stock checksum/length words and are preserved byte-for-byte rather than regenerated;
13. final activation writes control `0x0045`, waits 1,500 ms, requests `0x0046`, waits 1,500 ms, and compares four bytes to `46 00 d3 8c`;
14. transfer/compare retry and whole-image retry paths are reconstructed; update work retries the decoder once after 100 ms;
15. recovery rereads telemetry and `0x00c1`, conditionally issues stock control commands `0x0041`, `0x0021`, and `0x0067`, reads block `0x00c5`, seals with `0x0030`, and reruns `hal_fg_init`;
16. fallback mode and force flags are cleared on exit; errors retain explicit failure status/logging.

No update, reset, flash, NVM, calibration, or profile transaction was executed. See `kernel/phase4-sh366003-afi-contract.md`.

# I2C transaction contract

- telemetry uses `i2c_smbus_read_word_data`/`write_word_data`; SMBus word payloads are little-endian
- direct command encoding uses low register byte
- command bit 27 selects MAC: write low 16-bit subcommand to `0x3e`, then read `0x40`
- command bit 26 selects control: write low 16-bit subcommand to `0x00`, wait 10 ms, then read `0x00`
- block MAC reads use two raw `i2c_msg` operations
- AFI writes use one raw message containing register plus payload; compare uses write-register then read-data messages
- mutexes serialize telemetry, update/calibration, and block operations

All update/control writes are marked `DO_NOT_RUNTIME_TEST`. See `kernel/phase4-sh366003-i2c-contract.md`.

# Struct layout

The stock probe allocates 1,064 bytes. Proven offsets include device/client pointers, five mutexes, the 16-entry command table, monitor delayed work at `0x148`, update delayed work at `0x1d0`, normal/fallback telemetry caches, update flags, power-supply descriptor/config, charger state, SOH/cycle/remaining/FCC diagnostics, charging values/status, manufacturer bytes, serial, packed date and decoded date fields. Unknown padding remains unnamed. See `kernel/phase4-sh366003-struct-layout.md`.

# PM behavior

There are no suspend/resume callbacks, wakeup-source objects, or reboot notifier. `remove` is an exact no-op; `shutdown` only conditionally logs. Stock does not cancel either delayed work in remove/shutdown. The reconstruction preserves this behavior rather than adding lifecycle imports. See `kernel/phase4-sh366003-pm-contract.md`.

# Userspace integration

No vendor/system binary contains a direct `3rd-gauge` or `sh366003` literal. Kernel consumers do: `mt6375-battery.ko`, `mt6375-charger.ko`, `mtk_charger_framework.ko`, `mtk_pd_charging.ko`, `mtk_pep.ko`, and `mtk_pep50.ko`. `mt6375-battery.ko` reads `3rd-gauge` in `battery_psy_get_property`, `battery_update_psd`, `battery_update`, `battery_update_routine`, and daemon handling; charger framework `get_uisoc` reads capacity. SELinux contains exact sysfs labels for the `9-0055/power_supply/3rd-gauge` path. `fuelgauged` uses the MediaTek gauge library and has no direct SH literal. See `kernel/phase4-sh366003-userspace-contract.md`.

# Exact-GKI build

Workspace: `/home/armol/kernel-work/gki-12901745-workspace`

Target: `//lieppos/sh366003-recon:sh366003_recon`, kernel build `//common:kernel_aarch64`, Linux `6.1.115-android14-11`, common commit `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`.

- BUILD_RC: **0**
- compiler warnings: **0**
- modpost warnings: **0**
- unresolved symbols: **0**
- fake providers: **none**
- CRC patching/ELF editing: **none**

The exact stock YFT CRC file is supplied with `KBUILD_EXTRA_SYMBOLS`. Build log: `workspace/phase4-sh366003/recon/exact-gki-build.log`.

# Structural comparison

- functions stock/rebuilt/shared: **39 / 39 / 39**
- stock-only/rebuilt-only: **0 / 0**
- size-identical: **3**
- byte-identical: **2**
- undefined imports: **35 / 35, exact set**
- MODVERSION entries: **36 / 36, exact map**
- global KCFI entries: **8 / 8, exact map**
- `.rodata`: **2,728 / 2,728 bytes**

Full details: `kernel/phase4-sh366003-structural-comparison.md`.

# Behavioral verifier

`kernel/scripts/phase4_sh366003_verify_recon.py` is fail-closed and offline. It validates the stock hash, exact import and 36-entry MODVERSION maps, all three YFT CRCs, named function set, KCFI map, exact embedded AFI bytes and full record structure, data-flash progression, final verification tail, hardware/DT constants, property order, scaling, monitor timing/call contract, register/MAC constants, sysfs names, and AFI safety gates.

Final result: **527/527 checks passed; BEHAVIORAL_VERIFIER=PASS**.

# Runtime correlation

Frozen logs match the recovered loop:

`RSOC=79, Volt=8398, Curr=83, Temp=375, SoH=94, cycnt=26, Rc=6715, FCC=8594, Vchg=8900, Ichg=9500, BatS=0x0080`

The read-only power-supply snapshot independently reports SOC 79, voltage 8397, current 13000 uA, temperature 375, FCC 8594, and cycle count 26. The 5-second log cadence matches 1,250 jiffies. See `kernel/phase4-sh366003-runtime-correlation.md`.

# Residual differences

1. Reconstruction is not instruction-byte, function-size, relocation, full-string, `.data`, or `.bss` identical; only two functions are byte-identical.
2. Exact live two-byte FW string and `0x0046` AFI value were not captured; their read/format mechanisms are exact.
3. Silicon revision is not separately exposed by stock code.
4. Meanings of proprietary data-flash fields inside the exact image are not named without a datasheet; their addresses, payloads, checksums, waits, ordering, and verification are exact.
5. Physical battery wiring remains inferred, not schematic-proven.
6. Rebuilt vermagic contains the workspace suffix `maybe-dirty`; KMI/MODVERSIONs are exact.
7. No runtime load or hardware behavior was tested because doing so would violate the safety boundary.

# Safety

Default development build sets `SH366003_ALLOW_AFI_PROGRAMMING=0`. The exact recovered algorithm and image compile into the module, but `file_decode_process`, `force_upgrade`, and manufacturing-date programming fail closed before any dangerous write. Oracle-parity programming mode requires the explicit compile-time value `SH366003_ALLOW_AFI_PROGRAMMING=1`; it was not built for deployment or run.

Ordinary read-only telemetry, probe identity reads, power-supply behavior, and monitor behavior are not altered by the gate.

# Runtime-validation status

**STATIC/OFFLINE ONLY.** No live register write, AFI trigger, reset, NVM operation, bind/unbind, module insertion/removal, sysfs write, flash, reboot, or slot switch was performed.

# Evidence index

- stock inventory: `kernel/phase4-sh366003-stock-oracle.txt`
- ELF inventories: `kernel/phase4-sh366003-{functions,objects,imports,exports,modversions,relocations,strings}.tsv`
- source/RED: `kernel/phase4-sh366003-source-candidates.md`, `kernel/phase4-sh366003-RED.md`
- contracts: `kernel/phase4-sh366003-{hardware,dt,yft-devinfo,units,power-supply,monitor,battery-topology,afi,i2c,struct-layout,pm,userspace,runtime-correlation}*.md`
- register map: `kernel/phase4-sh366003-register-map.tsv`
- AFI records/assets: `kernel/phase4-sh366003-afi-records.tsv`, `kernel/phase4-sh366003-firmware-assets.md`
- reconstruction source: `kernel/phase4-sh366003-recon/`
- verifier: `kernel/scripts/phase4_sh366003_verify_recon.py`
- structural comparison: `kernel/phase4-sh366003-structural-comparison.md`
- preserved oracle/rebuilt artifacts: `workspace/phase4-sh366003/`

# Final verdict

The stock consumer ABI and all ordinary SH366003 telemetry behavior are reconstructed, the firmware/profile image and update interpreter/state machine are statically recovered byte-for-byte/transition-for-transition, exact stock YFT MODVERSIONs are produced naturally, and the exact-GKI build/verifier pass. Because full binary structure, proprietary data-flash field names, captured live FW/AFI values, and physical wiring are not exact, the defensible final classification is **BEHAVIORAL_RECONSTRUCTION_WITH_DOCUMENTED_RESIDUALS** rather than COMPLETE/exact-source identity.
