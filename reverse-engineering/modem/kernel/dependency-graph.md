# Linux modem kernel dependency graph

Generated from stock `depends=`/undefined symbols and source call sites.

```
                                  aee_aed / mrdump / EMI-MPU / SMPU
                                                ^
                                                |
ccci_auxadc ---------------------> ccci_util_lib <------------------- mtk_mdpm
      ^                                  ^   ^                             ^
      |                                  |   |                             |
      +--------------------------- ccci_md_all ----------------------------+
                                          ^
                    +---------------------+------------------+
                    |                     |                  |
                ccci_ccif           ccci_dpmaif       ccci_fsm_scp
                (control)              |                  |
                                       |             scp + tinysys_ipi
rps_perf ---> ccmni ---- ccmni_ops -----+
                    ^                   |
                    +----- port_net <----+

ccci_md_all <--- md_cooling_all
ccci_md_all <--- mtk_md_power_throttling
ccci_md_all <--- c2k_usb <--- c2k_usb_f_via_{atc,ets,modem}
ccci_md_all <--- mddp <--- wlan_drv_gen4m (already closed in connectivity)
ccci_util_lib <--- conninfra (SMEM_USER_RAW_MD_CONSYS)
ccci_util_lib <--- snd-soc-mtk-common (SMEM_USER_RAW_USIP)
```

## Load/ownership summary

| owner | modules | status |
|---|---|---|
| CCCI core/control | ccci_util_lib, ccci_md_all, ccci_auxadc, ccci_ccif, ccci_fsm_scp | active, exact |
| packet data | ccci_dpmaif, ccmni, rps_perf | active, exact |
| direct-path offload | mddp | active, exact; already part of MT6637-WIFI-KERNEL closure |
| MD power/thermal | mtk_mdpm, md_cooling_all, mtk_md_power_throttling | active, exact |
| C2K USB gadget/debug | c2k_usb + 3 rawbulk functions | shipped/configured, exact; not evidence that a cable function is active during normal boot |

The MD firmware is not a kernel dependency: LK starts/loads it and Linux communicates through
CCIF, DPMAIF and reserved shared memory.
