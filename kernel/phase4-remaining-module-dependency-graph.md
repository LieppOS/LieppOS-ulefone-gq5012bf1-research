# Phase 4 — remaining-module dependency graph (GQ5012BF1)

Purpose: prevent reconstructing a consumer before its provider chain is ready,
and make every module-to-module ABI edge that a rebuild could break explicit.

Edge weights are **counts of imported symbols**, computed from
`kernel/stock-module-imports.tsv` × `kernel/stock-module-exports.tsv`.
`[stock]` = still a stock blob. `[frozen]` = already reconstructed/frozen.
`[port]` = MediaTek/Nothing source exists, forward-port only.

Load-order indices are `P:n` = vendor_boot platform `modules.load`,
`V:n` = vendor_dlkm `modules.load`, `R:n` = `modules.load.recovery`.

---

## 0. Global rule

> **Never rebuild a provider without first proving the export CRCs that its
> stock consumers import.**

The complete provider→consumer edge set for the Ulefone-only modules is
`kernel/ulefone-only-intermodule-edges.csv`. The single most dangerous provider
is `yft_devinfo` (§6).

---

## 1. Cluster: DISPLAY (main panel)

```
                       GKI core (source-built, ab/12901745)
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
   mtk_panel_ext [port]     mediatek_drm [port]    drm_dma_helper [GKI]
        P:75                     P:80 / R:78            P:74
              │  6 symbols          │  1 symbol
              └──────────┬──────────┘
                         ▼
        panel_ky_vtdr6115_dphy_cmd  [stock]  P:76 / R:74
        compatible "hx,vtdr6115,cmd,120hz,ky"
        38 kernel imports · 7 intermodule · 0 exports  → LEAF
```

**Root providers:** `mtk_panel_ext`, `mediatek_drm` (both platform
forward-port work, outside this triage set).

**Critical ordering fact:** the panel loads at **P:76, four slots before
`mediatek-drm.ko` at P:80**. It registers the `drm_panel` that `mediatek-drm`
subsequently binds. Reordering it after `mediatek-drm` will break display bring-up.

Full stock `depmod` chain (38 modules) is in the master CSV; the load-order
critical prefix is:

```
P:72 mtk-mml → P:73 mtk-mml-mt6878 → P:74 drm_dma_helper → P:75 mtk_panel_ext
   → P:76 panel-ky-vtdr6115-dphy-cmd → P:77 mediatek-drm-gateic
   → P:78 mediatek-drm-panel-drv → P:79 drm_display_helper → P:80 mediatek-drm
```

**Current action:** retain stock `mtk_panel_ext` → `mediatek-drm` → panel as one ABI island. The panel logic is reconstructed, but a source build remains `BLOCKED_WITH_EXACT_MISSING_EVIDENCE` until the provider type graph reproduces all seven stock CRCs.
Because the panel has **zero exports**, reconstructing it can never break
anything downstream — the risk is entirely upstream (its 7 imported CRCs).

---

## 2. Cluster: POWER / CHARGING

```
   charger_class [port] P:130 ──1──▶ sc8571_charger [recon-static-pass] P:147 / R:145
                                     sc,sc8571-master @ I2C 11-0066
                                     sc,sc8571-slave  @ I2C  6-0067   → LEAF
                                     import CRC 0x36325d38

   (kernel only) ───────────────────▶ sc851x_charger [recon-exact] P:146 / R:144
                                     sc,sc8510 @ I2C 6-0069           → LEAF
                                     30 kernel imports · 0 intermodule

   yft_devinfo [stock] ──3──────────▶ sh366003_fg   [stock] P:133 / R:131
   (fuelgauge_fw_version,             sh,sh366003 @ I2C 9-0055        → LEAF
    yft_fuelgauge_device_add,
    yft_set_fuelgauge_device_used)

   mt6375_charger [port] ──1────────▶ yft_tiny2c_usb [stock] V:194   → LEAF
```

Stock load neighbourhood (P:129-147) shows the charging framework is fully
assembled before the vendor charge pumps attach:

```
P:129 adapter_class → P:130 charger_class → P:131 mtk_charger_algorithm_class
   → P:132 mt6375-charger → P:133 sh366003_fg → P:134 pd_dbg_info [frozen]
   → P:135 tcpc_class [frozen] → P:136 tcpc_mt6375 [frozen]
   → P:137 mtk_chg_type_det → … → P:143 mtk_charger_framework
   → P:144 rt_pd_manager → P:145 mt6375-battery
   → P:146 sc851x_charger → P:147 sc8571_charger
```

