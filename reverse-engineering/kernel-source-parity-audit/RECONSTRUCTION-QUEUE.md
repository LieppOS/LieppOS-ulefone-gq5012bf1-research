# Authoritative staged source reconstruction queue

458 identities /471 occurrences; 30 uncertified identities. Generated from current identity-keyed audit, not a stale file replacement.

Completed integration (CANONICAL-INTEGRATION-01): AUDIO-BATCH-01, SCP-CONNECTIVITY-BATCH-01, AUDIO-DEPENDENCIES-BATCH-02, NEXT-DG-BATCH-01, ALL-C-TO-A-CLOSURE and the USB-TYPEC-CLOSURE C-evidence update; BOOT-DEPENDENCY-BATCH-01 (16 first-stage D->A); LOW-POWER-BATCH-01 (12 LPM/SWPM/SSC/mbraink D->A); PERFORMANCE-POWERHAL-BATCH-01 (14 performance/PowerHAL/FPSGO/CPUQoS D->A); KDM-MEDIA-SECURITY-BATCH-01 (10 media/security/platform D->A; flashlight retained D); REMAINING-KERNEL-SOURCE-BATCH-01 (5 reboot/kernel_modules/Mali-test D->A); G-SOURCE-RECOVERY-BATCH-01 (22 camera-lens/modem-interface/secure-transport G->A, tmem_ffa G->C with 4 TrustKernel import CRCs not waived); DISPLAY-BACKLIGHT-G-BATCH-01 (8 display/backlight/PWM/MET-backlight G->A); G-SOURCE-RECOVERY-BATCH-02 (7 board-IO/camera-aux/biometric G->A; aw36515/aw36518/aw36518_v2/fingerprint/tkcore_drv G->C). Retained C proof obligations are separate from code/hardware/component status.

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

## 9. G-SOURCE-RECOVERY-BATCH-02:biometric_transport — P0_BOOT
- 2 identities: fingerprint.ko;tkcore_drv.ko
- Classes: C:2
- Source: ../android_kernel_modules_biometric_transport_ulefone_gq5012bf1
- Provider gaps: FINISH:TRUSTKERNEL-SOURCE-ABI
- Proof needed: {"data":"28/30","functions":"50/50","imports":{"__tee_get":{"rebuilt":"0xe6373d87","stock":"0xa4df7b8a"},"tee_core_add":{"rebuilt":"0xc606dc1c","stock":"0x74f0ee2b"},"tee_core_alloc":{"rebuilt":"0x95d1d719","stock":"0x68aaf1dc"},"tee_core_del":{"rebuilt":"0x422a1656","stock":"0xf53dbff2"},"tee_supp_cmd":{"rebuilt":"0x964749ad","stock":"0x6f7dfbee"}},"nonGNU_sections":[{"different_overlap_bytes":21,"rebuilt_bytes":245,"rebuilt_sha256":"37c3f77327d32879ef674f93e8565f0bb7ca22bc3c4d115b2ee3cef13af84751","section":".modinfo","stock_bytes":245,"stock_sha256":"d9a70670e1f34f0dee45fa1f843ba2365bb9a2fec273b969983d73f9e9c31007"},{"different_overlap_bytes":20,"rebuilt_bytes":4288,"rebuilt_sha256":"79999f58c0856dbc54d536bd16600e8404fe459282f4370ff524dc9d9e5eaf5e","section":"__versions","stock_bytes":4288,"stock_sha256":"d48d658c8e10ac802599886aeef636c02e8897a4239eb127d34a3f7a262cdecc"}],"provenance_gap":"Original exactsourcegeneration/sourcecode scheduling/dataorder/metadata provenance notfound; do not waive"};{"data":"30/35","functions":"16/16","imports":{},"nonGNU_sections":[{"different_overlap_bytes":98,"rebuilt_bytes":5976,"rebuilt_sha256":"0b733cd4d5f707889ef6afede728bd781392db7d47f9f1f6ebd4ac8f31328263","section":".rela.text","stock_bytes":5976,"stock_sha256":"6dd351960a57661b27e520d0090fa5d0b88308a577aeff14616ddf23fc63f1cf"},{"different_overlap_bytes":4,"rebuilt_bytes":192,"rebuilt_sha256":"ec9c1945a09b2c74801663de19f5a1560a6888dc2cf69fd6f79bc986efc6073d","section":".rela.init.text","stock_bytes":192,"stock_sha256":"5a429623f7144a771bda086f22e496f250eb74106ce419042ccc0a19970db03b"},{"different_overlap_bytes":1,"rebuilt_bytes":168,"rebuilt_sha256":"7559b265e0fe023f277dde79ca81cbc23d355cc1b5b5e12539ae36a545e391fe","section":".rela.data","stock_bytes":168,"stock_sha256":"0fe27a66bab56e60085a5f0c87dad33e40f4736b7772e588e2b62fec87f36d0b"},{"different_overlap_bytes":1431,"rebuilt_bytes":1534,"rebuilt_sha256":"0dcc5ec1879a53ffe6b7aa4d1039ed5ad182eca4f9aaabf75129cb06c5426677","section":".rodata.str1.1","stock_bytes":1529,"stock_sha256":"6f9a3c594603befa39a2a690d5593a7baa9d9edd9ca40e1e4fea315cbd24ce9b"},{"different_overlap_bytes":18,"rebuilt_bytes":4632,"rebuilt_sha256":"8ee3c5cd610d471f34071f00bffdebf0234fda783b18f91f561ae2d991e28007","section":".symtab","stock_bytes":4632,"stock_sha256":"62afbb7e6ad805570f735381a8dcdd379a1df431f87b4f33f926174a5eb625b6"},{"different_overlap_bytes":169,"rebuilt_bytes":2887,"rebuilt_sha256":"c28853b85264a672ae80202fb779193f58d3927b1c29455aa4ebc43115b68d5e","section":".strtab","stock_bytes":2887,"stock_sha256":"1eadfa365a4fc0c50d24a394333d6a725bddd76acd9d2da6292ad82f57fe2cd8"}],"provenance_gap":"LiteralOEMglue/headerlist notfound; pure-Ccandidateprovenance explicit"}

