# MicroArray fingerprint TEE — reconstruction report

Consumer module `microarray_fp_tee.ko` for Ulefone Armor 29 Pro Thermal
(`GQ5012BF1`, MT6878/MT6878T), reconstructed clean-room from the frozen stock
oracle and built against the exact GKI.

## Completion classification

**BEHAVIOURALLY-COMPLETE, LOAD-COMPATIBLE, WITH DECLARED ABI PROVENANCE SPLIT.**

- Every Linux-side behaviour the stock binary exhibits is recovered and
  reimplemented; nothing is left as a guess.
- Post-`spi-mt65xx` closure, 65/66 MODVERSION edges have natural ABI
  provenance; the two SPI edges now come from the real source-built provider.
- One edge, `tee_spi_transfer`, remains a stock-runtime `tkcore` witness.
- The acceptance target reaches 66/66 exact MODVERSION parity and exact
  `depends` without changing MicroArray behavior.
- Secure-world internals remain opaque and are classified, not invented.

## Artefacts

| artefact | sha256 | size |
|---|---|---|
| stock oracle `microarray_fp_tee.stock.ko` | `8e1449cea5d07ef663d368ce5eea27e8c879a9cd70d39f8fc2b5b25445c2cf33` | 69296 |
| natural build `microarray_fp_tee.recon.ko` | `a34840ae46f581820093d3bbca3f05c0084503b21898de1004adef3cb4a39f29` | 69688 |
| stock-ABI build `microarray_fp_tee.recon-stockabi.ko` | `08e57d1f8aa11854f97574ca77e031bb573be0392789fb5846d0549c25db8ad7` | 69688 |

Source of record (single copy, shared by both targets):
`/home/armol/kernel-work/gki-12901745-workspace/lieppos/microarray-fp-tee-recon/microarray_fp_tee.c`
(the stock-ABI package holds a symlink, not a second copy).

## Build targets

```
tools/bazel build \
  //lieppos/microarray-fp-tee-recon:microarray_fp_tee_recon \
  //lieppos/microarray-fp-tee-recon-stockabi:microarray_fp_tee_recon_stockabi
```

| target | provider symvers inputs | MODVERSION result |
|---|---|---|
| `microarray_fp_tee_recon` | historical natural-evidence target | historical 63 NATURAL + 3 declared `PROVIDER_ABI_GAP` |
| `microarray_fp_tee_recon_stockabi` | real source-built `fingerprint-recon`, real source-built `spi-mt65xx`, plus stock-runtime tkcore ABI record | **65 NATURAL + 1 `STOCK_PROVIDER_WITNESS` = 66/66 exact** |

Both builds: `BUILD_RC = 0`, zero compiler warnings, zero modpost warnings,
zero unresolved symbols, no `KBUILD_MODPOST_WARN`.

Build environment note: this workspace's kernel targets capture `TMPDIR` into
`kernel_aarch64_env.sh`; builds must be run with a `TMPDIR` that still exists.
Builds for this phase were run pinned to 32 threads on NUMA nodes 0 and 2
(`taskset -c 0-15,32-47`, `--local_cpu_resources=32 --jobs=32`) so the local LLM
keeps nodes 1 and 3.

## Parity against the stock oracle

| check | result |
|---|---|
| defined function set | **27/27 exact**, no missing, no extra |
| `MODULE_AUTHOR` | exact — `Microarray` |
| `MODULE_DESCRIPTION` | exact — `Driver for microarray fingerprint sensor` |
| `MODULE_LICENSE` | exact — `GPL` |
| module name | exact — `microarray_fp_tee` |
| OF aliases | exact — `of:N*T*Cmediatek,madev_finger`, `of:N*T*Cmediatek,madev_fingerC*` |
| `depends` | stock-ABI target **exact** (`fingerprint,spi-mt65xx,tkcore`); natural target carries the witness module names, declared |
| MODVERSION table | see the provenance split |
| `vermagic` | base release `6.1.115-android14-11` exact; scmversion stamp differs (see below) |

Function set recovered and reimplemented: `mas_select_transfer`,
`ma_spi_change`, `mas_remove_platform`, `mas_switch_power`,
`mas_finger_set_gpio_info`, `mas_enable_spi_clock`, `mas_disable_spi_clock`,
`mas_get_irq`, `mas_sync`, `mas_mmap`, `init_connect`, `deinit_connect`,
`mas_plat_probe`, `mas_plat_remove`, `mas_probe`, `mas_set_input`,
`mas_remove`, `mas_work`, `mas_interrupt`, `mas_read`, `mas_write`,
`mas_ioctl`, `mas_compat_ioctl`, `chip_id_show`, `mas_get_platform`,
`init_module`, `cleanup_module`. Static/global linkage matches stock per
symbol (only `mas_set_input`, `mas_work`, `mas_interrupt`, `mas_read`,
`mas_write`, `mas_ioctl`, `mas_compat_ioctl`, `chip_id_show` are local).

## ABI provenance — the required statement

