# Exact YFT delta from pinned gpio_keys

The reconstruction differs from exact-GKI `gpio_keys.c` only as follows:

1. compatible: `gpio-keys` -> `yft-gpio-keys`;
2. platform-driver name: `gpio-keys` -> `yft-gpio-keys`;
3. default missing `debounce-interval`: 5 -> 16 ms;
4. GPIO ISR calls `disable_irq_nosync(irq)` before wake/debounce handling;
5. debounce completion calls `enable_irq(bdata->irq)` after report/sync/relax;
6. each successful GPIO report logs `[%s] button=...,state=...` and a pressed/released line;
7. each successful report calls `irq_set_irq_type`: state 1 -> EDGE_RISING, state 0 -> EDGE_FALLING.

Module basename/name changes naturally to `yft_gpio_keys` through the source/object filename. Author, description, license and platform alias remain inherited.

No kernel-side long press, short press, double/multi-click, remap, SOS, camera, flashlight, PTT, factory/charger mode, Android property access, sysfs/proc extension, suppression or press counter exists. Evidence: complete 23-function/27-object inventory; no extra functions/objects/imports/strings; exact source delta gives byte-identical code and hardware-relevant data.

**Conclusion: `NO_YFT_BEHAVIORAL_DELTA_BEYOND_IDENTITY_DEFAULT_DEBOUNCE_IRQ_MASKING_EDGE_REARM_AND_LOGGING`.** Higher-level smart-key/SOS/PTT/camera behavior exists in Android `YftPhoneWindowManager`, not this module.
