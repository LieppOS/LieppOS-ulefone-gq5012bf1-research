# Phase 8 / 9 — RED baseline and the complete v1.6.0 → v1.7.1 delta ledger

## RED: the untouched donor, built against exact GKI 12901745

```
target : //lieppos/aw883xx-recon/donor-build:aw883xx_driver_donor
source : github.com/awinic-driver/aw883xx @ 4f52a10, copied verbatim
kernel : //common:kernel_aarch64  (GKI ab/12901745, 6.1.115-android14-11-g6b18f0b574ab)
result : BUILD_RC 0
```

The only modpost warnings in the RED build were three unresolved symbols —
`filp_open`, `kernel_read`, `kernel_write` — all coming from the donor's
`AW_CALI_STORE_EXAMPLE` block, which the stock module does not contain.

### RED result (untouched donor vs stock oracle)

| metric | stock | RED donor | delta |
|---|---|---|---|
| defined `.text` functions | 236 | 244 | +8 |
| imported symbols | 73 | 80 | +7 |
| `__versions` records | 74 | 81 | +7 |
| exported symbols | 2 | 0 | −2 |
| `.rodata.str1.1` strings | 991 | 1000 | +9 real |
| functions differing in relocation/call/string sequence | — | 16 / 236 shared | — |
| `sizeof(struct aw_device)` | `0x750` | `0x748` | +8 |

Raw evidence: `RED-raw-donor-vs-stock.txt`, `RED-function-sequence-diff.txt`.

Because the delta was small and fully enumerable, the reconstruction is a
**delta reconstruction**, not a rewrite. Every change below is justified by an
artifact in the stock binary; nothing was changed "to make it build" or on a
hunch.

---

## Delta ledger

Each entry: what changed, the exact evidence, and the source edit.

### D1 — driver version string

* **Evidence.** `drv_ver_show()` prints `AW883XX_DRIVER_VERSION`. The stock
  `.rodata.str1.1` contains `v1.7.1`; it does not contain `v1.6.0`.
* **Change.** `aw883xx.c:48` `#define AW883XX_DRIVER_VERSION "v1.7.1"`.

### D2 — `AW_CALI_STORE_EXAMPLE` is not enabled

* **Evidence.**
  * stock imports/`__versions` contain no `filp_open`, `filp_close`,
    `kernel_read`, `kernel_write` or `skip_spaces` (the RED build had all five);
  * no `/mnt/vendor/persist/factory/audio/aw_cali.bin` string;
  * no `aw_cali_write_re_to_nvram` symbol;
  * strings `channel:%d open %s failed`, `write re to nvram failed!`,
    `channel:%d buf:%s cali_re:%d`, `channel:%d buf:%s int_cali_re: %d`,
    `write re failed`, `%10d` are all RED-only.
* **Change.** `aw883xx_calib.h`: the `#define AW_CALI_STORE_EXAMPLE` is removed
  (the commented-out form from upstream is kept, with a comment explaining why).
* **Consequence.** Kernel-side calibration is volatile. Persistence is owned by
  MTK NVRAM in userspace — see `calibration-contract.md`.

### D3 — `g_cali_re_time` default is 1000 ms, not 3000 ms

* **Evidence.** `.data+0x1e8` (`g_cali_re_time`) initialiser is `0x000003e8`
  (1000) in the stock module and `0x00000bb8` (3000) in the RED build. With this
  one word fixed, the non-relocated bytes of `.data` become **identical**.
* **Change.** `aw883xx_calib.h`: `AW_CALI_RE_DEFAULT_TIMER (1000)`.
* **Consequence.** A Re calibration run dwells 1000 ms (scaled by
  `AW_CALI_DELAY_CACL`) before sampling, not 3000 ms.

### D4 — `struct aw_sysst_desc` loses `st_sws_check`

