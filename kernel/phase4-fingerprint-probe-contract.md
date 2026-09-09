# `fingerprint.ko` probe contract

## Platform probe

`yft_finger_plat_probe(struct platform_device *pdev)` performs exactly:

1. publish `pdev` to global `yft_finger_plat`;
2. print `yft_finger_plat_probe entry`;
3. call `yft_finger_get_gpio_info(pdev)`;
4. discard that return and return 0.

There is no allocation, `platform_set_drvdata`, GPIO request, IRQ request,
initial pin selection, reset pulse, power operation, or cleanup branch.

## DT/pinctrl parser instruction-level behavior

`yft_finger_get_gpio_info(pdev)` performs:

1. `of_find_compatible_node(NULL, NULL, "mediatek,yft_finger")`;
2. immediately dereference and print `node->name` and `node->full_name` (no
   NULL check and no `of_node_put`);
3. `wake_up_interruptible(&finger_init_waiter)`;
4. `devm_pinctrl_get(&pdev->dev)` and publish the result globally;
5. if the handle is `ERR_PTR`, `dev_err` and return its truncated `PTR_ERR`;
6. print the platform-device name;
7. lookup reset high then reset low;
8. print that power GPIO is unnecessary; do not lookup power states;
9. lookup MI SPI/GPIO, MO SPI/GPIO, CLK SPI/GPIO, CS SPI/GPIO;
10. lookup IRQ pull-down, pull-up, then bias-disable;
11. print success and return 0.

Every lookup stores its result first, then tests `IS_ERR`. The first error logs
the state-specific stock string and returns that error. Earlier global pointers
and the devm pinctrl handle are retained. No state is selected during parsing.

## Error branches

| condition | parser action/return | resources/state retained | platform probe result |
|---|---|---|---|
| compatible node absent | unchecked dereference; potential fault | global pdev already published | no normal errno path |
| `devm_pinctrl_get` error | store ERR_PTR, `dev_err`, return PTR_ERR | global pdev and ERR_PTR | 0 (ignored) |
| any state lookup error | store ERR_PTR, `dev_err`, return PTR_ERR | handle and all earlier states | 0 (ignored) |
| all success | return 0 | all 13 used states published | 0 |

The ready wake occurs before every pinctrl error point. Thus probe success is
not proof that the board-control exports are usable.

## Driver-core registration

The OF match table contains one entry, `mediatek,yft_finger`, followed by a zero
terminator. Driver name is `yft_finger`. The platform driver has only probe and
remove pointers; shutdown and PM pointers are NULL.
