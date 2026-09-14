# GQ5012BF1 — microarray_fp_tee static SPI trace

`microarray_fp_tee` is **FROZEN FOR RE** and was read only. Nothing in it was
modified, and no runtime test was performed.

## Call sites

Exactly **five** direct calls to `tee_spi_transfer`, all inside `init_connect`
— matching the five-step probe-time chip-identification sequence already
established by the MicroArray reconstruction.

| # | Offset | `conf` | `conf_size` | `txbuf` | `rxbuf` | `len` |
|---:|---|---|---:|---|---|---:|
| 1 | `0x4a8` | `.data+0x158` | 80 | `x29-0xc` | `x29-0xc` | 4 |
| 2 | `0x4d0` | `.data+0x158` | 80 | stack | `sp+0x14` | 4 |
| 3 | `0x544` | `.data+0x158` | 80 | stack | `sp+0xc` | 5 |
| 4 | `0x56c` | `.data+0x158` | 80 | `sp+0x20` | `sp+0xc` | 5 |
| 5 | `0x5b4` | `.data+0x158` | 80 | `sp+0x18` | `sp+0xc` | 5 |

Every site passes the same **fixed 80-byte secure configuration blob**
(`conf_size = 0x50`), confirming the recorded MicroArray evidence.

## Consumer requirements vs the Phase-3D provider

| Requirement | Provider behaviour | Verdict |
|---|---|---|
| symbol `tee_spi_transfer` exported | exported naturally | OK |
| imported CRC `0x184ce7da` | provider CRC `0x184ce7da` | **NATURAL** |
| KCFI `0xffeb18b3` | reproduced exactly | OK |
| 5-argument prototype | identical | OK |
| non-NULL `conf`/`tx`/`rx` accepted | all five sites pass non-NULL | OK |
| `len` of 4 and 5 accepted | only `len == 0` is rejected | OK |
| `conf_size == 80` accepted | `conf_size` is not validated | OK |
| TA UUID `966d3f7c-04ef-1beb-08b7-57f37a6d87f9` | identical UUID in `.data` | OK |
| command 0, paramTypes `0x75` | identical | OK |
| result `0` on success | identical | OK |

## Note on site 1

At the first call site `txbuf == rxbuf` (both `x29-0xc`). The reconstruction
performs the same `memcpy(rxbuf, txbuf, len)` that stock performs, so the
behaviour is identical to stock for this consumer — the copy is a no-op when
the two pointers coincide.

## Result

```text
PASS_STATIC_SPI
```

The consumer source requires **no modification**, which is the required
outcome: a need to edit the frozen consumer would have indicated the provider
ABI reconstruction was wrong.
