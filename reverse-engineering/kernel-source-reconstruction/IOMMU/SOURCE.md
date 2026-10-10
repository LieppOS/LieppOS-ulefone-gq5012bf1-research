# Maintained source and reproducible inputs

Repository:
`/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_iommu_ulefone_gq5012bf1`

Accepted commit:**110251e6d0983ea4a8a0a9fadd104aeaacb229b9**. No remote/push.
Recovery: source/android_kernel_modules_iommu_ulefone_gq5012bf1.bundle and source/COMMIT.

| Role | Full public revision | Verified tree |
|---|---|---|
| ALPS compiled target/provider C and headers |5e415e059253ce0d2e61c97108e5f5785d71f06f|9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c|
| NothingOSS vendor Kconfig/defconfig only |957dac185efe46cbf6336b0fff9516d84c8cd78f|05f9c65d40ef9e4bdbe17397a90edd303a5da6dd|
| GKI common headers/kbuild/modpost |6b18f0b574ab3267615ae6ce642d5a7c3c21ac09|710eb859513863cda0204995a411d5795ad3fe92|
| clang-r487747c subtree |7775eb113f960bc69a780b621d03a715914d4bca|8eb8e3afb00a52d48b29381d73daf352362231ad|

SOURCE-PINS.tsv records original HTTPS URLs/roles; offline bootstrap retrieves immutable
public Git objects from the separately preserved interconnect-pin-mirror and validates
these identities. Compiler subtree and GKI12901745 vmlinux.symvers are content checked.
Clang17.0.2 build10087095, lld/LLVM tools. No copied stock vendor object as a build input.

Actual unit:**drivers/iommu/mtk_iommu.c**, generated mtk_iommu.mod.c from modpost.
Public provider units: drivers/misc/mediatek/iommu/{iommu_debug,iommu_secure}.c and
drivers/misc/mediatek/smi/mtk-smi-dbg.c. None of their whole modules is owned here.
22 actual target/provider local C/header dependencies are snapshotted and byte-verified
against public5e41 Git blobs in source/compiled-inputs / COMPILED-INPUTS.tsv.
Path canonicalization removes ../ in compiler dependency spelling only; no bytes changed.
Generated .mod.c and common/generated headers have distinct provenance, not mislabeled
as ALPS C. Native conditional compilation follows pinned Kconfig/config and Makefile.

Patch0001-owned-iommu-build-scope.patch replaces root traversal and adds leaf Kbuild
including native Makefile flags, obj-m=mtk_iommu.o and obj-y empty. Unrelated ARM/SMMUv3
platform modules are excluded. **No target/provider C/header changed.**
Patched target tree:**215dc02bdad5d17160d13e5efa51ac9e35f6e41b**.
Pristine provider tree:**9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c**.

License/provenance retained in recipe LICENSE-PROVENANCE.md and upstream source notices.
Source/evidence hashes and local Git commits preserve results. No private firmware,
stock KO, calibration, secrets, hidden uncommitted header edits or temporary helper dependency.
