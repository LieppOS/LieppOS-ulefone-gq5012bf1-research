# yft_gpio_keys IRQ contract

## GQ5012BF1 buttons

Both keys use GPIO-derived IRQs (`gpiod_to_irq()`), handler `gpio_keys_gpio_isr`, initial flags `IRQF_TRIGGER_RISING | IRQF_TRIGGER_FALLING | IRQF_SHARED`. Neither uses IRQF_ONESHOT; neither is can-disable. `devm_request_any_context_irq()` selects normal or nested-thread context as required by the IRQ controller, but the registered callback is the primary handler and performs no explicit threaded-handler split.

## Stock YFT flow

1. Assert `irq == bdata->irq`.
2. **YFT delta:** `disable_irq_nosync(irq)` immediately, preventing another edge during debounce.
3. For wake keys, `pm_stay_awake()`. If suspended EV_KEY, emit synthetic press.
4. Schedule per-key debounce: relative hrtimer for non-sleeping GPIO, otherwise delayed work.
5. Return `IRQ_HANDLED`.
6. Completion samples the logical GPIO and emits/syncs it.
7. **YFT delta:** after successful sample, logical 1 arms rising; logical 0 arms falling. Because the DT GPIOs are active-low, this arms release after press and press after release.
8. Relax wake state, then **YFT delta** `enable_irq()`.

Initial request is both-edge, but the first state report changes it to one next edge. No manual GPIO direction or pinctrl action occurs.

The inherited IRQ-only path (`gpio_keys_irq_isr` plus release hrtimer) is present byte-for-byte but unused by this DT. It uses locking, immediate press/sync and optional delayed release; this is not a hidden third button.
