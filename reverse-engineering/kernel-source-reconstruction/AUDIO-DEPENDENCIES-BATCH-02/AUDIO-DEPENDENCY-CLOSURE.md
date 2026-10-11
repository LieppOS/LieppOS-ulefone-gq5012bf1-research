# Audio dependency closure — measured graph and selected source scope

## Existing coverage

The preserved21-module AUDIO-BATCH-01 foundation is verified, not rebuilt:20 A and one Claude-owned C. Canonical245/213 counts do not include its20 pending certifications or SCP/connectivity's17 pending certifications. All41 identities from those two frozen batches are excluded from new reconstruction; all current canonical C and A/B identities are excluded too.

## Actual ABI graph

`AUDIO-DEPENDENCY-GRAPH.tsv` contains all1,162 imported-symbol edges from the21 audio identities. They resolve against SHA-verified stock export slots or pinned GKI core symvers; there are30 distinct direct provider identities including GKI_CORE. Per-edge export CRC/license/namespace, symbol type, provider KCFI prefix evidence, source ownership/location and committed-versus-pending status are separate fields. CRC agreement alone is never asserted to prove callsite type equivalence.

The complete read-only ELF graph for all458 identities is retained in `evidence/all-module-abi-graph.tsv`. Starting from the21 audio identities, its transitive provider closure reaches74 module identities. After excluding canonical A/B, all C and pending-owned scopes,19 reachable uncertified identities remain. Private originals match every frozen stock SHA, including authentic signed GKI modules copied from the separately verified image extraction; no shared canonical input was repaired.

Direct currently uncertified audio providers:

- `adsp` imports `slbc_power_off`, `slbc_power_on`, `slbc_release`, `slbc_request` from `mtk_slbc`.
- `snd-soc-mtk-common` imports `get_md_resv_mem_info` from `ccci_util_lib` and `get_smem_phy_start_addr` from `ccci_md_all`.
- SCP and audio transport providers already have pending independently certified source. They are coverage dependencies, not new targets.

Historical voice prose attributed some shared-memory API names/providers incorrectly. The new report uses these exact stock imported symbols, not the old generic description.

## Why display and shared-buffer providers appear

`ccci_md_all` genuinely imports `mtk_disp_mipi_ccci_callback` and `mtk_disp_osc_ccci_callback` from `mediatek-drm`; this is not a userspace/DT/firmware-inferred edge. The DRM provider's own actual imports extend into display helpers, panel extension, sync, notify, profiling, DVFS/debug, LEDs and system DMA heap. They are **transitive ABI infrastructure**, not newly claimed audio engines or physical routes. These12 ancillary provider identities are selected because the exact dependency graph requires them, not to fill a numerical quota.

The other seven reachable targets are SLBC plus CCCI util/core/AUXADC, CCMNI/RPS and modem power model. `ccmni_ops` is an exported data object imported by `ccci_md_all`; export resolution must not omit it by counting functions only.

## Source-supported host registrations

CCIF, DPMAIF and CCCI's SCP FSM bridge are additionally selected as the coherent CCCI implementation family. Host operations are registered and invoked through `ccci_hif_op`, not expressed as reverse direct imports from the core. Saved stock port/runtime research and actual sources distinguish:

- CCIF: modem control/character/speech channels;
- DPMAIF: packet data and common host readiness/recovery, **not voice sample transport**;
- CCCI SCP FSM: MD/SCP state synchronization through registered notifications and IPI.

These three are explicitly source/registration-mediated edges, not fabricated direct ELF import edges. Together with the19 reachable provider identities, the batch is22 modules. C2K USB rawbulk, MDDP, standalone modem thermal/power consumers and unrelated radio modules are not added merely because their names are modem-related.

## Remaining gates

The manifest is a source-work scope, not certification. Complete source recovery, actual builds, all parity axes, source commits, independent B1/B2 and mutation validation are required before any classification proposal. User-visible voice functionality, firmware algorithms, tuning and Android audio HAL operation are not proven by kernel source parity.

Integration is separate: concurrent Claude assignments must finish; canonical owner must restore the signed stock operands; current field preconditions and isolated audit validators must pass. No canonical audit edit, phone operation or push is performed here.
