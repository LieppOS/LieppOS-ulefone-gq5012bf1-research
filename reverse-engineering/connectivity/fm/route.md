# FM receiver: end-to-end route (GQ5012BF1)

## Answer: how does FM audio reach the AFE?

FM audio is **digital I2S over the internal CONNSYS audio interface**: the AFE "Connsys I2S"
DAI, `CONNSYS_I2S_CH1/CH2`. It does **not** use the analog codec input, an external I2S pad, or
the merge interface.

Proof chain, all static:

1. `fmradio_drv_connac2x.ko` (365/365 functions, 79/79 data, ABI exact) asks conninfra for the
   A-die id. On this board that is 0x6637 (`mt6637.md`). `fm_which_chip()`
   (`fmradio/core/fm_main.c:288`) maps 0x6631/0x6635/0x6637 → `FM_AD_DIE_CHIP` and reports
   0x6637 as 0x6635 "for APP compatible".
2. `fm_cust_config()` (`fmradio/core/fm_config.c:447`): for `FM_AD_DIE_CHIP`/`FM_SOC_CHIP` it sets
   `aud_path = FM_AUD_I2S`, `i2s_info.mode = FM_I2S_MASTER`, `rate = FM_I2S_32K`,
   `i2s_pad = FM_I2S_PAD_CONN`. `FM_AUD_ANALOG` is only reachable for `FM_COMBO_CHIP` builds with
   `FM_ANALOG_INPUT`, which does not apply here.
3. The audio HAL `audio.primary.mediatek.so` (`AudioALSAFMController`, `WCNChipController`) reads
   this through `FM_IOCTL_GET_AUDIO_INFO`. It asserts `aud_path != FM_AUD_ANALOG` and checks
   `IsFmChipPadSelConnSys` (strings `FM_I2S_PAD_CONN`, `FM_I2S_32K`, `FM_I2S_MASTER`).
4. `vendor/etc/audio_device.xml` FM paths only use the CONNSYS I2S inputs of the MT6878 AFE
   (`snd-soc-mt6878-afe`, DONE in the audio pass):
   * `CONNSYS_TO_ADDA_DL`: `HW_GAIN0_IN_CH1/2 ← CONNSYS_I2S_CH1/2`, `ADDA_DL_CH1/2 ←
     HW_GAIN0_OUT_CH1/2`. This goes to the MT6369 DAC → HPL/HPR (wired headset/headphones).
   * `CONNSYS_TO_I2S1`: `HW_GAIN0 → I2SOUT4_CH1/2`. I2S_OUT4 is the AW88394 smart-amp port (audio
     research). This path is declared, but the audio policy does not list FM as a Speaker source,
     so runtime use is unproven.
   * `CONNSYS_TO_CAPTURE3` (`UL0 ← CONNSYS_I2S`) and `HW_GAIN1_TO_CAPTURE6` (`UL4 ← HW_GAIN0`):
     FM recording / software path.
5. `audio_policy_configuration.xml`: `devicePort "FM Tuner In"` (`AUDIO_DEVICE_IN_FM_TUNER`) is a
   source for the **Wired Headset, Wired Headphones, USB Device Out and USB Headset Out** routes.
   It is not a source for Speaker, Earpiece or BT SCO.

## Full trace

```
YftFmRadio.apk (system_ext, YFT app; replaces MTK FMRadio)
  └─ libyftfmjni.so (system_ext/lib64; JNI: FMR_tune/seek/scan/stop_scan, RDS on/off/read, BLER)
       └─ open("/dev/fm") + FM_IOCTL_* (fm_ioctl.h: POWERUP, TUNE, SEEK(_NEW), SCAN(_NEW), STOP_SCAN,
          RDS_ONOFF, RDS_SUPPORT, GETRSSI, SETMONOSTERO, GET_AUDIO_INFO, ...)
            └─ fmradio_drv_connac2x.ko  (misc dev "fm"; DT node "mediatek,fm": IRQ 486,
               family-id 0x6983, host-id 0x6878, conn-id 0x205)
                 ├─ POWERUP: gpio_set_value(GPIO 72 /*fmradio fm_lna_gpio*/, 1) → fm_powerup → fm_tune
                 ├─ conninfra_pwr_on(CONNDRV_TYPE_FM), conninfra_spi_read/write (A-die regs),
                 │  conninfra_adie_top_ck_en_on, fm_top_reg_* → MT6637 FM core
                 ├─ DSP patch/coeff: request_firmware("mt6635_fm_v<rom>_patch.bin" / "_coeff.bin")
                 │  (connac2x_patch_tbl; 0x6631 would use mt6631_* instead); stock ships v1 only
                 └─ fm_cust.cfg (vendor/firmware) RX thresholds, de-emphasis 50 µs, OSC 26 MHz
  Audio side (parallel):
  AudioManager/AudioPolicy: AudioPatch FM Tuner In → Wired Headset/Headphones
    └─ audio.primary.mediatek.so AudioALSAFMController.setFmEnable()
         ├─ ioctl(/dev/fm, FM_IOCTL_GET_AUDIO_INFO) → I2S master 32 kHz, pad = CONN
         ├─ ioctl FM_IOCTL_I2S_SETTING / FM_IOCTL_SETVOL (chip volume)
         └─ tinymix path CONNSYS_TO_ADDA_DL → AFE HW_GAIN0 (digital FM volume) → ADDA DL
              → MT6369 DL → HPL/HPR → headset
  Antenna: headset cable; GPIO 195 (mt6369-accdet, YFT delta) switches it with plug state.
```

## Capabilities (driver level)

| item | value | source |
|---|---|---|
| band | 87.5–108.0 MHz (`FM_RX_BAND_FREQ_L/H = 8750/10800`, `FM_UE_FREQ_MIN/MAX`) | `fmradio/inc/fm_config.h` |
| seek / scan | yes (`FM_IOCTL_SEEK`, `_SEEK_NEW`, `_SCAN`, `_SCAN_NEW`, `_STOP_SCAN`, `_PRE_SEARCH`, `_SET_SEARCH_THRESHOLD`) | `fm_ioctl.h`, JNI exports |
| RDS | yes, RX (`mt6635_fm_rds.o` linked, `FM_IOCTL_RDS_ONOFF/RDS_SUPPORT`, `readRds`, `readRdsBler`) | Kbuild.include, JNI |
| FM TX | ioctls exist, but connac2x/A-die is RX only (`FMRXForceDisableFMTX` in HAL) | HAL strings |
| short antenna | no (`fm_cust.cfg` has no short-antenna setting; the antenna is the headset cable) | config |
| de-emphasis | 50 µs (`FM_RX_DEEMPHASIS = 0`) | `fm_cust.cfg` |

## Remaining runtime items

* `fm_lna_gpio` / GPIO 195 toggling and the CONNSYS I2S rate on a running device. A read-only
  test plan is in `../runtime-test-plan.md`.
* The actual `rom_ver` (it selects `mt6635_fm_v<N>_*`). Stock ships only `mt6635_fm_v1_*`, which
  implies ROM v1.