* **Evidence.**
  * `offsetof(aw_device, profctrl_desc)` is `0xe8` in stock vs `0xec` in the RED
    build (anchored on the `{reg=0x04, mask=0xffffff7f}` pair written by
    `aw883xx_pid_2049_dev_init`, and `rcv_mode_val=0x80` at `+0xf0`/`+0xf4`);
  * stock `aw883xx_pid_2066_dev_init` / `aw883xx_pid_2183_dev_init` write
    **`0x311`** into `sysst_desc.st_check` (`aw_device+0xd4`) and write nothing
    at `aw_device+0xe8`; the RED build writes `0x211` at `+0xd4` and `0x311` at
    `+0xe8`. `0x311` is `*_BIT_SYSST_SWS_CHECK`, `0x211` is
    `*_BIT_SYSST_NOSWS_CHECK`.
* **Change.** Field removed from `struct aw_sysst_desc`; PID 2066/2183 init now
  assign `st_check = *_BIT_SYSST_SWS_CHECK`.

### D5 — `struct aw_noise_gate_en` becomes a 2-entry SYSST gate table

* **Evidence.** Stock `aw883xx_device_start` (with `aw_dev_sysst_check` inlined),
  offsets `0x5d30`–`0x5dc8`:

  ```
  5d30  ldr  w20, [x19, #0xd4]      ; check_value = sysst_desc.st_check
  5d34  cmp  w1,  #0xff             ; w1 = [x19,#0x318]
  5d38  b.eq 5d7c
  5d3c  ...  ops.aw_reg_read(aw_dev, [0x318], &reg_val)
  5d68  ldr  w9,  [x19, #0x31c]
  5d6c  bics wzr, w8, w9            ; reg_val & ~mask
  5d70  b.eq 5d7c
  5d74  ldr  w8,  [x19, #0x320]
  5d78  and  w20, w8, w20           ; check_value &= [0x320]
  5d7c  ldr  w1,  [x19, #0x324]     ; second entry, identical shape
  ...   [0x328] mask, [0x32c] and-mask
  5dc8  <SYSST poll loop, 10 tries, usleep_range(0x7d0,0x7da)>
  ```

  and the corresponding RED code, which instead does
  `csel x21, (aw_device+0xe8 = st_sws_check), (aw_device+0xd4 = st_check)`.

  Init tables (all from stock `*_dev_init`, which are byte-identical in the
  final build):

  | PID | gate[0] | gate[1] |
  |---|---|---|
  | 2049 | `{0xff, -, -}` | `{0xff, -, -}` |
  | 2066 | `{0x16 PWMCTRL3, 0xffffdfff NOISE_GATE_EN_MASK, 0xfffffeff}` | `{0xff, -, -}` |
  | 2183 | `{0x16 PWMCTRL3, 0xffffdfff NOISE_GATE_EN_MASK, 0xfffffeff}` | `{0x69 BSTCTRL10, 0xfffffffb (bit 2), 0xfffffdff}` |

  `0xfffffeff == ~(1<<8) == ~*_SWS_SWITCHING_VALUE` (`*_SWS_START_BIT` = 8) and
  `0xfffffdff == ~(1<<9) == ~*_BSTS_FINISHED_VALUE` (`*_BSTS_START_BIT` = 9),
  both taken from the donor's own register headers.
* **Change.**
  ```c
  struct aw_sysst_gate { unsigned int reg, noise_gate_mask, st_and_mask; };
  #define AW_SYSST_GATE_NUM (2)
  struct aw_noise_gate_en { struct aw_sysst_gate gate[AW_SYSST_GATE_NUM]; };
  ```
  and in `aw_dev_sysst_check()`:
  ```c
  check_value = desc->st_check;
  for (i = 0; i < AW_SYSST_GATE_NUM; i++) {
      if (gate[i].reg == AW_REG_NONE) continue;
      ops.aw_reg_read(aw_dev, gate[i].reg, &reg_val);
      if (reg_val & ~gate[i].noise_gate_mask)
          check_value &= gate[i].st_and_mask;
  }
  ```
  For PID 2066 this is *behaviourally identical* to the old
  `st_check`/`st_sws_check` pair. For PID 2183 it adds a second, genuinely new
  condition. For PID 2049 — the part fitted on GQ5012BF1 — both entries are
  `AW_REG_NONE`, so the loop is inert.
