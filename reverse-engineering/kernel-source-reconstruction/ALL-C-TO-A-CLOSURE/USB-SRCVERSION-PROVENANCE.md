# USB source fingerprints — genuine token provenance remains open

No USB identity is promoted by this checkpoint. The latest USB-TYPEC-CLOSURE source
and 709/709-function TCPC reconstruction are retained. Fingerprints are neither rewritten
nor normalized, and no dummy counter users or declaration deletions are introduced.

`evidence/srcversion/sumversion-probe.c` wraps the unmodified pinned kernel
`scripts/mod/sumversion.c`. It calls the actual `parse_file`/MD4 implementation in the
same-directory dependency order established by earlier modpost read traces. It does not
hash a guessed preprocessor stream or synthesize a requested srcversion.

## Bounded public-history search

`srcversion-history-scan.py` collects coherent source/header snapshots from all fetched
refs and then varies one file at a time. For modules with more than two inputs this is
**not** the complete Cartesian product of all versions. Results are bounded to the
recorded fetched histories, not proof that no public or OEM matching source can exist.

| Module | NothingOSS tests | MiCode tests | Stock srcversion | Hits |
|---|---:|---:|---|---:|
| charger_class | 120 | 525 | E4A92CD3F20A3D2142F16B6 | 0 |
| mtk_chg_type_det | 940 | 3857 | F7A2E5433A38379D631644F | 0 |
| rt_pd_manager | 13 | 25 | C4301583FE25F39BA52E75D | 0 |
| tcpc_mt6375 | 27 | 36 | D27BCF95DDC8F09B632224B | 0 |

Totals: 1100 + 4443 candidate combinations, 0 hits. These tests do not include tcpc_class's
larger multi-object token set. That identity retains its already documented trace/residual;
it must not be represented as covered by this four-module scan.

The scanner and JSON/log results are preserved. Its ordered inputs come from the latest
USB closure read traces, not the older Batch04 source. For ST21 NFC the same fingerprint
method separately tested 20 NothingOSS and 28 MiCode pairs, also without a stock hit.

Next action: recover a new authentic OEM/ODM token stream, or a demonstrated new input
composition justified by actual modpost dependency traces. Mere extra whitespace/comments
or manipulating output metadata is not a closure experiment.
