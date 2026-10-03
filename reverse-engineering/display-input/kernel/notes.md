# Display kernel scope — first two modules closed

Build environment is the same as the NFC closure: GKI
`6.1.115-android14-11-g945dff7bc1bf`, clang r487747c, KDM tree
`kernel_device_modules-6.1` (baseline commit `0579490`, "NothingOSS
device_modules 957dac1 pristine").

## Which source variant ships

`mtk_disp_notify.c` exists twice in the KDM tree (`dummy_drm/` and
`mediatek_v2/`). The shipped module exports **six** symbols
(`mtk_disp_notifier_{register,unregister,call_chain}` **and**
`mtk_disp_sub_notifier_{register,unregister,call_chain}`) — the `dummy_drm`
variant only has the first three. **PROVEN: the device ships the
`mediatek_v2` variant.** The earlier `dummy_drm` build failure
(`mtk_panel_ext.o` errors in that directory) was therefore a dead end, not a
blocker.

## Isolated-module build technique

Both modules are standalone objects inside directories whose other objects do
not build in this configuration. Instead of fixing the whole directory, each
module is built from a scratch `M=` directory containing only the one source
plus a 3–7 line Kbuild that re-adds the include paths it needs
(`reconstruction/*/Kbuild.isolated`). `depends=` in the shipped modinfo
confirms this is how they were built upstream too (both are `depends=`-empty
single-object modules).

## `mtk_disp_notify.ko` — EXACT

A = stock vendor-ramdisk module, sha256
`28fb6a324e432547b98f618d7981a4940dc3e5bf9b319b0181b339d3e8bd062b`.
B = isolated rebuild of unmodified `mediatek_v2/mtk_disp_notify.c`.

| axis | result |
|---|---|
| functions | **6/6 byte-identical** |
| data objects | **11/11 byte-identical** |
| imports | **5/5** names + modversion CRCs |
| exports | 1/1 (all six `__ksymtab_gpl` entries in one group) |
| `.modinfo` | identical (`author=Freya Li`, `description=mtk disp notify`, `license=GPL v2`, `vermagic`, `depends=` empty) |
| RELA | 56/56 entries structurally identical, all addends normalise equal |
| residual | DWARF sections only (`.debug_*`, `.rela.debug_*`) and the resulting `.symtab`/`.strtab`/`.shstrtab` size change |

**Zero source deltas** — the donor file is the shipped file. This closes the
`MTK-DISP-NOTIFY` component: it was PARTIAL exactly for "complete stock parity".

Role: `BLOCKING_NOTIFIER_HEAD` pair (`disp_notifier_list`,
`disp_sub_notifier_list`) that the panel path calls and that
`focaltech_touch_spi_ft3680` and the sensorhub register against for
screen-on/off events. The only log string is `"[DISP][%s line:%d]:%s"`
(`DDPFUNC` in `mtk_log.h`).

## `mtk_panel_ext.ko` — one instruction field short of exact

A = stock, sha256
`b5cd837c26e7d356ee5b35b7a030e269e8f6120db2c478e7530e2e9d35473c20`.
B = isolated rebuild of `mediatek_v2/mtk_panel_ext.c` **minus the donor's
fingerprint/HBM block**.

| axis | result |
|---|---|
| functions | 12/12 present, 12/12 size-identical, **12/12 byte-identical** |
| data objects | **13/13 byte-identical** |
| imports | **6/6** names + modversion CRCs |
| exports | 1/1, 9 exported symbols |
| `.modinfo` | identical |
| RELA | 112/112 entries structurally identical, addends normalise equal |

### Delta 1 (recovered, source-level)

The donor carries a Nothing-specific block at the top of the file — statics
`g_lcm_hbm_status` / `g_lcm_ui_status` and four exported functions
`mtk_panel_update_lcm_state_to_fingerprint`, `mtk_panel_proc_hbm`,
`mtk_panel_get_ui_status`, `mtk_panel_proc_ui_status` which push
`FP_NOTIFIER_EVENT_UI` into the disp notifier chain for an under-display
fingerprint sensor. **The GQ5012BF1 module does not contain any of it**: those
four functions, the two statics, the two function-local `static` counters, the
extra `.rodata.str1.1` (273 bytes of `printk` text) and the
`mtk_disp_notifier_call_chain` import are all absent from stock. Removing the
block (`reconstruction/mtk_panel_ext/donor-to-stock.diff`, 50 lines) takes the
module from 11/16-vs-12 with 4 surplus functions to an exact function/data/
import/export match. This is consistent with the device having a side-mounted
capacitive fingerprint reader, not an under-display one.

### Delta 2 — RESOLVED (header layout)

The two surplus donor members are **`set_backlight_pack`** (donor offset 24)
and **`hbm_set_pack`** (donor offset 224), both `dcs_write_gce_pack` variants.
Removing them makes `get_lcm_version` land at `0xf8` and the rebuild reaches
**12/12 byte-identical functions**, 13/13 data, 6/6 import CRCs, identical
`.modinfo`.

The proof came from naming evidence that was not used before: stock
`mediatek-drm-panel-drv.ko`'s 320-byte `mtk_drm_panel_ext_funcs` object fills
30 slots with handlers named after the member they implement
(`mtk_panel_set_bl_elvss_cmdq` @0, `mtk_panel_set_aod_light_mode` @32,
`mtk_panel_reset` @48, `mtk_panel_hbm_set_cmdq` @208,
`mtk_panel_get_lcm_version` @248, `mtk_panel_read_panelid` @288 …), and stock
`panel-ky-vtdr6115-dphy-cmd.ko`'s `ext_funcs` fills two more
(`mtk_get_res_switch_type` @80, `mtk_scaling_mode_mapping` @88). Aligning the
two layouts member-by-member leaves exactly those two donor entries unmatched.
See `../reconstruction/mtk_panel_ext/header-donor-to-stock.diff` and
`../yft-vtdr6115-deltas.md` §9.

### Historical statement of the bound (superseded)

`mtk_panel_ext_create` is the single remaining differing function, same size
(284 B), and the difference is **one instruction field**:

```
stock    f9407e68   ldr x8, [x19, #0xf8]     ; ext_funcs->get_lcm_version
rebuild  f9408668   ldr x8, [x19, #0x108]
```

i.e. the donor's `struct mtk_panel_funcs` is **16 bytes (2 function pointers)
larger ahead of `get_lcm_version`** than the one the stock module was compiled
against. Independent evidence pins the shape of that delta:

- `pahole` on the rebuild: donor `struct mtk_panel_funcs` = **336 bytes**, 42
  members, `get_lcm_version` at 264.
- stock `mediatek-drm-panel-drv.ko` object `mtk_drm_panel_ext_funcs` is
  **320 bytes** → the stock struct has exactly 40 members; its populated slots
  are `0,16,32,40,48,56,64,72,96,112,120,128,136,144,160..248,264..288`
  (gaps at 8, 24, 80, 88, 104, 152, 256).
- stock `panel-ky-vtdr6115-dphy-cmd.ko` object `ext_funcs` relocates
  `mtk_get_res_switch_type` at **offset 80** and `mtk_scaling_mode_mapping` at
  **offset 88**; in the donor header those members sit at 88 and 96.

Therefore: **exactly one surplus member lies at donor offset ≤ 80, and exactly
one more between 88 and 264** (both are removed in the stock header, giving
`get_lcm_version` at 248 = 0xf8). Which two members they are is *not*
determined by this evidence — any such pair reproduces the same binary. This
is a cosmetic header-layout question only: the rebuilt code is otherwise
identical, and the correct `0xf8` can be produced by deleting any two
qualifying members. Resolving it properly needs either a second MTK 6.1 panel
header from a different vendor tree or the stock `mediatek-drm.ko` call-site
offsets (5.7 MB module, not analysed yet).

Verdict: `mtk_panel_ext` is **byte-exact** (12/12 functions, 13/13 data,
6/6 import CRCs, identical `.modinfo`). Residual: DWARF only.
