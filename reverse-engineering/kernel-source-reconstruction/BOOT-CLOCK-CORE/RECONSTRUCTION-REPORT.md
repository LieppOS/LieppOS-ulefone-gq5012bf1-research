# BOOT-CLOCK-CORE — reconstruction report

**Result: all six modules are source-reconstructed and byte-identical to stock except the
20-byte GNU build ID (class A, BYTE_EXACT).** Offline and static only; no device interaction.

| Module | Functions exact | Data exact | Imports / exports (CRC) | KCFI type IDs | Relocations | Sections | Residual | Source status |
|---|---:|---:|---:|---:|---:|---|---|---|
| `clk-common.ko` | 225/225 | 105/105 | 114/114 · 87/87 | 8/8 | 3447/3447 | 44 + build-id | build ID @0x1bd90+20 | A |
| `clk-mt6878.ko` | 12/12 | 130/130 | 26/26 · 1/1 | 1/1 | 1524/1524 | 43 + build-id | build ID @0x9f90+20 | A |
| `clk-mt6878-bus.ko` | 3/3 | 19/19 | 7/7 · 0/0 | 0/0 | 86/86 | 36 + build-id | build ID @0x20d0+20 | A |
| `clk-mt6878-peri.ko` | 3/3 | 35/35 | 7/7 · 0/0 | 0/0 | 286/286 | 36 + build-id | build ID @0x3910+20 | A |
| `clk-mt6878-vlp.ko` | 3/3 | 15/15 | 7/7 · 0/0 | 0/0 | 50/50 | 36 + build-id | build ID @0x1d10+20 | A |
| `clk-fmeter-mt6878.ko` | 10/10 | 20/20 | 16/16 · 0/0 | 0/0 | 326/326 | 39 + build-id | build ID @0x4610+20 | A |
| **Total** | **256/256** | **324/324** | **177 · 88** | **9/9** | **5719/5719** | **234 + 6** | **0 unresolved** | **6 × A** |

Exports are counted from `__crc_*` slots, so they include the 23 exported clock-ops *data
objects* in `clk-common` (64 exported functions + 23 objects = 87). `.modinfo` (license,
description, author, vermagic, `name`, `depends`) is identical; none of the six has `srcversion`.

Every row is in `module-parity.tsv`, `function-parity.tsv`, `data-parity.tsv`,
`evidence/acceptance/{abi,sections}-parity.tsv` and `relocations-parity.tsv.xz`. Functions/data
are keyed by section, offset, name and size and compared on raw bytes; relocations are compared
raw *and* semantically (offset, type, target symbol, addend); every section header field
(type, flags, size, align, entsize, offset, link, info) matches and every section's content is
identical except `.note.gnu.build-id`. The verifier asserts the whole-file byte difference lies
only inside the 20-byte build-ID descriptor.

## How parity was reached

1. **Unmodified ALPS `5e415e059253` (Nothing MT6878 KDM history)** built cleanly:
   `clk-common`, `clk-mt6878-bus`, `clk-mt6878-vlp`, `clk-fmeter-mt6878` were already
   byte-exact (build ID only). `clk-mt6878` differed in `clk_mt6878_top_probe`, `top_muxes`
   and a missing `top_disp_pwm_parents`; `clk-mt6878-peri` in `perao_clks`/`perao_mcd`.
2. Decoding both stock tables against relocations showed **exactly** one extra 104-byte
   `mtk_mux` (`top_disp_pwm_sel`, ID 282, 7 parents, CLK_CFG_7 lsb 24 width 3, pdn 31,
   CLK_CFG_UPDATE1 shift 0) and two extra 80-byte gates (`peraop_disp_pwm0/1`, IDs 31/32,
   bits 10/11, parent `top_disp_pwm_ck`); `perao_mcd.num_clks` 33 vs 31.
3. All eight public `clk-mt6878.c` revisions and five `clk-mt6878-peri.c` revisions were built
   against the pinned tree. Earlier revisions carry the mux but are incompatible with the later
   dt-binding IDs (`CLK_VLP_TIA_ULPOSC_SEL`, `CLK_PERAOP_SSUSB0_REF`…), so no single public
   revision matches. ALPS `591991d44aad` ("remove no owner clock node") is where the mux was
   removed upstream.
4. The board DT proves the device keeps that path:
   `disp-pwm0/1@1100e000/1100f000 clocks = <&pericfg_ao 31/32>, <&topckgen 282>, <&topckgen 184>`.
5. Patch 0002 restores the pre-`591991d` mux, parents and `top_disp_pwm_ck` factor parent name
   verbatim, adds the two gates, and appends the IDs (282; 31/32; NR 283/33). The final string-pool
   difference (`disp_pwm_sel` vs `top_disp_pwm_sel`) was the factor-parent rename in the same
   commit; restoring it closed the last byte.

No stock instruction or data byte was copied; every value is source text derived from
public history and confirmed by the stock tables and the board DT.

## Classification of all differences

| class | count |
|---|---|
| BYTE_EXACT | all functions, data, sections (except one per module), relocations, CRCs, KCFI, modinfo |
| BUILD_METADATA_ONLY | 6 × 20-byte GNU build ID (`.note.gnu.build-id` descriptor) |
| PROVEN_SEMANTIC_EQUIVALENT / COMPILER_ONLY / UNRESOLVED | 0 |

## Reproducibility

Maintained source: `android_kernel_modules_boot_clock_ulefone_gq5012bf1` @ `e99d919`
(bundle in `source/`). A fresh clone in a new workspace, with the development workspace and
scratch tree moved away, bootstrapped from the offline pin mirror, verified every pin tree ID,
regenerated `.config` (sha256 `8f9d1d29…`) and the AEE provider CRCs from source, built B1 and
B2 from scratch and passed the full stock acceptance. B1 == B2 for raw and stripped modules,
all 23 target `.o`/`.mod.o`, `Module.symvers`, provider witnesses, kernel config and source
trees. See `build-reproduction.md`.

## Boundaries

* Hardware execution is not validated: no clock was enabled, measured or re-parented on a device.
* `aee_aed`, `clk-bringup`, `clk-chk-mt6878`, `pd-chk-mt6878`, `clk-dbg-mt6878` and the other
  `clk-mt6878-*` domain modules are **not** in this scope; their owners are unchanged.
* Signing: the stock vendor_boot copies carry **no** appended module signature, and the rebuilds
  match them byte-for-byte including that absence; no signature delta exists for these six.
