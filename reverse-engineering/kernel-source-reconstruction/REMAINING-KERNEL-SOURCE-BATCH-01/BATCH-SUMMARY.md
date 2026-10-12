# REMAINING-KERNEL-SOURCE-BATCH-01 — summary

**Result:** all 5 frozen Category D targets are independently certified as **Category A** from complete public
source. Only the 20-byte GNU build ID differs from stock; for the reboot pair that includes the entire split `.BTF`.

| | |
|---|---|
| Baseline | canonical `0390534d` (after KDM-INTEGRATION-01: A385 B1 C10 D8 G54 = 386/458) |
| Manifest | 5 identities, sha256 `22ede98587a67e88888258afeaf515c00180c34aa19a946f5c76542092d3b987`, committed `e220d890` before source work |
| Source | `android_kernel_modules_remaining_ulefone_gq5012bf1` @ `7e07384a`; bundle sha256 `9ceed647…`, verified and cloned fresh twice |
| Proposed totals | **A390 B1 C10 D3 E0 F0 G54 = 391 certified / 67 remaining (85.4%)** |

| Module | Original | Final | Functions | Data | Imports/Exports | KCFI IDs | Relocs | BTF | Residual |
|---|---|---|---|---|---|---|---|---|---|
| reboot-mode | D | A | 7/7 | 12/12 | 16/4 | 0 | 62 | entire .BTF exact | none |
| syscon-reboot-mode | D | A | 4/4 | 19/19 | 9/0 | 0 | 37 | entire .BTF exact | none |
| hbt | D | A | 6/6 | 13/13 | 32/0 | 0 | 661 | none in stock | none |
| scheduler_ext | D | A | 2/2 | 12/12 | 1/0 | 0 | 6 | none in stock | none |
| mali_dmabuf_test_mt6878_r44 | D | A | 16/16 | 16/16 | 49/0 | 0 | 484 | none in stock | none |

CRCs, licences, namespaces, section headers, symbol and string tables, raw and semantic relocations, `.modinfo`
(vermagic, srcversion, intree, scmversion, depends) all match stock. Nothing was forced, transplanted or patched in a
binary, and no `*_o_shipped` object is present in any build tree.

## Source findings

- **Reboot pair:** GKI `drivers/power/reset` sources, blob-identical in GKI 6b18f0b5 and MTK ACK c364c39a. Built
  in-tree against the OEM split-BTF base rebuilt from public source (`cafe5987…`, identical in B1 and B2).
- **hbt:** Nothing's tree only has dangling `hbt_driver` symlinks and a fallback stub that cannot be stock. The exact
  source is MiCode `MTK_kernel_modules` `hbt_driver` at `a875701d` (Android-U blob `caccc39e`), carried verbatim with
  pinned blob IDs.
- **scheduler_ext:** Nothing `sched_cus/src/sched_main.c`; an inert init/exit module, distinct from the certified
  `scheduler.ko`. The co-located `cpuqos_ext`/`eas_ext` units link shipped objects and are scoped out.
- **Mali test exporter:** ARM r44p1 DMA-BUF test exporter from the same Nothing pin as the certified GPU repo.
  Diagnostic only; not the runtime GPU driver or firmware.

## Hardware findings (HARDWARE-CONTRACT.md)

- Stock DT `syscon-reboot-mode`: offset `0x24`, mask `0x0f`, modes charger 1, recovery 2, bootloader 3,
  dm-verity-dev-corrupt 4, kpoc 5, ddr-reserve 6, meta 7, rpmbpk 8. Nothing was written or rebooted.
- hbt exposes `/dev/hbt` and `/dev/vhbt` (0666, ABI 2.0) as a userspace compatibility bridge.
- The Mali exporter exposes `/dev/dma_buf_te`.

## Dependencies

107 import edges: 106 to GKI vmlinux, 1 intra-batch (`syscon-reboot-mode` → `reboot_mode_register`). All CRCs
consistent, 0 unresolved, no external vendor provider.

## Reproducibility

- **Final B1/B2:** fresh bundle clones, offline bootstrap, development quarantined. 5/5 acceptance and 69/69 ELF
  mutations each; 10/10 output files, 13/13 intermediates, configs, native symvers, source trees and BTF base
  byte-identical.
- **Preserved negative result:** the first proof (`d331daa6`) showed workspace-path-dependent build IDs for the three
  external modules; fixed by prefix maps, with no change to any accepted byte.

## Excluded

- **flashlight:** retained D; GPL source-request specification in NEXT-BATCH.md.
- **fpsgo, msync2_frd:** retained D under the project decision on prebuilt `*_shipped` objects.

## Safety

Canonical master was not modified. Codex's branch, worktrees and 23 frozen G rows were untouched. No phone access,
no push, no deletion of other agents' data. Build workspaces under
`/home/armol/kernel-work/remaining-kernel-source-batch-01/` were kept.

Reports: BASELINE-AND-SELECTION.md, BATCH-MANIFEST.tsv, BATCH-PARITY.tsv, SOURCE-LINEAGE.md, SOURCE-REPOSITORIES.tsv,
ABI-PROVIDERS.tsv, DEPENDENCY-GRAPH.tsv, HARDWARE-CONTRACT.md, EXPERIMENTS.tsv, BLOCKERS.tsv, BUILD-REPRODUCTION.md,
AUDIT-DELTA.tsv, PROPOSED-AUDIT.patch, MERGE-INSTRUCTIONS.md, NEXT-BATCH.md, BATCH-STATE.json.
