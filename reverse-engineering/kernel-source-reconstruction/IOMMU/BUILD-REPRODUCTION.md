# Independent deterministic IOMMU build and stock acceptance

Accepted source commit:**110251e6d0983ea4a8a0a9fadd104aeaacb229b9**.
Fresh clone /home/armol/kernel-work/iommu-cleancheck/repo; initially empty sibling ws.
Development /home/armol/kernel-work/iommu-dev was moved unavailable throughout bootstrap,
B1/B2 and separate stock acceptance, then restored only afterward. Public inputs came
from independently preserved /home/armol/kernel-work/interconnect-pin-mirror, never copied
objects, mutable donor outputs or a hidden prepared kout. Offline Git file IO only.

```sh
git clone '<recipe-or-source/android_kernel_modules_iommu_ulefone_gq5012bf1.bundle>' \
 /home/armol/kernel-work/iommu-repro/repo
cd /home/armol/kernel-work/iommu-repro/repo
export LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror
export JOBS=12 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp
unset ACK_DIR
scripts/bootstrap.sh /home/armol/kernel-work/iommu-repro/ws
scripts/b1b2.sh /home/armol/kernel-work/iommu-repro/ws '<stock-platform-module-dir>'
```

## Environment

Exact GKI12901745 source/toolchain/KMI pins in SOURCE.md. Vendor config is common
gki_defconfig +957dac mgk_64_k61_defconfig/KCONFIG_EXT_PREFIX, SHA256:
**8f9d1d2901dfbc77062764b4f9e21bc1000097392a36f8ba1eebd9c47d35f50e**.
IOMMU_API/IOMMU_DMA and ARMV7S io-pgtable enabled; vendor IOMMU/SMI and misc debug/secure
are modules. KCFI and modversions preserved. MODULE_SRCVERSION_ALL unset, no target
srcversion. ARCH=arm64 LLVM=1 LLVM_IAS=1, fixed user/host/version/timestamp, stock
release stamp6.1.115-android14-11-g945dff7bc1bf, native include ordering and __FILE__
prefix mapping, -faddrsig and __ANDROID_COMMON_KERNEL__. ACK/private header overlay forbidden.
Only one host glibc/bpf qualifier diagnostic is demoted; no target warnings suppressed.

Every build recreates source trees, applies exact indexed Kbuild patch, checks target/provider
tree IDs, deletes kout/regenerates config/headers and recompiles all three real provider
objects. Their natural18 #SYMVER records and actual GPL export sections must equal the
reference assertions. Modpost generates metadata/depends; only owned target .ko is allowed.
No vendor compiler code/ELF/CRC bytes patched. Stock packaging is llvm-strip --strip-debug.

B1/B2 matches: one raw debug KO, one packaged KO, mtk_iommu.o and mtk_iommu.mod.o,
three provider .o files, Module.symvers, external symvers/witnesses, configuration and
both source trees. All source/objects/symvers/config are regenerated each time.
Stock acceptance separately checks complete packaged ELF outside the parsed GNU descriptor,
then materializes function/data/import/export/KCFI/section/relocation proof. Both tests are
required; determinism alone is insufficient.14 disposable full-file verifier mutations pass.

Verbatim clean-checkout log, object/config/source hashes and three compressed provider
compiler commands are in evidence/build. Source/COMPILED-INPUTS.tsv identifies every actual
local public dependency and checks its immutable Git blob. Core symvers/compiler hashes
and public source mirror provide explicit provenance, not hidden development-directory inputs.

## Host-only research regeneration

```sh
python3 scripts/finish-evidence.py '<recipe>' '<accepted-ws>'
python3 scripts/map-topology.py '<accepted-ws>' '<stock-merged.dtb>' '<saved-devicetree.tar>' '<output>'
python3 scripts/test-acceptance.py '<recipe>' '<accepted-ws>/out/B1'
```

Historical prepare-reference.py freezes scope/stock assertions and generates the committed
patch; it is not a required hidden build script. An initial detached tool sandbox lost its
TMPDIR after bootstrap launched; persistent /tmp fixed that host-only launcher failure.
It was not a source/ABI delta and the final independent run passes without it.
No deployment, hardware IO, firmware handling or pushes.
