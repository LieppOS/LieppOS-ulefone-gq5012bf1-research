# DW9800W-class AF actuator (×3)

Fitted behind cameras 0 (imx989, `7-000c`), 2 (s5kjn1main2, `2-000c`) and
3 (ov64b, `4-000c`). One protocol, three instances; driven by the generic MTK
table-driven drivers `main_vcm` / `main4_vcm` / `main2_vcm`.

* [`protocol.md`](protocol.md) — identity, init/move/park/release sequence, timing, error handling
* [`register-map.tsv`](register-map.tsv) — every register the stock software writes, binary-proven vs inferred
* parity of the drivers: [`../parity/`](../parity/)

No firmware, patch RAM, NVM or OTP is accessed: the stock protocol contains
writes to `0x02/0x03/0x04/0x06/0x07` only and no read at all.
**NO FIRMWARE BOUNDARY.**
