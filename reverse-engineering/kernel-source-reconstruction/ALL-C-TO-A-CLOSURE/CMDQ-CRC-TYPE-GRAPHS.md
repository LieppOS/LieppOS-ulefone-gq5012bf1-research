# CMDQ recursive CRC graph — resolved from configuration

Static/offline only. Four selected CMDQ identities now pass complete stock ELF acceptance.
All 35 modules in the joint build scope pass in both independent workspaces. No ownership
transfer or new certification is claimed for the other 31 identities.

## Root cause

The generic NothingOSS MT6878 `mgk_64_k61_defconfig` enables Microtrust. That makes
`cmdq_sec_mtee.h` include `teei_client_main.h`; its `suspend.h` / `tee_private.h` include
closure exposes additional cdev, swap, memory-control and writeback types to genksyms.
The compiled CMDQ executable code was already exact, but the recursive type graph was not.

A visibility search reproduced stock CRCs with these six recursive type nodes opaque:
`dev_iommu`, `iommu_ops`, `mbox_chan`, `msi_device_data`, `readahead_control`,
`wait_page_queue`. See `evidence/cmdq/visibility-search-hit.log`. This search was diagnostic;
it was not implemented as a type-hiding/header patch in the accepted recipe.

The defensible configuration correction is `CONFIG_MICROTRUST_TEE_SUPPORT=n`.
The stock inventory ships TrustKernel `tkcore` / `tkcore_drv`, and no Microtrust module.
Disabling the unnecessary Microtrust subtree naturally restores the matching include/type
visibility and all 23 previously mismatching export CRCs (16 secure + 7 core), along with
the four selected downstream import CRC differences and counter-derived ELF metadata.
Absence of a module alone is not the proof: complete stock bytes and CRCs in B1/B2 are.

The attempted broader change disabling both Microtrust and Trustonic was rejected:
GenieZone `tz_system.c` needs the genuine GP `tee_client_api.h` include path. Trustonic
therefore stays enabled. There is no claim that the TrustKernel private ABI island is closed.

## Accepted inputs and evidence

Build commit: `059e2fe439309c3adc2e95b87aa547967e7e5f80` in the isolated CMDQ source clone.
Final preserved commit: `0b4b07f38397ca6c0630b9edc5ccf2df9251da1d` (README and host-bytecode cleanup only).
Public ALPS source pin remains `5e415e059253ce0d2e61c97108e5f5785d71f06f`.
Board fragment: `reference/gq5012bf1-tee.config`; no target source bytes or CRC constants patched.

- `evidence/cmdq/B1/` and `B2/`: every selected function/data/section/relocation/ABI ledger.
- Joint acceptance logs: 35/35 in each build.
- `build-input-comparison.json`: 120/120 intermediate objects identical after debug stripping;
  vendor config and naturally emitted symvers match (workspace paths normalized for text only).
- `B1-B2-compare.txt`: all 35 stripped operands identical outside GNU build ID.
- `mutations-B2.json`: 40/40 checks pass, including export CRC and KCFI absolute-ID flips.
  Only the build-ID mutation is accepted; absent exports/KCFI axes are explicitly recorded.

Stock reference files were not edited. Official GKI core symvers are retained; vendor CMDQ
provider CRCs are generated from their rebuilt source, not injected from stock.
No runtime, CMDQ execution, secure-world or flashing validation was performed.
