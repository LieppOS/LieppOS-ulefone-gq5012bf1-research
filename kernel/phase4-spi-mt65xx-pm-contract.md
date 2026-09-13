# GQ5012BF1 `spi-mt65xx` runtime-PM/autosuspend contract

## Probe-time PM setup

- `master->auto_runtime_pm = true`
- DT `mediatek,autosuspend-delay` is read as a `u32`; if absent (as on the
  merged GQ5012BF1 DT), default is **10 ms**
- `pm_runtime_set_autosuspend_delay(dev, delay)`
- `pm_runtime_use_autosuspend(dev)`
- `pm_runtime_enable(dev)`

`clock-source-type == "mainpll"` sets `no_need_unprepare=true`; probe then
prepares `spi_clk` once with `clk_prepare`. Every other value/missing property
uses the univpll/default path (`no_need_unprepare=false`). GQ5012BF1 SPI0 says
`mainpll`; SPI1-SPI7 say `univpll`.

## Runtime suspend/resume

| path | suspend | resume |
|---|---|---|
| `mainpll` / pre-prepared | `clk_disable(spi_clk)` | `clk_enable(spi_clk)` |
| other (`univpll` on SPI1) | `clk_disable_unprepare(spi_clk)` | `clk_prepare_enable(spi_clk)` |

Resume first applies a pending exported-delay update, clears the pending flag,
and logs it. Clock-enable failure is logged and returned.

## Exported autosuspend helper

`void mtk_spi_set_autosuspend_delay(struct spi_device *spi, int delay_ms)`:

1. Recover controller private data from `spi->master`.
2. `WARN` if `delay_ms > 10000`.
3. If the value differs, store it into private **`u32`**
   `auto_suspend_delay` and set `suspend_delay_update=true`.
4. Do not call a PM API immediately; the new delay becomes active on the next
   runtime resume.

No NULL/error guard exists. Negative `int` input is not rejected and converts
to `u32`; this report records source behavior without endorsing it.

## System sleep

Suspend calls `spi_controller_suspend(master)` first. If that succeeds and the
device is not already runtime-suspended, it invokes the same runtime-suspend
clock transition.

Resume invokes runtime resume first only when the device is not already
runtime-suspended, then calls `spi_controller_resume(master)`.

## Remove/shutdown

Remove disables runtime PM, resets the controller, and returns zero. There is
no shutdown callback and no extra autosuspend/clock cleanup hidden from this
source.
