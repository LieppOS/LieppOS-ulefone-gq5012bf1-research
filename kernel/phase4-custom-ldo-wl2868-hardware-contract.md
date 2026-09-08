# Hardware contract

- IC family: Will Semiconductor WL2864C/WL2868C-compatible seven-output camera LDO.
- Stock I2C bus/address from board evidence: bus 11, address `0x29` (7-bit).
- Stock driver identity: `wl2864c`; module description `WL2864 & WL2868 Power IC Driver`.
- Raw register transactions use `i2c_transfer`; no regulator framework or regmap imports are present.
- Chip selection is by the register-0 identity byte: dispatch accepts `0x01` as WL2864C and `0x82` as WL2868C. Exact reset-time identity sequence is preserved in the disassembly evidence; no live read/write was performed.
- LDO vset registers are `0x03..0x09`; enable register is `0x0e`.
- GPIOs are consumer names `reset`, `vin1_en`; a separate integer `vin2` GPIO is stored for the exported/internal `wl2864c_vin2_power` path.

Safety: this is static evidence only. No I2C transfer, GPIO transition, module insertion/removal, camera open, or rail change was attempted.