* **Naming honesty.** Bit 2 of register `0x69` (`BSTCTRL10`) has no name in any
  published Awinic header. It is carried by address as
  `AW_PID_2183_REG_0X69_BIT2_MASK`. Its *meaning* is not claimed; only its
  numeric effect (drop the boost-finished requirement from the SYSST check) is
  asserted, and that is directly readable from the disassembly.

D4 + D5 together account for exactly the `+8` growth of `struct aw_device`
(`0x748 → 0x750`) and the `+12` shift of `cali_desc` (`0x384 → 0x390`, verified
independently by the `sub x0, x0, #0x390` container_of in
`aw883xx_cali_get_ra` / `aw883xx_cali_set_cali_re`), `monitor_desc`
(`0x460 → 0x468`, verified by `add x23, x20, #0x468` in the ACF monitor-section
parse) and `ops` (`0x660 → 0x668`).

### D6 — `aw_dev_sysint_check()` is gone

* **Evidence.** Stock has no `aw_dev_sysint_check` symbol; `aw883xx_device_stop`
  never references `get int status fail ret:%d` or `int check fail:0x%04x`, and
  the only stock callers of `aw_dev_get_int_status` are `aw883xx_device_params`
  and `aw_dev_clear_int_status`. The stock `aw883xx_device_stop` reloc sequence
  runs `aw_dev_set_intmask → aw_dev_dsp_enable` with nothing in between.
* **Change.** Function deleted; `aw883xx_device_stop` now evaluates only
  `monitor_int_st = aw_dev_get_monitor_sysint_st(aw_dev)` and enters the
  DSP-recovery block on `monitor_int_st < 0` alone.
* **Consequence.** On power-down the driver no longer probes SYSINT directly;
  it relies on the interrupt state latched by the monitor path.

### D7 — ACF v1.0.0.0 dev/default parsers merged into `aw_dev_parse_scene_v_1_0_0_0`

* **Evidence.**
  * stock strings contain `aw_dev_parse_scene_v_1_0_0_0` and
    `no valid device scenario resolved`, and contain **no** reference from
    `aw_dev_parse_by_hdr_v_1_0_0_0` to `get dev type failed, get num [%d]`;
  * `aw_dev_parse_dev_type_v_1_0_0_0` and `aw_dev_parse_default_type_v_1_0_0_0`
    do not exist in stock;
  * stock `aw883xx_dev_cfg_load` at `0x21ec` reads `prof_info.prof_type`
    (`aw_device+0x74`), branches `cbz → w21=1` / `cmp #2 → w21=0` /
    `b.ne → "prof type matched failed, get num[%d]"`, i.e. **one** call site with
    a boolean selector;
  * the loop at `0x241c` gates the bus/addr comparison on `tbz w21,#0`
    (`adapter->nr` vs dde+0x16, `i2c->addr` vs dde+0x18) and otherwise compares
    `aw_dev->channel` (`+0x1c`) against dde+0x14, then always compares
    `aw_dev->chip_id` (`+0x14`) against dde+0x4c;
  * matching indices are **insertion-sorted ascending by `dev_profile`**
    (dde+0x1a) into a 32-entry stack array at `sp+0x338` (bounds-checked against
    `0x1f`) — new in v1.7.1; v1.6.0 filled `prof_desc[]` in file order;
  * the second pass at `0x2648` walks the sorted indices and dispatches
    `data_type == 0xa (MONITOR) → aw883xx_monitor_parse_fw(&aw_dev->monitor_desc …)`,
    `== 0x7 (MUTLBIN) → aw_dev_prof_parse_multi_bin(…, &prof_desc[cur])` with
    `prf_str = dde+0x2c`, `id = dde+0x1a`, `cur++`, `default → "unsupported
    SEC_TYPE [%d]"` — i.e. the existing
    `aw_dev_parse_data_by_sec_type_v_1_0_0_0()` helper, inlined.
