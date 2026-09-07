# Mandatory RED — untouched public AW36518 donor

This baseline was completed **before meaningful reconstruction edits**.

## Frozen donor

* source: MotorolaMobilityLLC `kernel-mtk`, commit `ecf0e8f4448b5464d80c5dcd13b7573e9b2d39de`
* path: `drivers/misc/mediatek/flashlight/v4l2/aw36518.c`
* donor source copied byte-for-byte to `~/kernel-work/gki-12901745-workspace/lieppos/aw36518-recon/donor-build/aw36518.c`
* only build glue and unchanged MediaTek headers were added
* target: exact `//common:kernel_aarch64`, common `6b18f0b574ab`, CI ab/12901745
* target label: `//lieppos/aw36518-recon/donor-build:aw36518_donor`

## RED build result

`BUILD_RC = 0`.

Two source-version warnings were deliberately downgraded by build glue so the untouched Linux-5.10 donor could be measured on Linux 6.1: its `%d` for an `unsigned long`, and its old `int i2c remove()` callback assigned to the 6.1 `void` slot. Modpost reported the expected unresolved structural-provider symbols `flashlight_dev_register_by_device_id`, `flashlight_kicker_pbm`, and donor-only `flashlight_pt_is_low`; the baseline used `KBUILD_MODPOST_WARN=1`. These are RED observations, not final-build allowances.

## Structural result

| metric | stock | untouched donor | result |
|---|---:|---:|---|
| defined functions, all text sections | 23 | 22 | 20 shared |
| shared functions with identical size | — | — | 6/20 |
| imports | 46 | 40 | 38 shared |
| `__versions` records | 47 | 38 | 37 shared; all 37 CRC-identical |
| exports | 0 | 0 | exact |
| `.rodata.str1.1` records | 63 | 42 | 21 direct shared |
| objects | 32 | 39 | 31 shared names |

The donor's three unresolved flashlight imports have no generated `__versions` record in the RED object; this explains the donor import/version count difference.

### Stock-only functions

* `aw36518_init`
* `reg_show`
* `reg_store`

### Donor-only functions

* `aw36518_enable_ctrl` (stock compiler inlines this helper into its callers)
* `aw36518_shutdown`

### Shared-name size differences

`aw36518_close`, `aw36518_cooling_set_cur_state`, `aw36518_ioctl`, `aw36518_led0_get_ctrl`, `aw36518_led0_set_ctrl`, `aw36518_open`, `aw36518_parse_dt`, `aw36518_probe`, `aw36518_remove`, `aw36518_resume`, `aw36518_set_driver`, `aw36518_strobe_store`, `aw36518_suspend`, and `aw36518_torch_brt_ctrl` differ in size. Six shared functions have equal size.

### Stock-only imports

* `device_create_file`
* `devm_gpio_request_one`
* `gpio_to_desc`
* `gpiod_set_raw_value`
* `is_yft_cts_board`
* `of_get_named_gpio_flags`
* `regmap_write`
* `sscanf`

### Donor-only imports

* `___ratelimit`
* `flashlight_pt_is_low`

### Stock-only strings (semantic groups)

* stock `aw36518[%s]` diagnostic prefix and `V1.0.0`;
* GPIO/HWEN setup and invalid-pin diagnostics;
* chip-ID read and register-0x07 software-reset diagnostics;
* sysfs `reg` dump/write diagnostics;
* explicit init/subdev/control/DT/set-driver function-name strings;
* `flash-externel` / `flash_externel` thermal-cooling names.

### Donor-only strings

* unprefixed `pr_info` formats;
* `pt is low`;
* `aw36518_shutdown`;
* standalone `aw36518_open` and `aw36518_close` names retained due donor logging.

## Data/table and behavior differences

* stock cooling states are exactly four literal currents `{150000, 100000, 50000, 25000}`; donor has five `{100000, 80000, 60000, 40000, 20000}`;
* stock has GPIO/HWEN setup and software reset through register 0x07; donor does not;
* stock has a `reg` sysfs attribute; donor does not;
* stock imports and calls `is_yft_cts_board`; donor does not;
* donor checks `flashlight_pt_is_low`; stock does not;
* stock implements a dedicated hardware-init function and longer PM/open/close/driver paths;
* stock DT parser differs materially from the donor and is also the sole material code difference from stock `aw36518_v2.ko`;
* common current/timeout conversions and V4L2/MediaTek operation architecture remain credible donor evidence only where verified against stock instructions/constants.

## RED verdict

The public file is a strong structural donor but **not** a direct source match. Reconstruction is therefore an evidence-led source-delta recovery, using stock `aw36518.ko` as oracle and stock `aw36518_v2.ko` as a binary sibling control. Raw inventories are under `red/`; the complete relocation-aware stock and donor disassemblies are `stock-disasm.txt` and `red/donor-disasm.txt`.