## 10. PRESERVE:SC8510-BIDIRECTIONAL-CHARGE-PUMP — P0_BOOT
- 1 identities: sc851x_charger.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/SC8510-BIDIRECTIONAL-CHARGE-PUMP/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 11. PRESERVE:SC8571-CHARGE-PUMP — P0_BOOT
- 1 identities: sc8571_charger.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/SC8571-CHARGE-PUMP/source
- Provider gaps: FINISH:BATCH04:charger_class
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 12. PRESERVE:SH366003-FUEL-GAUGE — P0_BOOT
- 1 identities: sh366003_fg.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/SH366003-FUEL-GAUGE/source
- Provider gaps: FINISH:YFT-DEVINFO
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 13. PRESERVE:VTDR6115-DISPLAY — P0_BOOT
- 1 identities: panel-ky-vtdr6115-dphy-cmd.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/VTDR6115-DISPLAY/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 14. PRESERVE:YFT-TPD-GESTURE — P0_BOOT
- 1 identities: yft_tpd_gesture.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/YFT-TPD-GESTURE/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 15. G-SOURCE-RECOVERY-BATCH-01:NORMAL-WORLD-SECURE-TRANSPORT — P1_RADIO_OR_SECURITY
- 1 identities: tmem_ffa.ko
- Classes: C:1
- Source: ../android_kernel_modules_secure_transport_ulefone_gq5012bf1
- Provider gaps: FINISH:TRUSTKERNEL-SOURCE-ABI
- Proof needed: Four naturalpublicTrustKernel7:2.2 provider importCRCs differ fromstock6:1.1: TEEC_FinalizeContext/InitializeContext/OpenSession/RegisterSharedMemory; full141functions/allnonversiondata/rawrelocs exact; originalprivatecontextABI sourceclosure missing. SourceB1/B2 reproducible, NOTstockaccepted; outsideC tkcore ownerunchanged.

## 16. FINISH:FT3680-TOUCH — P2_ACTIVE_FEATURE
- 1 identities: focaltech_touch_spi_ft3680.ko
- Classes: C:1
- Source: ../Reverse Engineer - PARTIAL/FT3680-TOUCH/source
- Provider gaps: FINISH:YFT-DEVINFO;PRESERVE:YFT-TPD-GESTURE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 17. PRESERVE:CO5300-REAR-DISPLAY — P2_ACTIVE_FEATURE
- 1 identities: spi_tiny_co5300_lcd.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/CO5300-REAR-DISPLAY/source
- Provider gaps: FINISH:YFT-DEVINFO;PRESERVE:HYNITRON-REAR-TOUCH
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 18. PRESERVE:CUSTOM-LDO — P2_ACTIVE_FEATURE
- 1 identities: custom-ldo.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/CUSTOM-LDO/source
- Provider gaps: PRESERVE:WL2868-CAMERA-LDO
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 19. PRESERVE:FM78100-COMPANION — P2_ACTIVE_FEATURE
- 1 identities: yft_tiny2c_usb.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/FM78100-COMPANION/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 20. PRESERVE:HYNITRON-REAR-TOUCH — P2_ACTIVE_FEATURE
- 1 identities: hynitron.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/HYNITRON-REAR-TOUCH/source
- Provider gaps: FINISH:YFT-DEVINFO
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 21. PRESERVE:WL2868-CAMERA-LDO — P2_ACTIVE_FEATURE
- 1 identities: custom-ldo-wl2868.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/WL2868-CAMERA-LDO/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 22. AUDIO-BATCH-01:CODEC-AMP — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: aw883xx_driver.ko
- Classes: C:1
- Source: ../android_kernel_modules_audio_ulefone_gq5012bf1
- Provider gaps: NONE
- Proof needed: inlined v1.7.1 scene-parser codegen (insertion-sort loop shape) not reproduced; stock semantics restored

