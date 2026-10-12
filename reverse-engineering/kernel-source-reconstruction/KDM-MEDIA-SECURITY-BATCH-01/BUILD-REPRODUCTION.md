# Build reproduction

## Development (quarantined, not deleted)

`/home/armol/kernel-work/kdm-media-security-batch-01/dev` was renamed to `quarantined-development` before the proof.
Its experiments are recorded in `evidence/development/`:

| Run | Inputs | Result |
|---|---|---|
| D1 | ALPS + NothingOSS config, 11 targets | object exit 2: `flashlight-core.c` does not compile with `CONFIG_MTK_FLASHLIGHT_PT` unset (pt_* used outside the `#ifdef` in `fl_parse_dt`). The other 10 objects built; 36/36 provider witnesses exact |
| X1 (experiment) | + `CONFIG_MTK_FLASHLIGHT_PT=y` (config `df2c3ae2…`) and a hand-added `register_battery_oc_notify` symvers line (stock CRC 0xfcab3894) | 11/11 linked. Per-module unchanged verifier: 9/11 PASS. mtk_irtx_pwm failed (stock-only `dma-mask-bit` code), and flashlight failed (OEM variant). **Neither change is kept**: the config and the symvers line were reverted, and their artefacts are evidence only |
| D3 | committed recipe 79a7d92 (10 owned targets + irtx delta, config b826d842) | object/module exit 0, 10/10 whole-file PASS, 131/131 mutation controls; then pinned trees → repo 973eb04a |

## Independent proof (`scripts/prove-fresh.sh`)

`EXPECT_COMMIT=973eb04a… prove-fresh.sh B1 56-59` and `… B2 60-63` ran in parallel, each at nice 10 with JOBS=4. Each:

1. took a fresh `--no-hardlinks` clone of `bundles/kdm-media-security.bundle`, with fsck and bundle verify;
2. bootstrapped offline from the read-only pin mirror;
3. ran `bulk-build.sh` (which builds its own kout), then the unchanged strict `verify.py` with ledgers and
   `mutation-test.py`.

| Check | B1 | B2 | B1 vs B2 |
|---|---|---|---|
| object / native / module exit | 0 / 0 / 0 | 0 / 0 / 0 | — |
| provider witnesses | 32/32 | 32/32 | identical natural symvers |
| whole-file acceptance | 10/10 | 10/10 | identical normalized hashes |
| ELF mutation controls | 131/131 | 131/131 | — |
| raw + stripped .ko (20 files) | — | — | byte-identical, and equal to D3 |
| intermediates (80) | — | — | byte-identical |
| vendor `.config` | b826d842 | b826d842 | identical |
| joint-extra / batch Module.symvers | — | — | identical (path-mapped for the batch file) |
| assembled / target source trees | b8c0bdb8 / 24288c4f | same | equal to `reference/` |

The stock operands are a read-only flat copy of the 11 frozen targets. They were taken from a private copy of all
471 stock occurrences, whose sha256 list equals canonical.
