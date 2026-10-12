# Authoritative staged source reconstruction queue

458 identities /471 occurrences; 108 uncertified identities. Generated from current identity-keyed audit, not a stale file replacement.

Completed integration (CANONICAL-INTEGRATION-01): AUDIO-BATCH-01, SCP-CONNECTIVITY-BATCH-01, AUDIO-DEPENDENCIES-BATCH-02, NEXT-DG-BATCH-01, ALL-C-TO-A-CLOSURE and the USB-TYPEC-CLOSURE C-evidence update; BOOT-DEPENDENCY-BATCH-01 (16 first-stage D->A). Retained C proof obligations are separate from code/hardware/component status.

## 1. FINISH:BATCH04:charger_class — P0_BOOT
- 1 identities: charger_class.ko
- Classes: C:1
- Source: ../android_kernel_modules_charging_battery_ulefone_gq5012bf1
- Provider gaps: NONE
- Proof needed: Srcversion-only raw OEM source-token/dependency lineage remains unavailable; instructions/data except fingerprint, ABI and relocations exact; no metadata waiver

## 2. FINISH:BATCH04:mtk_chg_type_det — P0_BOOT
- 1 identities: mtk_chg_type_det.ko
- Classes: C:1
- Source: ../android_kernel_modules_charging_battery_ulefone_gq5012bf1
- Provider gaps: FINISH:BATCH04:charger_class;FINISH:BATCH04:tcpc_class
- Proof needed: Srcversion-only raw OEM source-token/dependency lineage remains unavailable; instructions/data except fingerprint, ABI and relocations exact; no metadata waiver

## 3. FINISH:BATCH04:rt_pd_manager — P0_BOOT
- 1 identities: rt_pd_manager.ko
- Classes: C:1
- Source: ../android_kernel_modules_usb_typec_ulefone_gq5012bf1
- Provider gaps: FINISH:BATCH04:tcpc_class
- Proof needed: Srcversion-only raw OEM source-token/dependency lineage remains unavailable; instructions/data except fingerprint, ABI and relocations exact; no metadata waiver

## 4. FINISH:BATCH04:tcpc_class — P0_BOOT
- 1 identities: tcpc_class.ko
- Classes: C:1
- Source: ../android_kernel_modules_usb_typec_ulefone_gq5012bf1
- Provider gaps: NONE
- Proof needed: 709/709 instruction bodies/positions and 113/114 data objects exact, including all54 timers; natural srcversion, six source-line diagnostic strings/37 BUG lines and string-pool relocations remain; no A/B waiver

## 5. FINISH:BATCH04:tcpc_mt6375 — P0_BOOT
- 1 identities: tcpc_mt6375.ko
- Classes: C:1
- Source: ../android_kernel_modules_usb_typec_ulefone_gq5012bf1
- Provider gaps: FINISH:BATCH04:tcpc_class
- Proof needed: 66/66 code exact; genuine license/version order restored; unknown +1 counter prefix and natural srcversion remain; no fabricated declarations or metadata

## 6. FINISH:ST21NFC — P0_BOOT
- 1 identities: st21nfc.ko
- Classes: C:1
- Source: ../Reverse Engineer - DONE/ST21NFC/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 7. FINISH:TRUSTKERNEL-SOURCE-ABI — P0_BOOT
- 1 identities: tkcore.ko
- Classes: C:1
- Source: ../Reverse Engineer - BLOCKED/TRUSTKERNEL-ABI-ISLAND/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 8. FINISH:YFT-DEVINFO — P0_BOOT
- 1 identities: yft_devinfo.ko
- Classes: C:1
- Source: ../Reverse Engineer - PARTIAL/YFT-DEVINFO/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 9. PRESERVE:AW2013-RGB-LED — P0_BOOT
- 1 identities: leds-rgb-aw2013.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/AW2013-RGB-LED/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 10. PRESERVE:DISPLAY-GLUE — P0_BOOT
- 7 identities: leds-mtk-disp.ko;mediatek-drm-gateic.ko;met_backlight_api.ko;mtk-pwm.ko;mtk_disp_sec.ko;pwm-mtk-disp.ko;rt4831a_drv.ko
- Classes: G:7
- Source: .
- Provider gaps: CANDIDATE:device_modules:drivers/dma-buf/heaps
- Proof needed: Independent source-input closure unproved. Existing artifact parity is not discarded; inspect ../Reverse Engineer - DONE/BACKLIGHT-DISPLAY-GLUE/scripts/glue.py and preserve all exact inputs before claiming A/B.