**Root providers:** `charger_class`, `mt6375-charger`, `yft_devinfo`.

**Recommended build order:**
1. keep stock `yft_devinfo` (see §6),
2. re-land the completed `sc851x_charger` reconstruction (zero intermodule
   imports; exact-GKI build and structural parity pass),
3. re-land the completed `sc8571_charger` reconstruction against the proven
   `charger_class` CRC `0x36325d38` (exact-GKI build and bounded static
   ABI/behavioral parity pass),
4. `sh366003_fg` (needs the stock `yft_devinfo` CRCs).

All four are leaves — nothing depends on them, so a mistake cannot cascade.
SC851x and SC8571 are no longer RE tasks, although SC8571 still requires a
stock-compatible `charger_class` provider and neither reconstruction was
activated under the live-power safety boundary. SC851x provides static
converter configuration/debug/IRQ behavior, not charger policy; uSmart VBUS
instead resolves to the MT6375 OTG regulator through `extcon-mtk-usb`.

---

## 3. Cluster: CAMERA POWER

```
   custom_ldo_wl2868 [recon/residual] V:101   will,wl2864c_pmu @ I2C 11-0029
   27 kernel imports · 0 intermodule · 2 exports (export CRCs exact)
            │
            │ 2 symbols (will_ldo_en, will_ldo_vout)
            ▼
   custom_ldo        [recon-exact] V:102   pure shim, stock 10 296 B, 2 functions
   1 kernel import · 2 intermodule · 2 exports (functions/ABI exact)
            │
            │ 2 symbols (custom_ldo_en, custom_ldo_vout)
            ▼
   imgsensor         [port]  V:105
```

Load neighbourhood: `V:101 custom-ldo-wl2868 → V:102 custom-ldo →
V:103 mtk-cam-isp7sp → V:104 imgsensor-glue → V:105 imgsensor`.

This is a strict three-link chain and **the hard gate on cameras**. The
`custom_ldo` shim is now reconstructed completely: both forwarding functions
are byte-identical and its consumer/provider CRCs are exact. The WL2868
hardware provider retains separate documented structural residuals.

**Recommended build order:** `custom_ldo_wl2868` → `custom_ldo` → (`imgsensor`
as part of the platform forward-port programme). Never the other way round.

Note `imgsensor` additionally imports `is_yft_cts_board`, `yft_camera_device_add`
and `yft_set_camera_device_used` from `yft_devinfo` — so the camera cluster has
a second dependency on §6.

---

## 4. Cluster: CONNECTIVITY

```
                          ┌──────────────── connadp [port] V:117
                          │                 connscp [port] V:118
                          │                 ccci_md_all, aee_aed,
                          │                 device-apc-common, mtk_disp_notify [frozen]
                          ▼
        connfem [frozen] ─┴─▶  conninfra [port] V:120        81 exports
                                    │  (root provider of the cluster)
        ┌───────────────┬───────────┼──────────────┬──────────────┐
        │ 21            │ 25        │ 19           │              │
        ▼               ▼           ▼              │              │
 wlan_drv_gen4m_6878  bt_drv_6878  gps_drv_dl_v051 │        fmradio_drv_connac2x
   [port] V:122       [port] V:167  [port] V:129   │            [port]
        ▲                  ▲                       │
        │13                │3 connadp              │
 wmt_chrdev_wifi_connac2   │3 connfem              │
   [port] V:121            │5 bluetooth [port] V:168
   40 kernel · 0 inter     │2 mtk_disp_notify [frozen]
   18 exports              │
        ▲                  │
        │ also: cfg80211 (45, GKI system_dlkm), connadp (6), connfem (3),
        │       mddp (2), mtk_disp_notify (2), aee_aed (1),
        │       pmic_lbat_service (1), ccci_md_all (1)
        │
 connadp [port] ──3──▶ gps_pwr [port]   (on-demand: init.gps_pwr.rc)
 connscp [port] ──5──▶ gps_scp [port]   (on-demand: init.gps_scp.rc)
                        + scp, mtk-mbox [frozen], mtk_rpmsg_mbox [frozen],
                          mtk_tinysys_ipi [frozen]
```

Stock load neighbourhood:

