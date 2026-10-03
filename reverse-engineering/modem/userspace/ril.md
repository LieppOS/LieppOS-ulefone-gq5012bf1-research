# Telephony → RIL → CCCI → MD (stock, static)

```
Android Telephony (framework + mediatek-telephony-{base,common}.jar, ImsService.apk)
   │ AIDL android.hardware.radio.* V2 + vendor.mediatek.hardware.mtkradioex.*
   ▼
mtkfusionrild (librilfusion.so, libmtk-ril.so, libmipc.so)          [SELinux: rild]
   │ MIPC frames                          │ legacy/aux
   ▼                                      ▼
/dev/ttyCMIPC1 (CCCI_MIPC1, ch 216/217, CCIF q5)   /dev/ttyC0 (UART2, AT), /dev/ttyC6 (DISP),
                                                   /dev/ccci_mdx_sta, /dev/ccci_pin_sta,
                                                   /dev/ccci_wifi_proxy (libwpfa), /dev/ccci_vts
   ▼
ccci_md_all port_char → ccci_ccif (CCIF0) → MD1 firmware (L3/NAS/IMS/RRC)
data: MD → DPMAIF → ccmniN (IRadioData setupDataCall returns the ifname)
```

## Daemons and boot ordering (vendor init)

| service | binary | class/trigger | kernel interfaces |
|---|---|---|---|
| ccci_mdinit | /vendor/bin/ccci_mdinit 0 | core, oneshot, prio -20 | `/dev/ccci_ioctl0`, `/dev/ccci_monitor`, `/dev/ccci_md1_sta`, `/sys/kernel/ccci/{boot,kcfg_setting,lk_md}`, `/dev/ccci_fs` (ccci_fsd thread), `/dev/ccci_ipc_5`, `/proc/ccci_dump` |
| vendor.ccci_rpcd | /vendor/bin/ccci_rpcd 0 | core | `/dev/ccci_rpc`, `/dev/block/by-name/md1img` |
| vendor.ril-daemon-mtk | mtkfusionrild | main; `ro.vendor.mtk_mipc_support=1` | see above |
| nvram-aidl | vendor.mediatek.hardware.nvram-service | hal | `/dev/ttyCMIPC0`, `/mnt/vendor/nvcfg` |
| atcid-daemon-u | /vendor/bin/atcid | | `/dev/ttyCMIPC2`, `/sys/kernel/ccci/{boot,md_en}` |
| md_monitor | /vendor/bin/md_monitor | disabled; `persist.vendor.mdmmonitor=1` | `/dev/ccci_mdl_monitor`, `ccci_raw_mdm`, `ccci_ccb_md_monitor` |
| vendor.muxreport-daemon | /vendor/bin/muxreport | `vendor.ril.muxreport=1` | CCCI node table (MD reset reporting) |
| vendor.bip_ap | /vendor/bin/bip_ap | `vendor.ril.md_status_from_ccci=ready` | `/dev/ccci_bip` |
| agpsd / mnld | mtk_agpsd, mnld | | `ttyC2`, `ccci_ipc_1220_0`, `ccci_c2k_agps`, `ttyCMIPC5` |
| thermal_core | /vendor/bin/thermal_core | | `ttyCMIPC9` |
| mdlogger / emdlogger* | system_ext | debug | `ttyC1`, `ccci_md_log_ctrl`, CCB DHL |

## Service paths

* **Voice (CS/VoLTE):**
  * Control: `IRadioVoice` → MIPC → MD.
  * Speech control: audio HAL ↔ `/dev/ccci_aud`. Speech parameters: `/dev/ccci_raw_audio`.
  * PCM: AFE PCM1 (see `../telephony/audio-voice.md`).
* **SMS:** `IRadioMessaging` → MIPC; SMS-over-IMS is done inside the MD-resident IMS stack.
* **Data:** `IRadioData.setupDataCall` → MD activates the PDN → returns `ccmniN` → netd.
* **SIM:** `IRadioSim` (+ `imsSlotN`, `seN`) → MIPC → MD UICC driver. STK BIP uses
  `/dev/ccci_bip`. SIM lock uses `libsimlock` and `libsimmelock` (`ro.vendor.sim_me_lock_mode=3`).
* **Emergency:** ECC lists come from `vendor/etc/ecc_list*.xml` (operator overlays OP01/02/09/12/17/18/20/236).
  Live `ril.ecclist`=112,911. Calls go through `IRadioVoice.emergencyDial`, and
  emergency-callback-mode indications travel on the `imsSlotN` voice instances.
* **Carrier config:** framework CarrierConfig, MD **MCF** (`mcf_ota` partition, SBP id),
  `vendor/etc/md/apncfg` (IMS/emergency APN per MCC_MNC) and
  `/mnt/vendor/nvdata/APCFG/APRDCL/{MD_SBP,CXP_SBP}` (SBP selection persisted by ccci_mdinit and rild).
