# GQ5012BF1 APUSYS/NPU kernel reconstruction report

## Result

The complete explicitly owned normal-world set—`apu_top.ko` and `apusys.ko`—is reconstructed from public source and accepted. There are no unresolved compiled behavioral/ABI differences. The only raw difference in either installed ELF is the GNU build-ID descriptor.

| Module | Function occurrences | Exact | Semantic-only | Compiler-only | Metadata-only | Unresolved | CRC/KCFI | Rebuild |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `apu_top.ko` | 343 | 343 | 0 | 0 | 0 | 0 | exact (180 imports, 21 exports, 19 KCFI IDs) | clean B1=B2 |
| `apusys.ko` | 1,965 | 1,965 | 0 | 0 | 0 | 0 | exact (375 imports, 11 exports, 152 KCFI IDs) | clean B1=B2 |

The build-ID is whole-file provenance and lies outside every function/data/ABI object; it is reported at file level, not misclassified as a function difference.

## Source and device delta

Public ALPS commit `5e415e059253ce0d2e61c97108e5f5785d71f06f` is exact source. No C/header change is required. The only device reconstruction is deterministic Kbuild scope and the stock MDLA object order formerly delegated to filesystem-dependent `find(1)`. See `SOURCE.md` and `source-lineage.md`.

Maintained source commit: `924f66b779a64ae0b05f89e233ff2317866050ba`. Exact GKI/toolchain/vendor pins and clean commands are in `SOURCE.md`. Full machine ledgers are under `evidence/reconstruction/`.

## Hardware and firmware

The stock DT identifies MT6878 APU RV/APU-top, APUMMU/IOMMU, one MDLA core, MVPU/EDMA and RPMsg/shared memory. The rebuilt `apu_top` closes power/RPC/regulator/DVFS support; the rebuilt monolithic `apusys` closes middleware, buffers, schedulers, transport, interrupt/completion, timeout/recovery, and teardown code. Multiple compiled generations remain dormant unless matched by DT/firmware.

The kernel-facing boundary includes remoteproc/RPMsg boot/handshake and command/completion structures; signed `firmware/apusys.img` internals and proprietary APUware/NeuroPilot algorithms remain retained. Exact image metadata is in `firmware-boundaries.tsv`; no claim is made that firmware source or cryptographic material was reconstructed.

## Android contract and reachability

Stock load order, dependencies, `/dev/apusys`, four ioctl families, dma-buf ownership, graph/fence submission, negotiated firmware protocol and error cleanup are documented in `source-to-userspace-contract.md`. Stock HAL/library declarations prove intended consumers and static reachability. They do not prove actual inference.

## Determinism and residue

The final fresh clone rebuilt from pins twice. Raw `.ko`, stripped `.ko`, all target `.o`, `Module.symvers`, provider CRC witnesses and source tree IDs match B1/B2. Stock comparisons cover every function, data object, section, symbol/string, modinfo, import/export CRC, KCFI ID and relocation. Each stock comparison has exactly 20 differing bytes, all within `.note.gnu.build-id`; normalized whole-file hashes match.

## Runtime limitation

Offline static work cannot establish successful probe, signed firmware boot, RPMsg handshake, real NPU execution rather than CPU fallback, power/thermal behavior, recovery, suspend/resume or performance. The precise later acceptance sequence is the final section of `source-to-userspace-contract.md`. No reboot, flash, module load, clock/voltage change, firmware write or hardware command occurred.
