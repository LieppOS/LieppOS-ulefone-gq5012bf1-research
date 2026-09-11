# `camplight_mode` contract

Device attribute mode is 0644; stock init later chmods the path 0777. Show is
`<name>\n` from this exact table:

| value | show | exact action |
|---:|---|---|
| 0 | `OFF` | cancel gate timer if active; disable PWM; GPIO22 high; EN=0, POWER=0; disable again, GPIO22 high then low; relax camping wake source |
| 1 | `LOW` | PWM3 OLD width17/thresh16; EN=1, then POWER=1 |
| 2 | `NORMAL` | PWM3 OLD width17/thresh12; EN=1, then POWER=1 |
| 3 | `HIGH` | PWM3 OLD width17/thresh1; EN=1, then POWER=1 |
| 4 | `BLINK` | GPIO22 low; gate EN every 50 ms; POWER=1 |
| 5 | `SOS` | GPIO22 low; start exact variable-period EN state machine; POWER=1 |

Store uses `sscanf("%d")`. Parse failure returns the supplied byte count with no
change. A signed `mode >= 6` comparison rejects 6 and above, but negative values
are accepted: they execute the common PWM/timer/gate shutdown, take the switch
default, assert POWER, and cache the negative mode. A later show indexes the
six-entry table with that negative value and reaches the compiler bounds trap.
This unsafe stock bug is preserved. A value equal to the cached mode is a
complete no-op. All stores return count, not an errno.

Transitions are unlocked except for gate-timer start/cancel. Nonzero modes hold
`ln2403_wake_lock`; mode 0 relaxes it. No kernel auto-off exists.
