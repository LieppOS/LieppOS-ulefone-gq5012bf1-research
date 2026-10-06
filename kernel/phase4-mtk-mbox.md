# mtk-mbox — Ulefone GQ5012BF1

Status: donor/source validation

## Stock modules discovered

The Ulefone image contains a MediaTek mailbox stack consisting of distinct
modules:

- `mtk-mbox.ko`
- `mtk-mbox-mailbox.ko`
- `mtk_rpmsg_mbox.ko`

`mtk-mbox.ko` appears in both vendor_dlkm and the vendor_boot platform ramdisk.

## Public NothingOSS MT6878 source mapping

Core mailbox library:

`device_modules/drivers/soc/mediatek/mtk-mbox.c`

Public API header:

`device_modules/include/linux/soc/mediatek/mtk-mbox.h`

Linux mailbox-controller layer:

`device_modules/drivers/mailbox/mtk-mbox-mailbox.c`

RPMSG mailbox layer:

`device_modules/drivers/rpmsg/mtk_rpmsg_mbox.c`

These are separate modules and must not have their ABI/symbol contracts mixed
during comparison.

## Order

Validate `mtk-mbox.ko` first because it provides the common MediaTek mailbox
API used by higher layers.

Then validate:

1. `mtk_rpmsg_mbox.ko`
2. `mtk-mbox-mailbox.ko`
3. `mtk_tinysys_ipi.ko`

No reverse engineering is justified until the public `mtk-mbox.c` donor has
been compared against the stock binary.

## Initial stock-vs-public-source evidence

The vendor_dlkm and vendor_boot copies of `mtk-mbox.ko` are byte-identical:

`SHA256 95e3aa8d68b69504ae273bbd1979ea6d8b9c958b57a97b423cc696218ebfbe7c`

Therefore one stock binary is sufficient as the oracle.

The stock module exports the same major API present in the NothingOSS
`drivers/soc/mediatek/mtk-mbox.c` donor, including:

- mtk_mbox_write_hd
- mtk_mbox_read_hd
- mtk_mbox_write
- mtk_mbox_read
- mtk_mbox_clr_irq
- mtk_mbox_trigger_irq
- mtk_mbox_check_send_irq
- mtk_mbox_read_recv_irq
- mtk_mbox_set_base_reg
- mtk_mbox_set_base_addr
- mtk_mbox_cb_register
- mtk_mbox_polling
- mtk_smem_init
- mtk_mbox_probe
- mtk_mbox_clr_index_record
- mtk_mbox_get_index_record
- mtk_mbox_print_recv
- mtk_mbox_print_send
- mtk_mbox_print_minfo
- mtk_mbox_dump_all
- mtk_mbox_dump_recv
- mtk_mbox_dump_recv_pin
- mtk_mbox_dump_send
- mtk_mbox_dump
- mtk_mbox_log_enable
- mtk_mbox_reset_record

The stock module also embeds the source path:

`../kernel_device_modules-6.1/drivers/soc/mediatek/mtk-mbox.c`

and contains the expected MediaTek mailbox tracepoints:

- mtk_mbox_isr_entry
- mtk_mbox_isr_exit
- mtk_mbox_polling

Current classification:

`LIKELY_DIRECT_SOURCE_MATCH`

Do not reverse-engineer unless an unchanged donor build against exact GKI
12901745 demonstrates a substantive source difference.

## Standalone Kleaf include-path finding

The first unchanged-source standalone build reached compilation but failed to
resolve:

`<linux/soc/mediatek/mtk-mbox.h>`

Kbuild diagnostics showed:

- `src=../lieppos/mtk-mbox-direct`
- `obj=../lieppos/mtk-mbox-direct`
- `M=../lieppos/mtk-mbox-direct`
- `CURDIR=.../out/android14-6.1/common`

Therefore:

`ccflags-y += -I$(src)/include`

was being resolved relative to the kernel output-tree working directory rather
than the Bazel execroot external-module source directory.

The standalone wrapper was changed to:

`ccflags-y += -I$(KERNEL_SRC)/$(M)/include`

which resolves the include directory from the actual kernel source root plus
the external-module path.

This is standalone Kleaf build plumbing only. No NothingOSS donor source or
header content was modified.

## Final exact-GKI validation

The unchanged NothingOSS MT6878 `drivers/soc/mediatek/mtk-mbox.c`
source was successfully built against exact Google GKI build 12901745.

