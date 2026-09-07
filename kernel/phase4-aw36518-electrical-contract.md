# GQ5012BF1 — AW36518 electrical / current / timing contract (Phase 8 + 9)

Safety-critical.  Every number here is read out of the stock binary; none is
taken from a datasheet, and no flash or torch path was executed on the phone.
The full per-instruction table is `phase4-aw36518-register-map.tsv`.

## Units

The V4L2 flash class defines `V4L2_CID_FLASH_INTENSITY` and
`V4L2_CID_FLASH_TORCH_INTENSITY` in **microamps**.  The stock module registers
those controls with the ranges below and converts them with a linear
`(value - min) / step` mapping into an 8-bit register code, so the driver's
internal "brightness" values are µA, and the register values are chip current
codes.  This is proven by the code, not assumed:

| Path | min (µA) | step (µA) | max (µA) | register | code |
|---|---|---|---|---|---|
| Flash | 2940 | 5870 | 1 499 790 | `0x03[7:0]` | `(brt - 2940) / 5870` (0…255) |
| Torch | 750 | 1510 | 385 800 | `0x05[7:0]` | `(brt - 750) / 1510` (0…255) |

`1 499 790 = 2940 + 255 × 5870` and `385 800 = 750 + 255 × 1510`, i.e. both
maxima are exactly the full-scale register code — a strong independent
confirmation that the units are µA and the mapping is linear over 8 bits.

Compiler evidence for the divisions (they appear as magic multiplies):
`umull x8, w8, #0xb2a20f87; lsr #44` = ÷5870 and
`umull x8, w8, #0x0ad9af4d; lsr #38` = ÷1510.

Below-minimum requests are **not** clamped to the minimum: they are treated as
"off" and route into `aw36518_enable_ctrl(..., false)`.

## Fixed operating points used by stock

| Site | Current | Notes |
|---|---|---|
| `FLASH_IOC_SET_ONOFF` on | 250 000 µA torch | literal `0x3D090` |
| `flashlight_strobe_store` | `level × 25 000 µA` torch | literal `0x61A8` multiplier |
| probe defaults (`pdata == NULL`) | flash 1 499 790 µA, torch 385 800 µA, timeout 1600 ms | 8-byte store `0x0016E28E_00000640` + `0x0005E308` |
| `flash->target_current` initial | 1 499 790 µA | thermal ceiling = flash max |
| `flash->ori_current` initial | 385 800 µA | torch max (donor initialises 0 — stock does not) |

## Timeout

* Register `0x08`, mask `0x0F`, code = `timeout_ms / 40`.
* `aw36518_init()` always programs **400 ms** (code `0x0A`) — this is the value
  in effect for every flashlight-core session and after resume.
* `V4L2_CID_FLASH_TIMEOUT` exposes 40…1600 ms in 40 ms steps; values ≥ 640 ms
  overflow the 4-bit field (stock performs no clamp — reproduced verbatim).
* The donor's `tout ≤ 40 → 0`, `≤ 400 → tout/40 - 1`, else `0x09` staircase is
  **not** what stock does; stock is the plain `tout / 40` division (proved by
  the 400 ms init programming code `0x0A`, not `0x09`).

## Enable / mode encoding (register 0x01)

| Field | Mask | Values used |
|---|---|---|
| LED enable | `0x03` | `0x03` = on, `0x00` = off |
| Mode | `0x0C` | `0x00` none/standby, `0x08` torch, `0x0C` flash (table `.rodata+0x468 = {0x00,0x0C,0x08}` indexed by `enum v4l2_flash_led_mode`) |
| Strobe source (+mode) | `0x2C` | `0x0C` software strobe, `0x20` external/hardware trigger |

Every enable/disable also calls `flashlight_kicker_pbm(on)` **before** touching
the register, so the peak-power budget manager always sees the transition even
when the write is skipped for a non-zero channel.

## Thermal cooling device

* Registered as `flashlight_cooler` on the AW36518 DT node
  (`#cooling-cells = <2>`), `devdata = flash`.
* `max_state = 4`; `get_cur_state` returns `target_state`.
* `set_cur_state(state)`: clamps `state > max_state`, returns 0 when unchanged,
  logs `set thermal current:%lu`, then
  * `state == 0` → `need_cooler = 0`, `target_current = 1 499 790 µA`,
    `torch_brt_ctrl(LED0, 385 800 µA)` (restores torch maximum);
  * `state > 0` → `need_cooler = 1`,
    `target_current = flash_state_to_current_limit[state-1]`, then
    `torch_brt_ctrl(LED0, target_current)`.
* `flash_state_to_current_limit[4] = { 150000, 100000, 50000, 25000 }`
  (`.rodata.cst16`, byte-identical in the reconstruction).  Same µA units as the
  torch control: codes `98, 65, 32, 16`.
* The clamp is applied inside both brightness paths:
  torch: `if (need_cooler && brt > target_current) brt = target_current;`
  (else `ori_current = brt`), flash: `if (need_cooler == 1 && brt >
  target_current) brt = target_current;`.  The cooler can only ever *reduce*
  current.

## Fault / protection behaviour

* Fault source register: `0x0A`, read on demand from
  `V4L2_CID_FLASH_FAULT` and once at the end of `aw36518_init()`.
* Mapping (see framework contract): bit0 → `TIMEOUT`, bit2 →
  `OVER_TEMPERATURE`, bit4|bit5 → `SHORT_CIRCUIT`.  No over-voltage,
  over-current, UVLO or LED-open bit is decoded by stock, and no fault is
  auto-cleared, latched in software, or reported to the flashlight core.
* No IRQ, no polling timer, no watchdog, no workqueue: the driver imports no
  IRQ, timer or workqueue symbol at all.
* Register `0x0B` (the donor's `REG_FLAG2`) is **never** touched by stock: the
  donor's `.shutdown` and `.close` writes to it do not exist here.
* Protection that stock *does* rely on: the chip's own 400 ms flash timeout,
  the mode/enable sequencing above, `flashlight_kicker_pbm()` accounting, the
  thermal cooling clamp, and — inside `flashlight.ko` — the Ulefone
  name-matched bypass of the low-battery cut-off for `aw36518-led0`.

## Deviations in the reconstruction

None.  No safety gate, clamp, delay or ordering change was introduced; the
reconstruction contains no `AW36518_ALLOW_FLASH`/`ALLOW_TORCH` build switch
because any such gate would alter stock behaviour at its default setting for a
driver that is loaded on every boot.
