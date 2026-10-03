# Focused pre-LK NONRST_REG2 analysis

The fast machine-code scan found constructions of physical address
`0x1c00a024` outside the main LK payload.

Independent candidates exist in:

- `bl2_ext`;
- AEE;
- stock MT6878 preloader.

The stock preloader is particularly important because it executes before
main LK and therefore could modify `MTK_WDT_NONRST_REG2[3:0]` before LK's
known recovery-mode consumer reads it.

The earlier full-image disassembly approach was abandoned. This analysis
disassembles only small windows around the exact machine-code matches.

No phone state is modified.
