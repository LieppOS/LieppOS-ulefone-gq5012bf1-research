# Phase 4 — remaining stock-module triage (GQ5012BF1)

Scope: what still stands between the current source-reconstruction state and a
practical first source-based LieppOS custom-kernel boot on Slot B.

This is a **triage** document. Its original baseline started no new reverse
engineering and touched no hardware. It now carries append-only/current-status
updates from later dedicated reconstruction tasks; `custom_ldo` and
`sc851x_charger` are complete. All device evidence remains static/read-only.

Baseline (unchanged):

| | |
|---|---|
| kernel | Linux 6.1.115-android14-11 |
| GKI CI build | `ab/12901745` |
| Android Common commit | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` (`android14-6.1-2024-12_r4`) |
| exact workspace | `/home/armol/kernel-work/gki-12901745-workspace` |
| research repo | `LieppOS/ulefone-gq5012bf1-research` |

Machine-readable form of this table: `kernel/phase4-remaining-module-triage.tsv`
(37 columns × 23 rows).

---

## 1. Summary — disposition

| disposition           | count |
| --------------------- | ----: |
| DIRECT_SOURCE         |     0 |
| SOURCE_DELTA          |     2 |
| FORWARD_PORT          |     7 |
| SOURCE_RECONSTRUCTED  |     2 |
| RE_REQUIRED           |     4 |
| BLOCKED_WITH_EXACT_MISSING_EVIDENCE | 1 |
| STOCK_TRANSITION_BLOB |     7 |
| NOT_REQUIRED          |     0 |
| UNKNOWN               |     0 |
| **total**             |**23** |

## 2. Summary — priority

| priority                | count |
| ----------------------- | ----: |
| P0_BOOT_CRITICAL        |     2 |
| P1_CORE_HARDWARE        |     5 |
| P2_MAJOR_FEATURE        |    11 |
| P3_OPTIONAL_FEATURE     |     5 |
| P4_DEBUG_FACTORY_LEGACY |     0 |
| NOT_REQUIRED            |     0 |
| **total**               |**23** |

## 3. Summary — source confidence

| source confidence      | count |
| ---------------------- | ----: |
| EXACT_SOURCE           |     7 |
| STRONG_SOURCE_MATCH    |     1 |
| RELATED_SOURCE         |     0 |
| STRUCTURAL_DONOR_ONLY  |     4 |
| NO_USEFUL_SOURCE       |    11 |

## 4. Summary — stock transition-blob safety

| classification                  | count |
| ------------------------------- | ----: |
| YES_SAFE_TRANSITION             |     7 |
| YES_WITH_STOCK_PROVIDER_CHAIN   |    16 |
| NO_SOURCE_STACK_REQUIRED        |     0 |
| UNKNOWN                         |     0 |

**No unresolved module blocks a Slot-B boot as a stock blob.** See §7.

---

## 5. How the authoritative unresolved set was built

### 5.1 Population

Full stock module population, re-derived from the committed extraction rather
than from a status table:

| source | count |
|---|---|
| module placements (`stock-module-placements.tsv`) | 471 |
| distinct SHA256 module binaries (`stock-module-master.csv`) | 458 |
| vendor_boot platform ramdisk `.ko` files on disk | 196 |
| vendor_dlkm `.ko` files on disk | 215 |
| system_dlkm `.ko` files on disk | 60 |
| `vendor_boot/lib/modules/modules.load` entries | 184 |
| `vendor_boot/lib/modules/modules.load.recovery` entries | 189 |
| `vendor_dlkm/lib/modules/modules.load` entries | 195 |
| `system_dlkm/lib/modules/modules.load` entries | 60 |
| `odm_dlkm` | present but contains **no** kernel modules (only `etc/`) |

Cross-checked inputs: `modules.load`, `modules.load.recovery`, `modules.dep`
(via the `modules_dep_dependencies` column), `modules.alias`, `modules.softdep`,
`stock-module-imports.tsv`, `stock-module-exports.tsv`,
`stock-intermodule-abi.csv`, `ulefone-only-intermodule-edges.csv`,
`exact-gki-full-crc-comparison.csv`, `unknown-exact-audit.md` and every existing
Phase-4 reconstruction report.

### 5.2 Subtraction

Removed from the unresolved set because an authoritative solved/frozen report
exists (per the user's frozen list and the reports in this directory):

`focaltech_touch_spi_ft3680`, `aw883xx_driver`, `aw36515`, `aw36518`,
`aw36518_v2`, `leds_rgb_aw2013`, `st21nfc`, `connfem`, `tcpc_class`,
`tcpc_mt6375`, `pd_dbg_info`, `mtk_disp_notify`, `mtk_mbox`,
`mtk_tinysys_ipi`, `mtk_rpmsg_mbox`, `mtk-mbox-mailbox`, `yft_tpd_gesture`.

Removed because the platform-source question is already settled: the 336
`LIKELY_PLATFORM_MATCH` + 100 `DIRECT_SOURCE_MATCH` modules, for which Phase 3
established a structural source resolution for 396/440 candidate names (90.0 %)
and Phase 4 recorded `UARTHUB` as excluded (`uarthub-disable = <1>` in the
GQ5012BF1 DT). Those are a bulk **FORWARD_PORT** programme, not a triage
problem, and are out of scope here.

### 5.3 Result — total remaining unresolved module count before triage: **23**

The 16 entries named in the task, plus 7 that were missing from it and are
proven still-unresolved:

| # | module | why it is in the set |
|--:|---|---|
| 1 | `panel_ky_vtdr6115_dphy_cmd` | task list; `NO_EXACT_HIT` in the exact audit |
| 2 | `leds_ln2403` | task list; `NO_EXACT_HIT` |
| 3 | `sh366003_fg` | task list; `NO_EXACT_HIT` |
| 4 | `custom_ldo` | task list; `NO_EXACT_HIT` |
| 5 | `gps_drv_dl_v051` | task list; `RELATED_SOURCE_HIT` only |
| 6 | `gps_pwr` | task list; `RELATED_SOURCE_HIT` only |
| 7 | `gps_scp` | task list; `RELATED_SOURCE_HIT` only |
| 8 | `wmt_chrdev_wifi_connac2` | task list; `STRONG_API_HIT` only |
| 9 | `sc851x_charger` | task list; `NO_EXACT_HIT` |
| 10 | `tkcore` | task list; `STRONG_API_HIT` (API-name collision only) |
| 11 | `tkcore_drv` | task list; `NO_EXACT_HIT` |
| 12 | `custom_ldo_wl2868` | task list; `NO_EXACT_HIT` |
| 13 | `fingerprint` | task list; `RELATED_SOURCE_HIT` (generic word noise) |
| 14 | `bt_drv_6878` | task list; `STRONG_API_HIT` only |
| 15 | `conninfra` | task list; `STRONG_API_HIT` only |
| 16 | `wlan_drv_gen4m_6878` | task list; `RELATED_SOURCE_HIT` only |
| 17 | `sc8571_charger` | **added** — `ULEFONE_ONLY`, absent from the task list, runtime-active, sibling of `sc851x_charger` |
| 18 | `microarray_fp_tee` | **added** — `ULEFONE_ONLY`; the actual fingerprint *sensor* driver (`fingerprint.ko` is only its glue) |
| 19 | `spi_tiny_co5300_lcd` | **added** — `ULEFONE_ONLY`, rear mini display |
| 20 | `hynitron` | **added** — `ULEFONE_ONLY`, rear touch |
| 21 | `yft_gpio_keys` | **added** — `ULEFONE_ONLY`, custom action keys |
| 22 | `yft_tiny2c_usb` | **added** — `ULEFONE_ONLY`, thermal-camera power/mode |
| 23 | `yft_devinfo` | **added** — reconstruction exists but is *partially* resolved: 10 export CRCs still gap, and those exports gate five stock consumers |

Two modules named in earlier stale tables are **not** unresolved and are not
carried here: `aw883xx_driver` (now `SOURCE_DELTA_RECONSTRUCTION_EXACT`) and
`leds_rgb_aw2013` (now byte-identical to a source rebuild).

---

## 6. Triage table

Full 37-column data is in `phase4-remaining-module-triage.tsv`. The condensed
view below carries the decision-relevant columns.

| module | placement | normal boot | recovery | kern/inter/exp imports | source confidence | blob safe? | disposition | priority |
|---|---|---|---|---|---|---|---|---|
| `panel_ky_vtdr6115_dphy_cmd` | vendor_boot platform | yes (idx 76) | yes (idx 74) | 38 / 7 / 0 | ORACLE_RECONSTRUCTION_PROVIDER_ABI_BLOCKED | YES_WITH_STOCK_PROVIDER_CHAIN | BLOCKED_WITH_EXACT_MISSING_EVIDENCE | P1_CORE_HARDWARE |
| `yft_devinfo` | platform + vendor_dlkm | yes (vdlkm idx 193) | yes (idx 187) | 40 / 0 / 27 | NO_USEFUL_SOURCE | YES_SAFE_TRANSITION | SOURCE_DELTA | P1_CORE_HARDWARE |
| `sh366003_fg` | vendor_boot platform | yes (idx 133) | yes (idx 131) | 33 / 3 / 0 | NO_USEFUL_SOURCE | YES_WITH_STOCK_PROVIDER_CHAIN | RE_REQUIRED | P1_CORE_HARDWARE |
| `sc8571_charger` | vendor_boot platform | yes (idx 147) | yes (idx 145) | 41 / 1 / 0 | STRUCTURAL_DONOR_ONLY | YES_WITH_STOCK_PROVIDER_CHAIN | RE_REQUIRED | P1_CORE_HARDWARE |
| `sc851x_charger` | vendor_boot platform | yes (idx 146) | yes (idx 144) | 30 / 0 / 0 | NO_USEFUL_SOURCE | YES_SAFE_TRANSITION | **SOURCE_RECONSTRUCTED** | P1_CORE_HARDWARE |
| `tkcore` | vendor_boot platform | yes (idx 99) | yes (idx 97) | 101 / 0 / 25 | NO_USEFUL_SOURCE | YES_SAFE_TRANSITION | STOCK_TRANSITION_BLOB | **P0_BOOT_CRITICAL** |
| `tkcore_drv` | vendor_boot platform | yes (idx 100) | yes (idx 98) | 54 / 13 / 0 | NO_USEFUL_SOURCE | YES_WITH_STOCK_PROVIDER_CHAIN | STOCK_TRANSITION_BLOB | **P0_BOOT_CRITICAL** |
| `conninfra` | vendor_dlkm | yes (idx 120) | no (vendor_dlkm unmounted) | 175 / 19 / 81 | **EXACT_SOURCE** | YES_WITH_STOCK_PROVIDER_CHAIN | FORWARD_PORT | P2_MAJOR_FEATURE |
| `wmt_chrdev_wifi_connac2` | vendor_dlkm | yes (idx 121) | no | 40 / 0 / 18 | **EXACT_SOURCE** | YES_SAFE_TRANSITION | FORWARD_PORT | P2_MAJOR_FEATURE |
| `wlan_drv_gen4m_6878` | vendor_dlkm | yes (idx 122) | no | 295 / 95 / 0 | **EXACT_SOURCE** | YES_WITH_STOCK_PROVIDER_CHAIN | FORWARD_PORT | P2_MAJOR_FEATURE |
| `bt_drv_6878` | vendor_dlkm | yes (idx 167) | no | 149 / 38 / 1 | **EXACT_SOURCE** | YES_WITH_STOCK_PROVIDER_CHAIN | FORWARD_PORT | P2_MAJOR_FEATURE |
| `gps_drv_dl_v051` | vendor_dlkm | yes (idx 129) | no | 105 / 19 / 0 | **EXACT_SOURCE** | YES_WITH_STOCK_PROVIDER_CHAIN | FORWARD_PORT | P2_MAJOR_FEATURE |
| `gps_pwr` | vendor_dlkm | on demand (init.gps_pwr.rc) | no | 21 / 3 / 0 | **EXACT_SOURCE** | YES_WITH_STOCK_PROVIDER_CHAIN | FORWARD_PORT | P2_MAJOR_FEATURE |
| `gps_scp` | vendor_dlkm | on demand (init.gps_scp.rc) | no | 26 / 5 / 0 | **EXACT_SOURCE** | YES_WITH_STOCK_PROVIDER_CHAIN | FORWARD_PORT | P2_MAJOR_FEATURE |
| `fingerprint` | vendor_boot platform | yes (idx 181) | yes (idx 185) | 18 / 0 / 10 | NO_USEFUL_SOURCE | YES_SAFE_TRANSITION | RE_REQUIRED | P2_MAJOR_FEATURE |
| `microarray_fp_tee` | vendor_boot platform | yes (idx 182) | yes (idx 186) | 59 / 7 / 0 | NO_USEFUL_SOURCE | YES_WITH_STOCK_PROVIDER_CHAIN | STOCK_TRANSITION_BLOB | P2_MAJOR_FEATURE |
| `custom_ldo` | vendor_dlkm | yes (idx 102) | no | 1 / 2 / 2 | NO_USEFUL_SOURCE | YES_WITH_STOCK_PROVIDER_CHAIN | **SOURCE_RECONSTRUCTED** | P2_MAJOR_FEATURE |
| `custom_ldo_wl2868` | vendor_dlkm | yes (idx 101) | no | 27 / 0 / 2 | STRUCTURAL_DONOR_ONLY | YES_SAFE_TRANSITION | RE_REQUIRED | P2_MAJOR_FEATURE |
| `yft_gpio_keys` | vendor_boot platform | yes (idx 179) | yes (idx 183) | 65 / 0 / 0 | **STRONG_SOURCE_MATCH** | YES_SAFE_TRANSITION | SOURCE_DELTA | P3_OPTIONAL_FEATURE |
| `spi_tiny_co5300_lcd` | vendor_dlkm | yes (idx 191) | no | 54 / 4 / 0 | NO_USEFUL_SOURCE | YES_WITH_STOCK_PROVIDER_CHAIN | STOCK_TRANSITION_BLOB | P3_OPTIONAL_FEATURE |
| `hynitron` | vendor_dlkm | on demand (init.touch.rc) | no | 51 / 3 / 2 | STRUCTURAL_DONOR_ONLY | YES_WITH_STOCK_PROVIDER_CHAIN | STOCK_TRANSITION_BLOB | P3_OPTIONAL_FEATURE |
| `leds_ln2403` | vendor_dlkm | yes (idx 192) | no | 30 / 2 / 0 | NO_USEFUL_SOURCE | YES_WITH_STOCK_PROVIDER_CHAIN | STOCK_TRANSITION_BLOB | P3_OPTIONAL_FEATURE |
| `yft_tiny2c_usb` | vendor_dlkm | yes (idx 194) | no | 22 / 1 / 0 | NO_USEFUL_SOURCE | YES_WITH_STOCK_PROVIDER_CHAIN | STOCK_TRANSITION_BLOB | P3_OPTIONAL_FEATURE |

---

## 7. Transition-blob policy — the decisive result

Every one of the 23 modules was re-checked against the exact Google GKI
`vmlinux.symvers` for `ab/12901745`:

```
module                        imports  kernel-resolved-MATCH  kernel-mismatch  intermodule  unresolved
panel_ky_vtdr6115_dphy_cmd         45                     38                0            7           0
yft_devinfo                        40                     40                0            0           0
sh366003_fg                        36                     33                0            3           0
sc8571_charger                     42                     41                0            1           0
sc851x_charger                     30                     30                0            0           0
tkcore                            101                    101                0            0           0
tkcore_drv                         67                     54                0           13           0
conninfra                         194                    175                0           19           0
wmt_chrdev_wifi_connac2            40                     40                0            0           0
wlan_drv_gen4m_6878               390                    295                0           95           0
bt_drv_6878                       187                    149                0           38           0
gps_drv_dl_v051                   124                    105                0           19           0
gps_pwr                            24                     21                0            3           0
gps_scp                            31                     26                0            5           0
fingerprint                        18                     18                0            0           0
microarray_fp_tee                  66                     59                0            7           0
custom_ldo                          3                      1                0            2           0
custom_ldo_wl2868                  27                     27                0            0           0
yft_gpio_keys                      65                     65                0            0           0
spi_tiny_co5300_lcd                58                     54                0            4           0
hynitron                           54                     51                0            3           0
leds_ln2403                        32                     30                0            2           0
yft_tiny2c_usb                     23                     22                0            1           0
```

**Zero CRC mismatches and zero unresolved imports across all 23 modules.** The
whole 2 946-symbol kernel-facing requirement set is `MATCH` against the exact
Google `vmlinux.symvers` (`exact-gki-full-crc-comparison.csv`,
`Counter({'MATCH': 2946})`).

Therefore: **a source-built `//common:kernel_aarch64` from the pinned
`ab/12901745` workspace can load every remaining stock module unchanged.** The
only remaining constraints are intermodule (module→module) provider CRCs, which
is what the `YES_WITH_STOCK_PROVIDER_CHAIN` classification tracks.

