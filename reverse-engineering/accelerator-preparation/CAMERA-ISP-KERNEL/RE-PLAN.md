# Source-parity reconstruction sequence — CAMERA-ISP-KERNEL

1. Read the 16 published function/data proof pairs first; match their stock hashes and preserve the existing grafted mtkcam 133c6c1 source. Do not replace byte-exact work with a pristine donor.
2. Prioritize PDA and VMM regulator/notifier: no function/data proof pair exists for these three owned targets. Recover their source/struct/callback deltas and compile separately.
3. Certify the already reconstructed HCP → imgsys command/ISP/V4L2 → CCD/RPMsg → CCU → camsys → AIE/DPE stack on full module axes, not function tables alone.
4. Certify imgsensor framework/glue and C2PS without reopening closed sensor TUs; preserve the one documented imgsensor semantic-equivalence residual.
5. Close CSI/SENINF, power/IRQ/DMA/IOMMU/media/IOCTL and HAL-consumer boundaries with the preserved stock contract.

For **each** target in stock-modules.tsv, create its own function/data/ABI/residual ledger and isolated source patch series. Do not bulk-mark a scope DONE after compiling one binary. Preserve existing exact camera data/function proofs and closed provider source.

Apply [PARITY-STANDARD.md](../PARITY-STANDARD.md) completely, then verify imports/exports across the source-built provider graph and DT/observable ABI. Report new results in authoritative research commits before scoped workspace synchronization. Runtime tests are a separate, later authorized phase; none is permitted by this preparation assignment.
