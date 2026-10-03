# IMS service / artifact map

| layer | stock artifact | interface / role |
|---|---|---|
| framework | `system/framework/ims-common.jar` | AOSP IMS API |
| MTK framework | `system_ext/framework/mediatek-ims-{base,common}.jar`, `mediatek-ims-extension-plugin.jar` | MediaTek IMS extensions |
| service | `system_ext/priv-app/ImsService/ImsService.apk` (`com.mediatek.ims`) | Android ImsService implementation; location-settings exemption in `com.mediatek.ims.config.xml` |
| entitlement | `product/priv-app/ImsServiceEntitlement.apk` | carrier entitlement/provisioning |
| operator | `OP08Ims.apk`, `OP12Ims.apk`, `OP12ImsPco.apk`; OP15/18/236 JARs | operator policy plugins |
| radio HAL | `librilfusion.so` | `android.hardware.radio.ims/IRadioIms/{slot1,slot2}` plus MTK ims/rcs/dch instances |
| RIL | `libmtk-ril.so`, `libmtkmipc-ril.so`, `libmipc.so` | requests/indications to MD over `/dev/ttyCMIPC1` |
| MD | md1rom in modem.img | SIP/IMS/AKA/IPsec/session control; signed proprietary firmware |
| IWLAN | `ipsec_mon`, `libipsec_ims_shr.so` | IPsec/IMS bearer monitoring; ccmni4 literal |
| media | `vtservice`, `vtservice_aidl`, `libimsma*`, `libvt_avsync.so` | ViLTE/ViWiFi media; `/dev/ccci_imsdc` |
| optional RCS | `rcs_volte_stack`, `volte_rcs_ua`, `librcs_volte_core.so`, RCS HAL libs | packaged; no stock init service found |
| optional client API | `volte_clientapi_ua` | starts only when boot complete and `persist.vendor.clientapi_support=1` |
| audio | audio.primary.mediatek + speech libs | `/dev/ccci_aud`, `/dev/ccci_raw_audio`, AFE MD1 PCM |

Complete ELF `DT_NEEDED` lists/hashes: `../userspace/dependency-map.tsv`.
