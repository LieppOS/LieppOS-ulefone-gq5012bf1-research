# Proposed PLATFORM-BATCH-05 —29 display/camera peripheral identities

**Proposal only: not executed/frozen.** Current245certified/213remaining(A244 B1 C14 D91 G108).29 actualuncertified identities:2D/27G. Reconcile this table against then-current458 audit and471stock occurrences;freeze/commit before implementation.

## Coherent scope and prerequisites

Closed clock/PINCTRL/regulator/PMIC/SPMI/IOMMU/power/thermal foundations support display/backlight/SPI endpoints and camera actuators/calibration/power/illumination. Most are historical whole reconstructions: recover source before rewriting. Preserve established owners and a small number of subsystem recipes. This is not a whole DRM/ISP or firmware reconstruction.

Do not silently include mediatek-drm,mtk_disp_sec,existingCMDQ/ADC or Batch04C. Their dependencies may remain source-only witnesses with explicit nonclosure; matching APIs do not certify whole providers. RT5133 read/probe failure remains a board finding, not F exclusion; preserving a driver does not prove the IC is successfully bound. MET backlight/camera EEPROM use separate source repositories:identify their authentic public/history pins rather than forcingALPS5e for all.

Source availability was checked offline: actual immutableALPS Kbuild where applicable and actual preserved historical wholeC/H/Makefiles withSHA256. DW9781C historical source directory is empty; only its immutable public candidate is available there, so recover the historical OEM source/patches before acceptance. See evidence/next-source-availability.json and NEXT-BATCH-PROPOSAL.tsv for full IDs,owners,stock hashes/occurrences,configs,recipes/dependencies. Historical source is a candidate until freshwholeELF acceptance.

## DISPLAY-LIGHTING-SPI

| Module | Class | Canonical owner | Exact identity |
|---|---|---|---|
| `leds-mtk-disp.ko` | G | MTK-PWM | `leds-mtk-disp.ko@7ea1f35740a6c2bebf67a1ec3426b491a16875203e4b6c293bc57a5e57a79653` |
| `leds-mtk.ko` | G | MTK-PWM | `leds-mtk.ko@d4e6e06b70a08f59e52e33bdfb2824815b97750b37ea0237483d509ab17ac49a` |
| `mtk-pwm.ko` | G | MTK-PWM | `mtk-pwm.ko@06c68f5df7b7b2b8adb3957ec8fdfac0b551c209fbdacb52cd147f2ac056fa8b` |
| `pwm-mtk-disp.ko` | G | MTK-PWM | `pwm-mtk-disp.ko@97aa2794589560a64088d21f13d9edafe9302b4ebf11607d4784a4413475409a` |
| `rt4831a_drv.ko` | G | MTK-PWM | `rt4831a_drv.ko@d9996b3feaa090ee2dff49f7f9a8f1d6edc1b4732ca93a2a8636a753f95dfb59` |
| `met_backlight_api.ko` | G | BACKLIGHT-DISPLAY-GLUE | `met_backlight_api.ko@88e928eb42cb086ccbdd571a4e8c810289a7806b4a0ac83973641254c55e531a` |
| `mtk_disp_notify.ko` | G | MTK-DISP-NOTIFY | `mtk_disp_notify.ko@28fb6a324e432547b98f618d7981a4940dc3e5bf9b319b0181b339d3e8bd062b` |
| `panel-ky-vtdr6115-dphy-cmd.ko` | G | VTDR6115-DISPLAY | `panel-ky-vtdr6115-dphy-cmd.ko@1e5778f3612378dd6fc3ba96ca461d8ba0661fc6617290a7c64245ede3f3af07` |
| `spi_tiny_co5300_lcd.ko` | G | CO5300-REAR-DISPLAY | `spi_tiny_co5300_lcd.ko@39eecad8254c2fc69f9c8d52902b443b3adc64c79c4c6a529af19b4b1f2a9742` |
| `spi-mt65xx.ko` | G | SPI-MT65XX | `spi-mt65xx.ko@5463e06c205623e4b1b713416836e3b5235dc246c7d536595f6613ba3492d712` |
| `leds-rgb-aw2013.ko` | G | AW2013-RGB-LED | `leds-rgb-aw2013.ko@97c86e3b3dd038c4fc90b73315aac966087a852d604f103fc166076bd28f7549` |

## CAMERA-ACTUATOR-EEPROM-POWER