## 23. CANDIDATE:device_modules:drivers/misc/mediatek/flashlight — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: flashlight.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/flashlight
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 24. CANDIDATE:kernel_modules:fpsgo_cus — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: fpsgo.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/kernel_modules/fpsgo_cus
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 25. CANDIDATE:kernel_modules:msync2_frd_cus — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: msync2_frd.ko
- Classes: D:1
- Source: ../kernel-research/nothing-mt6878/kernel_modules/msync2_frd_cus
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

## 26. G-SOURCE-RECOVERY-BATCH-02:camera_aux — P3_LOADED_PLATFORM_OR_OPTIONAL
- 3 identities: aw36515.ko;aw36518.ko;aw36518_v2.ko
- Classes: C:3
- Source: ../android_kernel_modules_camera_aux_ulefone_gq5012bf1
- Provider gaps: CANDIDATE:device_modules:drivers/misc/mediatek/flashlight;FINISH:YFT-DEVINFO
- Proof needed: {"data":"28/31","functions":"22/23","imports":{},"nonGNU_sections":[{"different_overlap_bytes":4,"rebuilt_bytes":5948,"rebuilt_sha256":"4ba98cfa1aa8d7653cbfbc6428fad977019b4541f474e9c34a9e440c02683c62","section":".text","stock_bytes":5948,"stock_sha256":"6560e67b7e587047d63a4d444240bd1b3f9e4bca750d0f399b6ad18de1dac3f4"},{"different_overlap_bytes":8,"rebuilt_bytes":6000,"rebuilt_sha256":"bf3a6a4da7f21a8e3b980c65eed52414ca1e31eda6ec3ae63375ed431c3ad1bd","section":".rela.text","stock_bytes":6000,"stock_sha256":"8a2f145c40de4c46d89e7cc63d01c5ee786243aa53cae15b5941e207ec8b667e"},{"different_overlap_bytes":4,"rebuilt_bytes":408,"rebuilt_sha256":"fb079249c873aa3a96ed91507e75cbc99e774b10d6b63c4fde541fbcac317cdc","section":".data","stock_bytes":408,"stock_sha256":"5fc4f33ff5f4cd4f093fe496fd2b5f3cde8cf028bb3837f34e748c055bd12998"},{"different_overlap_bytes":31,"rebuilt_bytes":384,"rebuilt_sha256":"5de32c6f0a4205510c757ed7d12d0d35609aafbfa77950c60f1801f6fdc143c8","section":".rela.data","stock_bytes":384,"stock_sha256":"93baff9d7ab058e9e59ef198a4821bbdbd1f9d13e41083c75ccad5450bb40e7d"},{"different_overlap_bytes":6,"rebuilt_bytes":48,"rebuilt_sha256":"6395974c01252892accf22095e660cc97aaee260ea187bd4db1e024dd058eeb2","section":".llvm_addrsig","stock_bytes":48,"stock_sha256":"d8eb77b00a857f4b14e2cffaad9223ee32a46bf8c9e80b50b5a1b7a0b0ef80d1"},{"different_overlap_bytes":3,"rebuilt_bytes":4176,"rebuilt_sha256":"c08220d6a15d05f7890845b0e486c0225889cb948e8682a87cf131a52d0a2325","section":".symtab","stock_bytes":4176,"stock_sha256":"9634c24860f770eb14df34b3fe91a85985d7d7338383c6a8329182be5499c9f8"}],"provenance_gap":"Original exactsourcegeneration/sourcecode scheduling/dataorder/metadata provenance notfound; do not waive"};{"data":"29/32","functions":"22/23","imports":{},"nonGNU_sections":[{"different_overlap_bytes":21,"rebuilt_bytes":6764,"rebuilt_sha256":"479d25f909be04dfd4ea0708fcf0bbddfd7b6a245af40669f0ad2366f8a2e3a1","section":".text","stock_bytes":6764,"stock_sha256":"41d4385ae18ee2970764b640f659caacd368596be8d449d75976c222727eb605"},{"different_overlap_bytes":9,"rebuilt_bytes":11736,"rebuilt_sha256":"d8c9d280dda3097c4a14e9c91e007f268d86ebda600bd30eac2b1f916470aad4","section":".rela.text","stock_bytes":11736,"stock_sha256":"6d0a9e394bc70fbfc330b9bbf67188c6670b390bfc90f431f489d17e19b02c9a"},{"different_overlap_bytes":4,"rebuilt_bytes":408,"rebuilt_sha256":"fb079249c873aa3a96ed91507e75cbc99e774b10d6b63c4fde541fbcac317cdc","section":".data","stock_bytes":408,"stock_sha256":"5fc4f33ff5f4cd4f093fe496fd2b5f3cde8cf028bb3837f34e748c055bd12998"},{"different_overlap_bytes":32,"rebuilt_bytes":408,"rebuilt_sha256":"2ffe29787b954b3ccd8bedd319888f260f4c55bfce02c05c06cd9e8c1aa27b6f","section":".rela.data","stock_bytes":408,"stock_sha256":"a3920acd51f5d45dd13a85097a29a3bc5efe8e7dcf4b13d5fa73f518c1246cd8"},{"different_overlap_bytes":6,"rebuilt_bytes":53,"rebuilt_sha256":"8a00f13f217495a85a28f83634c9b132ccb1d98ab56250d87c8ca195eb354b37","section":".llvm_addrsig","stock_bytes":53,"stock_sha256":"7151d9bfe6d855f38202fa1d072016f69cc204ddf933d1ab254a9e9dc2dcbb9b"},{"different_overlap_bytes":3,"rebuilt_bytes":4272,"rebuilt_sha256":"e31ca09ae224476d5fb721cf443638b48a397b5ea981b7e517860ae95624ed39","section":".symtab","stock_bytes":4272,"stock_sha256":"c69506783bcbf3c4739ee4bfa34534330f5b88a91539d9ba0ad7164ab0615488"}],"provenance_gap":"Original exactsourcegeneration/sourcecode scheduling/dataorder/metadata provenance notfound; do not waive"};{"data":"29/32","functions":"22/23","imports":{},"nonGNU_sections":[{"different_overlap_bytes":21,"rebuilt_bytes":6832,"rebuilt_sha256":"b9169089080d80ed189814d1dc5be652c52a5bb95a02f4b08bc4ee49d89fd3ff","section":".text","stock_bytes":6832,"stock_sha256":"32247cef0fe3faf3efbe12c423fbc831ccd38d9295dfb278d83fa42e5c407117"},{"different_overlap_bytes":9,"rebuilt_bytes":11760,"rebuilt_sha256":"669405a9d58708e68bd9179cfe68962c5e622c8b956fc07ae6b6949f7596b97e","section":".rela.text","stock_bytes":11760,"stock_sha256":"04200045c19f1c209ba4a58472a6ca6ad5ce943204ae35718ddba873ab859363"},{"different_overlap_bytes":4,"rebuilt_bytes":408,"rebuilt_sha256":"fb079249c873aa3a96ed91507e75cbc99e774b10d6b63c4fde541fbcac317cdc","section":".data","stock_bytes":408,"stock_sha256":"5fc4f33ff5f4cd4f093fe496fd2b5f3cde8cf028bb3837f34e748c055bd12998"},{"different_overlap_bytes":32,"rebuilt_bytes":408,"rebuilt_sha256":"b1a19f92f671992c9185e9b6de5bdabe357f6fe370326670f4aeaeb2a378d32d","section":".rela.data","stock_bytes":408,"stock_sha256":"b5061a9ea82ed60a94aca35d18402806bc0d8e96f3f68df483c1e9741b2afbf7"},{"different_overlap_bytes":6,"rebuilt_bytes":53,"rebuilt_sha256":"9f3dafdae48eedbf26f441884ea7659460366b4f376eff01faa7a1042fc79d7f","section":".llvm_addrsig","stock_bytes":53,"stock_sha256":"c18868096a22d3462ec70588cacc22274f5efba7928417730fb77b0c57500531"},{"different_overlap_bytes":3,"rebuilt_bytes":4296,"rebuilt_sha256":"23d81bd4cde4ee72d1f6047c29c0074958a7523d08ed2e00ff533763f3378ca0","section":".symtab","stock_bytes":4296,"stock_sha256":"893358bce79217a22f51455f127f80db3257d963b6b63e79330d03b218edc66d"}],"provenance_gap":"Original exactsourcegeneration/sourcecode scheduling/dataorder/metadata provenance notfound; do not waive"}

## 27. PRESERVE:LN2403-CAMPLIGHT — P3_LOADED_PLATFORM_OR_OPTIONAL
- 1 identities: leds-ln2403.ko
- Classes: G:1
- Source: ../Reverse Engineer - DONE/LN2403-CAMPLIGHT/source
- Provider gaps: NONE
- Proof needed: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing

