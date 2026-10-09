# MT6878 PINCTRL — four-module source reconstruction

**Static source certification: four D → A, no behavioral residue.** All four stripped
modules are whole-file identical to their exact stock operands except the 20-byte GNU
build-ID descriptor. Public ALPS C source matches without implementation patches.
Fresh independent committed clone: B1 == B2, then full stock acceptance. Offline only;
no ADB, hardware operation, flashing, module loading or GPIO/EINT manipulation occurred.

| Module | Functions exact | Data exact | Imports / exports | CRC / KCFI | Relocations | Sections (incl. null) | Residual | Final |
|---|---:|---:|---:|---|---:|---:|---|---|
| pinctrl-mt6363.ko | 4/4 | 37/37 | 5 / 0 | all / 0 | 66/66 | 39 | build ID @0x2710+20 | A |
| pinctrl-mt6878.ko | 1/1 | 227/227 | 8 / 0 | all / 5 | 1439/1439 | 33 | build ID @0x10250+20 | A |
| pinctrl-mtk-common-v2_debug.ko | 10/10 | 14/14 | 30 / 2 | all / 3 | 279/279 | 46 | build ID @0x3ad0+20 | A |
| pinctrl-mtk-v2.ko | 102/102 | 34/34 | 60 / 38 | all / 4 | 1160/1160 | 39 | build ID @0xd210+20 | A |
| **Total** | **117/117** | **312/312** | **103 / 40** | **all / 12** | **2944/2944** | **157** | **80 metadata bytes** | **4 × A** |

MT6878's large descriptor/field tables are data, not fabricated function coverage; its
single compiled function registers the platform driver. Function/data keys include section,
offset, name and size. Raw instruction bytes and relocation bytes match, establishing branch
and call targets, control flow, sizes and ordering—not merely size equality. Data comparisons
include initialized objects, BSS layout, ops structures, pin/function/register tables,
module descriptors and anonymous compound-literal arrays.

The raw four stripped files differ from stock at exactly 20 bytes each, all inside the
structurally validated GNU note. Every other file byte—including symbol/string tables,
section headers, padding, relocation records, KCFI code preambles, import/export CRCs and
`.modinfo`—is equal. No `srcversion` or appended signature exists in stock or the accepted
outputs. Raw unstripped builds contain debug sections absent from stock; stock comparison
uses only the standard `llvm-strip --strip-debug` operation, not executable/data edits.

`MODULE-PARITY.tsv`, `FUNCTION-PARITY.tsv`, `DATA-PARITY.tsv` and
`evidence/acceptance/` preserve every parity axis and raw residues. Classification:
**BYTE_EXACT** for all behavior/ABI; **BUILD_METADATA_ONLY** for GNU IDs;
**PROVEN_SEMANTIC_EQUIVALENT / COMPILER_ONLY / UNRESOLVED: zero**.

## Source and scope

Maintained repository: `../android_kernel_modules_pinctrl_ulefone_gq5012bf1` relative to
research root. All compiled C: public `5e415e059253ce0d2e61c97108e5f5785d71f06f`.
Vendor configuration: `957dac185efe46cbf6336b0fff9516d84c8cd78f`.
One complete Kbuild-only patch scopes output; no board-specific C delta is needed.
See `SOURCE.md`, `SOURCE-LINEAGE.md`, `BUILD-REPRODUCTION.md`.

## Board contract and limits

Generated ledgers map all 196 physical pins, 20 virtual descriptors, 1011 function/virtual
rows, 2108 register-field rows, 88 MT6363 regmap fields, 159 declared pinmux entries per DT
operand, 124 state references per operand, 48 GPIO references per operand and the 137-entry
four-instance EINT matrix. Static and previously captured live DT were parsed independently.
No mode number is inferred from a peripheral name. `PINMUX-MAPPING.md`,
`GPIO-EINT-CONTRACT.md` and `DEVICE-TREE-CONTRACT.md` classify board claims and retain
unselected alternatives and overlap risks. A configuration declaration is not proof of PCB
wiring, actual state selection, global GPIO base or successful probe.

All four are in the first-stage normal/recovery lists; MT6878 pins are necessary for
MSDC1 card-detect and MT6375 EINT, among other consumers. Certified UFS/clock code was not
modified. Future controlled runtime acceptance remains explicitly deferred in
`EARLY-BOOT-DEPENDENCIES.md`.

Ownership stays COVERED-GENERIC for three identities and MICROSD-KERNEL for the debug
module. PINCTRL is a reconstruction package, not a new registered DONE component.
