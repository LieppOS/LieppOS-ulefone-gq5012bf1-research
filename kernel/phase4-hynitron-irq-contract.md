# Hynitron IRQ contract

DT EINT/GPIO 11 resolves to Linux IRQ 56 in the live snapshot. DT and request
flags specify falling edge. Stock uses `request_threaded_irq(irq, NULL,
hyn_eint_interrupt_handler, IRQF_TRIGGER_FALLING | IRQF_ONESHOT,
"Hynitron Touch Int", data)`: no hard handler, non-shared threaded handler.

The thread disables the IRQ under the driver's state lock and queues the single
report work item. Work reads the touch packet (or gesture packet while gesture
mode is active), emits input events, and reenables IRQ on success, empty frame,
and I2C error. Repeated disable/enable calls are guarded by cached state.

Probe requests IRQ only after input registration, then immediately disables it
while sysfs/gesture initialization and the final reset complete; it enables IRQ
at successful probe end. `irq_set_irq_wake(irq,1)` is set once after request
and is not toggled by gesture helpers. Gesture mode disables IRQ, applies stock
`IRQF_TRIGGER_FALLING | IRQF_NO_SUSPEND` (`0x4002`) through
`irq_set_irq_type`, then reenables it. Normal mode performs the same bracket and
restores the DT/request flags (`IRQF_TRIGGER_FALLING | IRQF_ONESHOT`).
Non-gesture display-off disables IRQ before deep sleep. Removal frees IRQ after
removing interfaces; queued work is flushed.
