> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> Wi-Fi/BT has **no external FEM**; the cellular front end is MIPI-RFFE and architecturally invisible to software. See `connfem-selected-fem.md` and `antennas-rf-frontend.md`.

# Cellular modem and RF front end

## Hardware / platform

* SoC/baseband platform: MediaTek MT6878 family, marketed Dimensity 7400 / MT6878T. Baseband string: `MOLY.NR17.R1.MP5.RC.MP.V23.9.P1`.
* Integrated modem is 2G–5G capable, with 5G Release-16 class carrier aggregation/VoNR features in the platform description. Device configuration is dual-SIM dual-standby (`persist.radio.multisim.config=dsds`, `ro.vendor.radio.max.multisim=dsds`).
* ConnFem path: `mediatek,mt6878-connfem`, HWID GPIOs 131/132/92 (8 selections), 10 candidate FEM entries. Catalog includes Qorvo QM42195/QM45197 and Skyworks SKY85320/SKY85720/SKY85732/SKY85743 families plus bypass/no-FEM alternatives.

## Configured band claims

OEM/GSMArena list: GSM 850/900/1800/1900; WCDMA B1/B2/B4/B5/B8; LTE B1/B2/B3/B4/B5/B7/B8/B12/B17/B20/B28A/B38/B40/B41/B66; NR n1/n3/n5/n7/n8/n20/n28/n38/n41/n66/n77/n78/n79. These are product/firmware band claims, not a measured RF certification result.

## Stock usage

* RIL/AIDL radio, network, data, voice, messaging and SIM services are present. `persist.vendor.radio.volte_state=1`, VoWiFi support property is enabled, and DSDS is configured.
* Snapshot registration was emergency/no-SIM or no-network state; no carrier aggregation, NR attach, VoNR call or actual throughput was proven.
* MT6878 camera/ISP and modem share the SoC thermal budget; HAL exports PA temperature and a PA threshold ladder (68/90/100/110 °C).

## Hidden / unused

1. Platform-level n77/n78/n79, 3CC-CA, VoNR, VoLTE/VoWiFi and dual-SIM routing are available only when carrier profile, RF population and local bands permit.
2. Eight ConnFem HWID choices allow alternate PA/LNA/filter population; this is a major variant uncertainty.
3. Some candidate FEMs support 6-GHz Wi-Fi, but that does not imply cellular 6-GHz operation.

## Verification

Read live HWID GPIO values and ConnFem selected part; obtain modem band mask and carrier config; test each SIM, LTE/NR SA/NSA, CA and IMS mode with a permitted test SIM; identify shielded FEM package markings. Do not alter modem NV data without a full calibration backup.

Sources: S01–S07, S20; findings L02/L15 and local ConnFem reconstruction.
