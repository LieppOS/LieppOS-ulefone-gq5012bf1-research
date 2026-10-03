# IMS stack — proprietary boundary mapped (PARTIAL)

The Linux CCCI/DPMAIF transport beneath IMS is DONE. IMS itself is not reconstructed: the
framework Java, vendor RIL implementation, media libraries and MD-resident SIP/IMS protocol
engine remain proprietary stock code.

## Stock path

```
Telephony / Telecom
  -> system_ext/priv-app/ImsService/ImsService.apk (package com.mediatek.ims)
     + mediatek-ims-{base,common}.jar + mediatek-ims-extension-plugin.jar
     + operator plugins OP08/OP12 APK, OP15/OP18/OP236 JAR
  -> Android IRadioIms/slot1,slot2 + MediaTek mtkradioex.{ims,rcs,dch}/slot1,slot2
  -> librilfusion.so / libmtk[mipc]-ril.so
  -> MIPC on /dev/ttyCMIPC1
  -> MD1 firmware IMS stack
  -> IMS PDN on ccmniN (stock ipsec_mon explicitly monitors ccmni4)
```

`android.hardware.telephony.ims.prebuilt.xml` advertises the IMS feature. `ro.vendor.md_auto_setup_ims=1`
means the MD/RIL configures the IMS bearer. There is no separate AP SIP daemon in init; therefore
SIP registration, AKA/IPsec state and SMS-over-IMS are on the MD/RIL side, not an open Linux
service.

## Statically enabled SKU features

| feature | evidence | classification |
|---|---|---|
| VoLTE | `persist.vendor.ims_support=1`, `persist.vendor.volte_support=1`, `persist.vendor.mtk.volte.enable=1`; `IRadioIms`; audio CCCI speech path | **SKU enabled**; no call placed in this offline pass |
| VoWiFi | `persist.vendor.mtk_wfc_support=1`, `persist.vendor.wfc.sys_wfc_support=1`, `ro.telephony.iwlan_operation_mode=AP-assisted`; `ipsec_mon`, `libipsec_ims_shr.so` | **SKU enabled**; registration not runtime-proven |
| ViLTE / video telephony | `persist.vendor.vilte_support=1`, `persist.vendor.mtk.vilte.enable=1`, `ro.vendor.vt_hevc_support=1`; vtservice + vtservice_aidl | **SKU enabled** |
| SMS over IMS | Android `IRadioIms`/MTK IMS framework and MD IMS stack | platform/SKU path present; routing policy is carrier/runtime dependent |
| emergency IMS | `IRadioVoice` imsSlot instances and emergency-callback-mode indications in librilfusion; ECC XML overlays | path present; carrier/runtime dependent |
| RCS | RCS HALs/libs and three binaries exist | **packaged but not proven active**: no init service references `rcs_volte_stack` or `volte_rcs_ua`; `volte_clientapi_ua` only starts when `persist.vendor.clientapi_support=1` |

## VoWiFi boundary

`ipsec_mon` is a oneshot NET_ADMIN/NET_RAW service and contains the literal `ccmni4`.
`libipsec_ims_shr.so` supplies the proprietary IMS IPsec helper. The normal Wi-Fi and conninfra
kernel sides are already exact in `reverse-engineering/connectivity/`; no IMS-specific kernel
module exists. AP-assisted IWLAN policy is in ImsService/RIL/MD and carrier config.

## Video/audio

* `system_ext/bin/vtservice` starts when ViLTE or ViWiFi support is enabled.
* `vendor/bin/hw/vtservice_aidl` exposes `vendor.mediatek.hardware.videotelephony`.
* `libvt_avsync.so` opens `/dev/ccci_imsdc`; `libimsma.so`/`libimsma_rtp.so` implement media adaptation/RTP.
* Speech control and parameter buffers use `/dev/ccci_aud` and `/dev/ccci_raw_audio`; PCM samples
  use the dedicated AFE MD1 PCM path. See `../telephony/audio-voice.md`.

## Carrier configuration

The effective IMS configuration is layered:

1. Android CarrierConfig and ImsService operator plugins.
2. persisted SBP selection (`MD_SBP`, `CXP_SBP`) under nvdata.
3. `mcf_ota` MCF/SBP packages parsed by the modem.
4. 504 `vendor/etc/md/apncfg/<MCC>_<MNC>.conf` files (IMS/emergency APN definitions), IKEv2/TLS
   CA stores and TS25 PLMN tables.
5. opaque MD DRDI/NVRAM and carrier network policy.

No source-equivalence claim is made for any proprietary item above.