### 7.1 The one real ABI hazard: `yft_devinfo`

`yft_devinfo` is the single provider that can silently break the stock stack.
`phase4-yft-devinfo-reconstruction.md` records 17/27 export CRCs reproduced and
**10 gapped**, all `*_device_add()`, blocked on one 73-character vendor enum
type text.

Those ten symbols are consumed by:

| stock consumer | gapped symbol it imports |
|---|---|
| `sh366003_fg` | `yft_fuelgauge_device_add` |
| `hynitron` | `yft_touchpanel_device_add` |
| `spi_tiny_co5300_lcd` | `yft_tinylcd_device_add` |
| `imgsensor` | `yft_camera_device_add` |
| `hf_manager` | `yft_{acc,m,alsps,sar,baro}sensor_device_add` |
| `focaltech_touch_spi_ft3680` (reconstructed) | `yft_spitouchpanel_device_add` |

**Rule for Level A and Level B: keep the STOCK `yft_devinfo.ko` as the
provider, and link every consumer — including the reconstructed FT3680 — against
the STOCK `yft_devinfo` `Module.symvers`.** Feeding the stock CRCs through
`KBUILD_EXTRA_SYMBOLS` is linking against the real provider, not patching a
reconstruction's own exports, so it stays inside the project's evidence rules.
Shipping the *reconstructed* `yft_devinfo` instead would break five stock
consumers at once.