* **Change.** The two type-specific parsers are replaced by one
  `aw_dev_parse_scene_v_1_0_0_0(aw_dev, prof_hdr, bool dev_type)` that performs
  the sorted collection pass, calls
  `aw_dev_parse_data_by_sec_type_v_1_0_0_0()` per entry, and reports
  `no valid device scenario resolved` when nothing was produced.
  `aw_dev_parse_by_hdr_v_1_0_0_0()` validates `prof_type` first and then makes a
  single call with `prof_type == AW_DEV_TYPE_ID` as the selector — which is what
  makes the compiler inline it exactly as the stock does.
* **Runtime relevance for GQ5012BF1.** *None.* The shipped
  `aw883xx_acf.bin` has `a_hdr_version = 0x00000001` (`AW_CFG_HDR_VER_0_0_0_1`),
  so the v0.0.0.1 path (`aw_dev_load_cfg_by_hdr` →
  `aw_dev_parse_dev_type`/`aw_dev_parse_dev_default_type`) is what actually runs.
  This delta is reconstructed for completeness, not for playback.

### D8 — module packaging: library module, not an i2c driver

* **Evidence.**
  * stock has no `.init.text`/`.exit.text` and no
    `.rela.gnu.linkonce.this_module` ⇒ `struct module` `.init`/`.exit` are NULL;
  * stock `.modinfo` has no `alias=` record ⇒ no `MODULE_DEVICE_TABLE`;
  * stock imports no `i2c_register_driver` / `i2c_del_driver`;
  * `__ksymtab_strings` = `\0aw883xx_i2c_probe\0aw883xx_i2c_remove\0`,
    `__kcrctab` = `0x713728fc`, `0xb3e48038`;
  * `mtk-sp-spk-amp.ko` imports exactly those two names with exactly those CRCs
    and calls them via `R_AARCH64_CALL26` at its `+0x6f8` and `+0x768`;
  * `modules.dep`: `mtk-sp-spk-amp.ko` depends on `aw883xx_driver.ko`;
    `aw883xx_driver.ko` has no dependencies.
* **Change.** `aw883xx_i2c_id[]`, `aw883xx_dt_match[]`, `aw883xx_i2c_driver`,
  `aw883xx_i2c_init()`, `aw883xx_i2c_exit()`, `module_init`/`module_exit` and
  `MODULE_DEVICE_TABLE` are removed. `aw883xx_i2c_probe`/`aw883xx_i2c_remove`
  become non-static and are `EXPORT_SYMBOL`ed; prototypes were added to
  `aw883xx.h`.

### D9 — `aw883xx_i2c_remove` keeps the pre-6.1 `int` return

* **Evidence.** The `void` form (which the donor selects on 6.1 via
  `AW_KERNEL_VER_OVER_6_1_0`) genksyms to `0x64a36158`; the stock export and the
  `mtk-sp-spk-amp.ko` import are both `0xb3e48038`, and the stock function is
  260 bytes versus 256 for the `void` form (the extra `mov w0, wzr`).
* **Change.** The `#if defined AW_KERNEL_VER_OVER_6_1_0` split is removed;
  the function is unconditionally `int` and returns 0. `mtk_spk_i2c_remove()`
  discards the value, so this is safe.
* This was the last CRC mismatch; after the change both exported CRCs match the
  oracle exactly.

### D10 — bounded index array (LieppOS hardening, behaviour-neutral)

* The stock `aw_dev_parse_scene_v_1_0_0_0` relies on the compiler's
  array-bounds trap (`cmp x13,#0x20; b.eq <brk>`) for its 32-entry index array.
  The reconstruction returns `-EINVAL` instead of trapping. For any ACF with
  ≤ 32 matching DDEs — including the shipped one, which has 3 — the two are
  indistinguishable.

### D11 — build-time safety gates (default = stock behaviour)

Two `#ifndef`-guarded macros were added in `aw883xx_calib.h`, both defaulting
to `1`. With the defaults the generated code is byte-identical to stock; they
exist only so a bring-up build can neuter the dangerous paths.

