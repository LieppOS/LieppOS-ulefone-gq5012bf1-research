> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> The IMX989-vs-GN1 question is resolved as a **dual-source slot** in `camera-main-identity.md`; the full stream tables are in `camera-stream-configurations.md`; actuator mapping is in `ois-vcm-lens-mapping.md`.

# Cameras (rear triple + front)

Status legend: **PROVEN** = proven on this exact device · **PROBABLY** = strong inference · **NOT PRESENT** = software-only · **UNKNOWN**.

## Hardware found

| ID | Role | Driver name (stock HAL) | Facing | Flash/torch | Array/size evidence (stock HAL) | Verdict |
|---|---|---|---|---|---|---|
| 00 | rear main | `SENSOR_DRVNAME_IMX989_MIPI_RAW` | BACK (90/90) | hasFlashUnit=1, torch AVAILABLE_OFF | physical size **13.107 × 9.830 mm**, default mode **4096×3072**, max stream **8192×6144@30** | PROVEN present; identity PARTLY CONFLICTING (see below) |
| 01 | front | `SENSOR_DRVNAME_S5KJN1_MIPI_RAW` | FRONT (270/270) | no flash unit (torch NOT_AVAILABLE) | default size `4096x2304@30` (`mDefaultSize`) | PROVEN |
| 02 | rear ultra-wide (OEM: 50 MP, 16 mm, f/2.2, 117.3°, AF) | `SENSOR_DRVNAME_S5KJN1MAIN2_MIPI_RAW` | BACK | hasFlashUnit=1 | max **8192×6144** | PROVEN |
| 03 | rear macro — **no periscope exists**; the "108 MP periscope" marketing is withdrawn (C2) | `SENSOR_DRVNAME_OV64B_MIPI_RAW` | BACK | hasFlashUnit=1 | max **8192×6144**; OIS motor on its I2C segment | PROVEN |

Support silicon per camera (live I2C + merged FDT, `evidence/local/buses-live.txt`, `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`):

| Device | Adapter | DT node | Purpose |
|---|---|---|---|
| `camera-af-main` (`mediatek,main_vcm`) | `7-000a` | i2c@11e02000 | AF VCM, main camera |
| `camera-eeprom0` | `7-0051` | i2c@11e02000 | main-module calibration EEPROM |
| `camera-af-main-two` (`main2_vcm`) | `4-000b` | i2c@11c23000 | AF VCM, module 2 |
| `camera-ois-main` (`mediatek,dw9781c`) | `4-000e` | i2c@11c23000 | **OIS driver, populated, stock-disabled** |
| `camera-eeprom1` / `camera-eeprom4` | `4-0050` / `4-0051` | i2c@11c23000 | module EEPROMs (2 on this segment) |
| `camera-af-main-four` (`main4_vcm`) | `2-000d` | i2c@11c22000 | AF VCM, module 4 |
| `camera-eeprom2` | `2-0050` | i2c@11c22000 | module EEPROM |
| `aw36515` | `6-0063` | LED "1" | dual-channel flash/IR driver (2 emitters controllable independently) |
| `aw36518` | `8-0063` | LED "3" | single-channel 1.5 A boost flash |
| `aw36518_v2` | `12-0063` | LED "2" | single-channel boost flash (v2 driver) |

4 sensors ↔ 4 VCM-class devices ↔ 4 EEPROMs ↔ 3 flash ICs ⇒ **four optically independent modules, three of them with AF**. The OIS association is UNKNOWN: the DT node is named `camera-ois-main`, but it sits on the same I2C segment as module-2's VCM; the prior inventory attributed it to the OV64B module. Needs a module BOM/optical test.

## Chip capabilities (layer 1)

| Sensor | Documented ceiling | Source |
|---|---|---|
| IMX989-class 1″ 50 MP 1.6 µm, quad-Bayer | 8K stills/8K-class video, 4K high-framerate, dual-conversion-gain (DOL) HDR, on-chip 2×2 binning + remosaic | S14 (press/aggregator; **no public datasheet** ⇒ partially UNKNOWN) |
| S5KJN1 / JN1 50 MP 0.64 µm 1/2.76″ | **4K@60**, **1080p@240**, 12.5 MP binned remosaic, Smart-ISO HDR | S12 |
| OV64B 64 MP 0.7 µm | **8K@30**, **4K@60**, 12.5 MP binned **180 fps**, **3-exposure staggered (DCG) HDR**, on-chip remosaic | S13 |
| DW9781C OIS driver | I2C 2-wire OIS AF/OIS actuator driver family (Dahua/Dongwoon), voice-coil OIS with hall feedback, ~1–2° optical shift class | C-quality (family knowledge; exact datasheet not retrieved) |
| AW88394 PA, AW36515/18 flash | see `audio.md`, `misc-hardware.md` | S09/S10 |
| MT6878 ISP | up to 200 MP single / multi-cam; stock `MTKCamHal 3.0.00000`, `mStaticSceneSupportSensorNum:4` | S06/S07 + live |

## Board configuration (layer 2)

