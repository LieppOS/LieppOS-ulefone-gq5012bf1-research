# Hynitron V2.1 lineage

## Result

The exact GQ5012BF1 historical source repository was **not found**. The closest
public historical sibling is Ulefone's Power Armor 13 tree:

- repository: `ulefoneofficial/Power-Armor-13`
- commit: `de34198b04c5dc11b23c16ffcd121ce978c7bc1e`
- path: `kernel-4.14/drivers/input/touchscreen/hynitron/`
- embedded identity: `Hynitron TouchScreen Qualcomm Driver V2.1 20201222`

That identity is byte-for-byte the same version label as the GQ5012BF1 module,
but the source is not the GQ5012BF1 revision: function exit line numbers and
several bodies differ substantially. It is therefore lineage evidence, not a
claim of exact source provenance. The misleading `Qualcomm` word in this MTK
device is inherited vendor text.

## Other local lineage witnesses

| witness | identity | value |
|---|---|---|
| LineageOS AYN qcs8550 modules, commit `a552fac8fae2c65b7e2e1f3a42e4580732659a6c` | later Qualcomm family | complete multi-file donor; 228/258 normalized stock string anchors |
| scpcom/linux patch `39971b8c69144556d932b734427e23bc7180c813` | Spreadtrum V3.1 20230829 | complete multi-file donor; independently 228/258 anchors |
| Daria MTK donor | MTK V2.2 20210129 | closest practical base for tool/debug and firmware-selection bodies |
| G93 donor | Spreadtrum V2.2 20210129 | cross-platform body/layout witness |
| Rabbit/HCD donors | MTK V3.0 20230202 | later feature/body witness only |

`stock-string-provenance.tsv` records every stock string and both requested
donor-A/donor-B results. Presence means the normalized uncommon 22-byte anchor
(after stripping printk priority and `[HYN][Info|Error]`) exists in source. This
is the same conservative measurement that exposed the original 228/258 gap.
The exact rebuild is checked by compiled string offset/content and is 258/258.

## Reconstruction method

1. Preserve the public Hynitron multi-file split; file split affects inlining
   and link order.
2. Restore complete donor-family bodies before codegen tuning.
3. Select only feature gates and GQ5012BF1 constants demonstrated by stock.
4. Diff every function's symbolic AArch64 body and relocations.
5. Recover 41 stock `HYN_FUNC_EXIT()` `__LINE__` values and anchor them with
   `#line` directives.
6. Add global `KCFLAGS=-faddrsig`, matching the stock compiler-output section.
7. Verify all 65 functions, 40 data objects, 2080 non-DWARF relocations, ABI,
   and 258 strings.

The resulting `source/` is exact as compiled code/data even though the original
private YFT source checkout remains unavailable.
