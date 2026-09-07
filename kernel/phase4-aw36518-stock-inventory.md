# GQ5012BF1 — `aw36518.ko` stock ELF inventory (Phase 0/1)

Oracle module (read-only, never modified):

```
workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/aw36518.ko
size      43128 bytes
SHA-256   7dcf64a7d25c657d1a0795cc89ad519c954561c6c757949c247d623f16976247
build-id  da6b5af2f8a1168d78b60ddb13e22aa1b1da70ac
ELF       ET_REL, EM_AARCH64, 43 sections
compiler  Android (11349228, based on r487747c) clang 17.0.2
```

`aw36518.ko` exists exactly once in the stock image (`vendor_dlkm` only); the
whole-image module scan covers 471 module paths / 458 unique module hashes.
Sibling modules `aw36518_v2.ko` (43168 B, SHA-256 `c7faa3ba…1458e`) and
`aw36515.ko` (34768 B, SHA-256 `85e5a860…f643e8`) are separate modules, not
copies — see `phase4-aw36518-family-comparison.md`.

`modules.load` order: `… mtk-composite.ko, aw36515.ko, aw36518.ko,
aw36518_v2.ko, flashlight.ko …`.

`modules.dep`:

```
aw36518.ko: yft_devinfo.ko flashlight.ko mtk_peak_power_budget.ko mtk_pbm.ko
            mtk_mdpm.ko mtk_dynamic_loading_throttling.ko mtk_low_battery_throttling.ko
```

(The last five are transitive through `flashlight.ko`; `aw36518.ko` itself
imports only from `yft_devinfo` and `flashlight`, see the provider boundary.)

## modinfo

```
author       Alec <like@awinic.com>
description  Awinic AW36518 LED flash driver
license      GPL
vermagic     6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64
name         aw36518
depends      yft_devinfo,flashlight
alias        i2c:aw36518
alias        of:N*T*Cmediatek,aw36518
alias        of:N*T*Cmediatek,aw36518C*
parameters   (none)
srcversion   (absent — module built without MODULE_SRCVERSION)
```

## Symbol / section totals

| Item | Count |
|---|---|
| FUNC symbols (`.text` + `.init.text` + `.exit.text`) | 23 |
| Global functions | 2 (`init_module`, `cleanup_module`) |
| OBJECT symbols | 32 |
| Imports (undefined symbols) | 46 |
| Exports | 0 |
| `__versions` records | 47 (46 imports + `module_layout`) |
| KCFI type-id prefixes present | 20 of 23 functions |

Full tables: `phase4-aw36518-functions.tsv`, `phase4-aw36518-objects.tsv`,
`phase4-aw36518-imports.tsv`, `phase4-aw36518-modversions.tsv`.

## Function map (`.text` unless noted)

| Function | off | size | KCFI id |
|---|---|---|---|
| `aw36518_probe` | 0x0004 | 1588 | 0x5ef138aa |
| `aw36518_remove` | 0x063c | 88 | 0x8effdd6d |
| `aw36518_parse_dt` | 0x0694 | 364 | — (direct-call only) |
| `aw36518_open` | 0x0804 | 160 | 0x59c4d434 |
| `aw36518_close` | 0x08a8 | 40 | 0x59c4d434 |
| `aw36518_led0_get_ctrl` | 0x08d4 | 208 | 0x94281efb |
| `aw36518_led0_set_ctrl` | 0x09a8 | 1236 | 0x94281efb |
| `aw36518_torch_brt_ctrl` | 0x0e7c | 284 | — |
| `aw36518_flash_open` | 0x0f9c | 8 | 0x36b1c5a6 |
| `aw36518_flash_release` | 0x0fa8 | 8 | 0x36b1c5a6 |
| `aw36518_ioctl` | 0x0fb4 | 680 | 0x44a5bdc2 |
| `aw36518_strobe_store` | 0x1260 | 604 | 0x55f4a884 |
| `aw36518_set_driver` | 0x14c0 | 184 | 0x00050794 |
| `aw36518_init` | 0x1578 | 380 | — |
| `reg_show` | 0x16f8 | 212 | 0xdf43c25c |
| `reg_store` | 0x17d0 | 144 | 0x95a8ba07 |
| `aw36518_cooling_get_max_state` | 0x1864 | 20 | 0xc8202036 |
| `aw36518_cooling_get_cur_state` | 0x187c | 20 | 0xc8202036 |
| `aw36518_cooling_set_cur_state` | 0x1894 | 348 | 0x8b35064f |
| `aw36518_suspend` | 0x19f4 | 112 | 0x3f45655f |
| `aw36518_resume` | 0x1a68 | 72 | 0x3f45655f |
| `init_module` (`.init.text`) | 0x0004 | 44 | 0x36b1c5a6 |
| `cleanup_module` (`.exit.text`) | 0x0004 | 36 | 0xa540670c |