```
V:115 ccci_md_all → V:116 ccci_util_lib → V:117 connadp → V:118 connscp
   → V:119 connfem → V:120 conninfra → V:121 wmt_chrdev_wifi_connac2
   → V:122 wlan_drv_gen4m_6878          …          V:167 bt_drv_6878
   → V:168 bluetooth                    …          V:129 gps_drv_dl_v051
```

**Root providers:** `connadp`, `connscp`, `ccci_md_all`, `aee_aed`,
`device-apc-common`, `connfem` [frozen], `mtk_disp_notify` [frozen],
`cfg80211` (GKI), `bluetooth`, `mddp`, `pmic_lbat_service`.

**Recommended build order (strict):**

```
1. connadp, connscp, ccci_md_all, aee_aed, device-apc-common   (platform prereqs)
2. connfem [already frozen]  +  mtk_disp_notify [already frozen]
3. conninfra                       ← root of the cluster, 81 exports
4. wmt_chrdev_wifi_connac2         ← 18 exports consumed by WLAN
5. wlan_page_pool
6. wlan_drv_gen4m_6878             ← consumes 3, 4, 5
7. bt_drv_6878                     ← consumes conninfra + connfem + bluetooth
8. gps_drv_dl_v051                 ← consumes conninfra
9. gps_pwr (connadp), gps_scp (connscp + SCP/mailbox cluster)
```

Never build 6/7/8 before 3. `conninfra`'s 81 export CRCs are the gate for the
entire cluster.

---

## 5. Cluster: TEE / SECURITY

```
   ffa_v10 [port] P:97 ──2──┐
                            ├──▶ tkcore_drv [stock] P:100 / R:98   → LEAF (0 exports)
   tkcore  [stock] P:99 ─11─┘
      │  25 exports
      ├──1──▶ microarray_fp_tee [stock] P:182 / R:186   (tee_spi_transfer)
      └──7──▶ tmem_ffa          [port]  V:151           (TEEC_*)
                                        depends = gz_tz_system, tkcore, ffa_v10

   userspace (all vendor VINTF-declared):
     keymint@3.0-service.trustkernel · gatekeeper-service.trustkernel
     secureclock / sharedsecret .trustkernel · libwv_trustkernel.so
     /dev/tkcore_{client,admin,fp} · /proc/tkcore · RPMB · /mnt/vendor/persist/t6
```

Stock load neighbourhood: `P:96 clkbuf → P:97 ffa_v10 → P:98 teeperf →
P:99 tkcore → P:100 tkcore_drv` (recovery: 94/95/96/97/98).

**Root provider:** `tkcore` — and it has **zero** intermodule imports, so it
sits directly on the GKI core (101/101 kernel CRCs `MATCH`).

**Recommended build order:** none. This cluster stays on stock through Level B.
If `ffa_v10` is ever rebuilt from platform source, its two consumed export CRCs
must be verified first or `tkcore_drv` will fail to load and the TEE — and
therefore KeyMint/Gatekeeper/FBE — will not come up.

---

## 6. Cluster: YFT DEVICE REGISTRY — the critical provider

```
                       yft_devinfo [stock] V:193 / R:187
                       40 kernel imports · 0 intermodule · 27 exports
                       ┌──────────── 17 export CRCs reproduced from source ✔
                       └──────────── 10 export CRCs GAPPED (all *_device_add) ✘
                                     blocked on one 73-character vendor enum text
       ┌──────────┬──────────┬───────────┬───────────┬──────────┬──────────┐
       │3         │3         │3          │10         │3         │2         │1
       ▼          ▼          ▼           ▼           ▼          ▼          ▼
  focaltech_  hynitron   sh366003_fg  hf_manager  imgsensor  spi_tiny_  aw36518
  ft3680      [stock]    [stock]      [port]      [port]     co5300_lcd [frozen]
  [frozen]                                                   [stock]
       ▲ 3 symbols
       │
  yft_tpd_gesture [frozen] P:183 / R:188   (tpgesture_value/status/hander)

  yft_devinfo ──2──▶ spi_tiny_co5300_lcd ◀──2── hynitron
                     (tiny_tp_gesture_contorl, tiny_tp_power_contorl)
```

**Gapped symbols and who imports them:**