## 11. PRESERVE:FFA-V10 — P0_BOOT
- 1 identities: ffa_v10.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/FFA-V10/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 12. PRESERVE:FINGERPRINT-PLATFORM-SHIM — P0_BOOT
- 1 identities: fingerprint.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/FINGERPRINT-PLATFORM-SHIM/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 13. PRESERVE:MEDIATEK-DRM — P0_BOOT
- 1 identities: mediatek-drm-panel-drv.ko
- Classes: G:1
- Source: .
- Provider gaps: PRESERVE:DISPLAY-GLUE
- Proof needed: Independent source-input closure unproved. Existing artifact parity is not discarded; inspect ../Reverse Engineer - DONE/MEDIATEK-DRM/scripts/build.sh and preserve all exact inputs before claiming A/B.

## 14. PRESERVE:MICROARRAY-FP-TEE — P0_BOOT
- 1 identities: microarray_fp_tee.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/MICROARRAY-FP-TEE/source
- Provider gaps: FINISH:TRUSTKERNEL-SOURCE-ABI;PRESERVE:FINGERPRINT-PLATFORM-SHIM;PRESERVE:SPI-MT65XX
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 15. PRESERVE:PROGRAMMABLE-KEYS — P0_BOOT
- 1 identities: yft_gpio_keys.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/PROGRAMMABLE-KEYS/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 16. PRESERVE:RT5133-POWER-IC — P0_BOOT
- 2 identities: extdev_io_class.ko;rt5133-regulator.ko
- Classes: G:2
- Source: ../Reverse Engineer - DONE/RT5133-POWER-IC/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 17. PRESERVE:SC8510-BIDIRECTIONAL-CHARGE-PUMP — P0_BOOT
- 1 identities: sc851x_charger.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/SC8510-BIDIRECTIONAL-CHARGE-PUMP/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 18. PRESERVE:SC8571-CHARGE-PUMP — P0_BOOT
- 1 identities: sc8571_charger.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/SC8571-CHARGE-PUMP/source
- Provider gaps: FINISH:BATCH04:charger_class
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 19. PRESERVE:SH366003-FUEL-GAUGE — P0_BOOT
- 1 identities: sh366003_fg.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/SH366003-FUEL-GAUGE/source
- Provider gaps: FINISH:YFT-DEVINFO
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 20. PRESERVE:SPI-MT65XX — P0_BOOT
- 1 identities: spi-mt65xx.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/SPI-MT65XX/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 21. PRESERVE:TKCORE-DRV — P0_BOOT
- 1 identities: tkcore_drv.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/TKCORE-DRV/source
- Provider gaps: FINISH:TRUSTKERNEL-SOURCE-ABI;PRESERVE:FFA-V10
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 22. PRESERVE:VTDR6115-DISPLAY — P0_BOOT
- 1 identities: panel-ky-vtdr6115-dphy-cmd.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/VTDR6115-DISPLAY/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 23. PRESERVE:YFT-TPD-GESTURE — P0_BOOT
- 1 identities: yft_tpd_gesture.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/YFT-TPD-GESTURE/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 24. PRESERVE:GZ-MAIN-MOD — P1_RADIO_OR_SECURITY
- 1 identities: gz_main_mod.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/GZ-MAIN-MOD/source
- Provider gaps: CANDIDATE:device_modules:drivers/dma-buf/heaps;PRESERVE:FFA-V10;PRESERVE:GZ-TRANSPORT;PRESERVE:GZ-TZ-SYSTEM;PRESERVE:TMEM-FFA
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 25. PRESERVE:GZ-TRANSPORT — P1_RADIO_OR_SECURITY
- 5 identities: gz_ipc_mod.ko;gz_irq_mod.ko;gz_log_mod.ko;gz_trusty_mod.ko;gz_virtio_mod.ko
- Classes: G:5
- Source: ../Reverse Engineer - DONE/GZ-TRANSPORT/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 26. PRESERVE:GZ-TZ-SYSTEM — P1_RADIO_OR_SECURITY
- 1 identities: gz_tz_system.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/GZ-TZ-SYSTEM/source
- Provider gaps: PRESERVE:GZ-TRANSPORT
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 27. PRESERVE:MODEM — P1_RADIO_OR_SECURITY
- 7 identities: c2k_usb.ko;c2k_usb_f_via_atc.ko;c2k_usb_f_via_ets.ko;c2k_usb_f_via_modem.ko;md_cooling_all.ko;mddp.ko;mtk_md_power_throttling.ko
- Classes: G:7
- Source: .
- Provider gaps: NONE
- Proof needed: Independent source-input closure unproved. Existing artifact parity is not discarded; inspect reverse-engineering/modem/scripts/rebuild_all.sh and preserve all exact inputs before claiming A/B.