* HAL static metadata exposes `android.lens.info.availableOpticalStabilization = [0]` (**OIS disabled**) for all four cameras, and `availableVideoStabilizationModes` = 3 entries (PREVIEW/OIS/EIS values present as `[OFF,EIS]`-class list) on the main module vs 1 entry on the front module.
* `availableStreamConfigurations` present as `int32[860]`/`int32[844]` blobs (main/rear vs front) — full per-format table not decodable from this dump ⇒ per-format ceilings UNKNOWN.
* `availableStaticCharacteristics` include P1A_RAW16 + PRIVATE + JPEG vendor streams ⇒ RAW16 path exists on the MTK P0/P1 path.
* Front module: `torchModeStatus:NOT_AVAILABLE`; rear modules: `AVAILABLE_OFF`.
* HAL tuning DB `MTK_GMM_ZSL`, `videoSDKVersion:3`, `capBurstNum:[10]` (10-frame burst/multi-frame capture), 4-sensor static scene support.

## Stock usage (layer 3)

* Photo: full-res 50 MP/64 MP stills (8192×6144 @30 stream), 10-frame burst capture enabled.
* Video: OEM spec + GSMArena both list **only 4K@30 and 1080p@30** ⇒ no slow-motion, no 4K60, no 8K in stock.
* Stabilisation: EIS only (OIS absent from HAL).
* Torch: available on 3 rear modules; used by stock flashlight + `flashlight_cooler` thermal cooler device.
* IR illumination: AW36515 exposes 2 independent channels (used for the flashlight/IR array); the stock camera HAL registers no dedicated "IR camera" role, although the vendor native stack contains AC020/UVC/IR-camera/command code (`docs/camera-thermal.md`).

## Unused / hidden capabilities

1. **OIS**: DW9781C motor is powered and bound but not exposed — a real optical-stabilisation path exists behind `availableOpticalStabilization:[0]`.
2. **Sensor headroom**: JN1-class 4K60/1080p240 and OV64B 8K30/4K60/180 fps binned modes are physically supported by the dies; **the capture (taken under a LieppOS GSI, so not a stock-app statement)** exposes only up to 4K30 ⇒ MTK sensor driver mode tables + camera app policy are the limiter, not silicon.
3. **3-exposure staggered HDR / DCG** (OV64B) and **Smart-ISO** (JN1) not surfaced through the standard `requestPipelineCharacteristics` keys in stock — multi-frame/RGB HDR is instead implemented via MTK AINR/multiframe vendor tags (`capBurstNum`, vendor extensions).
4. **4-cell remosaic** on all three rear dies (full-res 50/64 MP without quad-Bayer upscaling) — 8192×6144 stream is only 12.6 MP-class, so the 50/64 MP stills path must run through the vendor remosaic/binning path (present in MTK HAL, not exposed as a public per-format ceiling).
5. Third flash channel (`aw36518_v2` @`12-0063`) and AW36515's second independent LED — used for the multi-level auxiliary light; per-channel max current vs programmed codes never verified against datasheet (UNKNOWN).

## Alternate candidates
Sensor vendor identity for cam00 (IMX989 vs GN1/S5KGN1 vs "GN1-class clone"): PROVEN geometry = IMX989; OEM marketing text says "IMX989 GN1"; GSMArena lists 1/1.31″ 1.2 µm (neither). Module sourcing may differ by production lot ⇒ multi-sourcing cannot be excluded (hardware-variants).

## Missing information / next verification
* Decode `availableStreamConfigurations` blobs (int32 arrays) from a rooted `dumpsys media.camera -a` to list per-format ceilings.
* Runtime OIS association: enable `dw9781c` via a custom sensor driver/OIS provider hook and measure which lens group moves (or read module BOM from Ulefone service info).
* IMX989 datasheet-level ceilings (needs NDA/leaked datasheet; currently press-quality B/C).
* Per-channel flash current codes vs AW36515/AW36518 datasheet maxima.

## Correction (2026-10-07, CAMERA-OV64B closure)

* Camera 3 (OV64B) is the night-vision camera, not a macro. The kernel's
  largest mode is 4624×3472, and the HAL publishes 9216×6912 BLOB; the "max
  8192×6144" value above is wrong for this camera.
* The night-vision IR pair is `aw36518` `8-0063` (ct 0) plus `aw36518_v2`
  `12-0063` (ct 1), both flashlight part 1. The shipped `imgsensor.ko` switches
  them on at OV64B (`sensor4`) init and off at its power-off, through
  `flashlight_drvctrl(1/11)` and `(0/10)`. `aw36515` `6-0063` is the ordinary
  flash and is not part of the IR array. The "third flash channel …
  auxiliary light" reading is withdrawn.
* DW9781C "populated, stock-disabled" is superseded: physical presence is not
  evidenced and no stock path reaches it
  (`reverse-engineering/camera-stack/dw9781c-ois/`).
* Proof: `reverse-engineering/camera-stack/ov64b/`.

## Correction (2026-10-07, CAMERA-S5KJN1MAIN2 closure)

* Camera 2 (`S5KJN1MAIN2`, ultrawide) is a JN1 die (0x38E1). The driver adds 1
  to the low ID byte, giving pseudo-ID 0x38E2, and binds only on non-CTS boards.
  Its AF actuator is `main4_vcm` (DT `2-000d`, wire 0x0C). The kernel has 5
  modes: 4080×3072@30, 8160×6144@10, and two hs/slim IMX989 placeholders the HAL
  never selects. So the JN1 "4K60/1080p240" capability is not exposed in stock.
* Its kernel EEPROM hook is the 4-cell XTC/PDXTC/GGC read from `2-0050`. QSC is
  never applied.
* Proof: `reverse-engineering/camera-stack/s5kjn1main2/`.
