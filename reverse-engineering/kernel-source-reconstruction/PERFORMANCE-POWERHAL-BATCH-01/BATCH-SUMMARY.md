# PERFORMANCE-POWERHAL-BATCH-01 — summary

**Result:** all 14 frozen MediaTek performance / PowerHAL / FPSGO / CPUQoS Category D targets were rebuilt from
unmodified pinned ALPS source. Each was independently certified as Category A by B1/B2 whole-stock ELF acceptance
under the unchanged strict verifier; the only difference is the 20-byte GNU build ID. No OEM patch, placeholder,
waiver or BTF base was needed.

Canonical was not edited. The identity-keyed CAS delta against `63f12972` validates at
**A375 / B1 / C10 / D18 / E0 / F0 / G54 = 376 certified, 82 remaining**: validator 0 errors, 14/14 audit
mutations, inventory 458/471.

| Item | Value |
|---|---|
| Baseline | canonical `63f12972` (BOOT-LOWPOWER-INTEGRATION-01 applied: A361 B1 C10 D32 G54) |
| Manifest | `BATCH-MANIFEST.tsv`, SHA256 `fa59a9044849c72d77c852132250ee250374105a9262991abd864a9b3dd37285`, committed at `84f9531e` before source work |
| Source | `android_kernel_modules_performance_ulefone_gq5012bf1` @ `7a1a1e298a2a…`; bundle `bundles/performance.bundle` (verified, cloned fresh twice) |

| Module | Family | Functions | Data | Imports/Exports | KCFI IDs | Relocs | Residual |
|---|---|---|---|---|---|---|---|
| mtk_perf_ioctl | PERF-IOCTL | 19/19 | 41/41 | 19/25 | 3 | 311 | none |
| mtk_perf_ioctl_magt | PERF-IOCTL | 13/13 | 47/47 | 30/4 | 3 | 322 | none |
| mtk_ioctl_powerhal | PERF-IOCTL | 8/8 | 26/26 | 16/11 | 3 | 178 | none |
| mtk_ioctl_touch_boost | PERF-IOCTL | 5/5 | 15/15 | 13/1 | 3 | 104 | none |
| powerhal_cpu_ctrl | POWERHAL | 45/45 | 59/59 | 74/4 | 2 | 905 | none |
| touch_boost | POWERHAL | 65/65 | 82/82 | 85/0 | 2 | 1594 | none |
| mtk_fpsgo | FPSGO | 811/811 | 956/956 | 177/63 | 7 | 17935 | none |
| frs | FPSGO | 11/11 | 26/26 | 22/0 | 0 | 147 | none |
| load_track | LOAD-TRACK | 5/5 | 16/16 | 23/2 | 1 | 182 | none |
| uload_ind | LOAD-TRACK | 36/36 | 52/52 | 39/0 | 2 | 610 | none |
| mtk_perf_common | PERF-COMMON | 76/76 | 149/149 | 89/2 | 3 | 1724 | none |
| scheduler | SCHED-CPUQOS | 729/729 | 906/906 | 290/145 | 25 | 11417 | none |
| cpuqos_v3 | SCHED-CPUQOS | 78/78 | 111/111 | 75/7 | 6 | 1185 | none |
| task_turbo | SCHED-CPUQOS | 86/86 | 136/136 | 76/0 | 4 | 1201 | none |

The following are byte-identical to stock in every module: all CRCs, licences, namespaces, KCFI type IDs, raw and
semantic relocations, section headers, symbol and string tables, and `.modinfo` (vermagic, srcversion, depends).
Nothing was forced, transplanted or patched.

## Dependencies

- **Graph:** 1028 import edges, CRC-consistent 1028/1028: 859 to GKI, 68 within the batch, and 101 to 12 external
  providers.
- **External providers:** all 12 are canonical A (cpufreq_sugov_ext 72 slots, thermal_interface, mtk_qos,
  mediatek-drm, ged, blocktag, mtk_gpu_hal, mtk_slbc, mtk_cm_mgr, cpudvfs, mtk-dvfsrc, mtk-dvfsrc-helper). All 98
  external symbols were compiled naturally from provider source, with exact CRC, licence, KCFI and namespace.
- **Load order:** every provider loads before its consumer.
- **FPSGO/mbraink:**
  - `mtk_fpsgo` is now Category A itself. The 4 symbols that certified `mtk_mbraink` (LOW-POWER-BATCH-01)
    imports from it were previously backed only by a compile-only witness.
  - `frs` uses 5 FPSGO EARA exports.
  - `fpsgo.ko` (36 imports) stays D because it links MediaTek prebuilt `*_shipped` objects.

## Findings (details in HARDWARE-CONTRACT.md)

- **FPSGO DT node:** the stock DT `/fpsgo` node fixes FPSGO's tuning (`cpu-limit=2`, `gcc-enable=1`, `fbt-cpu-mask`,
  `sbe-resceue-enable=1`, and the `fpsgo-perf-bw` interconnect path).
- **Absent DT nodes:** `mediatek,flt` and `mediatek,cpuqos-v3` have no stock DT nodes, so those DT paths are not
  taken.
- **Userspace ABI:** procfs ioctl endpoints under `/proc/perfmgr*`, `/proc/powerhal_cpu_ctrl`, `/proc/touch_boost`,
  `/proc/cpuqosmgr` and `/proc/cpu_loading`, plus uload_ind and GBE misc devices. Every ioctl number and structure
  layout is preserved exactly. Whether the userspace PowerHAL, FPSGO or MAGT services use them is UNKNOWN.
- **Vendor hooks:** 43 in scheduler, 16 in task_turbo, 2 in cpuqos_v3, 1 in mtk_fpsgo and 1 in mtk_perf_common.
  Policies and thresholds are unchanged, because the objects are byte-identical.

## Reproducibility and safety

- **B1/B2:** fresh bundle clones and fresh offline workspaces, with the development directory quarantined, at 4 CPUs
  and nice 10.
- **Identity:** 28 `.ko`/stripped outputs, 197 intermediates, configs, symvers and source trees are identical between
  builds and equal to D1/D3.
- **Mutation controls:** 189 + 189 ELF mutation controls rejected as expected.
- **Canonical:** Stage B did not touch canonical master. Only this task's scratch worktree was removed, after its
  evidence was copied here. No build workspace was deleted.
- **Offline:** no ADB, phone, flash or push.

Reports: BASELINE-AND-SELECTION.md, HARDWARE-CONTRACT.md, SOURCE-LINEAGE.md, PERFORMANCE-DEPENDENCY-GRAPH.tsv,
ABI-PROVIDERS.tsv, BATCH-PARITY.tsv, EXPERIMENTS.tsv, BLOCKERS.tsv, BUILD-REPRODUCTION.md, SOURCE-REPOSITORIES.tsv,
AUDIT-DELTA.tsv, PROPOSED-AUDIT.patch, MERGE-INSTRUCTIONS.md, NEXT-BATCH.md, BATCH-STATE.json.