Results:

- build: success
- donor source SHA256: unchanged
- public `mtk-mbox.h`: unchanged
- public trace/events/mbox.h: unchanged
- imported kernel symbols: exact
- imported MODVERSION contract: exact
- exported CRC table: exact
- exported global MediaTek function sizes: exact
- raw `.text` SHA256: exact
- raw `.text` comparison: `TEXT_CMP_RC=0`

Stock and reconstructed `.text` are byte-identical.

### Final classification

`mtk-mbox.ko`: **DIRECT_SOURCE_MATCH**

Primary donor:

`NothingOSS/device_modules/drivers/soc/mediatek/mtk-mbox.c`

Source reconstruction required: **NONE**

The only standalone-build adaptations were Kleaf/Kbuild wrapper and include-path
plumbing. MediaTek source and public headers were not modified.

The stock vendor_dlkm and vendor_boot copies are also byte-identical, so one
oracle is sufficient.

## Current final status

**Classification:** `DIRECT_SOURCE_MATCH`

The NothingOSS MT6878 source was built against exact GKI 12901745 and matches
the GQ5012BF1 stock module at the required implementation boundary.

Final raw `.text` SHA256:

    3bacf0f5b6efb58059f2b75c17f9b7a45602ec07c04eb387de720e06bb156fb9

This module is frozen for initial LieppOS custom-kernel integration.

## Literal and symbol-residue audit (re-audit, exact operands)

Frozen-status re-audit with the four `.ko` tools, on hash-pinned operands:

| operand | SHA256 (full) |
|---|---|
| stock (vendor_dlkm == platform ramdisk) | `95e3aa8d68b69504ae273bbd1979ea6d8b9c958b57a97b423cc696218ebfbe7c` |
| final / direct rebuild | `075e21b3643e398d6b12aa0c385b92f65b1d6cb56de113dfd611f48f8d8ab342` |
| `-faddrsig` probe rebuild | `8e300639bf7b21a7af71bade78e22d5249ba6733c01fa280a5d78ee4dbb83736` |

Both rebuilds reproduce byte-for-byte from `//lieppos/mtk-mbox-direct` and
`//lieppos/mtk-mbox-addrsig` in the GKI 12901745 workspace, so every number below
is re-derivable.

Per-section bytes (first 16 hex of SHA256, then size):

| section | stock | final | addrsig probe |
|---|---|---|---|
| `.text` | `3bacf0f5b6efb580`/11128 | identical | identical |
| `.rodata.str1.1` | `375ca3ba84b20f64`/1607 | identical | identical |
| `.rodata`, `.data`, `.ref.data`, `.gnu.linkonce.this_module`, `.altinstructions`, `__versions`, `__ksymtab_gpl`, `__ksymtab_strings`, `__kcrctab_gpl`, `__bug_table`, `__jump_table`, `__tracepoints`, `_ftrace_events`, `__bpf_raw_tp_map` | — | identical | identical |
| `.rodata.str` | `624de37a7b8e1c82`/61 | `dcfede0da44139ea`/38 | `a78d3892ab00feb1`/39 |
| `.modinfo` | vermagic `…-g945dff7bc1bf` | vermagic `…-maybe-dirty` | same as final |
| `.llvm_addrsig` | present/217 | absent | present/211 |

So exactly three asymmetries survive, and all three are build provenance:

1. `.rodata.str` holds one literal, the `__FILE__` that `__bug_table` points at
   (`PREL16` at `__bug_table+0x4`). Stock: `../kernel_device_modules-6.1/…/
   mtk-mbox.c`; rebuilds: `../lieppos/mtk-mbox-*/mtk-mbox.c`. Same basename,
   different build-tree prefix — an out-of-tree Kleaf build cannot reproduce
   MTK's in-tree path.
2. `.modinfo` differs only in the kernel version *descriptor* suffix
   (`g945dff7bc1bf` vs `maybe-dirty`); the vermagic release itself,
   `6.1.115-android14-11`, matches.
3. `.llvm_addrsig` is closed by a single build flag: adding
   `ccflags-y += -faddrsig` (no source change) restores the section and its
   section symbol, which also explains the whole `.symtab` size delta of 24 B
   (429 vs 428 symbols = exactly the unnamed `STT_SECTION` symbol for
   `.llvm_addrsig`). Table *size* still differs (217 vs 211) because the
   addrsig bitmap indexes lld's internal per-build symbol space, not source.