| gapped export | consumer |
|---|---|
| `yft_fuelgauge_device_add` | `sh366003_fg` [stock] |
| `yft_touchpanel_device_add` | `hynitron` [stock] |
| `yft_tinylcd_device_add` | `spi_tiny_co5300_lcd` [stock] |
| `yft_camera_device_add` | `imgsensor` [port] |
| `yft_{acc,m,alsps,sar,baro}sensor_device_add` | `hf_manager` [port] |
| `yft_spitouchpanel_device_add` | `focaltech_touch_spi_ft3680` [frozen] |

**Rule:** pin the **stock** `yft_devinfo.ko` as the provider for Levels A and B,
and link every consumer — reconstructed ones included — against the **stock**
`Module.symvers`. Shipping the reconstructed `yft_devinfo` instead breaks five
stock consumers simultaneously (fuel gauge, rear touch, rear display, camera
sensors, motion sensors).

`yft_devinfo` itself is `YES_SAFE_TRANSITION`: 40/40 kernel import CRCs `MATCH`
and it has no module dependencies of its own.

---

## 7. Cluster: FINGERPRINT

```
   fingerprint [stock] P:181 / R:185
   mediatek,yft_finger · 18 kernel imports · 0 intermodule · 10 exports
        │
        │ 4 symbols: yft_finger_set_irq, yft_finger_set_reset,
        │            yft_finger_set_spi_mode, yft_waite_for_finger_dts_paser
        ▼
   microarray_fp_tee [stock] P:182 / R:186          → LEAF (0 exports)
   mediatek,madev_finger · SPI1 · /dev/madev0
        ▲                    ▲
        │2 spi-mt65xx [port] │1 tkcore [stock]  (tee_spi_transfer)
        │  P:119             │  P:99
```

Load order is adjacent and must be preserved: `P:181 fingerprint →
P:182 microarray_fp_tee`.

**Root providers:** `fingerprint`, `spi-mt65xx`, `tkcore`.

**Recommended build order:** `fingerprint` first (its 10 export CRCs gate the
sensor driver), and only after `tkcore`'s ABI is frozen. `microarray_fp_tee`
stays stock — its behaviour is only observable through the secure world.

---

## 8. Cluster: REAR / SECONDARY DISPLAY

```
   yft_devinfo [stock] ──2──┐
                            ├──▶ spi_tiny_co5300_lcd [stock] V:191   → LEAF
   hynitron    [stock] ──2──┘     hxytech,spi_tiny_lcd @ SPI0
   hynitron,hyn_ts @ I2C 0-0015   /sys/class/misc/tiny_lcd_miscdev
   (on-demand load: init.touch.rc)
        ▲
        │3 yft_devinfo (second_touch_fw_version,
        │               yft_touchpanel_device_add,
        │               yft_set_touch_device_used)
```

Load neighbourhood: `V:190 c2ps_perf_ioctl → V:191 spi_tiny_co5300_lcd →
V:192 leds-ln2403 → V:193 yft_devinfo → V:194 yft_tiny2c_usb` (end of list).

Note `spi_tiny_co5300_lcd` at V:191 loads **before** `yft_devinfo` at V:193 in
the stock list; the registration is therefore late-bound (module_init /
deferred), not load-order dependent. Preserve the list verbatim rather than
"fixing" it.

**Recommended build order:** `yft_devinfo` → `hynitron` → `spi_tiny_co5300_lcd`.
Both consumers stay stock through Level B.

---

## 9. Cluster: LIGHTS / PERIPHERALS

```
   mtk-pwm [port] V:23 ──2──▶ leds_ln2403 [stock] V:192      → LEAF (0 exports)
                              mediatek,yft_camplight
                              sysfs: camplight_mode, leds_ctl,
                                     camplight_set_brightness

   (kernel only) ───────────▶ yft_gpio_keys [stock] P:179 / R:183  → LEAF (0 exports)
                              yft-gpio-keys · F1 (0x3b) / F2 (0x3c)
                              donor: exact-GKI drivers/input/keyboard/gpio_keys.c

   mt6375_charger [port] ──1─▶ yft_tiny2c_usb [stock] V:194    → LEAF (0 exports)
                              mediatek,yft_tiny2c_usb · thermal camera mode

   leds_rgb_aw2013 [frozen] P:178 · aw36515/aw36518/aw36518_v2 [frozen]
```

All four remaining members are **leaves with zero exports** — nothing in the
kernel can depend on them, so they are individually removable and individually
reconstructible in any order with no ABI risk to the rest of the stack.

