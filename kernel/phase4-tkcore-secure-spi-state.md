# GQ5012BF1 tkcore — secure-SPI shared state

Recovered before implementing any of the three SPI functions, as required.

## The headline finding

**There is no persistent secure-SPI state.** The three exported SPI functions
are not a SPI driver: each is a self-contained TEE client that opens its own
context and session, invokes one command against one TA, and tears everything
down again before returning.

Every item the investigation was asked to look for is therefore answered
"not present", and that is a measurement, not an assumption:

| Item investigated | Finding in stock |
|---|---|
| SPI device pointer | **none** — no `struct spi_device` is referenced |
| SPI controller/master relation | **none** |
| `spi_transfer` object(s) | **none** |
| `spi_message` object(s) | **none** |
| configuration buffer | not owned by tkcore; the caller's blob is passed through by pointer |
| pad-select state | **not cached** — `tee_spi_cfg_padsel` forwards the value and keeps nothing |
| clock relation | **none** — no `clk_*` call, no `tee_clkmgr_*` call |
| mutex / spinlock | **none** — zero locking primitives in all three functions |
| allocation ownership | **none** — no `kmalloc`/`kfree`/`devm_*`; all state is on the stack |
| DMA / bounce buffer state | **none** |
| maximum length | **not enforced** — only `len != 0` is checked |
| chip-select behaviour | not visible in the normal world; delegated to the TA |
| mode / bits-per-word / speed | not set by tkcore; carried opaquely inside the caller's config blob |
| lifecycle | per-call; nothing survives the function |
| enable/disable state | not tracked in the normal world |

The only shared datum is a single 16-byte constant.

## The one shared object

`.data+0x1f8`, 16 bytes, referenced by all three functions:

```text
raw bytes : 7c3f6d96 ef04 eb1b 08b7 57f37a6d87f9
TEEC_UUID : 966d3f7c-04ef-1beb-08b7-57f37a6d87f9
```

This is the TrustKernel secure-SPI proxy TA, and it is the same UUID the frozen
`microarray_fp_tee` reconstruction uses for probe-time chip identification.

It lives in `.data`, not `.rodata`: the reconstruction therefore declares it
non-`const` so that it lands in the same section as stock.

## Common session boilerplate

All three functions share an identical, independently repeated sequence. Stock
does not factor it into a helper, and neither does the reconstruction.

```text
memset(&context,   0, 0x108)     ; TEEC_Context   = 264 bytes
session.fd = 0                   ; TEEC_Session   =   8 bytes
memset(&operation, 0, 0x118)     ; TEEC_Operation = 280 bytes
return_origin = 0
TEEC_InitializeContext(NULL, &context)      ; NULL name => kernel-side client
TEEC_OpenSession(&context, &session, &uuid, 0, NULL, NULL, &return_origin)
  ... build operation ...
TEEC_InvokeCommand(&session, <cmd>, &operation, &return_origin)
TEEC_CloseSession(&session)
TEEC_FinalizeContext(&context)
```

Stack frame is `0x240` bytes in each, with a stack-protector cookie loaded from
`SP_EL0 + 0x638`.

## Error-path ladder (identical in all three)

| Failure | Cleanup performed | Return |
|---|---|---|
| `TEEC_InitializeContext` | **none** | the `TEEC_Result` |
| `TEEC_OpenSession` | `TEEC_FinalizeContext` only | the `TEEC_Result` |
| `TEEC_InvokeCommand` | `TEEC_CloseSession` + `TEEC_FinalizeContext` | the `TEEC_Result` |
| success | `TEEC_CloseSession` + `TEEC_FinalizeContext` | `0` |

## Command multiplexing

| Function | commandID | paramTypes |
|---|---:|---|
| `tee_spi_transfer` | 0 | `0x75` |
| `tee_spi_transfer_disable` | 1 | `0x00` |
| `tee_spi_cfg_padsel` | 2 | `0x01` |

## Explicit non-assumption

Ordinary Linux SPI semantics were **not** assumed anywhere. No pinctrl, no
`spi_sync`, no controller register access and no GPIO activity exists on any of
these paths in stock, so none was reconstructed.
