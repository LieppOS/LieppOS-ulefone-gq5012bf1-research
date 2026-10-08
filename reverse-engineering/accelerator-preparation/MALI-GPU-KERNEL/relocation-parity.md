# Relocation, section, string and modinfo parity — MALI-GPU-KERNEL (measured)

**Ledgers:** `parity/acceptance/relocation-parity.tsv`, `section-parity.tsv`, `residue.tsv`
(every differing file byte, attributed to its section).

## Relocations

| module | RELA sections | entries | semantic (offset, type, symbol, addend) | raw bytes |
|---|---|---|---|---|
| mtk_gpu_hal | 7 | 425 | identical | identical |
| mtk_gpu_qos | 10 | 274 | identical | identical |
| mtk_gpufreq_wrapper | 18 | 2821 | identical | identical |
| mtk_gpufreq_mt6878 | 10 | 1147 | identical | identical |
| ged | 17 | 11841 | identical | identical |
| mali_mgm_mt6878_r44 | 12 | 629 | identical | identical |
| mali_prot_alloc_mt6878_r44 | 9 | 171 | identical | identical |
| mali_kbase_mt6878_r44 | 21 | 31673 | identical | identical |

## Sections

* **Section layout.** Every module has the same number of sections, in the same order, with
  the same names, types, sizes and offsets. File sizes are equal.
* **Section contents.** Every section is byte-identical except:

| module | section | differing bytes | classification |
|---|---|---|---|
| all 8 | `.note.gnu.build-id` | 20 | **provenance.** lld SHA-1 over the linked object *including* the debug sections, which embed build paths. They are stripped afterwards, but the note survives. Proven path-dependent: identical sources built in two directories differ only here (`parity/build-id-path-dependence.txt`). |
| mali_kbase_mt6878_r44 | `.modinfo` | 23 (one value) | **provenance.** `srcversion`, modpost's MD4 over the source text. Every compiled byte is identical (source-lineage.md). |

* Identical by name, for kbase: `__bug_table` (WARN/BUG file+line records), `.rodata.str*`
  (incl. every `__FILE__`), `__ksymtab*`, `__kcrctab`, `__ksymtab_strings`, `__param`,
  `.altinstructions`, `__jump_table`, `__ex_table`, `__tracepoints*`, `_ftrace_events`,
  `_ftrace_eval_map`, `__bpf_raw_tp_map`, `.gnu.linkonce.this_module`, `__versions`,
  `.llvm_addrsig`, `.note.Linux`, `.note.gnu.property`, `.comment`, `.symtab`/`.strtab`
  (symbol names, order, types, binding, sizes, values) and `.shstrtab`. The other seven
  modules show the same, per `section-parity.tsv`.
