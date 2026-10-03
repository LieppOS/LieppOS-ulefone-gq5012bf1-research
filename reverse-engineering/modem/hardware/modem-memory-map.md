# Modem memory map (GQ5012BF1, from the live LK-patched DT)

Primary evidence: `/sys/firmware/devicetree/base/reserved-memory/*` and `mddriver@d180000` in the
read-only capture `live-stock-adb-20260831-115649/devicetree.tar`. Cross-checked against the stock
`modem.img` CHECK_HEADER and the exact `ccci_util_lib` source (`ccci_util_md_mem.c`,
`ccci_util_lib_fo.c`). Every address below comes from GQ5012BF1 evidence; none is taken from
generic MTK documentation.

## Reserved regions

| region (LK mblock name) | base | size | attr | owner / consumer |
|---|---|---|---|---|
| `mblock-34-md_mem_usage` | **0xd0000000** | 0x02f10000 (47.06 MiB) | no-map | MD1 ROM + RAM image. md1rom is 49,301,584 B = 0x2f04850, which fits the region |
| `mblock-36-md_mem_usage` | 0xd3000000 | 0x00250000 (2.31 MiB) | no-map | MD1 runtime region (inside the 480 MiB MD window) |
| `mblock-37-md_mem_usage` | 0xd4000000 | 0x06e00000 (110 MiB) | no-map | MD1 RAM / working memory |
| `mblock-38-md_mem_usage` | **0xed780000** | 0x00880000 (8.5 MiB) | no-map | MD DSP. Equals CHECK_HEADER `dsp_img_offset 0x1d780000` + MD base, size `0x880000` |
| `mblock-35-ap_md_c_smem` | **0x8a000000** | 0x01960000 (25.4 MiB) | no-map | AP<->MD **cacheable** shared memory: CCB rings, MD_CONSYS, NVRAM cache, USIP, UDC desc table, MD post-dump |
| `mblock-26-ap_md_nc_smem` | **0x8c000000** | 0x00130000 (1.19 MiB) | no-map | AP<->MD **non-cacheable** shared memory: exception/runtime data, CCISM (SCP/MCU), RAW_AUDIO, NETD, USB (MDDP), DBM, low-power, DFD, AMMS, DRDI |
| `mblock-33-ccci_tag_mem` | **0xbfdf0000** | 0x00010000 | no-map | LK → kernel CCCI tag area. `ccci,modem_info_v2` says base 0xbfdf0000, 0x1848 B used, **28 tags**, version 3, no load error |
| `ccci-dpmaif-cache-memory` | dynamic (alloc-range 0x40000000–0x130000000) | 0x00190000 | reusable | DPMAIF cacheable ring/BAT pool (`DPMAIF_CAP_USE_RESV_MEM`) |
| `ccci-dpmaif-nocache-memory` | dynamic | 0x00050000 | no-map | DPMAIF non-cacheable descriptors |
| `mblock-41/43 consys_*` | 0x87e00000 / 0x89f00000 | 0xd00000 / 0x20000 | no-map | connectivity, not modem. Listed so the neighbourhood is clear |

MD window (MD view 0 = AP 0xd0000000): `mem_size 0x1e000000` → AP 0xd0000000–0xedffffff. Only
the four `md_mem_usage` blocks are reserved from Linux. The remaining parts of the window are
handed back by LK (`retrieveN` / `free_in_kernel` logic in `ccci_util_lib_fo.c`). The exact
retrieved ranges are LK-tag runtime data and are not in the capture.

## Points inside the non-cache smem (LK DT properties)

| property | address | offset in nc smem |
|---|---|---|
| `md_low_power_addr` | 0x8c01fc00 | +0x1fc00 |
| `md_dbm_addr` | 0x8c01fe00 | +0x1fe00 |

## Shared-memory users (SMEM_USER ids)

Gen 6299 reads the per-user layout from LK tags (`get_md_smem_layout_tbl_from_lk_tag`). The
`gen6297_*` tables in `ccci_util_md_mem.c` are the compiled-in fallback and give the
user list and default sizes. They are byte-identical in our rebuild and the stock module.

| smem | user id | default size (fallback table) | Linux consumer |
|---|---|---|---|
| non-cache | RAW_DFD, RAW_UDC_DATA, MD_WIFI_PROXY, SECURITY_SMEM, RAW_AMMS_POS | LK-sized | ccci_md_all (UDC), rild WPFA (`ccci_wifi_proxy`) |
| non-cache | RAW_MDCCCI_DBG 2 KiB, RAW_MDSS_DBG 14 KiB, RAW_RESERVED 42 KiB, RAW_RUNTIME_DATA 4 KiB, RAW_FORCE_ASSERT 1 KiB | as listed | ccci_md_all FSM/EE |
| non-cache | LOW_POWER 512 B, RAW_DBM 512 B | | `ccci_raw_dbm`, `/proc/ccci_lp_mem` |
| non-cache | CCISM_SCP 32 KiB | | ccci_fsm_scp |
| non-cache | RAW_CCB_CTRL 4 KiB | | `/dev/ccci_ccb_ctrl` |
| non-cache | RAW_NETD 8 KiB | | `/dev/ccci_raw_netd`, mddp usage (`mddp_usage.c`) |
| non-cache | RAW_USB 4 KiB | | `/dev/ccci_raw_usb`, mddp IPC buffer (`mddp_ipc.c`) |
| non-cache | RAW_AUDIO 52 KiB | | `/dev/ccci_raw_audio` → audio HAL speech |
| non-cache | CCISM_MCU (720+1) KiB, CCISM_MCU_EXP (120+1) KiB | | MCU/SSPM shared |
| non-cache | RESERVED 18 KiB, MD_DRDI (BANK4_DRDI_SMEM_SIZE) | | MD DRDI data |
| cache | RAW_MD_CONSYS | LK-sized | **conninfra** (`mt6878_emi.c get_smem_phy_start_addr(MD_SYS1, SMEM_USER_RAW_MD_CONSYS)`) |
| cache | MD_NVRAM_CACHE | LK-sized | MD NVRAM cache |
| cache | CCB_START | LK-sized (gear list above) | `/dev/ccci_ccb_dhl`, `ccci_ccb_md_monitor`, `ccci_ccb_meta` |
| cache | MD_POST_DUMP (id 46) | LK-sized | `/dev/ccci_md_post_dump` |
| cache | RAW_UDC_DESCTAB | LK-sized | UDC |
| cache | RAW_USIP | LK-sized | **snd-soc-mtk-common** `mtk-usip.c` → `/dev/usip` (speech enhancement EMI) |

`SMEM_USER_MD_POST_DUMP = 46` was added to `mtk_ccci_common.h` in the stock revision. The
newer header is required for `ccci_util_lib` and `ccci_md_all` exactness. It is a plain enum
addition, and every other KDM consumer we re-checked (audio `snd-soc-mtk-common`, mddp,
md_cooling, md power throttling) stays byte-exact.

## Not captured (runtime only)

* The 28 LK tag payloads (exact per-user offsets/sizes in both smem regions, retrieved MD
  ranges, MD boot errno details). These are LK-written RAM contents. A read-only dump is in
  `../runtime-test-plan.md` (`/proc/ccci_dump`, `/sys/kernel/ccci/lk_md`).
