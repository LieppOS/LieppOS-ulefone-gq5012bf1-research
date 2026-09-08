# Mandatory RED — SC851x no-public-source baseline

**RED mode:** no-public-source.

**Oracle:** `workspace/phase4-sc851x/stock/sc851x_charger.ko`
**SHA-256:** `b5e5f08bcfe37ac8c81525b0d4fe514902b552cc45b7f99fbeda8b80f6c2aa0c`

`phase4-sc851x-source-candidates.md` records the local/public search and the
rejection of SC8551/SC8561/SC8571 code as a false donor. With no source donor to
build untouched, this RED freezes the complete stock decision surface used for
transcription.

Evidence tags:

| tag | meaning |
|---|---|
| `SYM` | ELF symbol/type/size/binding/section |
| `REL` | relocation-aware disassembly and relocation entry |
| `STR` | exact string and reference site |
| `DAT` | scalar `.rodata`/`.data` decoding |
| `ABI` | import/export/MODVERSION evidence |
| `DT` | stock/live device-tree bytes |
| `LIVE` | previously captured read-only sysfs/log snapshot |

## D1 — module boundary

Decision: single I2C leaf module, no intermodule ABI.

- 11 defined functions, 18 defined objects. (`SYM`)
- 30 imported symbols / 30 MODVERSION entries; zero exports. (`ABI`)
- `depends=` is empty and no imported symbol is provided by another stock
  module. (`ABI`)
- No parameter or module alias. (`SYM`, `STR`)

Consequence: reconstruction must not add `charger_class`, `power_supply`,
regulator, extcon, USB, Type-C, notifier, or other vendor dependencies.

## D2 — driver identity

```c
static struct i2c_driver sc851x_charger_driver = {
        .driver = {
                .name = "sc851x",
                .owner = THIS_MODULE,
                .of_match_table = sc851x_charger_match_table,
                .pm = &sc851x_pm,
        },
        .probe = sc851x_charger_probe,
        .remove = sc851x_charger_remove,
        .shutdown = sc851x_charger_shutdown,
};
```

OF table entries are `sc,sc851x`, `sc,sc8510`, `sc,sc8517`, terminator. There
is no `MODULE_DEVICE_TABLE`, which explains the absent aliases. (`DAT`, `REL`)

The 6.1 callback slots and KCFI words prove legacy two-argument `.probe`, void
`.remove`, and one-argument `.shutdown`. (`DAT`, `KCFI`)

## D3 — private layout

Decision: probe allocates 576 bytes. Recovered member offsets:

| offset | member |
|---:|---|
| `0x000` | `struct device *dev` |
| `0x008` | `struct i2c_client *client` |
| `0x010` | `struct regmap *regmap` |
| `0x018` | 50 `struct regmap_field *` pointers |
| `0x1a8` | 35 contiguous `u32` DT configuration values |
| `0x234` | IRQ GPIO number (`int`) |
| `0x238` | IRQ number (`int`) |
| `0x23c..0x23f` | tail padding |

Evidence: allocation immediate `0x240`, pointer loads/stores, property target
addresses, IRQ accesses, and table loop limits. (`DIS`, `REL`)

## D4 — regmap and exact field map

Decision: 8-bit register, 8-bit value, maximum register `0x15`; 50 fields.

- `.rodata+0x0c0`, size 328, decodes as `struct regmap_config` with
  `reg_bits=8`, `val_bits=8`, `max_register=0x15`. (`DAT`)
- `.rodata+0x208`, size 1000 = 50 × 20-byte `struct reg_field`. (`SYM`, `DAT`)
- Every field's register/lsb/msb and use classification is frozen in
  `phase4-sc851x-register-fields.tsv`.
- 35 are written from DT, one (`REG_RST`, `0x06[3]`) is written as reset, and
  14 are allocated but never read/written by stock. (`REL`, `DAT`)

The 14 unused fields remain named `RSVD_*` in reconstruction; no silicon
semantics are invented.

## D5 — DT contract

Decision: all 35 `sc,sc851x,*` scalar properties are required. First missing
property terminates parsing and probe. IRQ is a separate required
`sc,sc851x,irq-gpio` GPIO specifier. (`REL`, `STR`)

The exact property order, field target, and GQ5012BF1 raw value are in
`phase4-sc851x-register-fields.tsv`. The live DT has all 35. (`DT`)

## D6 — initialization sequence

Decision, in exact observable order:

1. field-write `REG_RST` (`0x06[3]`) = 1;
2. log reset failure but continue;
3. `msleep(10)`;
4. write the 35 DT fields in table order using `regmap_field_write` semantics;
5. field-write helper logs its copy/paste text
   `"sc851x read field %d fail: %d"` and returns the error, but the table loop
   ignores it;
