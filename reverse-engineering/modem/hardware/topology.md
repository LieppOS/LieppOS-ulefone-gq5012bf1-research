# Modem / AP topology (GQ5012BF1)

Sources: stock DTB (`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`), the live
read-only DT capture (`snapshots/live-stock-adb-20260831-115649/devicetree.tar`, LK-patched),
stock `modem.img` CHECK_HEADER, stock `vendor/build.prop`, and the byte-exact kernel modules.

## Silicon

| item | value | evidence |
|---|---|---|
| modem | integrated MT6878 MD1 (one instance, `MD_SYS1`); no external modem, no MD3/C2K co-processor | `mddriver@d180000` only; `bind_sys_id=1` in CHECK_HEADER; `ccci_md3_sta` unused |
| MD generation | **6299** (`mediatek,md-generation = 0x189b`) → mdee_dumper **v6**, smem layout from LK tags | DT + `ccci_fsm_ee.c` (`md_gen >= 6299`) |
| AP platform id | `mediatek,ap-plat-info = 0x1ade` (6878), same in the dpmaif node | DT |
| firmware RAT set | image type **14 = NLWCG** (NR + LTE-FDD + LTE-TDD + WCDMA + CDMA2000 + GSM), **no TD-SCDMA** | CHECK_HEADER `image_type=14`, `build_time ... *TK_MD*NLWCG_6878`; `ccci_util_md_rat.c` table |
| firmware build | `MOLY.NR17.R1.MP5.RC.MP.V23.9.P1`, platform `MT6878_S00`, 2025/10/22 22:04, TurnKey MD (`TK_MD`), release (`product_ver=2`) | CHECK_HEADER v6 |
| MD memory request | `mem_size = 0x1e000000` (480 MiB) from MD base 0xd0000000; DSP at +0x1d780000, 0x880000 | CHECK_HEADER; matches live `md_mem_usage` reserved regions |
| HIF selection | `mediatek,mdhif-type = 0x06` = CCIF (bit 1) + DPMAIF (bit 2); **CLDMA not used** (stock ships no `ccci_cldma.ko`) | DT, `enum CCCI_HIF` |
| CLDMA capability | `mediatek,cldma-capability = 0x0e` (unused because the HIF mask has no CLDMA bit) | DT |
| MD power | `power-domains = <scpsys 0>`; MD supplies `md-vmodem` 0.80 V, `md-vsram` 0.80 V, `md-vdigrf` 0.70 V (PMIC MT6369 phandles 0xba/0xbb/0xbc) | live DT |
| boot status | `mediatek,boot-status-config = 1`, `offset-epon-md1 = <0x64 0x06>` (EPON flag) | DT |

## Hardware blocks used by the Linux side

| block | DT node | regs | IRQs (GIC SPI) | driver |
|---|---|---|---|---|
| MD1 control | `mddriver@d180000` | 0x0d180000 +0x2000 | 0x1eb (MD WDT), 0xe4/0xe5 (CCIF0 AP/MD) | ccci_md_all (modem_sys1 / md_sys1_platform) |
| CCIF0/1 (control channel) | `ccifdriver@10209000` | 0x10209000, 0x1020a000; SRAM 0x200 | 0xe4, 0xe5 | ccci_ccif |
| CCIF2 (MD<->SCP) | `ccci-scp@1023c000` | 0x1023c000, 0x1023d000 | - | ccci_fsm_scp |
| DPMAIF v3 (data) | `dpmaif@10014000` | 0x10014000 (PD), 0x1022d000, 0x1022c000, 0x1022e000 (AO/MD) | 0xee, 0x103 | ccci_dpmaif |
| MD AUXADC | `md-auxadc` | io-channel 0x313 on the AUXADC provider | - | ccci_auxadc |
| MD power meter | `mdpm` (`mediatek,mt6878-mdpm`) | - | - | mtk_mdpm |
| MD power throttling | `md-power-throttling` (lbat max 3 lv: 0/6/6 dB TX reduce; OC max 2 lv: 0/6) | - | - | mtk_md_power_throttling |
| SIM1 hot-plug | `MD1-SIM1-HOT-PLUG-EINT` EINT0, level-low, debounce 10000 us, src-pin 1 | - | EINT | used by MD via CCCI RPC/EINT forwarding |
| SIM2 hot-plug | `MD1-SIM2-HOT-PLUG-EINT` **empty node (no interrupt)** | - | - | none |

Clocks (infracfg provider 0x40): `infra-dpmaif-clk`, `-blk-clk`, `-rg-mmw-clk`; `infra-ccif{,1,4,5}-{ap,md}`;
`infra-ccif2-{ap,md}` (SCP). DPMAIF votes interconnect `icc-mdspd-bw` and `required-opps` (DVFSRC);
`net-spd-ver = 5`, `hw-reset-ver = 1`.

## LK-populated properties (live DT only, not in the static DTB)

| node/property | value | meaning |
|---|---|---|
| `mddriver/ccci,modem_info_v2` | tag base 0xbfdf0000, size 0x1848, err 0, version 3, **28 tags**, ld_flag 1, ld_md_errno 0 | LK loaded MD1 successfully; tag area = `ccci_tag_mem` |
| `mddriver/md_dbm_addr` | 0x8c01fe00 | DBM block inside AP-MD non-cache smem |
| `mddriver/md_low_power_addr` | 0x8c01fc00 | MD low-power block inside non-cache smem |
| `mddriver/md1_ccb_cap_gear`, `md1_ccb_gear_list` | 1; `1(2,20);2(2,10);3(0,0);4(2,30);11(2,2);12(2,62)` | CCB (cache smem ring) size gears |
| `/md_attr_node` | `md_drdi_rf_set_idx = 0x0f0f0f0f`, `md_product_name_model_id = 0x0f0f0f0f` | DRDI RF-set index handed to MD over RPC (`port_rpc.c get_md_dtsi_val`) |
| `/gpio` (`mediatek,gpio_usage_mapping`) | FDD-BAND-SUPPORT-DETECT 1st/2nd = GPIO **99/100**; SIM1-HOT-PLUG GPIO **46**; SIM1 SCLK/SRST/SIO = **83/84/85**; SIM2 SCLK/SRST/SIO = **86/87/88** | GPIO names the MD resolves via CCCI RPC (`get_md_gpio_info`) |

Board consequences: two physical SIM interfaces, one hot-plug detect (SIM1 only), and two FDD
band-support detect straps that the MD reads at boot. The strap *levels* are runtime-only
(see `../runtime-test-plan.md`).

## Linux-side picture

```
             +----------------------------- MT6878 -----------------------------+
 LK  ------> | MD1 EMI 0xd0000000 (ROM/RAM/DSP)    CCB/smem 0x8a000000 (cache)  |
 (loads md1img, writes ccci tags 0xbfdf0000)      smem 0x8c000000 (non-cache)   |
             |                                                                   |
             |  MD1 <== CCIF0/1 (ctrl, 75 ports) ==> ccci_ccif ─┐                |
             |  MD1 <== DPMAIF v3 (data, 20 ports) ==> ccci_dpmaif ─> ccmni0..20 |
             |  MD1 <== CCIF2 ==> ccci_fsm_scp <== IPI ==> SCP                   |
             |  MD1 <== EMI smem ==> ccci_md_all port_smem / mddp / conninfra /  |
             |                       snd-soc-mtk-common (USIP)                   |
             |  MD1 <== PCM1 (AFE) ==> audio (voice PCM, not CCCI)               |
             +-------------------------------------------------------------------+
```
