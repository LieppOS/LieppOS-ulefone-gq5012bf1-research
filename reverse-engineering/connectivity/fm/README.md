# FM receiver (FM-KERNEL)

**Status: FM-KERNEL = DONE** (kernel driver + DT contract + audio route). The FM DSP patch/coeff
blobs, the YFT FM app/JNI and the MediaTek audio HAL remain proprietary userspace/firmware
scope.

| item | result |
|---|---|
| implementing silicon | MT6637 A-die FM core, controlled by the MT6878 CONNSYS via conninfra A-die SPI |
| kernel module | `fmradio_drv_connac2x.ko` (`depends=conninfra`) |
| source | NothingOSS `android_kernel_modules_nothing_mt6878` 2115d27 (alps-mp-u0.mp1-V9.9), `connectivity/fmradio/Build/connac2x` (`CFG_FM_PLAT=connac2x`, `CFG_BUILD_CONNAC2=true`, `CFG_FM_CHIP=mt6635`) |
| parity | **365/365 functions, 79/79 data**, imports 114/114, exports 1/1, modversions 115/115, export CRCs 1/1, modinfo 6/6, vermagic, section sizes 23/23. KCFI typeids are included in function bytes. |
| Ulefone delta in driver | none (stock is the unmodified MTK source) |
| board deltas | DT `fmradio { fm_lna_gpio = <&pio 72 0>; }` (not in the MTK reference mt6878.dts); headset-antenna GPIO 195 in `mt6369-accdet` |
| firmware | `/vendor/firmware/mt6635_fm_v1_patch.bin`, `mt6635_fm_v1_coeff.bin` via `request_firmware`; `fm_cust.cfg` |
| transport | `/dev/fm` ioctl (misc device) → conninfra sub-driver (`conninfra_sub_drv_ops_register`) → A-die SPI/top registers; RDS/IRQ via SPI 486 |
| audio | digital FM I2S, master 32 kHz, `FM_I2S_PAD_CONN` → AFE CONNSYS_I2S → HW_GAIN0 → ADDA DL → MT6369 → headset. See [`route.md`](route.md) |
| userspace | `YftFmRadio.apk` + `libyftfmjni.so` (system_ext); audio HAL `AudioALSAFMController` |

Rebuild: `scripts/build_ext.sh fmradio/Build/connac2x` (or `scripts/rebuild_all.sh`). Parity
files: `../binary-analysis/per-module/fmradio_drv_connac2x.*.tsv`.

## How this closes FM-RADIO-HEADSET's open questions

* Which chip: MT6637 A-die (not an external FM IC).
* Driver/source: exact, see above.
* Analog vs digital: digital via CONNSYS I2S (proven, `route.md`).
* Antenna: headset cable via GPIO 195, plus an FM LNA enable on GPIO 72 driven by the FM driver.

What stays open in FM-RADIO-HEADSET: physical LNA part and antenna matching (teardown) and
runtime RF performance.
