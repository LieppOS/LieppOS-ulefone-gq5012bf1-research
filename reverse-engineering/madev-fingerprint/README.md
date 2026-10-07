# MADEV-FINGERPRINT — closure (2026-10-07, static)

Workspace component: `Reverse Engineer - PARTIAL/MADEV-FINGERPRINT` → **DONE**.

## Selection log

SELECTED TARGET: `MADEV-FINGERPRINT`. VERIFIED: present in `Reverse Engineer - PARTIAL/`,
and the status index lists it as PARTIAL.

WHY: this is the remaining Linux piece of the fingerprint stack, the YFT board
glue `fingerprint.ko`. Its consumer, `MICROARRAY-FP-TEE`, closed byte-identical
the same day. Re-measured today, the existing reconstruction already had 16/16
function bodies byte-equal and was blocked only by bookkeeping.

CURRENT BLOCKERS (as recorded): "sensor protocol, templates/TA behaviour and
complete stock-free stack". Implicit: the reconstruction was "behavioural".
Measured whole-module parity was 6/16 functions with identical relocations,
`.rodata.str1.1` and the symbol table differed, and 1 746 bytes differed in total.

## Scope

`fingerprint.ko` (YFT `yft_finger` platform driver, author `Jay_zhou`, "for yft
fingerprint driver"): DT pinctrl/GPIO/IRQ provider, the ten exported board
controls, and their single consumer `microarray_fp_tee.ko`. It also covers how
the whole fingerprint stack is layered:

```
Android biometrics → AIDL service (…fingerprint-service.example, "Fingerprint HAL started - Microarray")
 → microarray.fingerprint.default.so → libfprint-x64.so (TEEC_*, /dev/madev0)
 → TA edcf9395-…  (secure world, TrustKernel)                         [external boundary]
 → microarray_fp_tee.ko  (/dev/madev0, SPI, IRQ, chip ID via tee_spi_transfer) [DONE: MICROARRAY-FP-TEE]
 → fingerprint.ko        (pinctrl/GPIO/IRQ board glue)                 [this component]
 → spi-mt65xx.ko [DONE: SPI-MT65XX], tkcore.ko [TRUSTKERNEL-TEE, BLOCKED]
```

## Result

| item | result |
|---|---|
| lineage | **BINARY-EQUIVALENT RECONSTRUCTION**, no public donor (YFT-private glue). Byte-identical except build-id. |
| B1 == B2 | `.ko`, stripped `.ko`, `.o` byte-identical (`parity/b1-b2-build.txt`) |
| stock (`f5d4dde1…`, 30 552 B) vs rebuild (stripped) | same size, **20 differing bytes, all `.note.gnu.build-id`** (`parity/fingerprint-parity.txt`) |
| detail | 16/16 functions (bytes, relocations, KCFI), 35/35 data, `__versions` 18/18, 10/10 export CRCs, modinfo, `.rodata.str1.1`, 41 section headers, ordered symtab 193/193 |
| consumer edge | `microarray_fp_tee.ko` imports `yft_finger_set_reset`, `_set_spi_mode`, `_set_irq` and `yft_waite_for_finger_dts_paser`. All four CRCs equal the provider's. |
| integration | 11/11 PASS (`evidence/integration-checks.txt`) |

Two corrections closed the gap left by the earlier reconstruction:
1. Five `pr_err`/`printk` format strings carry **no trailing `\n`** in stock (for
   example `"err: yft_finger_int_as_gpio is error!!!!"`). With the `\n`, the
   strings are 5 bytes longer, so lld places them in different shard positions.
   That changed the string table and every relocation pointing into it.
2. Stock `__COUNTER__` at `module_init` is 405, while the minimal include set
   gives 384, so `__UNIQUE_ID_*` symbol names differed. The source now adds
   `<linux/spi/spi.h>` (+19) and `<linux/compat.h>` (+2). **The exact stock
   include set is not uniquely recoverable.** Any set that adds 21 produces the
   same bytes (e.g. `spi.h` + `dma-mapping.h`), and this is declared.

## Behaviour (unchanged from the earlier contract notes, now byte-backed)

* Probe (`yft_finger` platform driver, OF `mediatek,yft_finger`):
  * `devm_pinctrl_get`, then 13 `pinctrl_lookup_state` calls:
    `finger_reset_en0/1`, `finger_spi0_{mi,mo,clk,cs}_as_{spi0_*,gpio}`,
    `finger_eint_pull_{down,up,dis}`.
  * `finger_power_en0/1` exist in DT but are never looked up ("no need
    finger_power_en"). `yft_finger_set_power` is a logging no-op returning 0.
  * Afterwards it sets `yft_finger_plat` and wakes `finger_init_waiter`.
* `yft_waite_for_finger_dts_paser()` waits interruptibly with a timeout until
  the platform probe has run. The consumer calls it first.
* `set_reset(v)` selects reset_en1/en0 and `set_irq(v)` selects
  eint_pull_up/down (dis otherwise). `set_spi_mode(1)` switches all four SPI
  pads to the SPI function; any other value selects GPIO.
* The IRQ number comes from `irq_of_parse_and_map(/yft_finger, 0)`; GPIOs come
  from `int-gpio` (GPIO3) and `reset-gpio` (GPIO30).
* No sysfs, PM, char device, SPI transfer or TEE call.

## Boundaries (external, not blocking)

* The secure world (MicroArray TA `edcf9395-…`, templates, matching) and the
  proprietary HAL/`libfprint-x64.so` internals. The Linux-visible ABI they use
  (`/dev/madev0` ioctl/read/write/mmap) is closed in MICROARRAY-FP-TEE.
* `tkcore.ko` (TRUSTKERNEL-TEE, BLOCKED). Its FP/SPI exports reproduce from
  public TrustKernel `core/`.
* Runtime enrol/match qualification.

## Stock quirks (reproduced)

* `init.yft.rc` chowns/chmods `/sys/bus/platform/drivers/yft_finger/tplcd_pattern`,
  which this module never creates (stale variant-common rc line).
* Public misspelling `yft_waite_for_finger_dts_paser` is ABI and kept.
* Error strings lack newlines (log lines may merge in dmesg).

## LieppOS contract

Build with `scripts/build_b1_b2.sh` (exact GKI 12901745 out-tree). The result
is a drop-in replacement for stock (build-id aside). Keep the `/yft_finger` DT
node with all 16 pinctrl states and the first-stage load order
`fingerprint.ko` → `microarray_fp_tee.ko`.

## Files

* `source/fingerprint.c` and `source/Makefile`.
* `scripts/`:
  * `build_b1_b2.sh`;
  * `ko_parity.py` (generic, from microarray-fp-tee), with `elfmini.py` and `fdis.py`;
  * `fp_integration.py`.
* `parity/`: `b1-b2-build.txt`, `fingerprint-parity.{txt,tsv}`.
* `evidence/integration-checks.txt`.
* `stale-claims.md`, `STATUS.md`.
