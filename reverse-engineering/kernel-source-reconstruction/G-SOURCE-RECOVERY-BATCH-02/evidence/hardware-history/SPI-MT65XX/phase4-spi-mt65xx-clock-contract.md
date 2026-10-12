# GQ5012BF1 `spi-mt65xx` clock contract

This contract is source-closed by exact function bytes and exact KCFI, not
inferred from names.

## `mt_spi_enable_master_clk`

Exact type: `void (struct spi_device *)`; KCFI `0xe397d461`.

1. Dereference `spidev->master`.
2. Recover private `struct mtk_spi *ms` with
   `spi_master_get_devdata(spidev->master)`.
3. Call `clk_prepare_enable(ms->spi_clk)`.
4. Store the integer return in local `ret`, but do not inspect, return, log, or
   unwind it.
5. Return `void`.

There is no NULL/ERR_PTR guard, lock, explicit runtime-PM get/put, or second
clock operation. The caller must provide a valid, probed `spi_device` whose
master devdata and `spi_clk` are initialized. Clock framework prepare/enable
reference counting is the only reference accounting.

## `mt_spi_disable_master_clk`

Exact type: `void (struct spi_device *)`; KCFI `0xe397d461`.

1. Recover `struct mtk_spi *ms` from `spidev->master` exactly as above.
2. Call `clk_disable_unprepare(ms->spi_clk)`.
3. Return `void`.

Again there is no NULL/error handling, lock, runtime-PM operation, or ownership
check. The caller is responsible for balanced ownership. Disable ordering is a
single combined `disable_unprepare` operation.

## Relationship to controller PM

These exports are direct vendor client hooks and do **not** share the driver's
`no_need_unprepare` distinction:

- controller runtime PM uses `clk_disable`/`clk_enable` for `mainpll` after a
  one-time probe `clk_prepare`;
- controller runtime PM uses `clk_disable_unprepare`/`clk_prepare_enable` for
  other sources (`univpll` on SPI1);
- the exported hooks always use combined prepare-enable and
  disable-unprepare.

The exact source therefore preserves an important caller assumption:
MicroArray's explicit hook pair manipulates only the controller functional
`spi-clk`; it does not alter `parent-clk`, `sel-clk`, autosuspend state, or CS.

## Failure behavior

Enable failure is intentionally silent because the API is `void` and the
source discards `ret`. There is no failure unwind because only one clock is
operated. Any change to return an error, invoke runtime PM, reorder clocks, or
add a lock would be behaviorally non-equivalent and is not present.