### 7.2 Second-order provider hazards

| if you rebuild… | verify these export CRCs first | because |
|---|---|---|
| `ffa_v10` | 2 symbols | `tkcore_drv` imports them |
| `mtk_panel_ext`, `mediatek_drm` | 6 + 1 symbols | `panel_ky_vtdr6115_dphy_cmd` imports them |
| `charger_class` | 1 symbol | `sc8571_charger` imports it |
| `mtk-pwm` | 2 symbols | `leds_ln2403` imports them |
| `spi-mt65xx` | 2 symbols | `microarray_fp_tee` imports them |
| `connadp`, `connscp`, `ccci_md_all`, `aee_aed`, `device-apc-common`, `mtk_disp_notify`, `mddp`, `pmic_lbat_service`, `cfg80211`, `bluetooth` | see TSV `stock_providers` | the whole connectivity cluster |
| `mt6375-charger` | 1 symbol | `yft_tiny2c_usb` imports it |

---

## 8. Connectivity — FORWARD_PORT, not RE (task §6)

The audit's `STRONG_API_HIT` / `RELATED_SOURCE_HIT` labels understated the
evidence. Re-checking the local NothingOSS MT6878 trees
(`kernel_modules` @ `5f75a3b13e8135d45b4b0b70ec893345144f70df`,
`device_modules` @ `957dac185efe46cbf6336b0fff9516d84c8cd78f`) produced **exact
named build targets** for all seven connectivity modules:

