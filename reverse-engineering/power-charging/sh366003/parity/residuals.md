# sh366003_fg.ko parity residuals

Operands:

- **A** = shipped stock `vendor_boot:/lib/modules/sh366003_fg.ko`, 85 968 B,
  sha256 `527bddb4ddb11e94ed85e6969a10f807178cbb3f0fd326c8509824800a3d61a7`, build-id `ca384423…6ffa6e`.
- **B** = rebuild from `source/sh366003_fg.c` (`scripts/build_sh366003.sh`), then
  `llvm-strip --strip-debug` (stock modules ship without DWARF). Unstripped B1 sha256
  `189f8da9…8250`; stripped `e7546e85…06d7`, 85 968 B, build-id `c0a3404c…60ce`.
- Two clean builds: **B1 == B2** (byte-identical, `cmp`).

| axis | result |
|---|---|
| file size | 85 968 = 85 968 |
| sections | 37/37 same names, sizes, flags; 34/37 byte-identical |
| functions | 39/39 present, 39/39 same size, **38/39 byte-identical** |
| data objects | 42/42 symbols (ko-pair-parity) / 30/30 (ko_parity), all byte-identical |
| `.rodata.str1.1` / `.rodata` | 194 / 829 entries identical; ko-str-refs: 0 A-only, 0 B-only literals |
| imports | 35/35; `__versions` 36/36 CRC-equal (incl. `module_layout`) |
| exports | 0/0 |
| KCFI | 28/28 type-id preambles equal, all 28 named (`kcfi-parity.tsv`) |
| relocations | 1513/1513 entries; 1509 identical, 4 ORDER-ONLY (R1) |
| `.modinfo` | identical (license, author, vermagic, name, depends=yft_devinfo, 3 aliases); stock has no `srcversion` and neither does B |
| symbol table | identical name/type/bind/size multiset |
| `.note.gnu.build-id` | differs (BUILD-ID) |
| DWARF | B has `.debug_*` before stripping; A has none (DWARF; removed by `--strip-debug`, stock pipeline) |

Byte-level difference between A and stripped B: `.text` 13 bytes, `.rela.text` 8 bytes,
`.note.gnu.build-id` 20 bytes. Nothing else.

## R1 — `sh_fg_probe` (inlined `Check_Chip_Version`): COMPILER/CODEGEN (register allocation)

- 11 of 809 instructions differ, all inside one window (insn 395–539).
- `scripts/probe_residual_check.py` proves it is a pure permutation: renaming x22↔x25 inside
  the window and swapping two independent adjacent `adrp/add` pairs (the hoisted
  `__func__ "Check_Chip_Version"` and the `read CMD_AFI_STATIC_SUM(0x0046) error` format address)
  makes the instruction streams identical. Output: `probe-residual-check.txt`.
- Same 4 relocations at 0x19cc–0x19d8 with addends swapped (`.rodata.str1.1+0xa29` / `+0x2126`).
- Same instruction count, same stack layout, same calls, same constants, same control flow;
  behaviour is identical.
- Root: the greedy register allocator's assignment in the inlined retry loop depends on block
  frequencies/vreg order from a source spelling not yet hit. 30+ spellings of the loop, the error
  branches, the flag variable, local types, declaration order and the probe caller were tried; all
  converge to this same permutation (or worse). Classified **COMPILER/CODEGEN** (register-allocation
  only); not SOURCE in any semantic sense, not STRUCT-LAYOUT, PROTOTYPE, CONFIG or UNKNOWN.

## R2 — `.note.gnu.build-id`: BUILD-ID

Hash of the linked object; differs by construction.

## R3 — DWARF: DWARF

Debug sections exist only in the unstripped rebuild; stock was shipped stripped.

No other residual exists.