**Recommended build order:** `yft_gpio_keys` first (in-tree donor, lowest risk),
then `leds_ln2403` and `yft_tiny2c_usb` whenever the corresponding userspace work
happens.

---

## 10. Consolidated build order across all clusters

```
TIER 0  source-built GKI core only; every vendor module stays stock
TIER 1  frozen reconstructions re-landed (no new providers introduced)
TIER 2  yft_devinfo pinned to STOCK; all consumers linked to stock symvers
TIER 3  retain stock mtk_panel_ext → mediatek_drm → panel ABI island;
        panel source waits for exact provider type graph (7 CRCs)
TIER 4  custom_ldo_wl2868 → custom_ldo
TIER 5  re-land completed sc851x_charger; charger_class verified → sc8571_charger → sh366003_fg
TIER 6  connadp/connscp/ccci_md_all/aee_aed/device-apc-common
          → conninfra
          → wmt_chrdev_wifi_connac2 → wlan_page_pool → wlan_drv_gen4m_6878
          → bt_drv_6878
          → gps_drv_dl_v051 → gps_pwr → gps_scp
TIER 7  fingerprint  (after tkcore ABI frozen)
TIER 8  yft_gpio_keys
TIER 9  held on stock indefinitely: tkcore, tkcore_drv, microarray_fp_tee,
        spi_tiny_co5300_lcd, hynitron, leds_ln2403, yft_tiny2c_usb
```

## 11. Leaf modules (zero exports — safe to touch in any order)

`panel_ky_vtdr6115_dphy_cmd`, `sh366003_fg`, `sc851x_charger`, `sc8571_charger`,
`tkcore_drv`, `wlan_drv_gen4m_6878`, `gps_drv_dl_v051`, `gps_pwr`, `gps_scp`,
`microarray_fp_tee`, `spi_tiny_co5300_lcd`, `leds_ln2403`, `yft_gpio_keys`,
`yft_tiny2c_usb`.

## 12. Providers (rebuilding these can break stock consumers)

| provider | exports | consumed by | consumed-symbol count |
|---|---:|---|---:|
| `yft_devinfo` | 27 | 7 modules | 23 |
| `tkcore` | 25 | `tkcore_drv`, `microarray_fp_tee`, `tmem_ffa` | 19 |
| `conninfra` | 81 | `wlan_drv_gen4m_6878`, `bt_drv_6878`, `gps_drv_dl_v051`, `fmradio_drv_connac2x` | 65+ |
| `wmt_chrdev_wifi_connac2` | 18 | `wlan_drv_gen4m_6878` | 13 |
| `fingerprint` | 10 | `microarray_fp_tee` | 4 |
| `custom_ldo` | 2 | `imgsensor` | 2 |
| `custom_ldo_wl2868` | 2 | `custom_ldo` | 2 |
| `hynitron` | 2 | `spi_tiny_co5300_lcd` | 2 |
| `bt_drv_6878` | 1 | (none in the stock set) | 0 |

## Phase 4 custom_ldo_wl2868 update (2026-09-08)

The provider node is structurally reconstructed and its two exports have exact CRC parity with the stock provider. Follow-up `custom_ldo` work proves its voltage argument is a microvolt setpoint, closing that provider residual; probe/data-layout and whole-function/source parity residuals remain.

## Phase 4 custom_ldo update (2026-09-08)

The middle node is complete at `STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION`: 2/2
functions byte-identical, exact KCFI, exact imports/exports/MODVERSIONS and
10/10 relocation parity, with exact-GKI `BUILD_RC=0` and unresolved symbols 0.
It builds naturally against the reconstructed provider's real CRCs and exports
exactly what stock `imgsensor` requires. The graph edge remains, but this node
is no longer an unresolved RE task.

## Phase 4 sc851x_charger update (2026-09-08)

The kernel-only leaf is now reconstructed from a no-public-source stock oracle.
All 11 function sizes/KCFI IDs, data, strings, 30 MODVERSION records and
relocation target/type sequences match; exact-GKI `BUILD_RC=0`, warnings 0,
unresolved 0. The board is SC8510 at `6-0069` (`@6f` is only a stale node
suffix). Its graph remains kernel-only: no intermodule import/export edge and
no charger-class, regulator, extcon or USB edge. uSmart's VBUS/control graph is
`MT6375 OTG → extcon-mtk-usb → USB1/UVC GPIOs`, explicitly excluding SC851x.