## 28. PRESERVE:TMEM-FFA — P1_RADIO_OR_SECURITY
- 1 identities: tmem_ffa.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/TMEM-FFA/source
- Provider gaps: FINISH:TRUSTKERNEL-SOURCE-ABI;PRESERVE:FFA-V10;PRESERVE:GZ-TZ-SYSTEM
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 29. FINISH:FT3680-TOUCH — P2_ACTIVE_FEATURE
- 1 identities: focaltech_touch_spi_ft3680.ko
- Classes: C:1
- Source: ../Reverse Engineer - PARTIAL/FT3680-TOUCH/source
- Provider gaps: FINISH:YFT-DEVINFO;PRESERVE:YFT-TPD-GESTURE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 30. PRESERVE:CAMERA-EEPROMS — P2_ACTIVE_FEATURE
- 1 identities: camera_eeprom_v4l2.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/CAMERA-EEPROMS/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 31. PRESERVE:CAMERA-VCMS — P2_ACTIVE_FEATURE
- 6 identities: camera_af_media.ko;main2_vcm.ko;main3_vcm.ko;main4_vcm.ko;main_vcm.ko;sub_vcm.ko
- Classes: G:6
- Source: ../Reverse Engineer - DONE/CAMERA-VCMS/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 32. PRESERVE:CO5300-REAR-DISPLAY — P2_ACTIVE_FEATURE
- 1 identities: spi_tiny_co5300_lcd.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/CO5300-REAR-DISPLAY/source
- Provider gaps: FINISH:YFT-DEVINFO;PRESERVE:HYNITRON-REAR-TOUCH
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 33. PRESERVE:CUSTOM-LDO — P2_ACTIVE_FEATURE
- 1 identities: custom-ldo.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/CUSTOM-LDO/source
- Provider gaps: PRESERVE:WL2868-CAMERA-LDO
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 34. PRESERVE:FM78100-COMPANION — P2_ACTIVE_FEATURE
- 1 identities: yft_tiny2c_usb.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/FM78100-COMPANION/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 35. PRESERVE:HYNITRON-REAR-TOUCH — P2_ACTIVE_FEATURE
- 1 identities: hynitron.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/HYNITRON-REAR-TOUCH/source
- Provider gaps: FINISH:YFT-DEVINFO
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 36. PRESERVE:WL2868-CAMERA-LDO — P2_ACTIVE_FEATURE
- 1 identities: custom-ldo-wl2868.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/WL2868-CAMERA-LDO/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 37. AUDIO-BATCH-01:CODEC-AMP — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: aw883xx_driver.ko
- Classes: C:1
- Source: ../android_kernel_modules_audio_ulefone_gq5012bf1
- Provider gaps: NONE
- Proof needed: inlined v1.7.1 scene-parser codegen (insertion-sort loop shape) not reproduced; stock semantics restored

## 38. CANDIDATE:device_modules:drivers/dma-buf/heaps — P3_LOADED_PLATFORM_OR_OPTIONAL
- 2 identities: mtk_heap_debug.ko;mtk_sec_heap.ko
- Classes: D:2
- Source: ../kernel-research/nothing-mt6878/device_modules
- Provider gaps: PRESERVE:TMEM-FFA
- Proof needed: Public candidate target at drivers/dma-buf/heaps; clean stock-compatible integration/config/provider-CRC/KCFI and full parity are not demonstrated. No missing implementation or compiler failure is assumed.

