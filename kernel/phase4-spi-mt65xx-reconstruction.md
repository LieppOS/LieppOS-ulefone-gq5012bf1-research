# GQ5012BF1 `spi-mt65xx` provider reconstruction

## Final verdict

- **Classification:** `DIRECT_SOURCE_MATCH`
- **FROZEN FOR RE:** **YES**
- **Static/offline closure:** PASS
- **Runtime stock dependency changed:** only `spi-mt65xx`; `tkcore` remains the stock runtime provider

The stock MediaTek SPI provider is source-closed by the exact pinned Nothing
MT6878 `device_modules` source. All three provider export CRCs arise naturally
from real C, the pinned vendor header, genksyms, and exact GKI ab/12901745. No
stock CRC or witness symvers is an input to the provider build.

## Oracle and placement

Canonical stock module:
`workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/spi-mt65xx.ko`

| property | stock value |
|---|---|
| SHA256 | `5463e06c205623e4b1b713416836e3b5235dc246c7d536595f6613ba3492d712` |
| size | 58144 bytes |
| build ID | `21ef9cb7c85ae00c724cf0f2fadca17f610de905` |
| compiler | Android clang 17.0.2, r487747c (`d9f89f4d1666`) |
| vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| name / description | `spi_mt65xx` / `MTK SPI Controller driver` |
| author / license | `Leilk Liu <leilk.liu@mediatek.com>` / `GPL v2` |
| dependencies | none |
| placement | vendor_boot platform ramdisk |
| normal / recovery load index | P:119 (line 120) / R:117 (line 118) |

The committed 471-placement stock extraction contains one physical payload;
normal and recovery lists reference that same byte-identical module.

## Source and build

Exact source revision:
`device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f`.

Source of record:
`/home/armol/kernel-work/gki-12901745-workspace/lieppos/spi-mt65xx/`.
The research mirror is `workspace/phase4-spi-mt65xx/source/`.

The C is the donor byte stream except for one permitted include-path redirect
to the byte-identical pinned vendor `spi-mt65xx.h`. This is required because
GKI Common's same-path header lacks three vendor `struct mtk_chip_config`
members. No declaration or executable statement changes.

```
tools/bazel build //lieppos/spi-mt65xx:spi_mt65xx
```

`BUILD_RC=0`; compiler warnings 0; modpost warnings 0; unresolved symbols 0.
The provider has no `KBUILD_EXTRA_SYMBOLS`, `KBUILD_MODPOST_WARN`, copied
`__versions`, CRC injection, fake provider, or ELF patching.

## Complete parity

| surface | stock | rebuilt | result |
|---|---:|---:|---|
| defined functions | 31 | 31 | 31 size-identical; 31 byte-identical |
| applicable KCFI IDs | 31 | 31 | 31/31 exact |
| kernel imports | 65 | 65 | exact names and CRCs |
| MODVERSION records | 66 | 66 | 66/66 exact |
| exports | 3 | 3 | names, classes, and natural CRCs exact |
| objects | 60 | 60 | all functional objects exact |
| relocations | 545 | 545 | exact in final target |
| strings | 120 | 120 | functional set exact; two provenance strings differ |

Complete natural export surface:

| symbol | stock CRC | rebuilt CRC | class | consumers |
|---|---|---|---|---|
| `mtk_spi_set_autosuspend_delay` | `0xd3e99558` | `0xd3e99558` | `EXPORT_SYMBOL` | none in stock population |
| `mt_spi_disable_master_clk` | `0xccc1e350` | `0xccc1e350` | `EXPORT_SYMBOL` | `microarray_fp_tee` |
| `mt_spi_enable_master_clk` | `0x1cc49782` | `0x1cc49782` | `EXPORT_SYMBOL` | `microarray_fp_tee` |

A full scan of all 471 stock `.ko` placements found exactly one consumer and
two edges. Provider P:119/R:117 precedes `microarray_fp_tee` P:182/R:186.

## MT6878 hardware and behavior closure

All eight controllers (`0x11010000`–`0x11017000`) bind
`mediatek,mt6989-spi`, selecting `mt6989_compat`: pad-select, enhanced timing,
36-bit DMA, IPM/quad/software-CS, and enhanced packet length are enabled;
must-RX/must-TX are false. SPI1 at `0x11011000`, IRQ cell `0x1cc`, is the
MicroArray controller. It uses `univpll`, three named clocks, pad 0, tick delay
2, `cs-gpios`, `tee-only`, and an 8 MHz `mediatek,madev_finger` child.
`tee-only` suppresses the controller `set_cs` callback.

The MicroArray clock exports are exactly `void (struct spi_device *)`, KCFI
`0xe397d461`. Enable calls only `clk_prepare_enable(ms->spi_clk)` and silently
discards its result; disable calls only `clk_disable_unprepare`. Neither adds
runtime-PM, locking, validation, or another clock operation.

Runtime PM defaults to 10 ms autosuspend on this DT. SPI1's univpll path uses
`clk_disable_unprepare`/`clk_prepare_enable`; mainpll uses disable/enable after
one-time prepare. The autosuspend export stores a changed `u32` delay and
applies it on the next resume. Transfer behavior closes PIO (32-byte FIFO,
200000-us polling), scatterlist DMA with 36-bit addresses, IRQ completion, IPM
SPI-memory operations, packet constraints, reset/error paths, and MT6989
CFG5 enhanced-length handling. Full contracts are in the dedicated reports.

## MicroArray acceptance and provider boundary

The frozen 27-function MicroArray source was rebuilt without behavioral
changes against:

- real source-built `fingerprint` symvers;
- real source-built `spi-mt65xx` symvers;
- the remaining stock-runtime `tkcore` ABI record for `tee_spi_transfer`.

Result: build RC 0, zero compiler/modpost warnings, zero unresolved symbols,
27/27 function set exact, exact `depends`, and 66/66 stock MODVERSION edges.
Provenance is now 65 natural edges, including **2 `NATURAL_SPI_PROVIDER`**
edges, plus 1 `STOCK_PROVIDER_WITNESS` runtime edge (`tee_spi_transfer`).
The separate tkcore ABI work naturally regenerates that symbol's type/CRC as
evidence, but tkcore is not reconstructed or replaced.

## Residual classification

Rebuilt size is 57936 bytes, SHA256
`1086283207ab8acb89c8e505aff408105e634840d0d1ce08c7a1d2721fe259f0`, build
ID `7cc4a1a17f13ae844f7439eca724aaf50b5ab114`. The only four non-byte-identical
object/section rows are `BUILD_PROVENANCE_ONLY`: vermagic unique object,
`.modinfo`, the `__FILE__` source-path string section, and link build ID.
There is no unexplained Linux-visible residual. Deployment must stamp the
LieppOS kernel/module release consistently; static RE is complete.

## Verification

```
python3 kernel/scripts/phase4_spi_mt65xx_verify.py
```

Result: **82/82 CHECKS PASSED**. Supporting evidence includes the frozen
oracle, complete ELF TSVs, mandatory RED, consumer/export ABI tables,
function/object parity tables, source lineage, DT/type/clock/PM/transfer/register
contracts, MicroArray acceptance JSON, and build logs under
`workspace/phase4-spi-mt65xx/`.

**FROZEN FOR RE: YES**