| stock module | exact build target | MT6878 evidence |
|---|---|---|
| `conninfra` | `//vendor/mediatek/kernel_modules/connectivity/conninfra:conninfra` | `Kbuild:424-436` adds `conn_drv/connv2/platform/mt6878/{mt6878,_ops,_soc,_atf,_pmic,_emi,_consys_reg,_pos,_pos_gen,_coredump,_debug_gen}.o` under `CONFIG_MTK_COMBO_CHIP_CONSYS_6878`; `Kbuild:194-197` adds the mt6878 include + CODA paths |
| `wmt_chrdev_wifi_connac2` | `//…/connectivity/wlan/adaptor/build/connac2x:wmt_chrdev_wifi_connac2` | `define_mgk_ko(name = "wmt_chrdev_wifi_connac2")`; deps `common:wmt_drv`, `conninfra` |
| `wlan_drv_gen4m_6878` | `//…/connectivity/wlan/core/gen4m/build/connac2x/6878:wlan_drv_gen4m_6878` | `define_mgk_ko(name = "wlan_drv_gen4m_6878")`; `build/connac2x/6878/Makefile:5 _MODULE_NAME := wlan_drv_gen4m_6878`; `gen4m/Kbuild:26-27` selects `Kbuild.6878`; deps `conninfra`, `connfem`, `wlan_page_pool`, `wmt_chrdev_wifi_connac2` |
| `bt_drv_6878` | `//vendor/mediatek/kernel_modules/connectivity/bt/mt66xx:btif` → `outs = ["bt_drv_6878.ko", …]` | `mt66xx/BUILD.bazel` `platforms` list contains `"6878"`; `6878/Kbuild:1 BT_PLATFORM := 6878`; `btif/Kbuild:142 MODULE_NAME := bt_drv_$(BT_PLATFORM)`; deps `conninfra`, `connfem` |
| `gps_drv_dl_v051` | `//…/connectivity/gps/data_link/plat/v051:gps_drv_dl_v051` | `Kbuild` sets `GPS_PLATFORM := v051`, `MODULE_NAME := gps_drv_dl_$(GPS_PLATFORM)`, and carries the literal comment `# For MT6878 SoC + MT6686 A-die`; dep `conninfra` |
| `gps_pwr` | `//…/connectivity/gps/gps_pwr:gps_pwr` | `define_mgk_ko(name = "gps_pwr")`; `gpspwr.c` |
| `gps_scp` | `//…/connectivity/gps/gps_scp:gps_scp` | `define_mgk_ko(name = "gps_scp")`; `gps2scp.c`, `init.gps_scp.rc` |

All seven are additionally enumerated by name in
`device_modules/kernel/kleaf/mgk_64_k61.bzl` `mgk_64_k61_kleaf_modules`.

Runtime confirmation from the committed read-only snapshot: `conninfra_cored`,
`conninfra_cb`, `sub_conninfra_t`, `sub_wifi_thrd`, `sub_gps_thrd`,
`mtk_wland_thread`, `wlan_rst_thread`, `BTMTK_RX_WQ`, `gps_kctrld` and seven
`irq/*-gps_*` threads are all present; `ro.vendor.wlan.chrdev` =
`wmt_chrdev_wifi_connac2` and `ro.vendor.gps.chrdev` = `gps_drv_dl_v051`.

**Verdict: the stock-vs-donor delta for this cluster is a MediaTek platform
revision question, not Ulefone-specific hardware. Binary reverse engineering of
WLAN/BT/conninfra is explicitly NOT recommended.** Module size (`wlan_drv_gen4m_6878`
is 390 imports / 95 intermodule) is not evidence for RE.

Residual risk to measure after the first build, not before: exact source
revision drift, exactly as happened with ST21 (donor 2.2.0.15 vs stock 2.2.0.19).
`bt_drv_6878` carries `srcversion=2420E1C5069124661AF298D`, which is the handle
for that comparison.

---

## 9. TEE / TrustKernel pair (task §7)

### Is `tkcore` source present in a MediaTek TrustKernel tree?

**No.** Searched with exact identifiers, not generic words:

* `grep -rl 'trustkernel\|TrustKernel\|tkcore'` across `nothing-mt6878/{kernel,device_modules,kernel_modules}` over `*.c *.h Kbuild Makefile *.dts *.dtsi` → **zero files**.
* Same search across `/home/armol/kernel-work/vendor-reference/{MiCode-bsp-klee-w-oss,MiCode-dash-w-oss,MiCode-MTK-kernel-device-modules-chagall-2.0.31}` → **zero hits**.
* No public TrustKernel TKCore kernel drop located.

The 60 `EXPORT` hits recorded in `unknown-exact-audit.md` all resolve to
`device_modules/drivers/tee/teei/510/…`, which is a **different** TEE
implementation (MicroTrust TEEI). The overlap is the GlobalPlatform `TEEC_*`
API-name surface. Confirmed as an API-name collision, not source lineage — the
existing note in `external-driver-donors.md` was already right and is upheld.

### Are they two targets of one source tree?

They are two distinct modules with a hard dependency, not two outputs of one
target:

* `tkcore.ko` — 221 352 B, 25 exports, 101 kernel imports, **0** intermodule imports, `depends=` empty. Provides the client/TEEC surface: `TEEC_{InitializeContext,FinalizeContext,OpenSession,CloseSession,InvokeCommand,RegisterSharedMemory,ReleaseSharedMemory,AllocateSharedMemory}`, `tee_core_{add,alloc,del,free}`, `tee_wait_queue_*`, `tee_clkmgr_*`, `tee_map_cached_shm`, `tee_unmap_cached_shm`, `tee_supp_cmd`, `__tee_get`, `tee_spi_transfer`, `tee_spi_transfer_disable`, `tee_spi_cfg_padsel`.
* `tkcore_drv.ko` — 63 480 B, 0 exports, `depends=tkcore,ffa_v10`. The SMC/FF-A transport: shared-memory pool, TEE log buffer, `tkcore_smc_task.%u` kthreads, `tkcoreos-rev: %d.%d.%d-gp`.

Load order is adjacent and fixed: platform ramdisk `97 ffa_v10.ko`,
`98 teeperf.ko`, `99 tkcore.ko`, `100 tkcore_drv.ko` (recovery: 95/96/97/98).

### Dependency relation and consumers

```
ffa_v10 ──2──┐
             ├──▶ tkcore_drv        (13 intermodule imports)
tkcore ──11──┘
tkcore ──1───▶ microarray_fp_tee    (tee_spi_transfer)
tkcore ──7───▶ tmem_ffa             (TEEC_* — MediaTek Trusted Memory Driver,
                                     vendor_dlkm idx 151, depends=gz_tz_system,tkcore,ffa_v10)
```

### Userspace consumers (from the committed stock `vendor` extraction)

