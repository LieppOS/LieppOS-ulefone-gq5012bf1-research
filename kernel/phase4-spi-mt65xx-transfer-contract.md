# GQ5012BF1 `spi-mt65xx` transfer / controller contract

## Installed controller callbacks

Probe installs:

- `prepare_message = mtk_spi_prepare_message`
- `transfer_one = mtk_spi_transfer_one`
- `can_dma = mtk_spi_can_dma`
- `setup = mtk_spi_setup`
- `cleanup = mtk_spi_cleanup`
- `set_cs_timing = mtk_spi_set_hw_cs_timing`
- `set_cs = mtk_spi_set_cs` only when DT lacks `tee-only`
- `mem_ops = mtk_spi_mem_ops` for IPM-compatible rows (including MT6989)

There is no `unprepare_message` callback. MT6989 mode bits add CS-high, loop,
dual, and quad support; must-RX/must-TX are false.

## Message preparation / CS

`prepare_message` programs CPHA/CPOL, bit order, endian, DMA-disable,
deassert-disable, sample selection, pad select, tick delay, IPM non-idle/loop,
and hardware CS timing. It rejects obsolete vendor `cs_setuptime`,
`cs_holdtime`, or `cs_idletime` via `BUG_ON`; Linux `spi_delay` CS fields are
used instead.

For non-TEE MT6989 controllers software CS toggles `SPI_CMD_CS_POL`; release
returns state to IDLE and resets the controller. On SPI1 `tee-only` suppresses
this callback; DT `cs-gpios`/SPI core owns CS.

## Clock rate / divider

For requested `speed_hz`, divider is `ceil(spi_clk_hz/speed_hz)` below half
rate, otherwise 1; high and low periods both use `(div+1)/2`. Enhanced timing
writes 16-bit high/low fields in `CFG2`; legacy rows use 8-bit `CFG0` fields.

## FIFO/PIO path

DMA is selected only when:

- length > 32 bytes, and
- both buffer addresses are 4-byte aligned (a NULL absent-direction pointer is
  naturally aligned).

Otherwise PIO processes chunks up to 32 bytes, disables finish/pause IRQs,
writes/reads 32-bit FIFO words plus a remainder word, starts ACT/RESUME, and
polls `STATUS1` atomically with a **200000 us** timeout per chunk. Timeout logs
`SPI PIO polling timeout` and returns the polling error.

## DMA path

DMA uses SPI-core mapped scatterlists. It enables TX/RX bits according to
present buffers, programs low 32-bit addresses plus high address registers for
36-bit-compatible hardware, splits work at scatterlist/packet boundaries, and
returns 1 for asynchronous completion. IRQ handling:

1. captures pause/idle state;
2. advances DMA addresses and scatterlist entries;
3. when both directions finish, clears DMA bits and calls
   `spi_finalize_current_transfer`;
4. otherwise programs the next segment/packet and resumes.

MT6989 probe sets a 36-bit DMA mask and a 16 MiB maximum segment size. No DT
DMA-engine channel is involved.

## Packet limits

- FIFO: 32 bytes
- legacy packet: 1024 bytes
- IPM packet: 64 KiB, loop count up to 256
- MT6989 `enhance_packet_len`: packet loop encoding is bypassed; `(len-1)` low
  16 bits go to `CFG1`, high 16 bits to `CFG5`, representing up to 4 GiB

## SPI memory operations

MT6989 supports exact `adjust_op_size`, `supports_op`, and `exec_op` callbacks.
The source validates bus-width consistency, maximum 15 address+dummy bytes,
nonzero data length, and IPM packet constraints where applicable. Execution
constructs command/address/dummy/data buffers, DMA-maps them, programs CFG3
half-duplex/pin width and DMA addresses, waits on an IRQ completion with a
transfer-derived timeout plus 1 s tolerance, resets on timeout, unmaps/frees,
and copies from a temporary aligned RX buffer when needed.

## Error recovery

- PIO timeout: return error; no invented retry
- SPI-memory timeout: controller reset, `-ETIMEDOUT`
- DMA ordinary transfer: completion/error behavior is exactly the IRQ-driven
  source path; no extra software timeout exists here
- probe/setup invalid pad/tick values return `-EINVAL`
