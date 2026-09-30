> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> Cooling is **entirely passive**: no fan, pump or TEC exists anywhere in the device tree. See the verification `cooling.md`.

# Cooling and thermal hardware

## Proven thermal control layer

* Thermal services: Android Thermal HAL AIDL 3, `thermal_core`, `vendor.thermal-mediatek`; at least 56 Linux thermal-zone nodes are present in `thermal-secondary-nodes.txt`.
* Current HAL exposes CPU, GPU, NPU, TPU, SOC, skin, battery, USB-port and power-amplifier temperatures. Snapshot values: CPU/GPU/NPU/TPU/SOC ~46.8 °C, skin 39.2 °C, battery 37 °C, USB 43 °C, PA 39.7 °C.
* Cooling devices: Mali devfreq, charger-cooler, LCD-backlight, Wi-Fi-cooler and flashlight-cooler.

## Thresholds (HAL policy, °C)

| Domain | Hot ladder visible |
|---|---|
| CPU/GPU/NPU/TPU/SOC | 85 / 90 / 100 / 117 |
| Battery | 50 / 55 / 59 / 60 |
| Skin | 43 / 45 / 55 / 65 / 75 / 80 |
| Power amplifier | 68 / 90 / 100 / 110 |
| USB port | no static hot ladder in dump |

## Physical cooling

The phone is a 688-g, 33.8-mm rugged chassis according to GSMArena and has a high-power Dimensity platform plus thermal camera. A vapor chamber, graphite stack, copper heat spreader, heat pipe, fan or active TEC is **not proven**: no teardown/FCC internal-shot set for GQ5012BF1 was found. The large mass is suggestive but cannot identify a cooling part.

## Stock use / capability gap

Thermal policy throttles performance, charging, display brightness, Wi-Fi and flash illumination through named cooling devices. The thermal-imaging camera is a separate 640×512/25-Hz module and is not a CPU cooling device. No user-accessible fan/TEC control exists.

## Hidden / unused

* Vendor thermal zones may include PMIC, modem, memory, camera and charger sensors that are not surfaced as Android named temperatures.
* Skin threshold starts at 43 °C while CPU throttling begins at 85 °C, so chassis comfort can reduce display/flash/charging before SoC hard limits.
* If a physical vapor chamber exists, its dimensions/material stack remain unknown and cannot be recreated in software.

## Verification

Map every thermal-zone type and trip point to DT nodes; run sustained CPU/GPU/camera/5G/120-W charging tests; log cooling-device states and skin/SoC gradients; inspect the copper/graphite stack only with a teardown.

Sources: S01–S05; `thermal-power.txt`, `thermal-secondary-nodes.txt`; no teardown evidence (S23 only sibling model).
