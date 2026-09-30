# `aw36518.ko` ↔ `aw36518_v2.ko` ↔ `aw36515.ko`: measured structural delta

Parent of the thermal-HAL reconstruction work
(`workspace/phase4-aw36518/`, whose Phase 15 asks for exactly this: evidence that
makes the sibling modules cheaper to reconstruct). Every number below is
**measured from the three frozen stock modules** — no upstream source is involved,
so nothing here depends on a vendor-source guess.

Tool: [`tools/ko-family-delta.py`](../tools/ko-family-delta.py). `--self-test`
asserts the invariants quoted on this page against the frozen modules. Inputs are
the Phase-0-frozen modules in
`workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/`.

## How the comparison is graded

Two modules are compared per function at four widening levels, so "it differs"
always says *how much* it differs:

| tier | canonicalised before comparing |
|---|---|
| `verbatim` | nothing — byte-exact identical instruction stream |
| `modulo_module_name` | the module name (`aw36518_v2_probe` → `@probe`) |
| `modulo_anchor_offsets` | + the `<nearest-symbol+off>` annotation objdump/llvm-objdump attach to `adrp`/`add` data references in an **unlinked** object (it moves whenever earlier code changes size) |
| `modulo_immediates` | + every literal `#0x…` operand |

What is left over is a genuine structural difference and is printed with its
instruction-level diff under `--verbose`.

## `aw36518` vs `aw36518_v2` — one functional difference, and it is named

```
functions: shared=29 verbatim-identical=12 +name=6 +anchors=7 +immediates=3
size diffs: parse_dt 364->296
imports: 46 vs 45; first-only=['is_yft_cts_board'] second-only=[]
calls parse_dt: [9, 8] first-only=['is_yft_cts_board']
```

| dimension | measurement |
|---|---|
| function set | **identical** (no v1-only, no v2-only symbol) |
| functions | 12 verbatim + 6 modulo-name + 7 modulo-anchor + 3 modulo-immediate = **28 of 29 explained**; `parse_dt` is the **only** structurally differing function (`--self-test` asserts exactly that) |
| function sizes | identical except `parse_dt` **364 → 296 B** |
| `.text` total | 6832 → 6764 B = **−68 B, exactly the `parse_dt` delta**: no other code moved |
| `.data` (408 B) | **byte-identical** |
| `.init_data`, `.exit_data`, `.rodata.cst16`, `.altinstructions`, `.comment`, `.shstrtab` | byte-identical |
| `.rodata` (1140 B) | **6 differing bytes, all inside the module-name field** (`0xf-0x11`, `0x98-0x9a`) |
| `.gnu.linkonce.this_module` (1088 B) | 3 differing bytes — the same `_v2` insertion |
| string pool | after name canonicalisation the multisets are **equal**; raw bytes 5821 → 6030 only because the longer name is embedded ~70 times (symtab/strtab/kstrtab/`____versions`/modinfo) |
| undefined symbols | v1 **46**, v2 **45**; the difference is exactly **`is_yft_cts_board`** |
| `modinfo depends` | v1 `yft_devinfo,flashlight` → v2 `flashlight` |
| `vermagic` | identical: `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |

The `parse_dt` delta itself, read off the instruction diff:

* v1's call multiset is v2's **plus exactly one target** —
  `R_AARCH64_CALL26 → is_yft_cts_board` inside `aw36518_parse_dt`. Every other call
  target matches 1:1 module-wide (166 vs 165 CALL26 relocations; the surplus is
  that one).
* v1 keeps a larger callee-saved set (frame `0x60`, `stp x28,x27` prologue) vs
  v2's `0x40` — 68 bytes of extra register saves around the extra branch.
* what both do is identical: walk children with `of_get_next_child`, read four
  arrays via `of_property_read_variable_u32_array` at struct offsets `+0x298`,
  `+0x29c`, `+0x2a0`, `+0x2a4` (plus one `snprintf` target at `+0x1e8`), then
  register through `flashlight_dev_register_by_device_id`.

`probe`, `suspend`, `resume` land in the `modulo_immediates` tier: their operands
move because the `_v2` name is 3 characters longer (`mov w2, #0xd` → `#0x10`;
`printk` format-string offsets `0x3a4→0x3a2`, `0x3da→0x3d8`, `0x3df→0x3dc`,
`0x3e1→0x3de`, `0x3ff→0x3fc`, `0x409→0x406`). Nothing behavioural.

### Classification (Phase 15 taxonomy)

`aw36518_v2.ko` is **the same source with a config difference** — not a newer
revision, not an independent driver: identical function set, identical sizes
except one function, identical `.data`, `.rodata` differing only by the module
name, exactly one removed vendor call (`yft_devinfo` CTS-board check in
`parse_dt`).