* `/vendor/bin/hw/android.hardware.security.keymint@3.0-service.trustkernel` + VINTF manifest
* `/vendor/bin/hw/android.hardware.gatekeeper-service.trustkernel` + VINTF manifest
* VINTF manifests for `android.hardware.security.secureclock-service.trustkernel` and `…sharedsecret-service.trustkernel`
* `/vendor/lib64/libwv_trustkernel.so` (Widevine)
* `/vendor/etc/init/trustkernel.rc`; `init.fingerprint.rc` gates on `on property:vendor.trustkernel.fs.state=ready`
* Device nodes `/dev/tkcore_client`, `/dev/tkcore_admin`, `/dev/tkcore_fp`; `/proc/tkcore`; RPMB; `/mnt/vendor/persist/t6`
* SELinux types `tkcore_{admin,client}_device`, `tkcore_{protect_data,systa,spta,data,log}_file`, `proc_tkcore`, `vendor_mtk_trustkernel_tee_prop`

Runtime: eight `[tkcore_smc_task.N]` kernel threads are live in the snapshot.

### Required for Android boot?

**Yes.** KeyMint 3.0 and Gatekeeper are the *only* declared implementations of
those HAL interfaces. Without them `keystore2` has no KeyMint backend, and the
device uses FBE (see `reports/CLAUDE_FBE_REPORT.md`), so encrypted `/data`
cannot be unlocked. Widevine and the fingerprint TA also depend on it.
Hence **P0_BOOT_CRITICAL**.

### Can stock blobs remain?

**Yes, and they should.** `tkcore` is `YES_SAFE_TRANSITION` (101/101 kernel CRCs
`MATCH`, zero intermodule imports — it depends on nothing but the GKI core).
`tkcore_drv` is `YES_WITH_STOCK_PROVIDER_CHAIN` (keep stock `tkcore` **and**
stock `ffa_v10`, or prove `ffa_v10`'s two consumed export CRCs before rebuilding
it).

Disposition for both: **STOCK_TRANSITION_BLOB**. Secure-world behaviour is
explicitly out of scope; only the Linux-side ABI is frozen here.

---

## 10. Power / charging cluster (task §8)

| | `sh366003_fg` | `sc851x_charger` | `sc8571_charger` | `custom_ldo_wl2868` | `custom_ldo` |
|---|---|---|---|---|---|
| DT node | `sh366003@55` | `sc851x-charger@6f` | `sc8571@66`, `sc8571@67` | `pmu@wl2864c` | none (symbol shim) |
| compatible | `sh,sh366003` | `sc,sc8510` (driver also matches `sc,sc851x`, `sc,sc8517`) | `sc,sc8571-master` / `sc,sc8571-slave` | `will,wl2864c_pmu` | — |
| bus / address | I2C 9 @ 0x55 (`i2c@11c24000`) | I2C 6 @ 0x69 | I2C 11 @ 0x66; I2C 6 @ 0x67 | I2C 11 @ 0x29 | — |
| alias | `i2c:sh366003`, `of:…Csh,sh366003` | none | none | none | none |
| live binding | `/sys/bus/i2c/devices/9-0055` → `sh366003` | `/sys/bus/i2c/devices/6-0069` → `sc851x` | `11-0066` → `sc8571` (`sc8571-master`), `6-0067` → `sc8571` (`sc8571-slave`) | `/sys/bus/i2c/devices/11-0029` → `wl2864c` | `/sys/module/custom_ldo` |
| providers | `yft_devinfo` (3) | none | `charger_class` (1) | none | `custom_ldo_wl2868` (2) |
| consumers | none | none | none | `custom_ldo` | `imgsensor` |
| userspace / HAL | `3rd-gauge` power supply; BatteryService reads MT6375 as primary | none observed | MediaTek `primary_dvchg` / `secondary_dvchg` charger_class names; thermal HAL `charger-cooler` | none | none |
| runtime-active | **YES** — `fg_monitor_workfunc` every ~5 s (`RSOC=79, Volt=8397, Curr=194, Temp=375, SoH=94, cycnt=26, FCC=8594`) | **YES** — `irq/57-sc851x-irq` thread | **YES** — `sc8571_enable_adc` / `sc8571_get_adc_data` polling; `irq/49-sc8571-master-irq`, `irq/63-sc8571-slave-irq` | **YES** — bound | **YES** — loaded before `imgsensor` |
| boot importance | none | none | none | none | none |
| charging importance | secondary gauge only | SC8510 static converter protection/timing configuration; no charging-policy API | **high** — PD/PPS direct charge | none | none |
| source candidate | none | none | OPLUS `oplus_sc8571_master.c` (register map only) | sonyxperiadev `wl2868c-regulator.c` (register/voltage map only) | none |

Answers to the specific questions asked:

* **Does `sh366003_fg` control the `3rd-gauge` power supply seen elsewhere?**
  Yes. `docs/battery-charging.md` records `SH366003 at I2C 9-0055, exported as
  3rd-gauge`, and the live `thermal-power.txt` dump contains three `3rd-gauge`
  references alongside three `mtk-gauge` references. The primary Android battery
  path is MT6375 `mtk-gauge` at I2C 5-0034 and is **not** provided by this
  module — so losing `sh366003_fg` degrades secondary gauge reporting but does
  not remove the battery.
* **Is `sc851x_charger` active in normal charging?** It is **bound and has a live
  IRQ thread**, but no `sc851x` event appears in the captured normal-charging
  dmesg window, whereas SC8571 is actively polled through `charger_class`.
  Reconstruction proves that SC851x resets the IC, writes 35 static
  protection/timing/frequency fields, dumps registers, and logs three IRQ flag
  bytes. It exposes no charging-policy or converter-direction API. SouthChip
  documents SC8510 silicon as a 2S forward-2:1/reverse-1:2 converter, but the
  board's exact mode/enable nets are schematic-unknown; the earlier claim that
  this Linux driver specifically serves reverse/OTG or an audio load switch is
  withdrawn. uSmart VBUS is separately proven to use MT6375 `usb-otg-vbus`.
* **Does `custom_ldo_wl2868` power cameras/sensors?** Yes. It is the WL2864C /
  WL2868C 7-channel camera PMU, and the only path from it into the rest of the
  kernel is `custom_ldo_wl2868 → custom_ldo → imgsensor`. It is loaded at
  vendor_dlkm indices 101/102, immediately before `mtk-cam-isp7sp` (103),
  `imgsensor-glue` (104) and `imgsensor` (105).
* **Is `custom_ldo` generic board power glue?** Yes, and it is trivially small:
  10 296 B, exactly two functions (`custom_ldo_en`, `custom_ldo_vout`), three
  imports (one kernel + two from `custom_ldo_wl2868`), two exports. It is a pure
  forwarding shim.

These do rank above the cosmetic modules: three of the five are
`P1_CORE_HARDWARE`, and the LDO pair is the hard gate on cameras.

No live charger or power writes were performed.

---

## 11. Display panel (task §9)

