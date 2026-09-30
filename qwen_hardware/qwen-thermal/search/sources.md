# Sources

## Primary local evidence
- Stock APKs: `system/app/M170infisens/M170infisens.apk`, `M170infDlp/M170infDlp.apk`, `FactoryMode/FactoryMode.apk`.
- Canonical arm64 native corpus: `workspace/gq5012bf1/stock/partitions/system/app/FactoryMode/lib/arm64/`; SHA-256 list: `evidence/binaries/SHA256SUMS.txt`.
- Decompiled sources: `re/apps/infisens`, `re/apps/infdlp`, `re/apps/factorymode`.
- Kernel: `vendor_dlkm/lib/modules/yft_tiny2c_usb.ko`; full strings/symbol/disassembly evidence under `evidence/local/fm78100/`.
- USB routing module: `vendor-ramdisks/platform-extracted/lib/modules/extcon-mtk-usb.ko`, focused disassembly `workspace/phase4-sc851x/usmart/extcon-uvc-power-objdump.txt`.
- Live DT/sysfs/boot snapshot: `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649` (note: userspace was a LieppOS GSI over stock vendor/kernel).
- APK calibration/ISP assets: `evidence/apk/infisens/assets/`; M170infDlp assets: `evidence/apk/infdlp/`.

## Public donor implementations
- [JAMBD/android_infiray_viewer](https://github.com/JAMBD/android_infiray_viewer) — independent P2 Pro Android UVC viewer; 256x192@25, 1/64 K conversion, raw frame handling.
- [leodj/p2pro-viewer](https://github.com/leodj/p2pro-viewer) — independent USB-trace-derived vdcmd implementation; control request/header/chunk/status behavior and a limited opcode table.
- [jiusiz/infiray](https://github.com/jiusiz/infiray) — InfiRay Xtherm demonstration/reference.
- [fbreitwieser/thermal-camera-android](https://github.com/fbreitwieser/thermal-camera-android) — compatible InfiRay/Topdon UVC host implementation.

Local shallow clones used for exact comparison are under `re/apps/donors/`. Donor hardware/firmware is not assumed identical to GQ5012BF1.
