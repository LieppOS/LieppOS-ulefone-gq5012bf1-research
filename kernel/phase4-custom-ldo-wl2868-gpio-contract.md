# WL2868 GPIO contract

## Stock GPIO paths

| Concept | Stock acquisition/use | Polarity/value | Lifetime |
|---|---|---|---|
| VIN1 | `devm_gpiod_get(dev,"vin1",GPIOD_OUT_HIGH)`; misleading failure string says `vin1_en` | logical high; `gpiod_set_value(desc,1)` | immediately `devm_gpiod_put` on success; get failure is non-fatal |
| reset | `devm_gpiod_get(dev,"reset",GPIOD_OUT_HIGH)` | logical 1 → 0 → 1, with 10–11 ms after **each** level | immediately `devm_gpiod_put` after third delay; get failure aborts probe |
| VIN2 | load integer state+0x40; `gpio_to_desc`; `gpiod_set_raw_value(desc,power != 0)` | raw, so active-low metadata is bypassed | no request/free; state defaults to GPIO 0 because probe zeros it and never populates it |

The frozen merged DT node supplies only `reset-gpios = <... flags 0>` (active-high). It supplies no `vin1-gpios`; this explains why stock deliberately tolerates the VIN1 lookup failure on this board. It also contains no VIN2 property consumed by this module.

## Exact sequencing and ownership quirks

`GPIOD_OUT_HIGH` has numeric value 3 in both gets. VIN1's success log precedes the explicit set-high call. Reset is explicitly set high even though acquisition requested output-high. All successfully acquired descriptors are released during probe itself; none is held until remove. The stale descriptor values remain in the global object after `devm_gpiod_put` but are not reused. Remove performs no GPIO action.

The stock module does not import `of_get_named_gpio`, `devm_gpio_request`, `gpio_request`, `gpio_free`, or descriptor direction APIs. No Sony/donor GPIO semantics are used here.

Safety: all findings are static. No GPIO was toggled during reconstruction.