## 39. CANDIDATE:device_modules:drivers/input/touchscreen — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: tui-common.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/input/touchscreen
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 40. CANDIDATE:device_modules:drivers/media/platform/mtk-jpeg — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: mtk_jpeg.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/media/platform/mtk-jpeg
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 41. CANDIDATE:device_modules:drivers/misc/mediatek/apusys/sapu — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: sapu.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/apusys/sapu
- Provider gaps: CANDIDATE:device_modules:drivers/dma-buf/heaps;PRESERVE:GZ-TRANSPORT;PRESERVE:GZ-TZ-SYSTEM
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 42. CANDIDATE:device_modules:drivers/misc/mediatek/cache-auditor/cpuqos_v3 — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: cpuqos_v3.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/cache-auditor/cpuqos_v3
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 43. CANDIDATE:device_modules:drivers/misc/mediatek/flashlight — P3_LOADED_PLATFORM_OR_OPTIONAL
- 2 identities: flashlight.ko;mtk-composite.ko
- Classes: D:2
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/flashlight
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 44. CANDIDATE:device_modules:drivers/misc/mediatek/irtx — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: mtk_irtx_pwm.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/irtx
- Provider gaps: PRESERVE:DISPLAY-GLUE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 45. CANDIDATE:device_modules:drivers/misc/mediatek/lpm — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: mtk-lpm.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/lpm
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 46. CANDIDATE:device_modules:drivers/misc/mediatek/lpm/governors/MHSP — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: lpm-gov-MHSP.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/lpm/governors/MHSP
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 47. CANDIDATE:device_modules:drivers/misc/mediatek/lpm/modules/debug/mt6878 — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: mtk-lpm-dbg-mt6878.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/lpm/modules/debug/mt6878
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/lpm/modules/debug/v2;CANDIDATE:device_modules:drivers/misc/mediatek/swpm
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 48. CANDIDATE:device_modules:drivers/misc/mediatek/lpm/modules/debug/v2 — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: mtk-lpm-dbg-common-v2.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/lpm/modules/debug/v2
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/lpm
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 49. CANDIDATE:device_modules:drivers/misc/mediatek/lpm/modules/platform/v1 — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: mtk-lpm-plat-v1.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/lpm/modules/platform/v1
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/lpm;CANDIDATE:device_modules:drivers/misc/mediatek/lpm/modules/debug/v2
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 50. CANDIDATE:device_modules:drivers/misc/mediatek/mbraink — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: mtk_mbraink.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/mbraink
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/lpm/modules/debug/v2;CANDIDATE:device_modules:drivers/misc/mediatek/performance/fpsgo_v3;CANDIDATE:device_modules:drivers/misc/mediatek/swpm
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 51. CANDIDATE:device_modules:drivers/misc/mediatek/mmdvfs — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: mtk-mmdvfs-v3-start.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules
- Provider gaps: NONE
- Proof needed: Public candidate target at drivers/misc/mediatek/mmdvfs; clean stock-compatible integration/config/provider-CRC/KCFI and full parity are not demonstrated. No missing implementation or compiler failure is assumed.