Consequence: **the AW36518 v1 reconstruction covers both modules up to that one
branch.** `aw36518_v2.ko` needs no second reconstruction — it is the v1 source
minus the `is_yft_cts_board()` branch and minus the `yft_devinfo` dependency (a
`CONFIG_YFT_DEVINFO`-style ifdef in vendor terms; to be confirmed by actually
building v2). That is the fastest available path for that Phase-15 sibling.

## `aw36518` vs `aw36515`: same family, different topology

```
functions: shared=25 verbatim-identical=10 +name=3 +anchors=2 +immediates=2
only in first:  ['init', 'parse_dt', 'resume', 'suspend']
only in second: ['led1_get_ctrl', 'led1_set_ctrl', 'set_ctrl', 'subdev_init']
imports: 46 vs 46; first-only=['is_yft_cts_board','pm_runtime_force_resume','pm_runtime_force_suspend']
                                   second-only=['flashlight_pt_is_low','fortify_panic','strnlen']
```

| dimension | measurement |
|---|---|
| sizes differing | `led0_set_ctrl` 1236→32 B, `probe` 1588→1032, `strobe_store` 604→368, `set_driver` 184→360, `ioctl` 680→436, `torch_brt_ctrl` 284→244, `cooling_set_cur_state` 348→372, `remove` 88→104 |
| `.data` (408 B) | **byte-identical to `aw36518_v2.ko`** — the writable tables are shared family-wide |
| `.rodata` / `.text` | 1140 vs 988 B / 6832 vs 5948 B |
| strings | after name canonicalisation the filtered pools show **no unique log/format strings on either side**; aw36515 only adds `flashlight_pt_is_low`, `strnlen`, `fortify_panic` as imports |
| call targets | aw36515 funnels LED setting into one `set_ctrl` helper (23 call sites) used by `led0_set_ctrl`/`led1_get_ctrl`/`strobe_store`/`torch_brt_ctrl`/`ioctl`, and moves DT parsing + V4L2 setup into `subdev_init` (23 sites: `v4l2_subdev_init`, `v4l2_async_register_subdev`, `v4l2_ctrl_handler_init_class`, `v4l2_ctrl_new_std{,_menu}`, `media_entity_pads_init`, `of_get_child_by_name`, `of_find_node_by_name`, `strscpy`, `strnlen`, `fortify_panic`) |

Classification: **same driver family, alternate chip/topology.** The
`led1_get_ctrl`/`led1_set_ctrl` pair plus a shared `set_ctrl` helper and a real
`subdev_init` say aw36515 is the **two-channel (torch + flash) variant that
registers its own V4L2 subdev**, while AW36518 in this build exposes only
`led0_*` and parses DT through `parse_dt`. It has **no `parse_dt`, `init`,
`suspend` or `resume` at all** — its PM path is structured differently (no
`pm_runtime_force_{suspend,resume}` users), so it needs its own reconstruction
pass. What carries over from AW36518 is the `.data` table layout, the `flashlight`
framework interface (`flashlight_dev_register_by_device_id`,
`flashlight_kicker_pbm`, plus aw36515's extra `flashlight_pt_is_low`) and the
register-access idiom (`regmap_read`/`regmap_update_bits_base` + raw GPIO through
`gpio_to_desc`/`gpiod_set_raw_value`).

## Thermal-relevance caveat (unchanged)

All three modules remain **not loadable** (`depends=flashlight`, `aw36518`
additionally `yft_devinfo`; neither `flashlight.ko` nor `yft_devinfo.ko` exists
anywhere in the package), and `is_yft_cts_board` — the *only* functional v1↔v2
delta — gates a board-classification branch at probe time, not a runtime thermal
path. None of the three is the camera thermal sensor path; that surface is covered
in [`vdm-opcode-recovery.md`](vdm-opcode-recovery.md).

## Reproduce

```sh
cd "…/ulefone-gq5012bf1-research/qwen_hardware/qwen-thermal"
python3 tools/ko-family-delta.py              # the tables above
python3 tools/ko-family-delta.py --verbose    # instruction-level diffs
python3 tools/ko-family-delta.py --json       # machine-readable
python3 tools/ko-family-delta.py --self-test  # asserts the invariants quoted above
```

`-v` is the short form of `--verbose`; `--all-sections` additionally byte-compares
`.symtab`/`.rela*`/`____versions`;
positional paths or `--modules-dir` point it at another module set (e.g. the
rebuilt candidate in `../../workspace/phase4-aw36518/rebuilt/`) — which is how the
reconstruction parity loop should be re-run after any source change.
