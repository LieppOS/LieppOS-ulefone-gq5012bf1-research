# Hynitron PM/wakeup contract

Stock has no independently registered system-sleep `dev_pm_ops` callback and no
FB/DRM notifier edge. Rear-display state is coordinated explicitly by stock
`spi_tiny_co5300_lcd.ko` through the two exported void(int) functions.

Display off therefore has two modes:

1. gesture policy false: reset, IRQ disable, controller deep sleep (`0xe5=3`);
2. gesture policy true: controller remains in low-power gesture scan, falling
   IRQ remains armed and wake-enabled.

Display on resets the CST820, flushes touch state, exits gesture mode if needed,
and restores normal falling-edge/oneshot IRQ flags. Probe calls
`irq_set_irq_wake(...,1)` once after IRQ registration; gesture/normal helpers do
not toggle wake, but switch the IRQ type between `0x4002` (falling plus
NO_SUSPEND) and the normal DT/request flags. There is no firmware
redetection/update on resume. This explicit export model is why the normal
Android PM path cannot be inferred from a generic donor's PM hooks.
