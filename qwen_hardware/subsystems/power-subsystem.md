> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> 2S/7.74 V topology, PD+PPS only (no UFCS), 120 W = 6 A x 20 V, and **no wireless charging** are established in `battery-pack.md`, `charging-capabilities.md` and `wireless-charging.md`. The system PMIC tier (MT6363/MT6369/MT6319/MT6685) and the reclassification of RT5133 as a camera LDO PMIC are in `power-support-ics.md`.

# Power, charging and battery

## Hardware found

| Function | Part / node | Evidence |
|---|---|---|
| Main PMIC / gauge / Type-C companion | MediaTek **MT6375**, `5-0034`, `mtk-gauge`, `mtk_tcpc` | live bus + DT |
| SoC PMIC | Richtek **RT5133**, `5-0018` | live bus; corrects old MT6369 label |
| Charge pumps | Southchip **SC8571** master `11-0066`, slave `6-0067`; SC851x-class `6-0069` | live bus/DT |
| Secondary gauge | **SH366003**, `9-0055`, consumer name `3rd-gauge` | live bus/DT |
| Buck-boost rails | Richtek **RT6160(A)**: `5-0075`, `6-0075` (`vbif`, `vpp`, `vsrf1_ant`) | DT + vendor reference |
| Pack | Li-ion, live battery voltage **8400 mV**; marketing **2×5300 mAh = 10600 mAh** | live power dump + S04 |

## Capability layer

* MT6375 is the main charger/fuel-gauge/USB Type-C component. **RESOLVED:** the fast-charge topology is 2S direct charge through two SC8571 pumps with an SC8510 reverse path, over **PD + PPS only**.
* SC8571/SC851x are Southchip switched-capacitor charge-pump family parts. Exact current/voltage limits were not publicly retrieved; parallel master/slave layout is consistent with high-power direct-charge operation.
* RT6160A reference capability: 2.2–5.5 V buck-boost, up to 3 A, ACOT control. The board config marks `vbif`, `vpp` and antenna rails always-on/boot-on; actual rail loads are unknown.
* RT5133 regulator tree has 16 buck and 53 LDO-style named rails; exact per-rail current/DVFS limits are UNKNOWN.

## Board configuration / stock observation

* MT6375 exports the primary Android battery path and Type-C TCPC/PD role manager. SC8571 nodes have parent/trickle charger and 100-kΩ power NTC configuration.
* Frozen snapshot: USB powered, wireless powered false, 79% level, Li-ion, charge counter 2,327,340 µAh, max charging current 1,000,000 µA and max charging voltage 5,000,000 µV. This is an idle/observed state, **not** the 120-W ceiling.
* Android reports `Design capacity=8,594,000 µAh` and `Maximum capacity=2,946,000` in the dump. These fields do not reconcile cleanly with the 10,600-mAh OEM claim; pack topology/unit semantics require confirmation.
* ~~OEM configuration claims 120 W wired, UFCS, PD/PPS, 50 W wireless and 30 W reverse~~ **CORRECTED 2026-09-08:** the OEM claims **120 W (20 V/6 A) PD/PPS and 10 W *wired* reverse**. There is **no UFCS** and **no wireless charging hardware**; the wireless constants seen in vendor config belong to a platform-wide ODM option set. See `../verification/findings/charging-capabilities.md` and `wireless-charging.md`.

## Stock usage

Battery, charger, gauge, thermal and Type-C services are loaded. Thermal policy includes `charger-cooler`; no wireless charging pad or reverse-power load was connected during capture.

## Hidden / unused

1. The SC8571 master/slave direct-charge path is hidden when only an SDP host is attached (as in the capture). **UFCS does not exist on this device.**
2. ~~50-W wireless and 30-W reverse constants~~ **CORRECTED:** no wireless receiver exists - no device-tree node, no `wireless` power supply and no receiver IC. Reverse output is **10 W wired** through the SC8510.
3. RT6160 boost rails may support wireless/reverse/FEM functions beyond the standard battery UI.
4. Secondary SH366003 gauge allows redundant/parallel SOC/health estimation, but its calibration relationship to MT6375 is unknown.

## Verification

Capture Type-C PDO/APDO negotiation with a certified 20 V/6 A **PD-PPS** source; inspect all power-supply sysfs nodes under load; measure pack voltage and current; test the **wired** 10 W reverse output; identify SC8571/SC8510 markings and read the gauge design-capacity register.

Sources: S01–S04, S07, S18, S22; `thermal-power.txt`; findings L04/L17.
