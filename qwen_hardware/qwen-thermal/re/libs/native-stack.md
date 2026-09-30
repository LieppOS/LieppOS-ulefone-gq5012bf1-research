# Native AC020 stack

| Library | Recovered role |
|---|---|
| `libAC020sdk.so` | JNI registration, handle lifecycle, DFU/DFUse, firmware/package JSON, conversions Y16/YUYV/NV12/BGR |
| `libircmd020.so` | driver-independent vdcmd command/control; standard/short/long frames, polling, CRC, ~441 `adv_*`/`basic_*` exports |
| `libusbuvccamera020.so` | Android USBFS libusb/libuvc, UVC descriptors/stream/control, normal+DFU open |
| `libdualuvccamera020.so` | dual UVC stream/control |
| `libomniircamera020.so` | omni UVC transport |
| `libircam.so` | public C handle façade: video/control handles and callbacks |
| `libadvirprocess.so` | KBC/DPC/RMVC/HBC/VBC/TNR/SNR/DDE/AGC/TPD processing |
| `libadvirparse.so` | combined frame and metadata parsing |
| `libadvirtempac020.so`, `libadvirtemp.so` | radiometry, KT/BT, NUC-T, environment/distance/emissivity correction and measurement reducers |
| `libcommonsdk.so` | product-specific `get_tempinfo*` and correction dispatch |
| `libcolormapping.so` | 256-entry RGB/RGBA palettes and temp-window rendering |
| `libdualcalibration.so`, `libdualcommon.so`, `libgpudual.so` | visible/thermal registration, fusion and factory calibration |
| `libframecache.so` | stream frame caching |
| `libirpack_tool.so` | firmware/package/file support |
| `libcommon_utils.so` | JNI helpers, package/certificate whitelist and CRC8 |
| `libencrypt_comm.so` | AES/hash/signature/config protection |

Build paths identify `ANDROID_RS300_SDK` on Jenkins and Raysentek/OpenCV workspaces. The same broad stack is copied into FactoryMode and OEM APKs; presence alone is not proof each feature is used.

Complete dynamic export inventories are in `evidence/binaries/symbols/` and `re/calibration/native-api-inventory.md`; hashes are in `evidence/binaries/SHA256SUMS.txt`.