| Module | Class | Canonical owner | Exact identity |
|---|---|---|---|
| `camera_af_media.ko` | G | CAMERA-VCMS | `camera_af_media.ko@a87b6538b92c13af5c400f7df41b6f47d1cd2a52fbeff199b13e8e562b0d51a6` |
| `main_vcm.ko` | G | CAMERA-VCMS | `main_vcm.ko@002ad3ef1927928c87cbddd2b27e926e59813ca2f62b5e3289655e0a6216a5e1` |
| `main2_vcm.ko` | G | CAMERA-VCMS | `main2_vcm.ko@7db2e9248c260f79b6dd37611c53907cac0e0e04b0f9550647c402cc6273d787` |
| `main3_vcm.ko` | G | CAMERA-VCMS | `main3_vcm.ko@6dc7458c47be8fecf6753bd5575ec1a90d4f5388d44165554588788e23751306` |
| `main4_vcm.ko` | G | CAMERA-VCMS | `main4_vcm.ko@9b36b90af67d0970ec9bf01a301ff1c27dd15c2e941704fe5f9c6f9b006f9ab9` |
| `sub_vcm.ko` | G | CAMERA-VCMS | `sub_vcm.ko@77aef22b818dbc19f2a06fbab9ccbeed901908dcc4e0eb75e3c2dbbe22f32c41` |
| `camera_eeprom_v4l2.ko` | G | CAMERA-EEPROMS | `camera_eeprom_v4l2.ko@0423196dc09885535bf6673e86cb8998653b164f28fe743a0f0da258118ee10a` |
| `custom-ldo-wl2868.ko` | G | WL2868-CAMERA-LDO | `custom-ldo-wl2868.ko@dab36e3d2593546d72b4fa7257b4a303c65c0ad4c507bbd1fbb50e1578111d48` |
| `custom-ldo.ko` | G | WL2868-CAMERA-LDO | `custom-ldo.ko@9d3d4a3786dd71af4fdee07e4bc332526816b62143925f4e5923f286c9d91556` |
| `dw9781c.ko` | G | DW9781C-OIS | `dw9781c.ko@5421b83cc767c5d57ee1db328189413d0e6f53eb6d272e418b52d83d76e7a61b` |
| `rt5133-regulator.ko` | G | RT5133-POWER-IC | `rt5133-regulator.ko@467dcf89b5d807c2735c22c3023edc1137d135302f14d236fc841d110b07bc03` |
| `extdev_io_class.ko` | G | RT5133-POWER-IC | `extdev_io_class.ko@60f520e3b7f2a0dda95b8844ead106430ec63ebf350b591a0da5db01fce3d2b4` |

## FLASH-CAMERA-ILLUMINATION

| Module | Class | Canonical owner | Exact identity |
|---|---|---|---|
| `flashlight.ko` | D | COVERED-GENERIC | `flashlight.ko@87b18cde1f47c857689602c3232f14874e84fb65b445e4308e80f04728bdefae` |
| `mtk-composite.ko` | D | MTU3-SSUSB | `mtk-composite.ko@1e41153e8cdcd3f7bf1a7789ea89849c0e09459439493af7910d756bdbc0cab0` |
| `aw36515.ko` | G | AW36515-FLASH | `aw36515.ko@85e5a860bc0ebae9c26e401ae333928ab8da9569b3892040da4f858cf6f643e8` |
| `aw36518.ko` | G | MTK-PWM | `aw36518.ko@7dcf64a7d25c657d1a0795cc89ad519c954561c6c757949c247d623f16976247` |
| `aw36518_v2.ko` | G | MTK-PWM | `aw36518_v2.ko@c7faa3ba4d8f14e4d24087f1dbd9f7c7c492e384214d571def17fb087de1458e` |
| `leds-ln2403.ko` | G | LN2403-CAMPLIGHT | `leds-ln2403.ko@211bda35ee3476c107d7e495a0463c27bbef114a031a6b81b8bb718bbe54ee94` |

## Acceptance, safety and continuation

Recover all fullcomposite implementations/publiclineage/OEMpatches/generatedheader needs;naturalCRC/export/license/KCFI witnesses;commit source;freshclone/hide originals/B1B2;raw/stripped/intermediate/source/config/symvers equality;separate completecode/data/ABI/relocation/ELF/BTF/metadata/signature acceptance, realELFmutations and recoverybundles. Retain honest C/D/G whereunclosed. Source availability is not same-session completion guarantee.

Record actual stock DT/resources/regulators/IRQs/clock/source APIs and savedbinding/load evidence. Never infer calibration,illumination limits,I2C transactions,physical camera movement or panel modes from source alone. Strict offline,no phone/reset/flash/register/GPIO/firmware/voltage/current/experimental loading or push.

If all29meetA/B:274certified/184remaining of458 (projection only). Generatedqueuehead timer-mediatek remains unchanged; this coherent29 recommendation is an explicit batch suggestion,not silent queue substitution or authorization to execute. ExistingCMDQ/nativeADC/fiveBatch04C remain separate exactblockers.
