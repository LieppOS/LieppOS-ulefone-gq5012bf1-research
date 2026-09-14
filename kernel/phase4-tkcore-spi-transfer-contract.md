# GQ5012BF1 tkcore — `tee_spi_transfer` recovered contract

Stock: `0x9218`, 452 bytes, KCFI `0xffeb18b3`, historical export CRC `0x184ce7da`.

## Prototype

```c
int tee_spi_transfer(void *conf, uint32_t conf_size,
                     void *txbuf, void *rxbuf, uint32_t len);
```

Confirmed against stock independently of the consumer oracle: the entry log
prints the five arguments in order as
`conf=%p conf_size=%u inbuf=%p outbuf=%p size=%u`, fixing argument 3 as the
input buffer and argument 4 as the output buffer.

## Validation

| Input | Checked? | Failure |
|---|---|---|
| `conf` | `!= NULL` | `pr_err("tkcore: Bad parameters NULL buf\n")`, return `-EINVAL` |
| `txbuf` | `!= NULL` | same |
| `rxbuf` | `!= NULL` | same |
| `len` | `!= 0` | `pr_err("tkcore: zero buf size\n")`, return `-EINVAL` |
| `conf_size` | **not checked** | — |
| maximum length | **not enforced** | — |
| zero `conf_size` | **not rejected** | — |

Both bad-parameter paths return `-22` (`-EINVAL`), not a `TEEC_*` code, and
return **before** any context is created, so no cleanup is needed.

The entry `pr_info` is emitted unconditionally, *before* validation.

## Configuration mapping

None. `conf`/`conf_size` are forwarded verbatim as an opaque blob. tkcore does
not interpret mode, speed, bits-per-word, chip select, pad selection, timing,
endianness, or any DMA/FIFO setting — none of those fields is read in the
normal world.

## Transfer behaviour

The exchange is **full duplex, performed in place on `rxbuf`**:

```text
memcpy(rxbuf, txbuf, len);          ; stage TX bytes into the RX buffer
...
operation.paramTypes        = 0x75  ; TEMP_INPUT, TEMP_INOUT, NONE, NONE
operation.params[0].tmpref  = { conf,  conf_size }
operation.params[1].tmpref  = { rxbuf, len }
TEEC_InvokeCommand(&session, 0, &operation, &return_origin);
```

- no `spi_message` or `spi_transfer` is constructed;
- no `spi_sync` or provider call is made;
- no temporary allocation occurs — `memcpy` targets the caller's own buffer;
- `txbuf` is **read only**; `rxbuf` is both the TX source and the RX destination;
- partial transfers are not represented: the TA either succeeds or returns an error;
- there is no locking and no clock control.

## Lifetime and ownership

| Object | Owner | Copied? | Survives the call? |
|---|---|---|---|
| `conf` | caller | no — passed by pointer | no |
| `txbuf` | caller | read, not retained | no |
| `rxbuf` | caller | written in place | contents replaced by RX data |
| context/session/operation | this function, on the stack | — | destroyed before return |

No state persists after the transfer.

## Return values

`0` on success; the failing `TEEC_Result` for any of the three TEEC steps;
`-EINVAL` for bad parameters.

## Reconstruction result

Size 452 == 452, KCFI `0xffeb18b3` exact, call multiset exact (including
`memcpy`), string set exact, relocation multiset exact.
Classification **SIZE_EXACT_SEMANTIC_EXACT**.
