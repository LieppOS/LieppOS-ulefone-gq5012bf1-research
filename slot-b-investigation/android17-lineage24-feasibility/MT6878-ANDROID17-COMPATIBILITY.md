# MT6878 / Android 17 compatibility landscape

## Source landscape

**PROVEN:** the generic official manifest contains no direct `MT6878`,
Dimensity 7300/7350/7400 device implementation and does not check out
`hardware/mediatek` or `device/mediatek/sepolicy_vndr`. Official Lineage
repositories for common MediaTek hardware and vendor sepolicy do have
`lineage-24.0` branches, but a device tree must add them explicitly.

A public donor/reference exists:

```text
Andreyka445/device_nothing_Galaxian
branch lineage-24.0
commit 827bca98f21638c358ad4b4009e419b7071b27e5
```

Reference URLs:

- `https://github.com/Andreyka445/device_nothing_Galaxian/tree/lineage-24.0`
- `https://github.com/LineageOS/android_hardware_mediatek/tree/lineage-24.0`
- `https://github.com/LineageOS/android_device_mediatek_sepolicy_vndr/tree/lineage-24.0`
- `https://github.com/NothingOSS/android_kernel_6.1_nothing_mt6878`
- `https://github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878`

That MT6878 tree uses a 6.1 kernel, vendor API 202404, MediaTek common hardware,
Mediatek sepolicy, IMS/radio packages, KeyMint compatibility service, MTK
memtrack and many proprietary blobs. NothingOSS also publishes MT6878 6.1
kernel and module repositories. **INFERRED:** this is useful architecture and
source reference. It is not evidence that Nothing binaries, DT, panel, camera,
radio calibration or partition geometry match Ulefone.

## Component risk table

| Component | Android 17 change risk | Vendor dependency | Known source/reference | Difficulty | Notes |
|---|---|---|---|---|---|
| early boot / vold / FBE | medium | MTK vendor ramdisk, KeyMint, metadata encryption | proven A16 and B15 boots; Galaxian KeyMint compat | medium | API-37 vold must open existing FBE; use isolated data first |
| graphics / gralloc / composer | medium-high | MTK mapper/allocator/composer blobs, Mali stack | stock VINTF; Galaxian MTK memtrack/common | high | interface may pass VINTF but buffer metadata ABI is runtime-sensitive |
| camera | high | sensor HAL, tuning, ISP, camera provider and Ulefone sensors | repository camera/thermal inventories; donor only structural | very high | donor sensors/tuning are not binary-compatible |
| audio | medium-high | MTK primary audio HAL, effects, policy XML, AW883xx | `docs/audio.md`, HAL/ELF closure | high | telephony audio and vendor parameter strings need runtime validation |
| radio / RIL | high | MTK radioex AIDL, modem services, dual-SIM config | live A radio services; Galaxian MTK telephony packages | very high | standard radio AIDL plus proprietary extensions; IMS is separate risk |
| IMS / VoLTE / VoWiFi | very high | MTK IMS APK/JAR/native stack, carrier overlays | stock blob recipe; Galaxian IMS dependencies | very high | framework classpath/signing and hidden API coupling likely |
| sensors | medium | MTK sensorservice/HIDL bridge and calibration | `docs/sensors.md`, stock manifests | medium-high | basic sensors likely; special sensors need overlays |
| fingerprint | high | vendor AIDL/HIDL, TEE app, calibration and UI contract | phase4 fingerprint research; donor pattern only | high | TrustKernel/vendor TEE identity must remain Ulefone-specific |
| GNSS | medium-high | MTK GNSS HAL/config/NVRAM | stock HAL map and blob closure | high | framework interface retained, behavior untested |
| NFC | high | ST21 service, configs, NFC APEX/JNI coupling | extensive `hardware/nfc/` reconstruction | high | do not substitute donor NFC stack |
| USB / Type-C | medium-high | MTK USB HAL, TCPC modules, gadget properties | Type-C/TCPC reconstruction reports | high | Android 17 property and init namespace tightening may expose assumptions |
| thermal | medium | MTK thermal HAL/config plus Ulefone thermal camera | `docs/camera-thermal.md` | medium-high | thermal safety config must remain exact |
| power | medium | MTK power HAL/libperfmgr profiles | stock service/HAL maps; Galaxian common | medium | boot likely; performance/battery behavior needs tuning |
| Bluetooth / Wi-Fi | medium | MTK connectivity firmware, vendor libs, kernel modules | `docs/connectivity.md`, module/KMI maps | high | firmware/module ABI proven only for current kernel |
| rear display / lights / IR | high | Ulefone-specific apps, services, DT and drivers | repository display/IR/hardware research | high | no donor equivalence |
| vendor sepolicy | medium | stock policy 34.0 plus MTK domains | official Lineage MTK sepolicy branch; captured policy | medium-high | Android 17 retains 34.0 mappings; new device policy still required |

## Classification

- **PROVEN:** no official in-manifest MT6878 device support; donor lineage-24.0
  work and official MTK common branches exist.
- **LIKELY:** core boot, storage and many standard HAL registrations can survive
  because the current vendor already boots an Android 16 GSI.
- **UNCERTAIN:** every proprietary extension and hardware behavior above.
- **KNOWN BLOCKER:** no `gq5012bf1` Lineage 24 device/product tree currently
  creates the required split images or integrates the 1,891-path vendor set.
- **TEST TO CONFIRM:** `checkvintf`, boot, service registration and one component
  at a time using Ulefone blobs/configs—not donor binaries.