- **65/66 MODVERSION edges have natural ABI provenance**: 59 exact-GKI
  exports, four real source-built `fingerprint` edges, and the two real
  source-built `spi-mt65xx` edges.
- `mt_spi_enable_master_clk` (`0x1cc49782`) and
  `mt_spi_disable_master_clk` (`0xccc1e350`) changed from
  `STOCK_PROVIDER_WITNESS` to **`NATURAL_SPI_PROVIDER`**.
- **1/66 remains `STOCK_PROVIDER_WITNESS`**: `tee_spi_transfer` from runtime
  stock `tkcore`. Separate tkcore work proves its natural ABI type/CRC, but
  tkcore itself remains `NOT RECONSTRUCTED / STOCK RUNTIME PROVIDER`.
- **The acceptance target reaches 66/66 exact.** The MicroArray behavior and
  source did not change.

Full per-symbol detail, the decisive control experiment, extraction method and
provider ELF hashes: `phase4-microarray-fp-tee-abi-provenance.md`.

## Behaviour

Full recovered contract — ioctl table with its holes, read/write clamps and
return-value quirks, mmap protection bits, the `tee_spi_transfer` TEEC ABI and
TA UUID, the five-step chip identification sequence, input/IRQ/work/power/probe
ordering, and the explicit unprovable list — is in
`phase4-microarray-fp-tee-behavior.md`.

Key architectural facts preserved exactly:

- The data path is **hybrid**: probe-time chip identification goes exclusively
  through TrustKernel `tee_spi_transfer`; all runtime `read`/`write` traffic
  goes through normal-world `spi_sync` under `dev_lock`. Neither substitutes for
  the other, and `tee_spi_transfer` was never replaced by a generic TEE call or
  a direct SPI transfer.
- `fingerprint.ko` → `microarray_fp_tee.ko` load adjacency is preserved
  (`modules.load` lines 182/183, recovery 186/187).
- The 80-byte secure-world configuration blob is reproduced byte for byte; its
  field semantics are classified UNPROVABLE rather than guessed.

## Known declared deltas

| delta | scope | status |
|---|---|---|
| `tee_spi_transfer` still uses stock runtime tkcore ABI | acceptance target | tkcore is not reconstructed; keep stock runtime provider |
| historical natural target's `depends` names ABI witness modules | historical target only | acceptance target has exact provider names |
| `vermagic` scmversion stamp is `-maybe-dirty`, stock is `-g945dff7bc1bf` | **workspace-wide**, identical for the already-accepted `fingerprint.ko` reconstruction | GKI commit `945dff7bc1bf` is not present in this mirror (`common` is clean at `6b18f0b574ab`, tag `android14-6.1-2024-12_r4`); a correct stamp requires `--config=stamp` against that commit, or the LieppOS kernel's own stamp at deployment |

The vermagic delta blocks loading against a *stock* kernel image, equally for
every LieppOS reconstruction, and is resolved at ROM build time, not here.

## Verification

```
python3 tools/phase4-microarray-fp-tee-verify.py \
  --stock  workspace/phase4-microarray-fp-tee/oracle/microarray_fp_tee.stock.ko \
  --recon  workspace/phase4-microarray-fp-tee/build/microarray_fp_tee.recon.ko \
  --accept-build-stamp-delta --expect-provider-abi-gaps \
  --json   workspace/phase4-microarray-fp-tee/build/verify-natural.json

python3 tools/phase4-microarray-fp-tee-verify.py \
  --stock workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/microarray_fp_tee.ko \
  --recon workspace/phase4-spi-mt65xx/acceptance/microarray_fp_tee.ko \
  --natural-provider workspace/phase4-spi-mt65xx/build/spi-mt65xx.ko \
  --provider workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/tkcore.ko \
  --allow-stock-provider-edges --accept-build-stamp-delta \
  --json workspace/phase4-spi-mt65xx/acceptance/verify.json
```

The historical natural-evidence run and the current acceptance run return
`PASS_WITH_DECLARED_DELTAS` with empty failure lists. The current run records
65 natural edges (two `NATURAL_PROVIDER`) and one stock-runtime witness.

## Provenance of the source

No donor source exists. See `phase4-microarray-fp-tee-source-candidates.md`
(`NO_USEFUL_SOURCE`) and `phase4-microarray-fp-tee-RED.md` (`EMPTY-SOURCE RED`).
The reconstruction is clean-room from the frozen oracle, the frozen device tree,
and the stock userspace binaries.

## Scope boundaries honoured

- `tkcore` was not reconstructed or replaced. Stock ABI is used for runtime
  `tkcore`; `tee_spi_transfer` was never replaced.
- `fingerprint.ko` and MicroArray behavior were not reopened; their existing
  source and real provider symvers are reused.
- `spi-mt65xx` is now source-closed separately as `DIRECT_SOURCE_MATCH`; only
  the two SPI ABI inputs changed provenance.
- No connectivity, panel/provider, `yft_devinfo` or uSmart work was touched.
- Static/offline only: no device interaction, module loading, SPI/TEE calls,
  fingerprint operations, flashing or rebooting.
