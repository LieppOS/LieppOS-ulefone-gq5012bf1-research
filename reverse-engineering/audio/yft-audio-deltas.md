# GQ5012BF1 / YFT audio deltas

| # | area | donor/upstream | GQ5012BF1 behavior | exact evidence / reconstruction | confidence |
|---:|---|---|---|---|---|
| 1 | ACCDET/FM | MT6369 donor has no board FM antenna GPIO | global GPIO parsed from `gpio-accdet-fm-switch`; requested/output-low at probe; set 1 on plug-in and 0 on unplug | stock disassembly, DT GPIO 195, reconstructed `mt6369-accdet.c`; module 49/49 + 24/24 exact | PROVEN |
| 2 | ACCDET EINT analog | donor follows generic external/internal resistor config | EINT0 path additionally sets `RG_EINT0HIRENB` (500 kΩ internal selection) | stock disassembly at register 0x251e; reconstructed exact | PROVEN |
| 3 | Nothing audio switch | Nothing donor config can export HL5280 callback | stock has no HL5280 wrapper/export/module/node | stock symbols/modules/DT and exact rebuild with option off | PROVEN |
| 4 | speaker dispatcher | ALPS table lacks AW883XX board binding | type 5 calls `aw883xx_i2c_probe/remove`; imports force dependency on `aw883xx_driver` | stock relocations/import CRCs; reconstructed `mtk-sp-spk-amp` 16/16 + 11/11 exact | PROVEN |
| 5 | machine speaker enum | donor lists five speaker choices | stock list adds `MTK_SPK_AW_AW883XX` at index 5 and AW882XX at 6 | exact `.rodata` relocation/string order; machine 15/15 + 322/322 exact | PROVEN |
| 6 | speaker I2S | generic platform selectable | DT chooses enum 25=I2S_OUT4 and 24=I2S_IN4; task 8/ref task 4 | DT + exact enum/source | PROVEN |
| 7 | fitted SmartPA | generic Awinic driver supports PIDs 2049/2066/2183 | one channel-0 PID 2049 = AW88394 at i2c-6/0x34 | ACF identity, DT, stock module, prior exact reconstruction | PROVEN |
| 8 | route policy | generic HAL supports internal/external/two-in-one speakers | product selects Awinic SmartPA, one speaker, `SPK_PATH_NO_ANA=yes`, `RCV_PATH_INT=yes` | `AudioParamOptions_vext.xml`; mixer routes | PROVEN CONFIG |
| 9 | microphone project | generic MT6369 supports AMIC/DMIC/ThreeMic | two built-in AMICs on AIN0/AIN2, MIC_BIAS_0 1.9 V; headset mic AIN1 | existing microphone RE + now-exact codec/AFE sources | PROVEN CONFIG |
| 10 | MT6369 PMIC IRQ | later ALPS header gives `VPA_OC=6` | stock resource table uses `VPA_OC=1` | one-line header delta; `mtk-spmi-pmic` 10/10 + 39/39 exact | PROVEN |
| 11 | build configuration | Nothing/engineering config enables RT5512, HL5280 and SCP debug | all three off in stock user build | absence of symbols/strings/modules plus exact module parity | PROVEN |
| 12 | speech features | platform supports handset/handsfree/VoIP DMNR variants | normal handset two-mic DMNR on; hands-free and VoIP DMNR options off | product audio options and HAL parameter categories | PROVEN CONFIG |
| 13 | VOW | platform supports GVA/Amazon/dual mic | VOW enabled, single main AMIC, max two PDK; GVA/Amazon/dual-mic off | product options, mixer XML, exact VOW modules | PROVEN CONFIG |
| 14 | playback format | platform supports multiple PCM widths | product requests 24-bit-only internal playback | product options + policy/HAL controls | PROVEN CONFIG |

Commits in the exact kernel workspace:

- `53e57119` — ACCDET/YFT FM switch and EINT delta;
- `27f8383` — MTK ALPS audio baseline and user-config enum;
- `85676ca` — AW883XX dispatcher/machine integration;
- `9c4bdbc` — exact common AFE source revision;
- `53995d5` — MT6369 VPA OC IRQ index.
