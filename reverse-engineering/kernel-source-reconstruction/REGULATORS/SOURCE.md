# Source identity and preservation

Maintained recipe: `../android_kernel_modules_regulators_ulefone_gq5012bf1`, accepted
commit `33130d53c94404f65e1661ffa4113bde21cb4b08` (also source/COMMIT).

| Input | Immutable full commit | Required tree |
|---|---|---|
| NothingOSS/ALPS compiled C + headers |5e415e059253ce0d2e61c97108e5f5785d71f06f|9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c|
| NothingOSS vendor Kconfig/defconfig |957dac185efe46cbf6336b0fff9516d84c8cd78f|05f9c65d40ef9e4bdbe17397a90edd303a5da6dd|
| Android kernel/common GKI12901745 |6b18f0b574ab3267615ae6ce642d5a7c3c21ac09|710eb859513863cda0204995a411d5795ad3fe92|
| Android clang prebuilts/r487747c |7775eb113f960bc69a780b621d03a715914d4bca|subtree8eb8e3afb00a52d48b29381d73daf352362231ad|

Exact upstream URLs, roles, full hashes and subtrees: source/SOURCE-PINS.tsv and the
maintained SOURCE-PINS.tsv. Source-candidate blob comparison is preserved in
`evidence/inventory/source-candidate-blobs.tsv`.

Main source: drivers/regulator/{mt6315-regulator,mt6363-regulator,mtk-dvfsrc-regulator,
rt6160-regulator}.c. Kconfig and Makefile are preserved upstream; a new explicit Kbuild
wrapper retains their flags but builds exactly those four.o entries, excluding extbuck,
RT5133, MT6369, camera VMM and other regulators. Config remains stock-equivalent.
Header layouts/registers come from the same immutable source, not copied private headers.

Two complete Kbuild-only patches in the maintained patches/ directory:
1.0001-owned-regulators-build-scope.patch: root scope and original regulator Makefile wrapper.
2.0002-dvfsrc-provider-witness-scope.patch: independently compile actual mtk-dvfsrc.c for
   genksyms/export-type/KCFI witnesses; no provider module shipped/certified here.

Patched full target tree:19842bca6547d2e4ce109e4a8705c6fd26dee842.
Patched witness tree:fe4b33e357ba4dc58aac7ee1513732ddf346dffe.
Every pristine/patched tree is verified during each assembly. No C source changed.

Recovery: source/android_kernel_modules_regulators_ulefone_gq5012bf1.bundle contains the
committed recipe, patches and reference assertions; source/stock-matched/ retains the actual
four C files and key GPL headers verbatim, with blob/SHA identity ledger. That selected
snapshot is an inspectable source aid, not a self-contained replacement for the full tree.
Independent builds retrieved identity-verified public inputs from
/home/armol/kernel-work/lieppos-gpu-pin-mirror. A separate complete regulator recovery mirror
was subsequently preserved at /home/armol/kernel-work/regulators-pin-mirror: all three public
Git pins, exact compiler archive and public core symvers; identities/archive hashes are in
source/offline-mirror.json. Neither contains old regulator build objects/kout. archive-pins.sh
recreates this mirror from verified public inputs. GKI symvers is
public build12901745, compressed and SHA-bound in reference/ for recovery.

Licensing: upstream notices retained, main sources/patches/local scripts GPL-2.0. Compiler
retains its LLVM licences; no firmware, stock binaries, proprietary PMIC data or calibration
is bundled. These drivers import no firmware/NVMEM interface. A source function touching
an EFUSE-named reserved register (VA15 path) is preserved, not executed or reinterpreted as
permission to access calibration.