* **Is it the active stock panel?** **Yes, proven three ways.**
  1. Kernel log: `lcm_prepare+ yft-lcm-vtdr6115-drv- start`,
     `lcm_panel_init+ … reset_gpio H-L-H,120`, `lcm_prepare- … end`,
     `lcm_enable+ … start`, `mtk_panel_ext_param_set+ … dst_fps=60`.
  2. Kernel command line: `lcmname=yft_vtdr6115_fhdp_dsi_cmd_hx_dphy_667_ky_lcm_drv`.
  3. Device tree: the only DSI panel child is `panel1@0` with
     `compatible = "hx,vtdr6115,cmd,120hz,ky"` — there is **no** `panel0@0`
     alternative, so this is not a multi-panel selection board.
* **Exact DT contract:** `hx,vtdr6115,cmd,120hz,ky`; `vci-gpios`, `dvdd-gpios`,
  `powerdm-gpios`, `reset-gpios`, `gate-ic = <0>`, `port/endpoint` to DSI0.
  `dsi-te` uses `mediatek, dsi_te-eint`.
* **Does it supply DRM panel registration?** Yes. It imports 6 symbols from
  `mtk_panel_ext` and 1 from `mediatek_drm`, exports nothing, and — decisively —
  **loads at platform index 76, before `mediatek-drm.ko` at index 80**
  (`75 mtk_panel_ext.ko`, `76 panel-ky-vtdr6115-dphy-cmd.ko`,
  `77 mediatek-drm-gateic.ko`, `78 mediatek-drm-panel-drv.ko`,
  `79 drm_display_helper.ko`, `80 mediatek-drm.ko`). It registers the panel that
  `mediatek-drm` then binds.
* **Structurally similar public driver?** Yes, but not a source match:
  Motorola `kernel-mtk` commit `0087a407394abd3ab073e1a2df164f1187959a3f`
  ("drm/panel: aion: add the driver for csot_vtdr6115 panel") adds
  `drivers/gpu/drm/panel/dsi-panel-mot-csot-vtdr6115-655-fhdp-dphy-vdo-144hz.c`
  (1 194 lines) plus an LHBM alpha table header. That is a **CSOT 6.55" 144 Hz
  VDO** panel; the Ulefone part is a **KY 120 Hz cmd** panel. Same DDIC family,
  different command tables. The Nothing tree ships the MediaTek panel skeleton
  family (`panel-hx-nt37701-dphy-cmd-120hz.c` etc.) but has **zero** `vtdr6115`
  hits.
* **Command tables / modes / refresh rates present in the stock binary:**
  `ext_params_90hz`, `ext_params_120hz`, `performance_mode_90hz`,
  `performance_mode_120hz`, `default_mode`, `get_mode_by_id`, `mode_switch`,
  `current_fps`, `lcm_get_modes`; DSC tables
  `vtdr6115_vdo_120hz_dphy_range_bpg_ofs`, `…_range_max_qp`, `…_range_min_qp`,
  `…_buf_thresh`; HBM path `set_hbm_backlight`, `sethbm_cmdq`,
  `last_hbm_backlight_value`, `yft_hbm_flag`; `lcm-degree` rotation property;
  `mtk_scaling_mode_mapping`. Framework HAL reports 60/90/120 Hz.
* **Dependencies:** 38 kernel imports (all CRC-`MATCH`), 7 intermodule
  (`mtk_panel_ext` 6, `mediatek_drm` 1); `depmod` chain pulls in the full
  MediaTek DRM/MML/SMI/MMDVFS stack (38 modules).
* **Can the stock blob coexist temporarily?** **Yes** —
  `YES_WITH_STOCK_PROVIDER_CHAIN`. Keep stock `mtk_panel_ext` and
  `mediatek-drm`, or verify their 7 consumed export CRCs first.

**Classification: `RE_REQUIRED`** — not `SOURCE_DELTA` (no matching source
exists to take a delta from) and not `STOCK_TRANSITION_BLOB` as a permanent
answer (this is the main display; it belongs in Level B). The Motorola driver is
a `STRUCTURAL_DONOR_ONLY` skeleton.

Per instruction, **no panel command-table reconstruction was started in this
task.**

---

## 12. LN2403 / camping light (task §10)

* **Physical role:** confirmed as the **Ulefone Armor camping / work light plus
  the red-blue warning LEDs**, not a backlight and not a flash. The DT node
  `yft_camplight` carries `ln2403-power-gpio`, `ln2403-en-gpio`,
  `leds-power-gpio`, `leds-red-gpio`, `leds-blue-gpio`. The stock module
  contains both `camplight_probe`/`camplight_remove` and `redblue_led_timer_func`.
* **Known compatible:** `mediatek,yft_camplight` — confirmed present in the
  merged GQ5012BF1 DT with `status = "okay"`.
* **Userspace / sysfs ABI:** `/sys/devices/platform/yft_camplight/camplight_mode`,
  `…/leds_ctl`, `…/camplight_set_brightness` — all chmod'd by
  `/vendor/etc/init/hw/init.yft.rc` (lines 222-224) and labelled
  `u:object_r:sysfs_yft_file:s0` in `vendor_file_contexts`. A legacy alias
  `/sys/devices/platform/soc/soc:gftk_camplight/camplight_mode` is also
  chmod'd. Userspace consumers are the stock `YftOutdoorLightUlefone` and
  `YftRedBlueLight` apps.
* **PWM/GPIO relationship:** `depends=mtk-pwm` with exactly **2** imported
  symbols; brightness is produced by PWM on the LN2403 enable pin, with four
  pinctrl states `default`, `ln2403_pwmoff_high`, `ln2403_pwmoff_low`,
  `ln2403_pwmon`. Internals: `ln2403_gpio_ctrl_apply`, `ln2403_pwm_work`,
  `gpio_ctrl_timer_handler`, `set_leds`, `ln2403_get_gpio`.
* **Public LN2403 source:** **none found.** `grep -rli ln2403` over the Nothing
  MT6878 trees, the MiCode vendor-reference BSPs and the exact GKI tree returns
  zero. Targeted public searches for `"Module For PWM LN2403"` and
  `mediatek,yft_camplight` return no driver.
* **Required for basic boot?** **No — proven.** It is the second-to-last
  vendor_dlkm module (index 192 of 195), it is **absent from
  `modules.load.recovery`**, it exports **zero** symbols so nothing can depend on
  it, and it has no boot-path consumers. Removing it cannot affect boot.

**Disposition: `STOCK_TRANSITION_BLOB`, `P3_OPTIONAL_FEATURE`.** Because it has
0 exports there are no CRC constraints on a future rewrite, and the DT + sysfs
ABI recovered above is already sufficient for a clean-room reimplementation
whenever it is wanted.

---

## 13. Fingerprint (task §11)

The word "fingerprint" was explicitly treated as noise; the 97 `RELATED_SOURCE_HIT`
records in `unknown-exact-audit.md` are netfilter OSF, x509 and unrelated DTS
matches and are rejected. The real identifiers are `mediatek,yft_finger` and
`mediatek,madev_finger`.

