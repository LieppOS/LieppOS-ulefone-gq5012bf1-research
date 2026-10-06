# RT5133 — fault handling

## Capability (exact stock code)

| source | register / bit | kernel handling | reaches |
|---|---|---|---|
| base events | `0x10` (any bit except bit6) | `dev_info "base event occurred [0x%02x]"` | log only |
| VREF event | `0x10` bit6 | ignored (fires whenever base is off) | — |
| LDOn over-current | `0x11` bit(n-1) | `regulator_notifier_call_chain(rdev[n], REGULATOR_EVENT_OVER_CURRENT)` | regulator consumers' notifiers |
| LDOn power-good-bad | `0x12` bit(n-1) | `regulator_notifier_call_chain(rdev[n], REGULATOR_EVENT_FAIL)` | regulator consumers' notifiers |
| hardware all-off policy | `0x19` bit7 (OC), bit6 (PGB) | set from DT `oc-/pgb-shutdown-all` = 0 → disabled | — |
| per-LDO protection select | `LDOn_CTRL1` bit5 OCPTSEL, bit4 PGBPTSEL | set to 1 from DT | — |

Mechanism: EINT19 falling edge → threaded IRQ (`IRQF_ONESHOT`, no hard handler)
→ bulk read `0x10..0x12` (3 bytes) → dispatch → bulk write back the read value
(write-1-clear). Returns `IRQ_NONE` on any I/O failure. No over-voltage,
under-voltage or thermal sources exist in the driver.

At probe all events are cleared (`FF FF FF` → `0x10`) and all masks opened
(`00 00 00` → `0x16`).

## On GQ5012BF1

**No fault path is active.** The probe aborts at the `CHIP_INFO` read, before
`rt5133_enable_interrupts()`, so EINT19 is never requested, no event register
is ever read, and no regulator exists to notify. There are also no consumers
that could register a notifier. This is an inactive capability, not a missing
behaviour.
