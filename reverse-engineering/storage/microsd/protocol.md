# MSDC1 microSD lifecycle (static, from exact `mtk-mmc.ko` source)

All behaviour below is from ALPS `5e415e059253` `drivers/mmc/host/mtk-mmc.c`, which is byte-exact to stock, plus the GKI MMC core. No card was inserted or removed for this work.

| stage | behaviour |
|---|---|
| probe | `mmc_of_parse` reads bus width, caps, UHS modes, `cd-gpios`, `max-frequency` and supplies. `ocr_avail = 0x30000` from `ocr-voltage`. The mt6878 compatible data sets: 12-bit clock divider, async FIFO, data tune, busy check, stop-clock (3/8), enhanced RX, 64 GiB DMA (`support_64g`), new TX v2 / RX v1, `set_crypto_enable_in_sw`, `need_power_voter`, `sw_infra_check`. GPD/BD DMA descriptors come from `dma_alloc_coherent`; `max_seg_size` is the BDMA buffer length (16- or 24-bit), `max_blk_count = max_req_size/512`, CMD23 is enabled |
| card detect | GPIO CD (`cd-gpios` GPIO14, active-high on this board) through the GKI `mmc_gpiod_request_cd` IRQ, then `mmc_detect_change`. `cd-debounce-delay-ms = 0`. `msdc_get_cd` returns `mmc_gpio_get_cd()`; the internal `MSDC_PS_CDSTS` path is only used when no GPIO is given. A "bad card" blocker (`block_bad_card`) forces "removed" and schedules a rescan 200 ms later |
| power | `vmmc` (MT6369 VMCH, card VDD) and `vqmmc` (MT6369 VMC, signalling) through the GKI regulator helpers |
| voltage switch | `msdc_ops_switch_volt`: only 3.3 V / 1.8 V are accepted. `mmc_regulator_set_vqmmc`, then pinctrl `state_uhs` (1.8 V) or `default` (3.3 V). The two pin states are identical on this board |
| bus modes | DS/HS (`cap-sd-highspeed`), UHS-I SDR12/25/50/104 and DDR50, 4-bit, up to 200 MHz |
| tuning | `msdc_execute_tuning` (CMD19 for SDR104/SDR50) with MSDC pad/data delay scan (`pad_tune_reg = MSDC_PAD_TUNE0`, `data_tune`). `hs400_tune` is false for mt6878 (HS400 is eMMC-only anyway). No `MMC_AUTOK` module ships |
| error recovery | `msdc_cmd_done`/`msdc_data_xfer_done` handle CRC/timeout interrupts. `msdc_reset_hw` on errors; request timeout work; bad-SD detector (`power_cycle_cnt`) leads to `block_bad_card` |
| crypto | `MMC_CRYPTO` (GKI) with SW-enabled crypto on mt6878 compat; MSDC1 has no crypto clock (see `crypto/inline-crypto.md`) |
| runtime PM | autosuspend **50 ms** (`MTK_MMC_AUTOSUSPEND_DELAY`). `msdc_runtime_suspend` gates clocks and releases the DVFSRC vcore vote; `msdc_runtime_resume` restores them |
| system PM | `msdc_suspend` → (`cqhci_suspend` if CQE) → `pm_runtime_force_suspend`; `msdc_resume` → `pm_runtime_force_resume` |
| block / tracing | GKI `mmc_block` (`CONFIG_MMC_BLOCK_MINORS=8`); I/O tracing via `blocktag` (`mmc_mtk_biolog_*`); command history via `mtk-mmc-dbg` |
| user space | vold `voldmanaged=sdcard1:auto`, `encryptable=userdata` (adoptable storage), path `/devices/platform/soc/11240000.mmc*` |

Filesystems available for SD (GKI built-in): vfat/msdos, exfat, ext4, f2fs. NTFS is **not** built.
