# `gz_tz_system` acceptance against real GenieZone providers

## Acceptance construction

The frozen `gz_tz_system` C behavior was not changed. A narrow acceptance copy was made only in the GKI workspace:

- deleted `stock-provider.symvers`;
- deleted `stock-provider.provenance.json`;
- removed both files from `BUILD.bazel`;
- replaced the witness `KBUILD_EXTRA_SYMBOLS` path with the real source-built transport `Module.symvers`;
- added a Kleaf dependency on `//kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/gz-trusty:gz_transport`.

A pre-build listing proved **no `stock-provider*` file existed** in the acceptance package.

Target: `//lieppos/gz-tz-system-accept:gz_tz_system_accept`

## Build result

- `BUILD_RC=0`
- compiler warnings: 0
- modpost warnings: 0
- unresolved symbols: 0
- `KBUILD_MODPOST_WARN`: absent

Frozen build log: `workspace/phase4-gz-transport/build/logs/gz-tz-system-acceptance-build.log`.

## Seven provider edges

| Provider | Count | Result |
|---|---:|---|
| source-built `gz_ipc_mod` | 5/5 | `tipc_k_connect`, `tipc_k_disconnect`, `tipc_k_read`, `tipc_k_write`, `port_lookup_tid` CRCs exact and natural |
| source-built `gz_trusty_mod` | 2/2 | `trusty_std_call32`, `trusty_enqueue_nop` CRCs exact and natural |

Machine evidence: `phase4-gz-transport-gz-tz-system-acceptance.tsv`.

## Frozen behavior parity

| Check | Stock | Acceptance | Result |
|---|---:|---:|---|
| functions | 61 | 61 | 61/61 shared; 0 missing; 0 extra |
| sizes | 61 | 61 | **61/61 identical** |
| bytes | 61 | 61 | **61/61 identical** |
| KCFI | 61 | 61 | **61/61 exact** |
| imports | 50 | 50 | **identical** |
| MODVERSIONs | 51 | 51 | **identical** |
| exports | 27 | 27 | **27/27 natural CRCs** |
| relocations | 1082 | 1082 | **all semantic records identical** |
| string inventory | 106 | 106 | **identical** (100 unique values) |
| module name/depends/license/aliases | — | — | identical |

Stock SHA/size/Build ID: `4b29f9b...e38`, 79,648, `dcba5910...b1a`.
Acceptance SHA/size/Build ID: `71ad6e33...986`, 79,632, `f4f80e67...12c`.

The whole-ELF difference is build provenance only: local `maybe-dirty` vermagic versus stock `g945dff7bc1bf`, Build ID, and associated LLVM/module-layout metadata. No function, KCFI, import, MODVERSION, export, relocation, or behavior changed. The frozen `gz_tz_system` classification is not reopened.

## Provenance transition

```text
BEFORE: 43 GKI_NATURAL + 5 GZ_IPC_STOCK_RUNTIME + 2 GZ_TRUSTY_STOCK_RUNTIME
AFTER:  43 GKI_NATURAL + 5 GZ_IPC_NATURAL       + 2 GZ_TRUSTY_NATURAL
```

**Acceptance: PASS.**
