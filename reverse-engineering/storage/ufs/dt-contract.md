# UFS DT contract → driver behaviour (GQ5012BF1)

The live DT node `soc/ufshci@112b0000` is **identical** to the donor `mt6878.dts` node (ALPS `5e415e059253`). It has the same 13 clocks, 3 resets, two supplies and five vendor booleans, so the board inherits the MTK reference UFS configuration. The table maps every property parsed by `ufs_mtk_init_host_caps()` and the related code to its effect.

| DT property | present | driver effect (ALPS `ufs-mediatek.c`) |
|---|---|---|
| `mediatek,ufs-qos` | **yes** | `qos_enabled = qos_allowed = true`. While UFS clocks are on, `cpu_latency_qos` is set to 0 (`ufs_mtk_pm_qos`); it is released when clocks are gated |
| `mediatek,ufs-mphy-debug` | **yes** | `UFS_MTK_CAP_MPHY_DUMP` → `ufs_mtk_dbg_phy_enable()`. M-PHY registers are dumped on errors and hibern8 notify (`ufs-mediatek-dbg`) |
| `mediatek,ufs-disable-mcq` | **yes** | `UFS_MTK_CAP_DISABLE_MCQ`: legacy single doorbell (32 tags). MCQ IRQ affinity code is unused |
| `mediatek,ufs-rtff-mtcmos` | **yes** | `UFS_MTK_CAP_RTFF_MTCMOS`. Suspend/resume powers the UFS MTCMOS through SiP `UFS_MTK_SIP_MTCMOS_CTRL`, with retention flip-flops |
| `mediatek,ufs-bypass-vccqx-lpm` | **yes** | `UFS_MTK_CAP_BYPASS_VCCQX_LPM`: VCCQ (`vufs12`) is **not** put in LPM during suspend |
| `mediatek,ufs-boost-crypt` | no | no crypto-engine DVFS boost (`ufs_mtk_boost_crypt` is a no-op) |
| `mediatek,ufs-support-va09` | no | no VA09 SiP power control |
| `mediatek,ufs-disable-ah8` | no | auto-hibern8 **enabled**; `UFSHCD_CAP_HIBERN8_WITH_CLK_GATING` not set |
| `mediatek,ufs-broken-vcc` | no | VCC managed normally (`vemc`) |
| `mediatek,ufs-pmc-via-fastauto` | no | power-mode change goes directly to HS (no FASTAUTO step) |
| `mediatek,ufs-tx-skew-fix` | no | — |
| `mediatek,ufs-broken-rtc` | no | `UFSHCD_QUIRK_MCQ_BROKEN_RTC` not set (irrelevant, MCQ is off) |
| `mediatek,ufs-vcc-by-num` / `-by-ver` | no | single VCC (`vcc-supply`) |
| `ufs_sel_max_src` / `ufs_sel_min_src` clocks | no | `ufs_mtk_is_clk_scale_ready()` is false, so `UFSHCD_CAP_CLK_SCALING` is **cleared** (no devfreq clock scaling) |
| `freq-table-hz` (all 0) | yes | the core does no frequency scaling |
| `clkscale` / `clk-scale-up-vcore-min` | no | no vcore floor for scale-up |
| `resets` `unipro_rst`/`crypto_rst`/`hci_rst` | yes | `ufs_mtk_init_reset()`. `ufs_mtk_host_reset()` asserts hci, crypto and unipro (plus M-PHY if present), waits 100–110 µs, then deasserts. Crypto is then re-enabled through SiP `UFS_MTK_SIP_CRYPTO_CTRL` |
| `phys = <&ufsphy>` | yes | `phy-mtk-ufs` power on/off from `setup_clocks` |
| `bootmode = <&chosen>` | yes | reads `/chosen` `atag,boot`; `boottype == BOOTDEV_UFS` sets `host->boot_device`. The `atag,ufs` blob (present in live `/chosen`) is kept in `host->atag` (RPMB key states; only consumed by the iSE variant, which is not shipped) |
| `vcc-supply` (`mt6363_vemc`) / `vccq-supply` (`mt6363_vufs12`) | yes | device rails. In suspend, `ufs_mtk_vsx_set_lpm` asks ATF (SiP `UFS_MTK_SIP_DEVICE_PWR_CTRL`, with `wSpecVersion`) to drop device power. `ufs_mtk_vccqx_set_lpm` returns early because of `bypass-vccqx-lpm` |

## Capabilities set unconditionally by `ufs_mtk_init()`

| item | value |
|---|---|
| `UFSHCD_CAP_RPM_AUTOSUSPEND` | yes; `rpm_autosuspend_delay` = `MTK_RPM_AUTOSUSPEND_DELAY_MS` = **500 ms** |
| `UFSHCD_CAP_CLK_GATING` | yes |
| `UFSHCD_CAP_CRYPTO` | yes, provided SiP `UFS_MTK_SIP_CRYPTO_CTRL` succeeds (else cleared) |
| `UFSHCD_CAP_WB_EN` | yes |
| `UFSHCD_CAP_CLK_SCALING` | set, then **cleared** (see above) |
| quirks | `UFSHCI_QUIRK_SKIP_MANUAL_WB_FLUSH_CTRL`, `UFSHCD_QUIRK_MCQ_BROKEN_INTR` |
| `wb_flush_threshold` | `UFS_WB_BUF_REMAIN_PERCENT(80)` |
| auto-hibern8 timer | vendor table, `wManufacturerID` `0x12C` (Micron) → **2 ms** (Samsung 3.5 ms, default 1 ms) |
| host gear capability | HS-G5 offered; device-limited (UFS 3.1 → G4 at most); rate B, 2 lanes (GKI defaults) |
