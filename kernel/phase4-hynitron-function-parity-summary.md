# Hynitron function parity summary

The frozen stock and rebuild each contain 65 defined functions and the name sets
are identical (65 shared, zero stock-only, zero rebuild-only). Nine functions
are size-identical and eight are byte-identical; the remaining functions are semantic clean-room
reconstructions with compiler/CFG size differences recorded row-by-row in
`phase4-hynitron-function-parity.tsv`.

KCFI is exact for all 63 functions for which a type ID is emitted/applicable.
The words immediately before local direct-only `hyn_find_fw_idx` and
`hyn_check_gesture` are instructions, not KCFI preambles, so both are correctly
reported N/A rather than fabricating IDs. Both externally consumed exports are
KCFI exact (`0x019c0cac`).

All 54 imported symbol/CRC pairs are exact, including 51 kernel/loader and three
stock yft_devinfo edges. Hardware/register/firmware constants are closed by the
corresponding contracts; no byte identity is claimed where not observed.
