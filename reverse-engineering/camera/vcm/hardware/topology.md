# Camera VCM / AF actuators — topology and association

## Result

Three AF actuators, all speaking one **DW9800W-class protocol** (lens_id `0x9800`),
each at 7-bit address **`0x0C` on its sensor's own I2C bus**. The front camera
is fixed-focus. Per-camera table: [`lens-association.tsv`](lens-association.tsv).

| camera | sensor (node) | bus | actuator (effective) | kernel subdev | AF rail |
|---|---|---|---|---|---|
| 0 | imx989 (`sensor0@10`) | i2c-7 | `7-000c` | `main_vcm` (DT `camera-af-main@a`) | WL2864C ch 5, 2.8 V |
| 1 | s5kjn1 (`sensor1@10`) | i2c-4 | **none — fixed focus** | — | — |
| 2 | s5kjn1main2 (`sensor2@10`) | i2c-2 | `2-000c` | `main4_vcm` (DT `camera-af-main-four@d`) | WL2864C ch 6, 2.8 V |
| 3 | ov64b (`sensor4@10`) | i2c-4 | `4-000c` | `main2_vcm` (DT `camera-af-main-two@b`) | WL2864C ch 5, 2.8 V |

## How the association is proven (four independent channels per camera)

1. **DT bus co-location.** Each lens node sits on the same I2C controller as
   exactly one sensor with AF (i2c-7: sensor0 + `main_vcm`; i2c-2: sensor2 +
   `main4_vcm`; i2c-4: sensor4 + `main2_vcm`). No sensor carries a lens phandle;
   lens nodes link only to the `mtk-composite-v4l2-2` media aggregator (ports 0..2,
   port 3 = `camera-ois-main@e`).
2. **HAL lens table** (`libcameracustom.lens.so`, `vcm_list_0`): sensor_id →
   kernel subdev name. `0x989`/`0x988`/`0x8e1` → `main_vcm`, `0x38e2` → `main4_vcm`,
   `0x566442` → `main2_vcm`. Sensor ids from the stock imgsensor data.
   The HAL opens the subdev **by name**, so this is the authoritative software link.
3. **Sensor power sequence** (stock imgsensor data, binary-exact): `HW_ID_AFVDD`
   (id 3) at 2.8 V in imx989, s5kjn1main2 and ov64b; **absent** in s5kjn1.
   The DT `custom_afvdd` channel exists on sensor0/2/4 only.
4. **Runtime static metadata** (stock capture): cameras 0/2/3 advertise
   `afAvailableModes = [0..4]` and `minimumFocusDistance` 6.67/1.0/1.0 D;
   camera 1 advertises `[0]` and `0` (fixed focus).

## Effective address ≠ DT `reg`

`main_vcm_init()` does `client->addr = g_vcmconfig.slave_addr >> 1` with the value
pushed by the HAL (`0x18` → **`0x0C`**). The DT addresses `0x0a/0x0b/0x0d` only
make three distinct I2C clients exist so each driver can bind; **no bus traffic
ever goes to them** (probe performs no I2C access). Earlier notes listing the
actuators at `0x0a/0x0b/0x0d` were wrong about the wire address.

## Power and GPIO

Lens nodes have **no `*-supply`, no `pinctrl-names`**. The VCM driver's
`devm_regulator_get("vin"/"vdd")` therefore returns the regulator core's
**dummy regulator** (GKI 6.1 `_regulator_get()`: no supply + DT populated →
`have_full_constraints()` → "supply vin not found, using dummy regulator"), whose
enable/disable are no-ops; `devm_pinctrl_get()` finds no states, so
`vcamaf_on/off` stay NULL. Driver `power_on/off` therefore toggles nothing
electrically. AF power is the sensor's AFVDD,
switched by imgsensor through the YFT custom LDO path (`custom_afvdd` channel
→ `custom-ldo-wl2868.ko`, WL2864C at `11-0029`). sensor0 and sensor4 share
channel 5. No reset/enable GPIO exists for any actuator.

## Fitted vs shipped

| module | class | basis |
|---|---|---|
| `main_vcm.ko` | **ACTIVE/FITTED** (camera 0) | all four channels |
| `main2_vcm.ko` | **ACTIVE/FITTED** (camera 3) | all four channels |
| `main4_vcm.ko` | **ACTIVE/FITTED** (camera 2) | all four channels |
| `camera_af_media.ko` | **ACTIVE** (media aggregator, not an actuator) | DT `mtk_composite_v4l2_2`, 4 ports |
| `main3_vcm.ko` | **PLATFORM-ONLY** | loads; no DT client; no HAL entry |
| `sub_vcm.ko` | **PLATFORM-ONLY** | loads; no DT client; no HAL entry |

"Fitted" rests on electronic/software evidence (HAL drives AF on these cameras,
sensors power AFVDD). The actuator protocol contains **no chip-ID read** (no
table command 2/4), so the exact die is not electronically identified beyond
"responds to the DW9800W command set at 0x0C"; see `../dw9800w-class/README.md`.

## Not an actuator despite matching strings

`thermal_interface.ko` ("md_actuator" = modem thermal), `pda_drv_mt6878.ko`
(`actuator_class` media-entity name), `camera_eeprom_v4l2.ko` (`do_lens_id_*`
EEPROM parsers), `imgsensor.ko` (`get_lens_driver_id`).
