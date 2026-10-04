# UFS power state machine (GQ5012BF1)

Labels: **[UP]** = upstream GKI `ufshcd` (ACK `6b18f0b574ab`), **[MTK]** = `ufs-mediatek-mod` vops (ALPS `5e415e059253`, byte-exact), **[BOARD]** = DT/device value on this phone.

## Probe / link startup

1. **[MTK]** `ufs_mtk_init`:
   - parse host caps ([`dt-contract.md`](dt-contract.md)) and init the resets
   - set caps: RPM_AUTOSUSPEND, CLK_GATING, CRYPTO, WB_EN; CLK_SCALING is cleared on this board
   - `ufs_mtk_init_clocks`, `init_sysfs`
   - MTCMOS on via SiP (`rtff-mtcmos` [BOARD])
   - `ufs_mtk_setup_clocks(on)`, `get_hw_ip_version`
   - add a `cpu_latency_qos` request
   - create the delayed error-handler workqueue `ufs_mtk_eh_wq`
2. **[MTK]** `hce_enable_notify` / `ufs_mtk_host_reset`: pulse `hci_rst`, `crypto_rst` and `unipro_rst` (100–110 µs). After the host is enabled, crypto is enabled through SiP `UFS_MTK_SIP_CRYPTO_CTRL`.
3. **[MTK]** `ufs_mtk_device_reset`:
   - SiP `UFS_MTK_SIP_DEVICE_RESET`(0)
   - `ufshcd_hba_stop`, wait 10–15 µs
   - SiP `DEVICE_RESET`(1), wait 10–15 ms
4. **[MTK]** `link_startup_notify` PRE/POST: UniPro/M-PHY vendor attributes (`VS_*`). The `pa_tactivate`/`pa_h8time` values printed by LK are host 5 / peer 1 ([BOARD]).
5. **[UP]** `ufshcd_link_startup` → NOP OUT → read descriptors.
6. **[MTK]** `ufs_mtk_fixup_dev_quirks` / `ufs_mtk_fix_ahit`: Micron (`0x12C`) → auto-hibern8 idle timer **2 ms** ([BOARD]).
7. **[MTK]** `pwr_change_notify(PRE)`:
   - host capability HS-G5, 2 lanes, Rate B
   - `ufshcd_get_pwr_dev_param` picks min(host, device)
   - if the device reports SLOW_MODE, PWM mode is used instead
   - `pmc-via-fastauto` is absent, so there is no intermediate FASTAUTO step ([BOARD])
8. **[UP]** WriteBooster probe: `UFSHCD_CAP_WB_EN` plus device ext-feature bit 8 plus an LU-dedicated buffer on LU2 means WB is enabled ([`feature-map.md`](feature-map.md)).

## Active ↔ clock-gated ↔ hibern8

| step | layer | behaviour |
|---|---|---|
| idle → auto-hibern8 | UP + MTK | HW enters H8 after 2 ms idle (AHIT programmed by `ufs_mtk_fix_ahit`) |
| clock gating | UP | `UFSHCD_CAP_CLK_GATING`; `HIBERN8_WITH_CLK_GATING` **not** set (AH8 is in use) |
| `setup_clocks(off, PRE)` | MTK | wait for `VS_LINK_HIBERN8` (≤15 ms) when AH8 is on or the link is in H8. Then: drop QoS, crypto boost (no-op on this board), **refclk release** (`ufs_mtk_setup_ref_clk(off)`: write `REFCLK_RELEASE` to `REG_UFS_REFCLK_CTRL`, poll ACK==REQ for ≤ `REFCLK_REQ_TIMEOUT_US` 3000 µs, ATF notified through SiP `REF_CLK_NOTIFICATION`; on timeout it assumes the clock is off), `phy_power_off` |
| `setup_clocks(on, POST)` | MTK | `phy_power_on`, refclk request (wait `REFCLK_DEFAULT_WAIT_US` 32 µs), QoS = 0 latency (`ufs-qos` [BOARD]) |

## Runtime / system suspend

| phase | behaviour |
|---|---|
| levels | **[UP]** default `rpm_lvl`/`spm_lvl` (not overridden by MTK). RPM autosuspend delay **500 ms** [MTK] |
| `suspend(PRE)` | [MTK] disable auto-hibern8 (`ufs_mtk_auto_hibern8_disable`); `-EAGAIN` if MTK EH in progress |
| `suspend(POST)` | [MTK] link in H8: `ufs_mtk_link_set_lpm` (clear `REG_UFS_XOUFS_CTRL` bit 8, UniPro LPM). Link not active: M-PHY power off. Link off: device-reset low (SiP). SRAM power off (SiP `SRAM_PWR_CTRL`). Clock scaling is off on this board, so there is no scale-down |
| device rails | [MTK] `ufs_mtk_dev_vreg_set_lpm(true)`: VCCQ LPM is **bypassed** ([BOARD] `bypass-vccqx-lpm`); device power via SiP `DEVICE_PWR_CTRL(wSpecVersion)` |
| MTCMOS | [MTK] RTFF MTCMOS off/on via SiP `MTCMOS_CTRL` in the `ufs_mtk_system_*`/`ufs_mtk_runtime_*` PM wrappers and at init ([BOARD] `rtff-mtcmos`) |
| `resume` | [MTK] vreg normal, SRAM on, M-PHY on, link HPM (`ufs_mtk_link_set_hpm`). On failure: `ufshcd_link_recovery`, always returns 0 ("cannot return fail, else IO hang") |

## Error recovery

- **[UP]** `ufshcd_err_handler` (host/device reset and link recovery).
- **[MTK]** The `ufs_mtk_event_notify` and `dbg_register_dump` vops feed `ufs-mediatek-dbg`.
  - `ufs_mtk_eh_err_cnt` → AEE warning "Error Dump %d".
  - `ufs_mtk_eh_abort` → AEE "ufshcd_abort at tag %d".
  - `ufs_mtk_eh_unipro_set_lpm` reports failures.
  - The AEE hooks live in `ufs-mediatek-dbg`.
- **[MTK]** `delay_eh_work` re-runs the error handler from `ufs_mtk_eh_wq`.
- **[MTK]** With `mphy-debug` [BOARD], the M-PHY register dump runs on error.
- **[MTK]** Command history and `/proc/ufs_debug` (`ufs-mediatek-dbg`); the I/O trace goes through `blocktag`.

## Not present on this board

- clock scaling (devfreq): no max/min source clocks in DT
- MCQ: `ufs-disable-mcq`
- VA09 rail control
- crypto DVFS boost
- low-battery or overcurrent power throttling: the headers are included only under `CONFIG_MTK_*_POWER_THROTTLING`, and no callback is registered in this object set
