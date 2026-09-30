# U4 - OIS / VCM / lens mapping

**Current claim:** DW9781C bound at i2c `4-000e`, node named `camera-ois-main`; lens association unknown; HAL reports OIS disabled.

**Previous confidence:** POSSIBLE (fitted but unassociated).

**New evidence**
* Full actuator map from the live device tree:
  | Bus | Device | Compatible | Serves |
  |---|---|---|---|
  | i2c-7 (`11e02000`) | `camera-af-main@0a` | `mediatek,main_vcm` | sensor0 (main) |
  | i2c-4 (`11c23000`) | `camera-af-main-two@0b` | `mediatek,main2_vcm` | sensor1 / sensor4 bus |
  | i2c-4 (`11c23000`) | `camera-ois-main@0e` | `mediatek,dw9781c` | OIS controller |
  | i2c-2 (`11c22000`) | `camera-af-main-four@0d` | `mediatek,main4_vcm` | sensor2 bus |
* **`sensor0` (main) is the only sensor whose power sequence owns OIS rails**: its `pinctrl-names` list contains `oisvdd_off` / `oisvdd_on`. No other sensor node has an `oisvdd` state.
* `sensor4` (OV64B) has `oisen_off` / `oisen_on` - an enable-line state, not a supply state.
* The camera LDO PMIC candidates both provide a dedicated OIS rail: **WL2864C** (fitted at i2c `11-0029`) has a `VDDOIS` channel; RT5133 provides VAF.
* `camera-ois-main@0e`'s only supply reference is `rst-supply -> odm/camera-common-dovdd`, i.e. the controller shares the common camera digital I/O rail; it carries no sensor phandle.
* `vendor_dlkm` ships `dw9781c.ko`, `main_vcm.ko`, `main2_vcm.ko`, `main3_vcm.ko`, `main4_vcm.ko` and `sub_vcm.ko`; `main3_vcm`/`sub_vcm` have **no** DT client - they are unused ODM options.
* HAL: `android.lens.info.availableOpticalStabilization = [0]` on **all four** cameras; `availableVideoStabilizationModes = [0,1,2]` (EIS) on cameras 0 and 1, `[0]` on 2 and 3.

**Contradicting evidence**
The DW9781C sits on i2c-4 together with sensor1/sensor4, **not** on i2c-7 with sensor0. Bus adjacency therefore points away from the main module, while the `oisvdd` power sequence and the node name point at it. Neither signal is conclusive on its own: OIS controllers are frequently routed to a different I2C segment than their sensor.

**Internet sources:** VI14 (WL2864C VDDOIS channel).

**Local evidence:** VL12, VL13; `../evidence/live-devicetree-extracts.md`.

**Read-only live evidence:** camera static metadata and bus bindings from the frozen capture.

**Final conclusion**
* A **DW9781C OIS controller is fitted and successfully bound** - that part is settled.
* **Three VCM/AF actuators are fitted**, one per rear optical path (`main_vcm`, `main2_vcm`, `main4_vcm`); the front camera has no VCM node of its own.
* **Physical lens ownership is unresolved.** Sensor0's pinctrl group switches `oisvdd`, sensor4's switches `oisen`, and `camera-ois-main@e` shares i2c-4 with sensor1 + sensor4 while sensor0 is on i2c-7. The ODM node name is not enough to assign the actuator to a lens.
* **Stock exposes no OIS at all**: every camera reports `availableOpticalStabilization = [0]`, so the fitted controller is unused by the Android camera API.

**Final confidence:** DW9781C fitted + bound = **PROVEN**. Three AF VCMs fitted = **PROVEN**. Which lens owns the OIS actuator = **UNKNOWN / TEARDOWN_REQUIRED**. OIS unavailable through the captured vendor camera HAL = **PROVEN**.

**Remaining uncertainty:** definitive association needs either the module BOM/EEPROM, a teardown, or a controlled actuator test (move the OIS and observe which image path shifts) - none of which is safe or possible without the device.

**Impact on final inventory:** YES - the actuator map is added. Capability matrix OIS row refined. Hidden-capability item 1 keeps its rank but the association caveat is made explicit.

**Answers:** (1) controller fitted and bound, 3 VCMs; (2) which optical module it drives; (3) partially; (4) no - needs actuation, which is not read-only; (5) no; (6) yes, or an EEPROM/BOM read; (7) DW9781C present, lens assignment unresolved; (8) UNKNOWN for the mapping, PROVEN for presence; (9) yes; (10) yes; (11) yes - false lens certainty removed.

## Second-pass update (2026-09-08)

* Runtime metadata (VL27): `LENS_INFO_AVAILABLE_OPTICAL_STABILIZATION = [0]` (OFF only) on **all four**
  logical cameras, and MediaTek's `com.mediatek.eisfeature.availableOisModes` + `com.mediatek.3afeature`
  `oisdata` pair exist as separate OIS plumbing. "Stock HAL exposes no OIS mode" is now confirmed from two
  metadata layers, and no OEM/retail source lists OIS for this model (VI1, VI5, VI7, VI25, VI27).
* The OIS power chain is fully traced: bound `dw9781c` at `camera-ois-main@e` takes
  `camreg = <&mt6363_vcm3 1250000 &sensor_dvdr 1200000 2800000 1800000>` with
  `VDD 1.2 V / ACCURACY 3.2 V / HALL1VDD 2.8 V / HALL1VDD_IO 1.8 V / rvdd_max 2.85 V`, while the
  the bound **WL2864C/WL2868C-family camera LDO PMIC owns `ois-en-gpios = <133>`** (L21, VI28). The hardware path is complete and
  merely un-advertised by the HAL.
* Ambiguity deliberately preserved: sensor0's pinctrl group has `oisvdd_on/off`, sensor4's has
  `oisen_on/off`; the bound OIS actuator shares `i2c-4` with sensor1 + sensor4 while `main_vcm`/sensor0 sit
  on `i2c-7`. Bus sharing alone cannot decide which optical module carries the gimbal, so the physical
  assignment stays **UNKNOWN / TEARDOWN_REQUIRED**.