Literal census (`ko-literal-census.py`, all RELA sections traced): every one of
the 46 literals in the three literal sections has an inbound relocation
(`.rodata.str1.1` 44/44, `.rodata.str` 1/1, `.rodata` 1/1), and the inbound
totals per target section are identical across all three objects
(`.text` 127, `.rodata.str1.1` 138, `UND` 170, `__ksymtab_strings` 52,
`.data` 15, `.ref.data` 9, `__tracepoints` 24, `.rodata` 3, `.rodata.str` 1).
Symbol-level residue (`ko-residue-diff.py`) is zero on every axis for both
pairs: defined `STT_FUNC` 46/46, exports 26/26, external (SHN_UNDEF) references
31/31, init/exit surface 0/0.

### Retraction of the earlier residue numbers

An earlier revision of this audit reported "23 stock-only strings" and five
stock-only symbols (`mtk_mbox_send_cmd`, `mtk_mbox_clr_record`,
`mtk_rpmg_md_settings`, `mtk_rpmg_dump`, `cmdq_dump_pktinfo`) and called
`__bug_table` 192 B/6 entries. All of that was tool error, and the tools are
now corrected:

* "23" is withdrawn as well: no operand has a 23-byte `.rodata.str` (they are
  61/38/39 B), so that count came from the superseded heuristic itself.
* Those five names occur **zero** times in the stock binary (verified by raw
  byte search); they came from dumping every `.strtab` token, and a `.ko` has
  two `SHT_STRTAB` sections named `.strtab` (one per symtab), so a naive token
  dump mixed in unrelated string tables.
* `EXPORT_SYMBOL` leaves no `__kcrctab_<name>` symbol in an lld-linked module,
  so the old "exports" axis was always empty — export names have to be read
  from the targets of `.rela__ksymtab*` (26 exports here, plus separately 31
  external references; all shared).
* `__bug_table` is 12 B — one entry, not six — in all three objects (identical
  `ed1e5ee7386ba685`/12), described by the 48 B `.rela__bug_table`: two
  `R_AARCH64_PREL16` entries at +0x0 (target `.text+0x2004`, the `BUG()` site)
  and +0x4 (target `.rodata.str+0x0`, the `__FILE__`), with the remaining word
  holding the literal `561`. The 12 raw bytes are identical in all three objects
  (`000000 000000 31020000`), so even the pre-link addends match. No field order
  is asserted from that.
  "192 B / 6 entries" matches no section on any operand measured here (the only
  6-entry table is the 144 B `.rela__bpf_raw_tp_map`), so it is withdrawn.

Corrected verdict: no stock-source residue of any kind. `DIRECT_SOURCE_MATCH`
stands; no source reconstruction is required for `mtk-mbox.ko`.

Evidence artifacts (regenerable, under the ignored `workspace/`):
`workspace/phase4-mtk-mbox/parity/mtk-mbox-stock-vs-{final,addrsig-probe}.txt`,
`…/mtk-mbox-strrefs-{final,probe}.txt`,
`…/mtk-mbox-strrefs-stock-vs-{final,probe}.{txt,json}`,
`…/mtk-mbox-residue{,-final}.{txt,json}`,
`…/mtk-mbox-literal-census.txt`.

## Source provenance re-verification (2026-10-05)

### Withdrawn draft of this section

An uncommitted draft of this section claimed a `<root>/<driver>` directory pair
under `…/MTK-MBOX/source/` (`drivers/misc/mediating_comm/mtk_mbox`, 11 files, plus
`subsys/core`, 2 files) from
`No-Stage/MT6879_AndroidT_ALPS_vendor_mediatek_proprietary_hardware`, a "36/36
unit hashes" result, two `mtk_rproc` blob hashes and 11 new `COPY-MANIFEST.tsv`
rows. None of it was ever executed. Measured now: `MTK-MBOX/source/` is flat (18
files, 4 of them `SHA256SUMS`) and has no `drivers/` or `subsys/` subtree; the
`mtk_mbox/Kbuild` / `export_test.h` layout it described exists in none of the four
local donor clones at `5e415e059253`; and `COPY-MANIFEST.tsv` has zero rows
mentioning `mediating_comm`. The same draft's first hand-rolled check also failed
for a method reason worth recording: it compared `sha256(file)` against the output
of `git rev-list <rev> -- <path>`, which is a *commit* SHA-1 and not a blob id -
two different hash functions over two different kinds of object - so its "0/66"
was an artefact of the harness, not a finding. Everything below comes from the
project's own verifier.