| macro | default | at 0 |
|---|---|---|
| `AW_ALLOW_CALIBRATION_WRITES` | 1 | `aw_cali_svc_cali_re()` and `aw_cali_svc_cali_f0_q()` return `-EPERM` (`cali function disable`) |
| `AW_ALLOW_FACTORY_MODE` | 1 | `reg_store`, `rw_store`, `dsp_rw_store`, `awrw_store` return `-EPERM` |

Playback initialisation, profile/firmware download, power sequencing and
monitor protection are **not** gated — the stock evidence proves they are
required for normal operation.

---

## Things that looked like deltas but were not

* **The 8 `import_ns` records.** They are not a vendor addition:
  `MODULE_IMPORT_NS(VFS_internal_…)` lives in `aw883xx.h`, and exactly 8 of the
  10 translation units include that header (`aw883xx_bin_parse.c` and
  `aw883xx_device.c` do not). Their `.modinfo` positions — five, then
  `description`+`license`, then three — fall out automatically once the object
  order matches the stock link order. An early hypothesis that the vendor had
  sprinkled `MODULE_IMPORT_NS` across 8 files was **withdrawn** after the
  `__UNIQUE_ID_import_ns<COUNTER>` values (461, 467, 397, 467, 467, …) were
  shown to be reproduced exactly by the header-only form.
* **ACF sub-bin type `0x12`.** Present in both profile containers, in neither
  the donor's nor the stock's `data_type_enum`. Both binaries skip it silently.
  Not a delta; documented in `firmware-config-contract.md`.
* **`AW_SYS_BATTERY_ST`, `AW_DEBUG`, `AW_MTK_PLATFORM_SPIN`,
  `AW_QCOM_PLATFORM_SPIN`.** All at their donor defaults. Verified by the
  import set (no `mtk_spk_send_ipi_buf_to_dsp`/AFE symbols) and by the absence
  of `dev_attr_vol`/`dev_attr_temp` from `aw_monitor_attr`.
* **Register renaming / instruction scheduling** inside
  `aw883xx_dev_cfg_load`. Not chased — see below.

---

## Verification (see `verify-*.txt`)

```
target : //lieppos/aw883xx-recon/recon:aw883xx_driver_gki
kernel : //common:kernel_aarch64  (GKI ab/12901745)
BUILD_RC: 0
compiler warnings : none (-Werror clean)
modpost warnings  : none (KBUILD_MODPOST_WARN=1, zero unresolved symbols)
```

| check | result |
|---|---|
| imported symbols | 73 / 73, exact set |
| `__versions` CRCs | 74 / 74 identical |
| exported symbols + CRCs | 2 / 2 identical (`0x713728fc`, `0xb3e48038`) |
| defined `.text` functions | 236 / 236, **0 extra, 0 missing** |
| byte-identical functions | **235 / 236** |
| functions with a differing relocation/call/string multiset | **0 / 236** |
| `.rodata.str1.1` strings | 991 / 991, 0 extra, 0 missing |
| `.rodata` bytes | identical |
| `.bss` | identical (50 bytes) |
| `.data` non-relocated bytes | identical |
| `.data` relocation (offset, target-symbol) list | identical |
| `OBJECT` symbols | 81 / 81, only `__UNIQUE_ID_vermagic` differs in length |
| `.modinfo` records | identical apart from `vermagic` |

### The single residual

`aw883xx_dev_cfg_load` is 3564 bytes versus the stock 3560. Its relocation,
call-target and string multisets are **identical** to the stock function; the
difference is a register-allocation swap (`x24`↔`x28`) and one spill slot moved
(`str x23,[sp,#0x10]` vs `[sp,#0x8]`) inside the inlined
`aw_dev_parse_scene_v_1_0_0_0` body. Per the task rules, compiler scheduling is
not chased once a semantic match is proven. The 4-byte shift is also the sole
cause of the `.text`-addend differences in `.data` relocations.

**Zero unexplained hardware-affecting differences remain.**
