# AF calibration: EEPROM → kernel → HAL → lens

Cameras with AF data: 0 (imx989), 2 (s5kjn1main2), 3 (ov64b). Camera 1
(s5kjn1, fixed focus) has none. This matches CAMERA-VCMS.

## Path

```
module EEPROM (i2c-7/0x50, i2c-2/0x50, i2c-4/0x53)
  0x076d u16 LE ─┐
  0x076b u16 LE ─┤  read_data() → preload cache → do_2a_gain_<sensor>()
                 ▼
STRUCT_CAM_CAL_DATA_STRUCT.Single2A   (kernel ABI, sizeof 0x2a88)
  +0x874 S2aVer=1   +0x875 S2aBitEn   +0x876 S2aAfBitflagEn
  +0x878 S2aAf[0] ← 0x076d             +0x87a S2aAf[1] ← 0x076b
                 ▼  ioctl CAM_CALIOC_G_GKI_READ (0xEA88690F), Command = 3A_GAIN
libfeatureiodrv_mem.so CamCalHelper::getCamCalData → CamCalDrv
                 ▼
HAL 3A AF (labels +0x878 "AFInf", +0x87a "AFMacro":
           libcameracustom.camera_calibration.core.so DoCamCal2AGain)
                 ▼
lens position 0..1023 → V4L2_CID_FOCUS_ABSOLUTE → main_vcm / main4_vcm / main2_vcm
                 (CAMERA-VCMS: vcm_bits = 10, af_calib_bits = 10)
```

## Proven facts

| item | value | proof |
|---|---|---|
| infinity slot | `S2aAf[0]` (+0x878) ← EEPROM `0x076d` | kernel parser (byte-exact); HAL stores `AFInf` to +0x878 |
| macro slot | `S2aAf[1]` (+0x87a) ← EEPROM `0x076b` | same; HAL `AFMacro` at +0x87a |
| encoding | u16 little-endian raw DAC, **no scaling** in the kernel | parser copies the value directly |
| scale | 10-bit EEPROM DAC → 10-bit lens range: `af_calib_bits = vcm_bits = 10`, so no rescale is needed | CAMERA-VCMS lens table |
| ordering check | `S2aAf[0] > S2aAf[1]` → `yft_otp_state_<cam> = 0`. The values are still returned. | parser |
| convention | stereo provider log: "DAC: Macro(max), Infinite(min)". The kernel check (inf ≤ macro) matches it. | `libfeature.stereo.provider.so` string |
| flags | imx989 / s5kjn1main2: `S2aBitEn = 3` (AWB+AF), `S2aAfBitflagEn = 0x0c`. ov64b: `S2aBitEn = 2` (AF only), `S2aAfBitflagEn = 0`. | parsers |
| fallback | read failure → `S2aBitEn = 0` (`CAM_CAL_NONE_BITEN`); no layout → error code `CAM_CAL_ERR_NO_3A_GAIN`; HAL AF then runs uncalibrated | parsers + `get_cal_data` |
| unused AF fields | `S2aAf[2..7]`, the whole `S2aAF_t` struct (hall, temperatures, posture, middle, zoom) are left zero (memset) | parsers |

## Not asserted

* Physical meaning of EEPROM 0x76b / 0x76d. The stock **ODM reconstruction's
  local variable names** (`AFMacro` for 0x76d, `AFInf` for 0x76b) are the
  opposite of the HAL slot labels. Names are not binary facts. Only offset → slot
  and the HAL's slot labels are proven. With the HAL convention, 0x76d holds
  the infinity DAC and 0x76b the macro DAC.
* No per-unit values are recorded.
