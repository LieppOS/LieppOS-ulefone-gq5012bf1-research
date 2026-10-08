# GPU-AI-AUX-KERNEL-INTERFACES status — DONE

**DONE (class A).** All three owned modules — `gpueb.ko`, `vcp.ko`, `vcp_status.ko` —
rebuild from **unmodified public MediaTek ALPS source** (`5e415e059253`) and are identical
to the shipped stock binaries except each module's 20-byte GNU build-ID descriptor.

Closed axes, measured on a clean checkout: 183 functions, 222 data objects, 142 sections
(layout and content), 7 867 relocations (raw **and** semantic), 203 import CRCs, 60 export
CRCs with licence buckets, 13 KCFI type ids, 18 `.modinfo` records, `vermagic`,
`srcversion`, module aliases, the external provider ABI (16/16 CRCs regenerated from
source) and B1 == B2 determinism including every intermediate `.o`.

Additionally: **67 cross-component ABI edges verified, 67 MATCH, 0 mismatch** — the
symbols MTK-VCODEC-KERNEL (26), MALI-GPU-KERNEL (15) and MEDIATEK-DRM (1) import from this
component are produced here with the exact CRCs those DONE modules record.

* Report: [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md)
* Source recipe: [SOURCE.md](SOURCE.md) → `android_kernel_modules_gpu_ai_aux_ulefone_gq5012bf1`
* Rebuild procedure and transcripts: [build-reproduction.md](build-reproduction.md)
* ABI: [abi-parity.md](abi-parity.md) · [cross-component-abi.tsv](cross-component-abi.tsv)
* Hardware: [hardware-contract.md](hardware-contract.md)
* Firmware/ownership: [firmware-boundary.md](firmware-boundary.md)
* Userspace: [source-to-userspace-contract.md](source-to-userspace-contract.md)
* Corrections: [stale-claims.md](stale-claims.md)

**Retained boundaries.** `gpueb.img` and `vcp.img` stay proprietary, unmodified and
unanalysed — recovering the kernel host does **not** recover firmware algorithms, signing
or the secure boot chain. MTK-MBOX, MTK-RPMSG-MBOX and MTK-TINYSYS-IPI keep their DONE
transport ownership; SCP (SENSOR-HUB-KERNEL) and ADSP (AUDIO-DSP-KERNEL) host code was not
duplicated; MCUPM/SSPM, CCU and APUSYS remain outside this scope. Only the export ABI of
the 9 provider modules was verified here.

**Not established.** Nothing was executed on hardware: no probe, firmware boot, IPI
exchange, mailbox interrupt, feature vote, suspend transition, watchdog or recovery.
Runtime acceptance items are listed in
[source-to-userspace-contract.md](source-to-userspace-contract.md) §4 and require separate
authorisation.

No ADD elsewhere, merge, removal, rename or unrelated status move is authorized by this pack.
