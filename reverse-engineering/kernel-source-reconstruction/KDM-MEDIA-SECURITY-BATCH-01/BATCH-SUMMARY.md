# KDM-MEDIA-SECURITY-BATCH-01 — summary

**Result:** 10 of the 11 frozen media/security/platform Category D targets are independently certified as
**Category A**.

- **How:** B1/B2 whole-stock ELF acceptance under the unchanged strict verifier; only the 20-byte GNU build ID
  differs.
- **Source:** 9 build from unmodified ALPS. `mtk_irtx_pwm` adds one proven OEM delta: historical LieppOS commit
  3b995377, the `dma-mask-bit` DT property, which the stock binary and the stock DT corroborate.
- **flashlight.ko:** remains **D**. It needs an OEM `flashlight-core.c` variant that is not available, and the exact
  residual is recorded.

Canonical was not edited in Stage B. The identity-keyed CAS delta against `ee1803b7` validates at
**A385 / B1 / C10 / D8 / E0 / F0 / G54 = 386 certified, 72 remaining**, with validator 0 errors and 14/14 audit
mutations.

| | |
|---|---|
| Baseline | canonical `ee1803b7` (PERFORMANCE-INTEGRATION-01 applied: A375 B1 C10 D18 G54) |
| Manifest | 11 identities, SHA256 `063a19ed6e8dc0d7254e47609dce081deec8b83e3e03ea9e2843a012e8c06e83`, committed `ddaa79ce` before source work |
| Source | `android_kernel_modules_kdm_media_security_ulefone_gq5012bf1` @ `973eb04ac0d0…`; bundle `bundles/kdm-media-security.bundle` (sha256 `c12a5623…`, verified, cloned fresh twice) |

| Module | Family | Final | Functions | Data | Imports/Exports | KCFI IDs | Relocs | Residual |
|---|---|---|---|---|---|---|---|---|
| mtk-composite | FLASHLIGHT (V4L2, not USB) | A | 7/7 | 18/18 | 23/0 | 0 | 132 | none |
| mtk_jpeg | MEDIA | A | 63/63 | 52/52 | 116/0 | 19 | 950 | none |
| mtk-mmdvfs-v3-start | MEDIA | A | 4/4 | 14/14 | 9/0 | 0 | 49 | none |
| mtk_sec_heap | DMA-HEAP | A | 29/29 | 34/34 | 74/3 | 0 | 1068 | none |
| mtk_heap_debug | DMA-HEAP | A | 40/40 | 41/41 | 92/0 | 3 | 1486 | none |
| widevine_driver | SECURITY | A | 8/8 | 28/28 | 25/0 | 0 | 281 | none |
| tui-common | SECURITY | A | 5/5 | 14/14 | 2/3 | 0 | 66 | none |
| sapu | SECURITY | A | 24/24 | 28/28 | 50/0 | 3 | 638 | none |
| mtk_irtx_pwm | PLATFORM-IO | A | 6/6 | 16/16 | 23/0 | 0 | 100 | none (OEM delta reproduced) |
| nvmem-mt635x-efuse | PLATFORM-IO | A | 4/4 | 22/22 | 19/0 | 0 | 81 | none |
| flashlight | FLASHLIGHT | **D** | 32/51 byte-identical (experiment) | — | 47/19 stock | — | differ | OEM `flashlight-core.c` variant unavailable |

For the 10 certified modules, every CRC, licence, namespace, KCFI type ID, raw and semantic relocation, section
header, symbol table, string table and `.modinfo` (vermagic, srcversion, depends) is byte-identical to stock.
Nothing was forced, transplanted or patched in the binary.

## Findings (details in HARDWARE-CONTRACT.md and SECURITY-BOUNDARIES.md)

- **Name correction:** "USB composite" is in fact the V4L2 flashlight composite `mtk-composite.ko`. The similarly
  named lens file belongs to Codex's `camera_af_media` and was not touched.
- **JPEG:** the stock DT carries only the JPEG **encoder** node (`jpgenc@17030000`) and no decoder node.
- **Secure heaps:** the secure-heap layout comes from the stock DT: page and region heaps for prot, svp, wfd and
  sapu, with tmem types and IOMMU bindings.
- **Security boundaries:** `mtk_sec_heap`, `sapu` and `widevine_driver` reach the secure world only through
  `tmem_ffa`, GenieZone KREE/trusty (Codex G providers, used as compile-only witnesses) and an APU rpmsg lock.
  No DRM, TEE or secure-memory claim is made.
- **efuse:** `nvmem-mt635x-efuse` is read-only by construction, and the stock DT binds the MT6363 and MT6373
  ("mt6369-efuse") PMIC efuse nodes.
- **irtx:** uses `pwm-supply = mt6369_vio28` and `dma-mask-bit = <0x23>`; the OEM delta consumes the latter.
- **flashlight:**
  - Stock needs `CONFIG_MTK_FLASHLIGHT_PT=y` with STRICT (proven by the `.data` values `pt_strict=1` and levels
    2/1/1).
  - Stock also contains three functions (`flashlight_drvctrl`, `flashlight_sw_ctrl_show`/`_store`) and an
    "ignore pt" path that exist in no available revision, and it drops the battery-OC callback.
  - The stock DT nevertheless sets `battery-oc-level = <2>`.

## Dependencies

- **Graph:** 480 import edges, all CRC-consistent: 438 to GKI, 3 intra-batch, 39 to 14 external providers.
- **Providers:** 10 are canonical A. 4 are G (tmem_ffa, gz_trusty_mod, gz_tz_system, mtk-pwm). All 32 witnessed
  external symbols were compiled naturally from provider source with exact CRC, licence, KCFI and namespace. No
  provider is certified or owned by this batch.

## Reproducibility and safety

- **B1/B2:** fresh bundle clones and offline workspaces, with the development directory quarantined.
- **Identity:** 20 `.ko`/stripped outputs, 80 intermediates, configs, symvers and trees are identical between
  builds and equal to D3. 131 + 131 ELF mutation controls.
- **Canonical:** Stage B did not touch canonical master. All C and G rows are unchanged, and Codex's repositories
  and workspaces are untouched.
- **Cleanup:** no build workspace was deleted. Only this task's scratch worktree was removed, after its evidence was
  copied here.
- **Offline:** no ADB, phone, flash, IR, USB, TEE or efuse operation, and no push.

Reports: BASELINE-AND-SELECTION.md, HARDWARE-CONTRACT.md, SECURITY-BOUNDARIES.md, SOURCE-LINEAGE.md,
KDM-DEPENDENCY-GRAPH.tsv, ABI-PROVIDERS.tsv, BATCH-PARITY.tsv, EXPERIMENTS.tsv, BLOCKERS.tsv, BUILD-REPRODUCTION.md,
SOURCE-REPOSITORIES.tsv, AUDIT-DELTA.tsv, PROPOSED-AUDIT.patch, MERGE-INSTRUCTIONS.md, NEXT-BATCH.md, BATCH-STATE.json.