## 52. CANDIDATE:device_modules:drivers/misc/mediatek/perf_common — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: mtk_perf_common.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/perf_common
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 53. CANDIDATE:device_modules:drivers/misc/mediatek/performance — P3_LOADED_PLATFORM_OR_OPTIONAL
- 4 identities: mtk_ioctl_powerhal.ko;mtk_ioctl_touch_boost.ko;mtk_perf_ioctl.ko;mtk_perf_ioctl_magt.ko
- Classes: D:4
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/performance
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 54. CANDIDATE:device_modules:drivers/misc/mediatek/performance/fpsgo_v3 — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: mtk_fpsgo.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/performance/fpsgo_v3
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/performance;CANDIDATE:device_modules:drivers/misc/mediatek/performance/powerhal_cpu_ctrl;CANDIDATE:device_modules:drivers/misc/mediatek/sched
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 55. CANDIDATE:device_modules:drivers/misc/mediatek/performance/frs — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: frs.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/performance/frs
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/performance/fpsgo_v3
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 56. CANDIDATE:device_modules:drivers/misc/mediatek/performance/load_track — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: load_track.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/performance/load_track
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 57. CANDIDATE:device_modules:drivers/misc/mediatek/performance/powerhal_cpu_ctrl — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: powerhal_cpu_ctrl.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/performance/powerhal_cpu_ctrl
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/performance
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 58. CANDIDATE:device_modules:drivers/misc/mediatek/performance/touch_boost — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: touch_boost.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/performance/touch_boost
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/performance;CANDIDATE:device_modules:drivers/misc/mediatek/performance/powerhal_cpu_ctrl;CANDIDATE:device_modules:drivers/misc/mediatek/sched
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 59. CANDIDATE:device_modules:drivers/misc/mediatek/performance/uload_ind — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: uload_ind.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/performance/uload_ind
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/performance/load_track
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 60. CANDIDATE:device_modules:drivers/misc/mediatek/sched — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: scheduler.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/sched
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/cache-auditor/cpuqos_v3;CANDIDATE:device_modules:drivers/misc/mediatek/performance/powerhal_cpu_ctrl
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 61. CANDIDATE:device_modules:drivers/misc/mediatek/ssc — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: mtk-ssc.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/ssc
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 62. CANDIDATE:device_modules:drivers/misc/mediatek/ssc/debug/v2 — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: mtk-ssc-dbg-v2.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/ssc/debug/v2
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/ssc
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 63. CANDIDATE:device_modules:drivers/misc/mediatek/swpm — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: mtk-swpm.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/swpm
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 64. CANDIDATE:device_modules:drivers/misc/mediatek/swpm/modules/debug/v1 — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: mtk-swpm-dbg-common-v1.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/swpm/modules/debug/v1
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/swpm
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 65. CANDIDATE:device_modules:drivers/misc/mediatek/swpm/modules/debug/v6878 — P3_LOADED_PLATFORM_OR_OPTIONAL
- 2 identities: mtk-swpm-cpu-dbg-v6878.ko;mtk-swpm-dbg-v6878.ko
- Classes: D:2
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/swpm/modules/debug/v6878
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/swpm;CANDIDATE:device_modules:drivers/misc/mediatek/swpm/modules/debug/v1
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 66. CANDIDATE:device_modules:drivers/misc/mediatek/task_turbo — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: task_turbo.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/task_turbo
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 67. CANDIDATE:device_modules:drivers/misc/mediatek/widevine_drm — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: widevine_driver.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/widevine_drm
- Provider gaps: CANDIDATE:device_modules:drivers/dma-buf/heaps
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 68. CANDIDATE:device_modules:drivers/nvmem — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: nvmem-mt635x-efuse.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/nvmem
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 69. CANDIDATE:kernel:drivers/power/reset — P3_LOADED_PLATFORM_OR_OPTIONAL
- 2 identities: reboot-mode.ko;syscon-reboot-mode.ko
- Classes: D:2
- Source: ../kernel-research/nothing-mt6878/kernel/drivers/power/reset
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 70. CANDIDATE:kernel_modules:fpsgo_cus — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: fpsgo.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/kernel_modules/fpsgo_cus
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/performance/fpsgo_v3
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 71. CANDIDATE:kernel_modules:hbt_driver_cus — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: hbt.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/kernel_modules/hbt_driver_cus
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 72. CANDIDATE:kernel_modules:msync2_frd_cus — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: msync2_frd.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/kernel_modules/msync2_frd_cus
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 73. PRESERVE:AW36515-FLASH — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: aw36515.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/AW36515-FLASH/source
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/flashlight
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 74. PRESERVE:AW36518-FLASH — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: aw36518.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/AW36518-FLASH/source
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/flashlight;FINISH:YFT-DEVINFO
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 75. PRESERVE:AW36518-V2-FLASH — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: aw36518_v2.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/AW36518-V2-FLASH/source
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/flashlight
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 76. PRESERVE:DW9781C-OIS — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: dw9781c.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/DW9781C-OIS/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 77. PRESERVE:LN2403-CAMPLIGHT — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: leds-ln2403.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/LN2403-CAMPLIGHT/source
- Provider gaps: PRESERVE:DISPLAY-GLUE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 78. CANDIDATE:kernel_modules:sched_cus — P4_DIAGNOSTIC_OR_REFERENCE
- 1 identities: scheduler_ext.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/kernel_modules/sched_cus
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 79. MALI-DMA-BUF-DIAGNOSTIC — P4_DIAGNOSTIC_OR_REFERENCE
- 1 identities: mali_dmabuf_test_mt6878_r44.ko
- Classes: D:1
- Source: git-object:gpu/gpu_mali/mali_avalon/mali-r44p1/drivers/base/arm/dma_buf_test_exporter/dma-buf-test-exporter.c
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

