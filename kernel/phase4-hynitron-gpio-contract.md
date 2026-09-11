# Hynitron GPIO/reset/power contract

| signal | DT property | MT6878 GPIO | flags/polarity | stock ownership |
|---|---|---:|---|---|
| interrupt | `hynitron,irq-gpio` | 11 | flags 0; input; falling EINT | Hynitron requests GPIO/IRQ |
| reset | `hynitron,reset-gpio` | 32 | flags 0; active-high run, low reset | Hynitron drives |
| VDD enable | `hynitron,vdd-gpio` | 119 | flags 0; high on | Hynitron drives; physical rail may be shared with rear assembly |

Probe requests VDD, drives it high, requests IRQ and reset GPIOs, configures IRQ
input, then uses reset low→20 ms→high→40 ms before identification; another
reset brackets final enable. `hyn_reset_proc(delay)` is low 20 ms, high, then
caller-selected high settling delay. GPIO polarity comes from actual DT and raw
GPIO operations, not generic active-low assumptions.

`tiny_tp_power_contorl` does not toggle VDD GPIO 119: off uses reset/sleep/IRQ or
gesture mode; on resets and reenables. Thus LCD coordination is through the two
exports, not direct ownership of an LCD GPIO. Probe errors free only resources
reached by the corresponding label. Remove frees reset, IRQ and VDD GPIOs; stock
does not explicitly drive VDD low first.
