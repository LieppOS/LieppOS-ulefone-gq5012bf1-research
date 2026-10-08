# MTK-VCODEC-KERNEL status — DONE

**DONE (class A).** All five owned modules — `mtk-vcodec-common.ko`, `mtk-vcodec-dec-v1.ko`,
`mtk-vcodec-enc-v1.ko`, `mtk-vcu.ko`, `clk-mt6878-vcodec.ko` — rebuild from **unmodified
public MediaTek ALPS source** (`5e415e059253`) and are identical to the shipped stock
binaries except each module's 20-byte GNU build-ID descriptor.

Closed axes, measured on a clean checkout: functions, data objects, section layout and
contents, raw and semantic relocations, import CRCs, export names/buckets/CRCs, KCFI type
ids, module strings, `.modinfo`, `vermagic`, external provider ABI (60/60 CRCs regenerated
from source), and B1 == B2 determinism including every intermediate `.o`.

* Report: [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md)
* Source recipe: [SOURCE.md](SOURCE.md) → `android_kernel_modules_vcodec_ulefone_gq5012bf1`
* Rebuild procedure and transcripts: [build-reproduction.md](build-reproduction.md)
* ABI: [abi-parity.md](abi-parity.md) · Hardware: [hardware-contract.md](hardware-contract.md)
* Firmware boundary: [firmware-boundary.md](firmware-boundary.md)
* Userspace: [source-to-userspace-contract.md](source-to-userspace-contract.md)
* Corrections: [stale-claims.md](stale-claims.md)

**Retained boundaries.** Signed VCP firmware (`vcp.img`) and vendor Codec2/OMX libraries stay
proprietary and unmodified. VCP host/status, TinySys IPI, CMDQ, SMI, SLBC, IOMMU-debug,
MMQoS/ICC, EMI, scheduler, system_heap and clk-common keep their own owners; only their
export ABI was verified here.

**Not established.** Nothing was executed on hardware: no probe, decode, encode, firmware
handshake, interrupt, DVFS transition or recovery. Advertised codec XML capability remains a
static declaration. Runtime acceptance items are listed in
[source-to-userspace-contract.md](source-to-userspace-contract.md) §3 and require separate
authorisation.

No ADD elsewhere, merge, removal, rename or unrelated status move is authorized by this pack.