**The fingerprint stack is two modules, not one:**

| | `fingerprint.ko` | `microarray_fp_tee.ko` |
|---|---|---|
| description | `for yft fingerprint driver` | `Driver for microarray fingerprint sensor` |
| compatible | `mediatek,yft_finger` | `mediatek,madev_finger` (also matches `mediatek,yft_finger`, `mediatek,finger_print-eint`) |
| DT node | `yft_finger` (platform) | `fingerprint@0` under `spi1` |
| role | **platform/power/reset/IRQ/pinctrl glue only** | **the actual sensor driver** |
| functions | 16, all `yft_finger_*` | sensor + TEE SPI transport |
| exports | 10 | 0 |
| imports | 18 kernel / 0 intermodule | 59 kernel / 7 intermodule |
| depends | none | `fingerprint`, `spi-mt65xx`, `tkcore` |
| load idx | platform 181 | platform 182 |

* **Is `fingerprint.ko` only glue?** **Yes, proven.** Its complete function list
  is `yft_finger_get_gpio_info`, `yft_finger_probe_isok`, `yft_finger_set_power`,
  `yft_finger_power_deinit`, `yft_finger_set_reset`, `yft_finger_set_irq`,
  `yft_finger_get_irqnum`, `yft_finger_get_irq_gpio`, `yft_finger_get_reset_gpio`,
  `yft_finger_set_spi_mode`, `yft_waite_for_finger_dts_paser`,
  `yft_get_max_finger_spi_cs_number`, `yft_finger_plat_probe`,
  `yft_finger_plat_remove` (+ init/exit). There is no sensor protocol in it. It
  exports exactly the four symbols `microarray_fp_tee` consumes:
  `yft_finger_set_irq`, `yft_finger_set_reset`, `yft_finger_set_spi_mode`,
  `yft_waite_for_finger_dts_paser`.
* **Exact sensor model:** **MicroArray**, on **SPI1**. Evidence: live binding
  `/sys/bus/spi/devices/spi1.0` → driver `madev`, modalias `spi:madev_finger`,
  module `microarray_fp_tee`; device node `/dev/madev0` labelled
  `u:object_r:mafinger_device:s0`; HAL `/vendor/lib64/hw/microarray.fingerprint.default.so`
  (strings `MICROARRAY`, `Microarray Fingerprint HAL`, `microarray.fingerprint`)
  which dlopens `libmicroarray.default.so`. The exact die/part number is **not**
  recoverable from the extracted artefacts.
* **DT properties (`yft_finger`, fully recovered):** `reset-gpio`, `int-gpio`,
  `interrupt-parent`, `interrupts = <3 1 3 0>`, `debounce = <3 0>`,
  `status = "okay"`, and **16 pinctrl states**: `default`, `finger_reset_en0/1`,
  `finger_power_en0/1`, `finger_spi0_{mi,mo,clk,cs}_as_spi0_*`,
  `finger_spi0_{mi,mo,clk,cs}_as_gpio`, `finger_eint_pull_{down,up,dis}`.
  The `madev_finger` node adds `vfp-supply`, `spi-max-frequency = 8000000`,
  `cs-gpios`.
* **HAL relationship:** `init.fingerprint.rc` gates the whole stack on
  `on property:vendor.trustkernel.fs.state=ready`; the sensor driver routes all
  SPI through `tkcore`'s `tee_spi_transfer`, and `/dev/tkcore_fp` exists. The
  fingerprint path is therefore **inseparable from the TEE**.
* **Public vendor driver candidates:** **none.** Targeted searches for
  `mediatek,madev_finger`, `madev_finger`, `microarray_fp_tee`,
  `mas_plat_probe`, `yft_waite_for_finger_dts_paser` and
  `yft_finger_set_spi_mode` returned no kernel driver. The only public
  "microarray" fingerprint code is a libfprint USB userspace driver for an
  unrelated USB part.
* **Can they stay as stock transition blobs for first boot?** **Yes.**
  `fingerprint` is `YES_SAFE_TRANSITION` (18/18 kernel CRCs `MATCH`, zero
  intermodule imports). `microarray_fp_tee` is `YES_WITH_STOCK_PROVIDER_CHAIN`
  (needs stock `fingerprint`, `spi-mt65xx`, `tkcore`).

Dispositions: `fingerprint` → **RE_REQUIRED** (LOW difficulty; 16 glue
functions, DT contract already fully recovered; but its 10 export CRCs must be
reproduced exactly because they gate the sensor driver).
`microarray_fp_tee` → **STOCK_TRANSITION_BLOB** (HIGH difficulty: all sensor
traffic is TEE-mediated and therefore not observable from the Linux side).

---

## 14. Modules that genuinely require reverse engineering

Five still require panel/hardware reverse engineering; VTDR6115 panel logic is now reconstructed but separately blocked at the provider ABI. `custom_ldo` graduated from this list after byte-identical two-function reconstruction:

| module | why no source path exists | difficulty |
|---|---|---|
| `sh366003_fg` | no public SH366003 Linux driver; vendor AFI upgrade engine | HIGH |
| `sc8571_charger` | only an OPLUS-framework donor; MediaTek `charger_class` glue absent | MODERATE |
| `sc851x_charger` | no public SC851x driver at all | LOW_TO_MODERATE |
| `custom_ldo_wl2868` | Sony donor is a regulator driver; stock is a chardev+export driver | LOW_TO_MODERATE |
| `fingerprint` | Ulefone/YFT-only pinctrl glue | LOW |

## 15. Modules that have usable source and need only build / forward-port work

Nine:

`conninfra`, `wmt_chrdev_wifi_connac2`, `wlan_drv_gen4m_6878`, `bt_drv_6878`,
`gps_drv_dl_v051`, `gps_pwr`, `gps_scp` (all `EXACT_SOURCE`, named bazel
targets), plus `yft_gpio_keys` (`STRONG_SOURCE_MATCH` against the exact-GKI
in-tree `drivers/input/keyboard/gpio_keys.c`) and `yft_devinfo`
(`SOURCE_DELTA`; complete buildable source already exists, blocked only on one
73-character enum text).

`yft_gpio_keys` evidence: `MODULE_DESCRIPTION` is byte-identical
(`"Keyboard driver for GPIOs"`); all 23 stock functions are a strict subset of
the 27 upstream `gpio_keys_*` functions; the delta is the module/compatible
rename `gpio-keys` → `yft-gpio-keys` (the `platform:gpio-keys` alias is
retained) plus the wakeup-enable helpers being inlined/compiled out.

## 16. Safe to keep temporarily as stock transition blobs

All 23 are ABI-safe against the source-built exact GKI. The seven for which
"keep stock" is the *recommended final disposition for now* are:

`tkcore`, `tkcore_drv`, `microarray_fp_tee`, `spi_tiny_co5300_lcd`, `hynitron`,
`leds_ln2403`, `yft_tiny2c_usb`.

