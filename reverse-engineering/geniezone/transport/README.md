# GenieZone transport (gz-trusty) — whole-stack static closure

All five stock modules built from `drivers/misc/mediatek/geniezone/gz-trusty`
rebuild **byte-identical to stock except `.note.gnu.build-id`** from unmodified
MTK ALPS mt6878 `5e415e059253`, and two independent rebuilds are identical.

| module | functions | data | imports (CRC, order) | exports (CRC) | KCFI | relocations | strings | sections |
|---|---|---|---|---|---|---|---|---|
| `gz_trusty_mod.ko` | 33/33 | 22/22 | 60/60 ✓ | 14/14 | 33/33 | 553/553 | 78/78 | 52/53 (build-id) |
| `gz_ipc_mod.ko` | 43/43 | 36/36 | 82/82 ✓ | 15/15 | 43/43 | 1003/1003 | 105/105 | 47/48 (build-id) |
| `gz_irq_mod.ko` | 12/12 | 19/19 | 42/42 ✓ | 0 | 12/12 | 271/271 | 28/28 | 44/45 (build-id) |
| `gz_log_mod.ko` | 14/14 | 17/17 | 40/40 ✓ | 1/1 | 14/14 | 300/300 | 46/46 | 49/50 (build-id) |
| `gz_virtio_mod.ko` | 25/25 | 24/24 | 61/61 ✓ | 0 | 25/25 | 445/445 | 72/72 | 43/44 (build-id) |

`llvm-objcopy --remove-section=.note.gnu.build-id` on stock (A) and rebuild (B)
→ `cmp` equal for all five. Stock operands (vendor_dlkm, sha256 prefixes):
`83e7e3d8…`, `87d8a2a1…`, `9972d4db…`, `194d1bd1…`, `46ab2c37…` — full
values in [`kernel/module-inventory.tsv`](kernel/module-inventory.tsv).

## What is new relative to the earlier GZ work

* `gz_irq_mod`, `gz_log_mod`, `gz_virtio_mod` had **no** parity closure before;
  they appeared only as consumers in the GZ-TRANSPORT acceptance scan
  (5 / 6 / 11 edges). They are now exact.
* The earlier `gz_trusty_mod` / `gz_ipc_mod` closure (`device_modules@957dac18`)
  left "vermagic/Build ID and eight `.llvm_addrsig` references per module, each
  file 8 bytes smaller". Building with `-faddrsig` and an empty
  `module_scmversion` reproduces vermagic and `.llvm_addrsig` exactly; the only
  residual is the build-id.
* Source lineage cross-check: every file of the earlier pinned donor
  `957dac185efe46cbf6336b0fff9516d84c8cd78f` that exists in ALPS
  `5e415e059253` is sha256-identical (the donor's extra `Makefile.vendor` is a
  build-layout file only). Blob ids: [`source/SOURCES.tsv`](source/SOURCES.tsv).

## Configuration

GKI 12901745 `kout` config with the gz-trusty `Makefile`;
`CONFIG_MT_GZ_TRUSTY_DEBUGFS` is unset, so `trusty-debugfs.o` is **not** part of
`gz_trusty_mod` — matching stock (33 functions; no debugfs symbols).

## YFT / Ulefone deltas

**DIRECT_SOURCE_MATCH** for all five modules. No Ulefone code in the GZ transport.

## Firmware boundary

The GenieZone hypervisor/TEE images and secure-world message payloads are
outside this scope (proprietary secure firmware); the kernel transport side is closed.

## Reproduce

Workspace `~/kernel-work/gki-12901745-workspace/lieppos/power`:

```sh
S=drivers/misc/mediatek/geniezone/gz-trusty
./sb.sh trees/5e41 gz_trusty_mod $S "trusty.o smcnr-table.o" B1
./sb.sh trees/5e41 gz_ipc_mod    $S "trusty-ipc.o"            B1
./sb.sh trees/5e41 gz_irq_mod    $S "trusty-irq.o"            B1
./sb.sh trees/5e41 gz_log_mod    $S "gz-log.o"                B1
./sb.sh trees/5e41 gz_virtio_mod $S "trusty-virtio.o trusty-mem.o" B1
```

(`sb.sh` = `reverse-engineering/power/rt5133/scripts/sb.sh`.)