6. read and log registers `0x00..0x15`; return only the final read status.

Evidence is the relocation-aware inlined sequence in the 1924-byte probe,
including the 35-iteration field-write loop/call site, reset write, `msleep`,
22 register reads, and associated string relocations. (`DIS`, `REL`, `STR`)

No allocated field is used as a converter/direction/charging enable by this
driver. That negative is bounded to software behavior; an external hardware pin
or reset default is not ruled out.

## D7 — sysfs ABI

Decision:

```c
DEVICE_ATTR(registers, 0660,
            sc851x_show_registers, sc851x_store_register);
```

Show reads `0x00..0x15`, emits only successful reads. Store parses `%x %x` and
writes when two values are parsed and `reg <= 0x15`. (`DAT`, `DIS`, `STR`)

Stock ignores `device_create_file()`'s return and never calls
`device_remove_file()`. Preserve this even though it is poor cleanup. Debug
writes were not exercised.

## D8 — IRQ behavior

Decision:

- required legacy GPIO input, label `sc851x_irq`;
- `gpiod_to_irq(gpio_to_desc(gpio))`;
- threaded IRQ only, flags `IRQF_TRIGGER_FALLING | IRQF_ONESHOT`, name
  `sc851x-irq`;
- call `irq_set_irq_wake(irq, 1)` after request;
- handler logs `INT OCCURED`, then reads `0x0c`, `0x0d`, `0x0e`, logging
  `FLAG1`, `FLAG2`, `FLAG3` only for successful reads; returns `IRQ_HANDLED`.

It performs no explicit acknowledgement write and no policy notification.
(`DIS`, `REL`, `STR`)

## D9 — PM and shutdown

Decision:

- suspend: info log; if wakeup-capable set IRQ wake to 1; disable IRQ; return 0;
- resume: info log; if wakeup-capable set IRQ wake to 0; enable IRQ; return 0;
- shutdown: set `AUDIO_EN` (`0x06[2]`) to zero and print exact close message;
  ignore write result.

`AUDIO_EN` is the vendor's field name. Public material inspected does not define
its detailed electrical behavior; it must not be rewritten as speaker power or
uSmart enable. (`DIS`, `STR`)

## D10 — hardware identity

Decision: silicon selected by this board is SC8510.

- DT path label: `sc851x-charger@6f`.
- `compatible` bytes: `sc,sc8510\0`.
- `reg` bytes: `00 00 00 69`.
- parent `i2c@11e01000` becomes Linux bus 6.
- live device: `6-0069`, driver `sc851x`, IRQ thread `irq/57-sc851x-irq`.

Thus `@6f` is stale node naming and does not override `reg=<0x69>`. (`DT`,
`LIVE`)

## D11 — deliberately excluded functionality

Do not add:

- charger-class or power-supply registration;
- regulator, extcon, USB role, OTG, Type-C or uSmart hooks;
- mode/direction/converter-enable policy absent from stock;
- ADC or telemetry interface;
- workqueues, locks or notifier chains;
- IRQ fault decoding beyond three raw logs;
- DT defaults for missing required properties;
- safer sysfs permissions/validation or cleanup that changes stock behavior;
- OF `MODULE_DEVICE_TABLE` aliases absent from stock.

## D12 — acceptance criteria and result

Required:

1. exact defined function key set and function sizes;
2. exact KCFI type words;
3. byte-identical `.rodata`, `.data`, `.rodata.str1.1`, `__versions`,
   `.init.text`, `.exit.text`, and compiler `.comment`;
4. exact 30 import names and CRCs; zero unresolved symbols;
5. exact relocation section/count and target/type sequence;
6. exact-GKI `BUILD_RC=0`, zero compiler warnings;
7. all observed calls, register operations, log strings, and failure behavior
   represented without added framework behavior.

Result: **PASS**. `workspace/phase4-sc851x/verify-recon-vs-stock.txt` records:

- 11/11 function sizes and all KCFI words exact;
- 8/9 behavioral `.text` functions byte-identical;
- probe size exact (1924) and all 215 `.rela.text` target/type entries in exact
  sequence;
- `.rodata`, `.data`, strings and `__versions` byte-identical;
- residual `.text` bytes are compiler-local stack/register scheduling in the
  inlined probe plus an equivalent unsigned GPIO range comparison;
- only module metadata delta is local GKI SCM suffix in `vermagic`;
- build succeeds with no warning or unresolved symbol.

This residual is reported, not rounded up to byte identity.
