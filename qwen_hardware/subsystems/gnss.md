> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> Five constellations plus QZSS on **L1 + L5/E5a/B2a** with OSNMA and L5 DCB calibration are established in the verification `gnss.md`.

# GNSS / location

## Hardware found

* MT6637-class connectivity ADIE is proven by `vendor.connsys.gps.adie.chipid=0x6637`.
* `connsys_gnss`, MediaTek GNSS AIDL service, `agpsd`, LBS/LPPE interfaces and GPS character device (`gps_drv_dl_v051`) are present and running.
* OEM/independent spec claims GPS, GLONASS, Galileo, BeiDou and QZSS; GSMArena additionally lists NavIC.

## Capability layer

The live properties prove an **L5-capable** configuration: `vendor.debug.gps.support.l5=1`. GNSS service capabilities include satellite PVT, measurements, navigation messages, low-power mode, blocklist, measurement corrections/correlation vectors, accumulated delta range and single/multiband tracking fields. Public snapshot signal output only listed GPS L1 at 1.57542 GHz, so actual dual-frequency constellation coverage remains partly UNKNOWN.

## Board configuration / stock use

* `ro.vendor.mtk_gps_support=1`, `ro.vendor.mtk_agps_app=1`, `persist.sys.gps.lpp=2`; `agpsd` and vendor GNSS service are running.
* GPS provider was enabled, but the frozen capture recorded no fix/locations. Cold-start time, carrier phase, NavIC and L5 lock were not tested.

## Hidden / unused

* L5/dual-frequency tracking, corrections, multi-band power telemetry and advanced measurement APIs are visible in the service capability set but not necessarily exposed to ordinary apps.
* Satellite blocklist and correction-vector controls are vendor/service features.

## Verification

Collect `gnss` HAL debug output in open sky; record constellation/frequency used, TTFF, accuracy and power; inspect firmware/NVRAM for exact MT6637 GNSS feature mask. Treat OEM constellation list as a claim until a fix log proves each constellation.

Sources: S01, S04–S06; live properties/connectivity; findings L02/L15.