### What was actually run

    python3 reverse-engineering/scripts/source-verify.py \
      "Reverse Engineer - DONE/<COMPONENT>" --manifest COPY-MANIFEST.tsv \
      --repo /home/armol/kernel-work/public-mtk/nt6878.git \
      --ref 5e415e059253ce0d2e61c97108e5f5785d71f06f \
      --json workspace/phase4-mtk-mbox/source-verify/<component>.json

`nt6878.git` is `NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878` - the
`kernel_device_modules-6.1` tree the stock sources came from. The blob comparison
is `git hash-object` of each local file against
`git ls-tree -r --format=%(objectname) %(path) <rev>`, i.e. git blob ids on both
sides, which is the only correct currency here.

| component | manifests | upstream blobs | COPY-MANIFEST | verdict |
|---|---|---|---|---|
| `MTK-MBOX` | 40 comparisons / 4 manifests, 0 bad | 6/14 verbatim + 8 registered non-donor | 51 rows / 51 verified, 1 uncovered | **PASS** |
| `MTK-RPMSG-MBOX` | none in pack (0 comparisons) | 5/8 verbatim + 3 registered non-donor | 43 / 43 | **FAIL** (see 1) |
| `MTK-TINYSYS-IPI` | none in pack (0 comparisons) | 7/10 verbatim + 3 registered non-donor | 47 / 47 | **PASS** |

`MTK-MBOX`: 6/6 real source files are verbatim donor blobs at `5e415e059253` -
`mtk-mbox.c` `da2c023500` ← `drivers/soc/mediatek/mtk-mbox.c`,
`mtk-mbox-mailbox.c` `a0e08a9556` ← `drivers/mailbox/mtk-mbox-mailbox.c`,
`mtk_rpmsg_mbox.c` `82ec9c50d3` ← `drivers/rpmsg/mtk_rpmsg_mbox.c`,
`mtk-mbox.h` `80ade10970`, `mbox.h` `682829997b` ← `include/trace/events/mbox.h`,
`mtk_rpmsg.h` `2e21c19cb1`. Every path the verifier resolved is exactly the path
registered for that blob in `notes/source-map.tsv`, for all three components.

The 8 non-donor files are all accounted for and none is a source file: the six
LieppOS build-plumbing files (`<module>-Makefile`, `<module>-BUILD.bazel` for each
of the 3 modules) plus two declared non-donor headers - `rpmsg_internal.h`
`39b646d0d4` ("reconstructed … not the GKI header: `63cb74ea68` at android14-d2,
`bf24c7494b` at android14-qpr3/15", `source-map.tsv` row 3) and `mtk_sip_svc.h`
`5df1e35a34` ("vendor copy", rows 1-2; `notes/PROVENANCE.md:45` classifies it
`reconstructed`, taken from the build workspace at exact GKI common `6b18f0b574ab`
/ ab/12901745). For contrast, the donor's own
`include/linux/soc/mediatek/mtk_sip_svc.h` at `5e415e059253` is
`11bc86778265a0705d5cf6980af46705903e77fa`: different on purpose.

### Two bookkeeping gaps found (open)

1. `MTK-RPMSG-MBOX` fails for exactly one reason. Its `notes/source-map.tsv`
   registers blob `1acca98c7c` = `drivers/soc/mediatek/mtk_tinysys_ipi.c` as a
   cross-reference row, but its `source/` pack does not carry that file - it lives
   in `MTK-TINYSYS-IPI/source/`. `MTK-MBOX` carries its own copy of its
   cross-referenced module (`mtk_rpmsg_mbox.c` is present there), which is why the
   same pattern passes there. The verifier treats a registered blob with no file
   on disk as a failure; the fix is to carry the file or drop the row, not to
   weaken the check.
2. `MTK-MBOX/notes/source-map.tsv` is the only file in that pack without a
   `COPY-MANIFEST.tsv` row, while both siblings manifest theirs.

Neither the source maps nor any pack file was modified while running this. The
JSON reports under `workspace/phase4-mtk-mbox/source-verify/` are the evidence.
