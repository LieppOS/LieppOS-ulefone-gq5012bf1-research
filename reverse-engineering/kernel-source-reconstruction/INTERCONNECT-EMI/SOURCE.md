# Source, identity and provenance

Maintained local repository:
`/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_interconnect_emi_ulefone_gq5012bf1`

Accepted commit: **e03fc92f55b2976c54b3461741fdcf55f870a3b9**.
No remote configured; no push. Recovery: source/android_kernel_modules_interconnect_emi_ulefone_gq5012bf1.bundle.

| Role | Immutable public revision | Verified tree |
|---|---|---|
| Compiled vendor source, headers, twelve provider objects | ALPS5e415e059253ce0d2e61c97108e5f5785d71f06f |9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c|
| Vendor Kconfig/defconfig only | NothingOSS957dac185efe46cbf6336b0fff9516d84c8cd78f |05f9c65d40ef9e4bdbe17397a90edd303a5da6dd|
| GKI common/kbuild/headers |6b18f0b574ab3267615ae6ce642d5a7c3c21ac09|710eb859513863cda0204995a411d5795ad3fe92|
| clang-r487747c subtree |7775eb113f960bc69a780b621d03a715914d4bca|8eb8e3afb00a52d48b29381d73daf352362231ad|

Full upstream URLs, role and tree declarations are in the maintained SOURCE-PINS.tsv;
Git and content identity are checked before use. Compiler is Android clang17.0.2 build
10087095 with pinned lld/LLVM. Core symvers is immutable public GKI12901745 metadata,
not a stock implementation. Its exact hash is in reference/gki-vmlinux.symvers.sha256.

## Actual compilation units

All under drivers/interconnect/mediatek:
- mmqos-common: **mmqos-mtk.c, mmqos-hrt.c, mmqos-vcp.c, mmqos-test.c**, linked together.
- mmqos-mt6878: **mmqos-mt6878.c**, descriptors/OF platform wrapper.
- mtk-emi: **mtk-emi.c**, Linux ICC vote provider, not the separate emi.ko controller.

45 actual vendor C/header dependencies are snapshotted in source/compiled-inputs with
COMPILED-INPUTS.tsv; every byte is checked against its public5e415e Git blob. Generated
.mod.c files are not mislabelled public source; modpost regenerates them. Common/GKI
headers and generated outputs are fixed by separate source/config identities.
Kconfig, native Makefile and actual #ifdef compilation come from the same pinned trees.

ALPS and957dac candidate blob comparison is preserved for each relevant file. The newer
mmqos-mtk.c changes record_idx initialization0→-1; a source difference alone does not
prove a missing OEM implementation or an accepted donor. The compiled older ALPS source
has complete stock parity. The other five C units have identical candidate blobs.

## Complete patches, no behavioral source patch

0001-owned-interconnect-build-scope.patch adds scoped Kbuild files, preserves native
Makefile flags, and uses -I$(src) for local trace header expansion in absolute builds.
0002-provider-trace-include.patch adds that same include fix to mtk-interconnect/core.c's
Kbuild. It compiles real full provider objects, not declaration shims.
Target patched tree:a3577732657286d71f3355d1439093e5229f1129.
Provider patched tree:24fc215eb884f013bdc3e16dc5d56b5bcabdea26.
All upstream C remains unchanged; no compiled ELF byte edits.

Public inputs additionally preserved at /home/armol/kernel-work/interconnect-pin-mirror;
compiler archive and core symvers have checksums, Git snapshots retain pinned objects.
This mirror is separate from development outputs. Source/evidence checksums preserve all
new findings. No private firmware, calibration, stock KO or unrelated compiled vendor
binary is included in the maintained recipe.
