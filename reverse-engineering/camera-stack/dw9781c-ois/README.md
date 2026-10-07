# DW9781C-OIS — closure (2026-10-07, static)

Workspace component: `Reverse Engineer - PARTIAL/DW9781C-OIS` → **DONE**.
Earlier notes: `../notes/dw9781c-ois.md`, `../README.md` §5,
`qwen_hardware/verification/findings/ois-vcm-lens-mapping.md`.

## Selection log

SELECTED TARGET: `DW9781C-OIS` (verified present in `Reverse Engineer - PARTIAL/`
and listed PARTIAL in `REVERSE-ENGINEERING-STATUS.md` before work began).

WHY: leaf component, stock module already shown to come from an unmodified
NothingOSS source, exact GKI toolchain and donor tree available locally, and the
only recorded blocker was one hardware question. The remaining questions could
be answered from stock binaries.

CURRENT BLOCKERS (as recorded): (1) "physical lens association (OV64B vs
IMX989) UNKNOWN without teardown/actuation"; (2) "no HAL consumer exists"
(stated, not proven exhaustively); implicit (3) parity had no B1==B2 run and
left `.modinfo`/relocation-order/addrsig differences unexplained.

## Scope

The DW9781C OIS controller as the stock firmware ships it: DT client, kernel
driver `dw9781c.ko`, its power/pin/clock use, register protocol, kernel
interfaces (V4L2 subdev, hf_manager sensor), every stock userspace path that
could reach it, and what LieppOS has to do with it. Out of scope: the chip's
internal firmware/servo algorithm, and whether a DW9781C is physically fitted
and to which lens (hardware only; see Boundaries).

## Result

| item | result |
|---|---|
| lineage | **DIRECT_SOURCE_MATCH** — NothingOSS MT6878 `device_modules/drivers/misc/mediatek/lens/ois/dw9781c/dw9781c.c` (sha256 `2391c3b1…`), unmodified |
| B1 == B2 | `dw9781c.o`, `dw9781c.ko`, stripped `.ko` byte-identical (`scripts/build_b1_b2.sh`) |
| stock vs rebuild | **58 208 / 58 208 bytes; only difference = the 20-byte GNU build-id** (`parity/dw9781c-parity.tsv`) |
| functions / data | 19/19 byte-identical (name, size, bytes) / 31/31 objects |
| KCFI | 19/19 type words |
| imports / exports | 37/37 UND / 0 exports |
| modversions | 38/38 `__versions` (name, CRC) |
| relocations | 1051/1051 (section, offset, type, symbol+addend), same order |
| strings / sections / symtab | 52/52 / 43/43 headers / 180/180 ordered symbols |
| `.modinfo` | identical, incl. `vermagic=6.1.115-android14-11-g945dff7bc1bf …`, `depends=hf_manager`; no `srcversion` on either side |
| I2C reachability | probe, runtime-PM, subdev open/close: **no bus access**. Only `S_OIS_INIT/UNINIT` ioctls and hf_manager `OIS1` enable/sample/custom_cmd reach `i2c_transfer` (`evidence/dw9781c-kernel-reachability.tsv`) |
| stock consumers | **none can reach the chip** (see "Stock behaviour") |

Residual: the build-id is computed by `ld.lld` over the unstripped module,
whose DWARF contains absolute build paths, so it cannot match the vendor's.
That is a provenance/debug-info residual, not a behavioural one.

## Interface (stock image)

* DT (live tarball, `i2c@11c23000` = i2c-4): `camera-ois-main@e { compatible =
  "mediatek,dw9781c"; reg = <0x0e>; rst-supply = <&camera_common_dovdd>;
  port/endpoint -> mtk-composite-v4l2-2 port@3 }`. No `vdd-supply`, no
  pinctrl, no clocks. `camera-common-dovdd` is a `regulator-fixed` 1.8 V with
  no enable GPIO, so `regulator_enable()` here switches nothing physical.
* Driver: probe forces `client->addr = 0x14>>1 = 0x0A` (sysfs name stays
  `4-000e`); `devm_regulator_get("vdd")` → dummy, `"rst"` → the fixed regulator;
  `pio_names[]` and `clk_names[]` are empty (all entries commented out).
* V4L2 subdev (`MEDIA_ENT_F_LENS`, registered via the composite lens notifier
  `mtk-composite-v4l2-2`, alias `main_ois_cam1_endpoint`): ioctls
  `0xC00856C2` S_OIS_MODE (log only), `0xC00856C3` G_OIS_POS_INFO (zero-filled
  `OisInfo`, no I2C), `0xC00456C7` S_OIS_INIT → `dw9781c_init()`,
  `0xC00456C8` S_OIS_UNINIT → `dw9781c_release()`.
* hf_manager device `dw9781c`, sensor `ois1`, type `SENSOR_TYPE_OIS1` (74),
  polling, sync bus. `enable(1)` queues `ois_init_fx` (power_on + init);
  `enable(0)` waits ≤1 s for it, releases and powers off; `sample` reads gyro,
  target and hall (unless locked by `fixmode`); `custom_cmd` 1/6 lock/unlock,
  3 manual target.
* Register protocol and the NVM-store hazard in `dw9781c_init()`: unchanged
  from `../notes/dw9781c-ois.md` (no firmware download compiled in).

## Stock behaviour (proven, `scripts/dw9781c_reachability.py`, all checks OK)

1. HAL OIS driver: `libcameracustom.lens.so` `ois_list_0..5` each contain only
   `{0xFFFF, "Dummy"}` → `OISDrv` never resolves a subdev name.
