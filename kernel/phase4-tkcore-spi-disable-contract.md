# GQ5012BF1 tkcore — `tee_spi_transfer_disable` recovered contract

Stock: `0x93e0`, 300 bytes, KCFI `0x36b1c5a6`, historical export CRC `0xadb9b21c`.

| Question | Answer |
|---|---|
| prototype | `int tee_spi_transfer_disable(void)` |
| KCFI | `0x36b1c5a6` |
| export CRC | `0xadb9b21c` (reproduced naturally) |
| what is disabled | **unknown to the normal world** — the request is delegated to the TA as command 1 with no parameters |
| idempotence | not enforced or tracked by tkcore |
| locking | **none** |
| clock interaction | **none** — no `clk_*` and no `tee_clkmgr_*` call |
| SPI state reset | none performed in the normal world |
| pad state | untouched |
| error convention | returns the `TEEC_Result`; the TEEC ladder is identical to the other two |
| memory freed | **none** — no allocation exists to free |
| device references dropped | **none** — no device reference is ever taken |
| effect on future transfers | not observable in the normal world; entirely a TA-side effect |

## The prototype takes no argument — and that is proven, not assumed

Stock never reads `x0`: the first use of that register is
`add x0, sp, #0x130`, which overwrites it. An unused parameter leaves no trace
in a function body, so the body alone cannot distinguish `(void)` from
`(bool)`. Two independent pieces of evidence settle it:

1. The recorded provider-ABI table spells it `int tee_spi_transfer_disable(void)`
   with historical CRC `0xadb9b21c`, which the island reproduces naturally.
2. KCFI type ids are derived from the function type. Stock's id is `0x36b1c5a6`,
   which the `(void)` spelling reproduces exactly. Independently, the two
   already-closed `int (*)(void)` functions `tee_peridev_init` and
   `plat_register_spi_clk` carry the **same** id `0x36b1c5a6` in both stock and
   the island — confirming that id belongs to `int(void)`.

An earlier revision of `tee_spi.h` declared `(bool disable)`. It was never
exercised, because the function had never been implemented. Phase 3D corrects it.

## Do not infer hardware power-off

Nothing in the normal-world code powers anything down. `disable` here means
"send command 1 to the SPI proxy TA". Any hardware effect happens inside the
secure world and is not observable from this module.

## Reconstruction result

Size 300 == 300, KCFI exact, call multiset exact, string set exact,
relocation multiset exact. Classification **SIZE_EXACT_SEMANTIC_EXACT**.
