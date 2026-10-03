# SC8571 2-cell switched-capacitor direct charger (×2): DONE

## Result

| item | value |
|---|---|
| stock module | `vendor-ramdisks/platform-extracted/lib/modules/sc8571_charger.ko` |
| stock SHA256 | `790065853b875213ee7906bb4c41a5f272106b24a537034a886f12f0153d1d0b` (49,768 B) |
| modinfo | `name=sc8571_charger`, `description=SC SC8571 Driver`, `author=South Chip <Aiden-yu@southchip.com>`, `license=GPL v2`, `depends=charger_class` |
| vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| load order | vendor_boot `modules.load` line 148, after `sc851x_charger.ko` (147) and `mt6375-battery.ko` (146) |
| source | `source/sc8571_charger.c` (copy of `kernel_device_modules-6.1/drivers/power/supply/sc8571_charger.c`, DM commit `7846896`) |
| **function parity** | **34/34 exact** |
| **data parity** | **24/24 exact** |
| **ABI** | **exact**: imports 41/41, exports 0/0, modversions 42/42, modinfo 6/6, vermagic, section sizes 15/15 |
| reports | `parity/sc8571_charger.{function,data,abi}-parity.tsv` |

The build uses the normal DM Kbuild against the reconstructed, stock-exact
`charger_class.ko` (90/90 functions, CRCs 85/85). It uses the real MTK
`charger_class.h`. Callbacks use `charger_get_data(chg_dev)`, which is
`dev_get_drvdata(&chg_dev->dev)` and loads offset `0xe0`. An earlier
phase-4 reconstruction instead had to invent a stock-ABI shim header that
placed `driver_data` at `0xe0`; that shim is no longer needed.

## Donor

SouthChip's own MTK/charger_class driver template was posted publicly as
`[PATCH] power: supply: Add SC8541 charger drivers` (LKML, 2025-10-13). A
copy is kept in `donor/sc8541-lkml-2025-10-13.patch.txt`. It matches the stock
driver's structure exactly:

- the same `MODULE_DESCRIPTION("SC SC85x1 Driver")` and `MODULE_AUTHOR("South Chip <Aiden-yu@...>")`;
- the same `sc-cp-{standalone,master,slave}` power-supply names and `*-irq` names;
- the same `reg_range` / `val2reg()` threshold encoder;
- the same `mtk_*` `charger_ops`, `registers` sysfs node and probe label ladder.

Applying the template forms took the earlier recovery from 20/34 to 34/34.
The template-specific forms were:

- `if (gpio_is_valid()) {…} else {…}`;
- `val2reg()` with the `u8` result;
- `(unsigned char)` casts in `regmap_write`;
- the `detect_device` / `create_device_node` / `set_work_mode` helpers;
- the error-label fall-through.

The template's ordering also corrected the names of the last six
`reg_field` entries. Stock `init_device` order proves that index 51 is
`VBUS_OVP_DIS` (0x41 bit 6), 52 is `PMID2OUT_OVP_DIS` (0x41 bit 5), 53 is
`PMID2OUT_UVP_DIS` (0x41 bit 4), 54 is `PMID2OUT_UVP` (0x42 bits 7:5) and 55
is `PMID2OUT_OVP` (0x42 bits 4:2). The old `phase4-sc8571-dt-contract.tsv`
mapped `pmid2out-ovp=7` onto a 1-bit field; that mapping is superseded by
`register-map.md`.

## Behaviour differences from the SouthChip SC8541 template

- **IRQ:** the handler logs `INT OCCURED`, dumps registers 0x00–0x42 and calls
  `power_supply_changed()`. It does **not** decode flags and does **not** call
  `charger_dev_notify()`, so PE5 never receives a HW-error notification from
  SC8571. PE5 protection is purely the PE5 polling of thresholds and ADC.
- **Charge enable:** `sc8571_enable_charge()` writes `CHG_EN` and then dumps
  all registers. The template dumps registers in `init_device()` instead.
- **YFT additions** (see `../yft-power-deltas.md`):
  - `/sys/class/fastcharge_<n>/chipid` (prints the device ID read in probe);
  - the `gftk chg_dev_name : %s` log in `parse_dt`;
  - shutdown clears `ADC_EN`.
- PM: `suspend` / `resume` toggle the IRQ wake and enable state.
  `remove` unregisters the power supply.

See `register-map.md` and `../hardware/charge-pump-topology.md`.
