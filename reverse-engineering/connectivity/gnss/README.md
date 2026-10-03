# GNSS (GNSS-KERNEL-TRANSPORT)

**Status: GNSS-KERNEL-TRANSPORT = DONE.** The GNSS firmware, `mnld`, `libmnl`, AGPS/SUPL and
the GNSS HAL are proprietary ([`firmware-boundary.md`](firmware-boundary.md)).

## Architecture

```
Android LocationManager / GnssManager
  └─ AIDL android.hardware.gnss (IGnss V3) : vendor.gnss-default =
     /vendor/bin/hw/android.hardware.gnss-service.mediatek
       (+ android.hardware.gnss-impl-mediatek.so, vendor.mediatek.hardware.gnss-impl.so;
        vendor.mtkgnss-service for vendor.mediatek.hardware.gnss.batching.IMtkGnssBatching)
       └─ socket "mnld" → /vendor/bin/mnld (libmnl.so = MTK navigation library, proprietary)
            ├─ /dev/gpsdl0, /dev/gpsdl1   (gps_drv_dl_v051: data link per GNSS link)
            ├─ /dev/gps_emi              (gps_drv_dl_v051: EMI window, 1 MiB @0x88a00000)
            ├─ /dev/gps_pwr              (gps_pwr.ko: battery-level / power notify)
            ├─ /dev/gps2scp              (gps_scp.ko → connscp → SCP CONAP: geofence/batching offload)
            ├─ AGPS: socket agpsd* ↔ /vendor/bin/mtk_agpsd (SUPL/LPP/RTCM, carrier profiles
            │        vendor/etc/gnss/agps_profiles_conf2*.xml), mtk_lbs_service
            └─ MNL_Config.xml (IFB, GGTO, per-chip L5 DCB, L1Only=0, GLP enabled)
  gps_drv_dl_v051.ko  (DT "mediatek,mt6878-gps" @0x18c00000, 7 IRQs)
    ├─ conninfra_pwr_on(GPS), conninfra_spi_* and conninfra_spi_1_* (A-die GPS regs),
    │  conninfra_bus_clock_ctrl, conninfra_get_clock_schematic, connsys_log/coredump
    └─ GPS MCU in CONNSYS (firmware preloaded by LK from partition connsys_gnss) + MT6637 A-die GNSS RF
```

* Constellations (MNL config + framework): GPS, GLONASS, BeiDou, Galileo, QZSS, NavIC
  (`GGTO` lists GLONASS/BEIDOU/GALILEO/NAVIC offsets). Dual frequency: L1 + L5 (DCB rows for chip
  6637, `L1Only=0`, `L5Test`). B1C/L1C/E5B/B2B signal disable mask = 0.
* A-die: 0x6637. `gps_dl_hw_dep_bgf.c` accepts 6637/6635/6686/6631; the MT6686 path is only for
  the 6631+6686 SKU, which is not this board.
* Time injection / assistance: `mnld` + `mtk_agpsd` (NTP/SUPL/LPP/RTCM handlers); kernel
  `FM_IOCTL_GPS_RTC_DRIFT` exists for FM-GPS RTC drift sharing. No GNSS-specific LNA GPIO in DT
  (the A-die GNSS LNA is internal).
* Coexistence: CONNSYS internal, plus modem→GNSS status. `b13b14-status-addr = <0x1c000008>`
  is read by `GPSDL_IOC_GPS_GET_MD_STATUS` as `MD2GPS_REG` (`gps_each_device.c:409`). The name
  most likely refers to cellular bands 13/14, whose uplink harmonics land near GPS L1; that is
  an interpretation of the name, not proven.

## Kernel modules

| module | functions | data | ABI | source / build |
|---|---:|---:|---|---|
| `gps_drv_dl_v051.ko` | **550/550** | **126/126** | exact (imports 123, modversions 124) | NothingOSS kernel_modules 2115d27 `gps/data_link/plat/v051` |
| `gps_pwr.ko` | 12/12 | 10/10 | exact | 2115d27 `gps/gps_pwr` (insmod `init.gps_pwr.rc`) |
| `gps_scp.ko` | 15/15 | 13/13 | exact | 2115d27 `gps/gps_scp` (insmod `init.gps_scp.rc`) |
| `connscp.ko` | 104/104 | 66/66 | exact | KDM 6df320423600 (see `../conninfra/`) |

DT contract: `gps@18c00000` (`conn_gps_base` 1 MiB, `conn_infra_base`, `status_dummy_cr`
0x1c000000, `tia2_gps_on/rc_sel/debug` 0x1c0130xx), IRQs 379-383, 389, 129, `emi-connac-ver = 2`,
EMI 1 MiB (live `emi-addr = 0x88a00000`, part of `consys_emi_reserved`).
`ro.vendor.gps.chrdev=gps_drv_dl_v051`.
