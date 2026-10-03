# CCCI (AP <-> MD control plane) — kernel scope DONE

| module | functions | data | ABI | whole file |
|---|---:|---:|---|---|
| ccci_util_lib | 126/126 | 133/133 | exact (imports 73/73, exports 44/44, modversions 74/74, export CRCs 44/44, 21/21 sections) | identical except the 20-byte GNU build-id |
| ccci_md_all | 370/370 | 163/163 | exact (imports 197/197, exports 40/40, modversions 198/198, export CRCs 40/40, 22/22 sections) | identical except build-id |
| ccci_auxadc | 6/6 | 9/9 | exact | identical except build-id |
| ccci_ccif | 43/43 | 21/21 | exact | identical except build-id |
| ccci_fsm_scp | 17/17 | 20/20 | exact | identical except build-id |

The build-id differs only because the stock id was hashed before `--strip-debug`, over DWARF
that contains build-host paths. Every other byte matches, including relocations, `.modinfo`,
`__versions`, KCFI type ids inside the code, and `.llvm_addrsig`. Reports:
`parity/summary.tsv` and `../binary-analysis/per-module/`.

## Exact source

* **MediaTek ALPS commit `fae67a9257dc`** ("[ALPS09525334] ccci: change the settle time judgment
  to 40ms", 2024-12-11) in the NothingOSS `android_kernel_device_modules_6.1_nothing_mt6878`
  history:
  * `drivers/misc/mediatek/eccci` tree `ca75801a968e…`
  * `drivers/misc/mediatek/ccci_util` tree `bbdb303389cc…`
  * `include/mt-plat/mtk_ccci_common.h` blob `415e7e6c3df6…`
* The 6df320423600 sync, which the connectivity pass used, differs **only** by a Nothing-added
  `#define MODEM_DUMP_FLAG` uevent block in `fsm/mdee_dumper_v6.c`. Stock does not import
  `kasprintf`/`kobject_uevent_env`, which proves the block is absent.
  `../reconstruction/eccci-6df320423600-revert-nothing-modem-dump-flag.patch` is that delta.
* Candidates ruled out by parity:

  | candidate | ccci_md_all | ccci_dpmaif |
  |---|---|---|
  | 957dac1 baseline | 347/370 | 208/222 |
  | 997360d | 4 diffs | 3 diffs |
  | a418d77 | 5 diffs | 7 diffs |
  | fe0dd0d | 6 diffs | 7 diffs |
  | 310a057 | 3 diffs | 1 diff |
  | 9780d13 | 9 diffs | 8 diffs |
  | f3c59df (UFS block/unblock) | 5 diffs | exact |

  Also ruled out: 6df32 as shipped (3 diffs, 2 extra imports).
* Ulefone/YFT code delta: **none**.

## Architecture (gen 6299, `md_ccci_ports[]`, not the 6293 table)

* **One modem instance**, MD1 (`MD_SYS1`). HIF mask 0x06:
  * CCIF (`ccci_ccif`) carries every control/char/tty/ipc/smem port (75 entries).
  * DPMAIF (`ccci_dpmaif`) carries the 20 CCMNI network ports.
  * CLDMA is compiled but not shipped or used.
* **Port layer** (`port_proxy.c`): 95 static entries, decoded from the *stock* binary into
  [`../kernel/ccci-port-map.tsv`](../kernel/ccci-port-map.tsv). The `/dev/<name>` char major
  is dynamic (`alloc_chrdev_region`) under the `ccci_node` class:

  | ops | count | notes |
  |---|---:|---|
  | char_port_ops | 48 | |
  | net_port_ops | 20 | ccmni0–7, 9–20 |
  | smem_port_ops | 12 | |
  | ipc_port_ops | 9 | |
  | rpc_port_ops | 2 | |
  | sys_port_ops | 1 | |
  | ctl_port_ops | 1 | |
  | poller_port_ops | 1 | |
  | ccci_udc_port_ops | 1 | |

  Of these, 64 create a char node, 11 are kernel-only and 20 are netdevs.
* **Other char nodes outside the port table:**
  * `/dev/ccci_monitor` (FSM monitor, `ccci_mdinit`)
  * `/dev/ccci_md1_sta`, `/dev/ccci_md3_sta`, `/dev/ccci_mdx_sta` (`ccci_md_sta` class, MD-state broadcast to ccci_mdinit, libmtk-ril and libtrm)
  * `/dev/ccci_pin_sta` (rild)
* **sysfs** `/sys/kernel/ccci/`: `boot`, `debug`, `dump_max`, `ecid`, `ft_info`, `kcfg_setting`,
  `lk_md`, `md1_postfix`, `md_chn`, `mdee`, `md_en`, `pincfg`, `version`.
  Users: `ccci_mdinit` (boot, kcfg_setting, lk_md), `atcid` (boot, md_en), `thermal_core` and
  `libmipc` (boot), `aee_dumpstate` (md_chn).
* **procfs**:
  * `/proc/ccci_dump`, `/proc/ccci_log`, `/proc/ccci_sib` (ccci_util_lib)
  * `/proc/ccci_lp_mem` (port_proxy)
  * `/proc/dpmaif_debug` (ccci_dpmaif)
* **FSM** (`fsm/ccci_fsm.c`):
  * Commands: START and STOP (from `ccci_mdinit` via ioctl), WDT (MD WDT IRQ 0x1eb), EE (MD
    exception via CCIF), MD_HANG (status poller `ccci_poll`).
  * Boot: `GATED → BOOT_WAITING_FOR_HS1 → BOOT_WAITING_FOR_HS2 → READY`. HS1/HS2 are
    `ccci_ctrl` (channel 0/1) control messages. `BOOT_TIMEOUT` is 30 s, and a missing
    handshake raises `EXCEPTION_HS1/HS2_TIMEOUT`.
  * States broadcast to userspace: `INVALID, GATED, BOOT_WAITING_FOR_HS1/2, READY, EXCEPTION,
    RESET, WAITING_TO_STOP`. The `vendor.mtk.md1.status` property is set by `ccci_mdinit`, and
    `vendor.ril.md_status_from_ccci` drives `bip_ap` start/stop in `init.bip_ap.rc`.
* **Exception / coredump:**
  * mdee_dumper **v6** (md_gen ≥ 6299).
  * EE handshake timeouts: CCIF 10 s, REC_OK 10 s, PASS 10 s, EE_DONE 30 s.
  * Data is copied into `/proc/ccci_dump` and AEE (`aed_md_exception_api`) and registered with
    mrdump (`mrdump_mini_add_extra_file`).
  * The post-dump region is `SMEM_USER_MD_POST_DUMP` (`/dev/ccci_md_post_dump`).
  * EMI-MPU, SMPU and devapc violations feed MD dumps through
    `mtk_emimpu_md_handling_register`, `mtk_smpu_md_handling_register` and
    `register_devapc_vio_callback`.
* **Flight mode:** RIL turns the RF off inside the MD (AT/MIPC); the CCCI link stays READY.
  `ccci_mdinit` only uses STOP/START for MD reset/reload. `vendor.ril.md_status_from_ccci=flightmode`
  is the userspace notification (it stops `bip_ap`).
* **SCP side:** `ccci_fsm_scp` relays MD state to SCP over CCIF2 + tinysys IPI
  (`mtk_ipi_send`, `scp_A_register_notify`) and uses `SMEM_USER_CCISM_SCP`.
* **RPC** (`ccci_rpc`, `ccci_rpc_k`): the MD queries the AP for GPIO numbers/levels through the
  LK `/gpio` mapping (FDD band-detect 99/100, SIM pins), ADC (`md-auxadc`) and the DT
  `md_drdi_rf_set_idx`.
* **IPC tasks** (`ccci_ipc_*`, minor = AP task id):

  | task id | name | char node |
  |---:|---|---|
  | 0 | AGPS | ccci_ipc_1220_0 |
  | 1 | DHCP | — |
  | 2 | GPS | yes |
  | 3 | WMT | no (`CONFIG_MTK_CONN_MD` is unset, so the in-kernel conn_md bridge is not built) |
  | 4 | MISCTA | yes |
  | 5 | CCCIIPC (time) | yes, used by ccci_mdinit |
  | 6 | GF | no |
  | 7 | PKTTRC | no |
  | 8 | USB | no |
  | 9 | LWAPROXY | yes |

## DT contract (stock DTB; LK adds the properties listed in `../hardware/topology.md`)

`mddriver@d180000`: `mdhif-type`, `ap-plat-info`, `md-generation`, `offset-epon-md1`,
`cldma-capability`, `boot-status-config`, reg, 3 IRQs, power domain, infracfg/topckgen
syscons, vmodem/vsram/vdigrf supplies. `ccifdriver@10209000`: 2 regs, `sram-size 0x200`,
`ccif-hw-reset-ver 1`, `ccif-hw-reset-bit 0x1a`, 2 IRQs, 6 clocks. `ccci-scp@1023c000`.
`md-auxadc`. `MD1-SIM1-HOT-PLUG-EINT`.

## Boundary

The Linux side is complete. Not covered here: MD1 firmware (signed, proprietary,
`../firmware/boundary.md`) and the userspace daemons that drive the ports
(`../userspace/`).
