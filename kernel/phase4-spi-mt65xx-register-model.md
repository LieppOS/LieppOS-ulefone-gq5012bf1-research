# GQ5012BF1 `spi-mt65xx` register / quirk model

## Register offsets

| register | offset | stock use |
|---|---:|---|
| `CFG0` | `0x0000` | legacy SCK high/low and CS hold/setup; enhanced 16-bit hold/setup |
| `CFG1` | `0x0004` | CS idle, packet loop/length, legacy tick delay |
| `TX_SRC` | `0x0008` | DMA TX address low |
| `RX_DST` | `0x000c` | DMA RX address low |
| `TX_DATA` | `0x0010` | PIO TX FIFO |
| `RX_DATA` | `0x0014` | PIO RX FIFO |
| `CMD` | `0x0018` | ACT/RESUME/reset/mode/DMA/IRQ/CS/tick controls |
| `STATUS0` | `0x001c` | pause-vs-idle completion state |
| `STATUS1` | `0x0020` | PIO polling completion/status |
| `PAD_SEL` | `0x0024` | pad selection |
| `CFG2` | `0x0028` | enhanced 16-bit SCK high/low |
| `TX_SRC_64` | `0x002c` | DMA TX high address bits |
| `RX_DST_64` | `0x0030` | DMA RX high address bits |
| `CFG3` | `0x0040` | IPM pin mode, half duplex, command/address/dummy sizing |
| `CFG5` | `0x0068` | enhanced packet-length high 16 bits |

## Command bits

`ACT` bit0, `RESUME` bit1, `RST` bit2, `PAUSE_EN` bit4, `DEASSERT` bit5,
`SAMPLE_SEL` bit6, `CS_POL` bit7, CPHA/CPOL bits8/9, RX/TX DMA bits10/11,
TX/RX MSB-first bits12/13, RX/TX endian bits14/15, finish/pause IRQ enables
bits16/17, `CS_PIN_SEL` bit18, IPM non-idle bit19, loop bit21, and 3-bit tick
delay at bits24:22. Pause status is `STATUS0 & 0x2`.

## Limits

- maximum pad selector: 3
- maximum tick delay: 7 (three bits)
- PIO FIFO: 32 bytes
- legacy packet: 1024 bytes
- IPM packet: 64 KiB × up to 256 loops
- MT6989 enhanced packet encoding: 32-bit `(length-1)` split between CFG1 and
  CFG5 (up to 4 GiB representation)
- DMA addresses: 36 bits for `dma_ext`, 32 otherwise
- PIO poll timeout: 200000 us

## Compatible-data rows

| compatible(s) | quirk row |
|---|---|
| `mt2701`, `mt6589`, `mt8135` | common (all flags false) |
| `mt2712` | must RX + must TX |
| `mt6765`, `mt8192` | pad select, must RX/TX, enhanced timing, extended DMA |
| `mt6983` | pad select, enhanced timing, extended DMA, IPM, quad |
| `mt6985` | mt6983 + software CS |
| **`mt6989`** | mt6985 + enhanced packet length |
| `mt7622`, `mt7629` | must RX/TX + enhanced timing |
| `mt8173` | pad select + must RX/TX |
| `mt8183` | pad select + must TX + enhanced timing |
| `mt6893` | pad select + must TX + enhanced timing + extended DMA |

## Active GQ5012BF1 row

Every merged stock controller node declares `mediatek,mt6989-spi`. Thus the
active row is exactly:

```
need_pad_sel=true   must_rx=false       must_tx=false
enhance_timing=true dma_ext=true        ipm_design=true
support_quad=true   sw_cs=true          enhance_packet_len=true
```

SPI1's `tee-only` DT property independently suppresses installing the software
CS callback; it does not change this compatible-data object.
