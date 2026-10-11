# Committed-source independent reconstruction protocol

Frozen manifest c8c1b58b, development research57191371. Source engine checkpoints: diagnostics5f4031c2935f167893dbb8e74577cff22baa44e9; METad786ee91d2e893add1fe3d496d8d463a54d9ed5. All22 independent source gates now PASS. Final locked build-engine commits are diagnostics694b9db8c0a6f50b7381a14f55999bf313e11ec4 and MET7839af7c1d400879bdf18c9c53edba0a675b3772. Initial fresh proof correctly rejected one native-vDSO preparation DWARF path discrepancy; failed proof/workspaces remain at evidence/independent-proof-failed01 and /home/armol/kernel-work/next-dg-batch-01/failed-proof-01. Compiler KCFLAGS mapping during actual preparation fixes it; repeat fullyfresh B1/B2 succeeds without waivers.

Final results:44 whole-stock A gates,44 raw/stripped file pairs,298 target/provider/preparation object pairs (119diagnostics+179MET),108 actual external export-slot records, identical source/config/natural symvers and550 real mutation controls (162+162diagnostics,113+113MET). Both authenticated bundles recovered exact commits/fsck/no alternates. evidence/independent-proof/RESULT.json records actual PASS.

## Inputs and strict isolation

Four allowed CPUs60–63, JOBS4, nice>=10. No ADB/device/network/push. GIT_NO_LAZY_FETCH=1, GIT_ALLOW_PROTOCOL=file prevent implicit promisor/public fetches. Exact public pin commit/tree and compiler provenance in each maintained SOURCE-PINS.tsv. Offline complete interconnect-pin-mirror supplies common/kdm/alps5e41/clang tar/public GKI core symvers; public-mtk/nkm.git supplies the complete exact5f75 MET tree. These existing mirrors are read-only. No reset/checkout of an existing validated source repo.

Original development dirs renamed, not symlinked/reused:
`/home/armol/kernel-work/next-dg-batch-01/dev/{diagnostics,met}` → `quarantined-development/{diagnostics,met}`. Only this assignment's directories move. Exact compile attempts/raw outputs/logs/providers/configs/source remain there; original pathname must not exist when independent recipes run. Private reference stock links point only to authentic separately copied read-only471-occurrence inventory in the next-dg worktree, not damaged shared files. Inventory validator passed before development.

## Actual automated proof

`scripts/prove-fresh.py` executes sequentially diagnosticsB1, diagnosticsB2, METB1, METB2. Every tag has a separate --no-hardlinks source Git clone at the committed exact tip, no alternates, new source/common/Kconfig/compiler recovery and new private workspace. A prior failed bootstrap cannot masquerade as a fresh independent run. It never copies a prepared development/common/kout/src/provider tree.

Each build creates genuine source objects → natural provider CRC/KCFI/license/namespace/type witnesses → natural target/module symvers and links → raw .ko → explicit separate-output llvm-strip. GKI/vendored Kbuild naturally emits srcversion/modinfo/ELF/symbols/relocations. No post-link modification except ordinary strip-debug into another output. No stock ELF machine code/data/metadata introduced.

Every22 target undergoes actual unchanged complete-file acceptance (build-ID descriptor only) and full per-function/data/BSS/section/symbol/string/ABI/KCFI/raw+semantic relocation ledger emission. Actual mutation controls run every owned module for unchanged positive, text/data/rodata/import-export CRC/modinfo/relocation/symbol/section-header/function KCFI-prefix/signature trailer/GNU-note header and sole accepted GNU20 descriptor.

B1/B2 compare actual bytes/hashes of ALL raw/stripped module files, every actual target/provider object and **all preparation objects under kout**, generated configs, actual assembled-source tree IDs and raw natural Module.symvers rows with only explicit workspace spelling in producer column mapped. No CRC/license/namespace/type values or empty final namespace columns are normalized. Provider object SHA checked against actual files after each build. Failed mismatches must be preserved/resolved, not removed from the object proof.

Authenticated source bundles created and verified; separate bundle-recovery fresh clones have exact committed tip, no alternates and full fsck. Maintained source repositories stay clean. Full recovery recipes/docs/license attribution are committed.

Output root `/home/armol/kernel-work/next-dg-batch-01/proof/`; durable source clone/bootstrap/build/mutation/stock acceptance/provider/object/source/config/symvers/driver progress records and bundles under evidence/independent-proof/. RESULT.json exists only after BOTH families pass every real check. The preserved driver prints per-tag and per-family completion; check it, never infer a completed B2 from a successful D3 or compiled wrapper.

Invocation (works only in this isolated researched environment with reviewed local input mirrors):
```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/prove-fresh.py
```

For a new machine, first use maintained README's offline mirror export/pin validation and supply authenticated stock operands. No hidden dependence on transient original development dirs. No live canonical audit changes until an owner explicitly reconciles a validated field-only proposal after Claude finishes.