Functions present in the source but fully inlined by the vendor build (proved by
their `__func__` strings and by the call/mask sequences at the inline sites):
`aw36518_gpio_init`, `aw36518_gpio_set`, `aw36518_mode_ctrl`,
`aw36518_enable_ctrl`, `aw36518_flash_brt_ctrl`, `aw36518_flash_tout_ctrl`,
`aw36518_get_ctrl`, `aw36518_set_ctrl`, `aw36518_subdev_init`,
`aw36518_init_controls`, `aw36518_v4l2_i2c_subdev_init`, `aw36518_uninit`.

## Static data

| Object | Section | Size | Meaning |
|---|---|---|---|
| `aw36518_i2c_driver` | `.data` 0x000 | 280 | `.probe`, `.remove`, `.id_table`, `.driver.name="aw36518"`, `.driver.pm`, `.driver.of_match_table`; **no `.shutdown`** |
| `aw36518_cooling_ops` | `.data` 0x118 | 56 | `thermal_cooling_device_ops` (get_max/get_cur/set_cur) |
| `aw36518_flash_ops` | `.data` 0x150 | 40 | MediaTek `flashlight_operations` (open, release, ioctl, strobe_store, set_driver) |
| `dev_attr_reg` | `.data` 0x178 | 32 | sysfs `reg` attribute, mode 0644, `reg_show`/`reg_store` |
| `aw36518_id_table` | `.rodata` 0x008 | 64 | `{"aw36518", 0}, {}` |
| `aw36518_of_table` | `.rodata` 0x048 | 400 | `{ .compatible = "mediatek,aw36518" }, {}` |
| `aw36518_pm_ops` | `.rodata` 0x1d8 | 192 | `SET_SYSTEM_SLEEP_PM_OPS(pm_runtime_force_suspend/resume)` + `SET_RUNTIME_PM_OPS(aw36518_suspend, aw36518_resume, NULL)` |
| `aw36518_regmap` | `.rodata` 0x298 | 328 | `reg_bits=8, val_bits=8, max_register=0xFF` |
| `aw36518_ops` | `.rodata` 0x3e0 | 64 | `v4l2_subdev_ops` (all NULL) |
| `aw36518_int_ops` | `.rodata` 0x420 | 40 | `v4l2_subdev_internal_ops` (`open`, `close`) |
| `aw36518_led_ctrl_ops` | `.rodata` 0x448 | 32 | `v4l2_ctrl_ops` (`g_volatile_ctrl`, `s_ctrl`) |
| mode table | `.rodata` 0x468 | 12 | `{0x00, 0x0c, 0x08}` indexed by `enum v4l2_flash_led_mode` |
| `flash_state_to_current_limit` | `.rodata.cst16` | 16 | `{150000, 100000, 50000, 25000}` (µA, see electrical contract) |
| `aw36518_flash_data` | `.bss` 0x08 | 8 | single global device pointer |
| `use_count` | `.bss` 0x10 | 4 | `flashlight_set_driver()` reference count |
| `aw36518_probe.__key` | `.bss` 0x00 | 1 | lockdep key for `&flash->lock` |

## Log-string ABI

The stock module has no `pr_fmt()` override.  Most call sites use a vendor
logging macro that expands to `printk(KERN_ERR "aw36518[%s] " fmt, __func__, …)`;
a small set of call sites use plain `pr_info()`/`printk()` (recovered strings:
`"snprintf failed\n"`, `"set thermal current:%lu\n"`,
`"thermal limit current:%d\n"` (torch path only),
`"%s:%d: do software reset0 reg0x07=0x%02x\n"`,
`"%s:%d: do software reset1 write data:0x%02x to reg 0x07\n"`).
The version string `"V1.0.0"` is printed once from `probe`.
The reconstruction reproduces all 63 stock strings exactly.

## Artifacts

Raw inventory (workspace, not committed — `workspace/` is gitignored):
`workspace/phase4-aw36518/stock-{sections,functions,objects,imports,exports,modversions,relocations}.tsv`,
`stock-disasm.txt`, `stock-strings.txt`, `stock-modinfo.txt`, section blobs, and
the extractor `tools-extract.py`.  The committed copies of the ABI-relevant
tables are the `kernel/phase4-aw36518-*.tsv` files.