2. Sensor-provider path: the camera stack selects the OIS sensor type from
   static metadata `com.mediatek.eisfeature.availableOisModes` (0x80070004).
   `FeatureSettingPolicy::emplaceStreamData`, `EisHalImp::Init` and
   `P1NodeImp::check_config` all map mode *m* ∈ {3..6} to
   `eSensorType = m + 10`, anything else to 13. `SensorProviderService::mapSensorType`:
   13→`OIS`(73), 14→`OIS2`(75), **15→`OIS1`(74)**, 16→`OIS2`(75). So only
   mode **5** can reach the DW9781C.
3. `libmtkcam_metastore.so` per-sensor values: IMX989 **3**, OV64B **6**,
   S5KJN1 / S5KJN1MAIN2 none (→13). Matches the runtime dump
   (camera 0 = 3, camera 3 = 6). No stock sensor uses mode 5; the MTK
   reference `IMX758`/`IMX758LITE` entries (5) are the only ones that would.
   The 13/16 requests go to `OIS`(73) and `OIS2`(75). No stock kernel module
   registers either (only `dw9781c.ko` carries an `ois*` hf sensor). Whatever
   answers them, they cannot route to the DW9781C.
4. No call to `SensorProvider::{enableSensor, …}` anywhere in
   `/vendor/lib64/mt6878` passes a literal eSensorType 15. The dynamic sites
   take their type from that same metadata mapping.
5. No ELF in `/vendor` or `/odm` encodes `S_OIS_INIT` or `S_OIS_UNINIT`.
   `G_OIS_POS_INFO` appears only in `libcam.hal3a.oisdrv.so` (unreachable, see 1)
   and `libcam.hal3a.tofdrv.so`, and it does no I2C anyway.
6. Android sensor list (frozen capture): no OIS sensor exported.

**Net:** stock loads the module, binds `4-000e`, registers `/dev/v4l-subdevN`
and the hf `ois1` sensor, and **never issues a single I2C transaction to the
DW9781C**. `availableOpticalStabilization = [0]` on every camera is the
intended configuration, not a bug.

## Board / ODM deltas versus the MediaTek reference camera DT

NothingOSS `cust_mt6878_alpha_camera_v4l2.dtsi` (reference) vs GQ5012BF1:

| reference | GQ5012BF1 |
|---|---|
| `&i2c7 { main2_vcm@b, sensor4 (imx758lite), eeprom4, camera-ois-main@e }` | the same block on **i2c-4**, sensor4 = **ov64b** |
| OIS node `vdd-supply = <&rt5133_ldo1>` | **removed** (dummy `vdd`) |
| sensor4 `oisvdd-supply = <&rt5133_ldo1>`, `oisen` pinctrl | `oisvdd-supply` **removed**; `oisen` pinctrl kept (GPIO3) but never selected: the stock OV64B pw_seq has no OIS step |
| sensor0 donor pw_seq has OISVDD 3.1 V | stock IMX989 pw_seq has no OIS step; `oisvdd` pinctrl (GPIO22) is never selected |
| IMX758 `availableOisModes = 5` (→ DW9781C) | OV64B = 6 (no provider), all `ois_list` = Dummy |

So the ODM kept the reference cam4 OIS node and module, removed every OIS power
connection, and pointed every OIS consumer away from it.

## Boundaries (external to this component)

* **Physical population and lens.** Binding `4-000e` touches no hardware.
  Nothing in stock ever addresses 0x0A on i2c-4, and no retail spec lists OIS.
  So whether a DW9781C is fitted, and on which lens, cannot be observed from
  stock software. The only static hint is DT authorship: the node sits in the
  inherited reference cam4 block, which is now OV64B. That is a hint, not proof.
  It is a hardware/teardown fact and affects no stock behaviour.
* DW9781C on-chip firmware and servo/gyro algorithm: proprietary and inside
  the chip. The driver only reads FW_VER/FW_DATE.
* hf_manager core (`hf_manager.ko`) and MTK camera HAL internals belong to
  other components (`SENSOR-HUB` transport, `CAMERA-HAL-ISP`).

## LieppOS contract

* **Stock parity:** build the unmodified source with `scripts/build_b1_b2.sh`
  (same flags, `-faddrsig`, `--strip-debug`, hf_manager CRCs from the stock
  import table). The result is byte-identical apart from the build-id. Load it
  after `hf_manager.ko`, and keep the DT node as above.
* **Equivalent minimal port:** leaving out `dw9781c.ko` and the DT node changes
  no observable stock behaviour, because no consumer exists. The only side
  effects of shipping it are a `/dev/v4l-subdevN` lens entity and the hf
  `ois1` sensor slot.
* **Enabling OIS** is new feature work, not reverse engineering. It needs
  hardware confirmation of the part and its lens, real VDD and coil rails
  (stock provides none), an `ois_list` entry, `availableOisModes = 5` for that
  sensor, and HAL tuning. Warning: `dw9781c_init()` can write the chip's
  calibration NVM.

## Runtime validation only (not performed)

A read-only check of i2c-4 address 0x0A with the camera rails on would show
whether the part is fitted. Lens ownership would need an actuation test. Both
are hardware validation; neither changes the software contract above.

## Files

* `scripts/build_b1_b2.sh`, `scripts/dw9781c_parity.py` → `parity/dw9781c-parity.tsv`
* `scripts/dw9781c_reachability.py` → `evidence/dw9781c-kernel-reachability.tsv`,
  `evidence/dw9781c-userspace-reachability.tsv`, `evidence/dw9781c-reachability-run.txt`
* `stale-claims.md`