Of the 23, seven are `YES_SAFE_TRANSITION` (no module-to-module provider at
all): `yft_devinfo`, `sc851x_charger`, `tkcore`, `wmt_chrdev_wifi_connac2`,
`fingerprint`, `custom_ldo_wl2868`, `yft_gpio_keys`.

## 17. Modules not required

**None.** No module in the unresolved set could be proven unnecessary. The only
module previously proven `NOT_REQUIRED` on this device is `uarthub_drv`
(`uarthub-disable = <1>`, OF entry resolves to `undef_plat_data`), and it was
already excluded before this triage.

`gps_pwr`, `gps_scp` and `hynitron` are **not** in any `modules.load` — but they
are demonstrably loaded on demand (`init.gps_pwr.rc`, `init.gps_scp.rc` on
`vendor.connsys.driver.ready=yes`; `init.touch.rc` for the touch family) and
`hynitron` is bound and has a live IRQ thread. They are therefore required, just
not statically loaded.

---

## 18. Recommended execution order

Rationale: reach a **safe, observable Slot-B boot** first; then restore the
display; then core power; then features. Providers always precede consumers.

```
NEXT  1  SOURCE_BUILD    //common:kernel_aarch64 @ ab/12901745 (GKI core only)
NEXT  2  TRANSITION_BLOB freeze all 23 unresolved stock .ko unchanged + preserve load order
NEXT  3  TRANSITION_BLOB pin stock yft_devinfo as THE provider; relink reconstructed
                         FT3680 against stock yft_devinfo Module.symvers
NEXT  4  SOURCE_BUILD    re-land the frozen reconstructions (st21nfc, mtk_disp_notify,
                         mtk_mbox, mtk_tinysys_ipi, mtk_rpmsg_mbox, connfem, tcpc_class,
                         tcpc_mt6375, pd_dbg_info, leds_rgb_aw2013, aw36515, aw36518,
                         aw36518_v2, aw883xx_driver, yft_tpd_gesture, ft3680)
NEXT  5  ABI_SOURCE      panel_ky_vtdr6115_dphy_cmd — panel logic reconstructed;
                         obtain exact mtk_panel_ext/mediatek-drm type graph for 7 CRCs
DONE  6  RE              custom_ldo: byte-identical wrappers, exact ABI/build;
                         custom_ldo_wl2868 remains structurally reconstructed with residuals
NEXT  7  RE              sc8571_charger, then sc851x_charger (charging)
NEXT  8  RE              sh366003_fg  (needs stock yft_devinfo CRCs — see NEXT 3)
NEXT  9  FORWARD_PORT    conninfra   (root of the whole connectivity cluster)
NEXT 10  FORWARD_PORT    wmt_chrdev_wifi_connac2, then wlan_drv_gen4m_6878
NEXT 11  FORWARD_PORT    bt_drv_6878
NEXT 12  FORWARD_PORT    gps_drv_dl_v051, gps_pwr, gps_scp
NEXT 13  RE              fingerprint  (10 export CRCs must match exactly)
NEXT 14  SOURCE_DELTA    yft_gpio_keys (low-risk, 0 exports, in-tree donor)
NEXT 15  TRANSITION_BLOB hold: microarray_fp_tee, tkcore, tkcore_drv,
                         spi_tiny_co5300_lcd, hynitron, leds_ln2403, yft_tiny2c_usb
NEXT 16  SOURCE_DELTA    yft_devinfo — only if a YFT BSP drop supplying the missing
                         73-character enum text ever becomes available
NEXT 17  DROP            nothing
```

Steps 1-4 require **zero** of the 23 unresolved modules to be reconstructed.

---

## 19. Level-A feasibility

**Yes — a Level-A Slot-B source-kernel boot is possible before any of the
remaining reverse engineering is complete.**

Grounds: the stock boot kernel is bit-for-bit identical to the published Google
`Image.lz4` for `ab/12901745`; all 2 946 kernel-facing `CONFIG_MODVERSIONS`
requirements are `MATCH`; and all 23 unresolved modules import **zero**
unresolved and **zero** mismatched kernel symbols. A self-built
`//common:kernel_aarch64` from the pinned workspace is therefore a drop-in for
the stock kernel with the entire stock vendor module set retained.

Details in `kernel/phase4-slot-b-minimum-source-stack.md`.

---

## 20. Cross-references

* `kernel/phase4-remaining-module-triage.tsv` — machine-readable, 37 columns
* `kernel/phase4-remaining-module-dependency-graph.md` — clusters and build order
* `kernel/phase4-slot-b-minimum-source-stack.md` — Level A / B / C targets
* `kernel/unknown-exact-audit.md` — original exact-evidence audit (with current-resolution notes appended)
* `kernel/phase4-buildability-plan.md` — build environment and frozen reconstructions

## 21. Safety statement

This task was static and read-only. No flashing, no slot switch, no
boot-control change, no `insmod`/`rmmod`, no bind/unbind, no sysfs write, no
GPIO change, no I2C write, no charging test, no panel command, no light
enable, and no calibration/NVRAM/DT/DTBO modification. All device evidence came
from the previously committed read-only snapshot
`workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/` and the
committed stock partition extraction.

---

## 22. Phase 4 `custom_ldo` update (2026-09-08)

`custom_ldo` is complete at `STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION`: stock
and reconstruction each contain exactly two 28-byte functions, both functions
are byte-identical, KCFI is exact, all three import CRCs and both export CRCs
match, relocation parity is 10/10, and exact-GKI `BUILD_RC=0` with unresolved
symbols 0. The build consumes the reconstructed WL2868 provider's real
`Module.symvers`. Stock `imgsensor` call sites additionally prove the forwarded
voltage value is in microvolts. Only generated srcversion/vermagic provenance
differs; the shim itself is no longer an RE task. The WL2868 provider retains
its separate documented structural residuals.

---

## 23. Phase 4 `sc851x_charger` update (2026-09-08)

`sc851x_charger` is now `SOURCE_RECONSTRUCTED`: no-public-source RED recovered
all 11 functions, 50 register fields, 35 required DT writes, raw-register
sysfs, IRQ, PM and shutdown behavior. Exact-GKI build is clean
(`BUILD_RC=0`, warnings 0, unresolved 0). All function sizes/KCFI IDs,
`.rodata`, `.data`, strings, 30 MODVERSION records and relocation target/type
sequences match; 8/9 behavioral functions are byte-identical and the inlined
probe retains a reported compiler-local text delta. DT/live identity is
resolved as SC8510 at `6-0069`; the `@6f` suffix is stale. Separate DT,
extcon, APK and symbol evidence proves uSmart VBUS/control uses USB1 and MT6375
OTG, not SC851x. Hardware runtime testing remains excluded by the safety policy.
