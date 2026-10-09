# Independent build reproduction

| Input/setting | Required value |
|---|---|
| common/KMI | GKI 12901745, common 6b18f0b574ab…; verified public vmlinux.symvers |
| compiler/linker | Android clang 17.0.2 build 10087095, clang-r487747c; LLD/LLVM same pinned tree |
| config | pinned gki_defconfig + 957dac mgk_64_k61_defconfig via KCONFIG_EXT_PREFIX |
| config SHA256 | 8f9d1d2901dfbc77062764b4f9e21bc1000097392a36f8ba1eebd9c47d35f50e |
| release | 6.1.115-android14-11-g945dff7bc1bf (stock vermagic) |
| make | ARCH=arm64 LLVM=1 LLVM_IAS=1; modules_prepare; one M=<src/kdm> modules run |
| KCFLAGS | -D__ANDROID_COMMON_KERNEL__ -faddrsig -fmacro-prefix-map=<kdm>/=../kernel_device_modules-6.1/ |
| includes | DEVCIE_MODULES_INCLUDE=-I<kdm>/include; original vendor -Werror and include/uapi retained |
| module config | DEVICE_MODULES_EINT_MTK=m, DEVICE_MODULES_PINCTRL_MTK_V2=m, DEVICE_MODULES_PINCTRL_MTK_PARIS=m, PINCTRL_MT6878=m, PINCTRL_MT6363=m |
| metadata | module_scmversion empty; build user/host/version/timestamp fixed |
| external providers | NONE; 12 intra-group imports resolved in one modpost; 91 imports use pinned GKI |

All flags/config used in the completed storage/clock recipe were revalidated by these four
ELFs; neither completed component was edited. Host glibc compatibility diagnostic demotion
in modules_prepare affects host resolve_btfids only, not module compilation.

## Independent clean checkout

1. Maintained recipe committed; fresh clone `/home/armol/kernel-work/pinctrl-cleancheck/repo`.
2. Development directory `pinctrl-reconstruction/` moved away for the entire verification.
3. Empty `…/ws`: all immutable inputs acquired from identity-verified public offline mirror,
   not the storage kout or development objects.
4. Source archive + complete scope patch reassembled and checked against full tree identity.
5. Kout regenerated, config hash asserted; core Module.symvers hash verified.
6. B1 built exactly four `.ko`, no compiler/modpost warning/error.
7. B2 independently deleted/recreated every target source and kout; repeat compilation.
8. B1 == B2: four raw + four stripped modules, all **11 target `.o`** including generated
   `.mod.o` and composite pinctrl-mtk-v2.o, module/core symvers, config and source identity.
9. Full stock acceptance: **4/4 PASS**, zero unexplained residue.
10. Development directory restored only after success.

Evidence: `evidence/build/b1b2-clean-checkout.log` and `B{1,2}-*` hash/log/identity records.
No reliance on the original development tree. Build-ID bytes are deterministic within
B1/B2 at the same workspace path; absolute debug paths affect cross-workspace raw IDs.
The initial independent source experiment also produced stock-equivalent stripped outputs.

Every raw stock difference is recorded before normalization in acceptance.json. Only the
20-byte GNU descriptor is zeroed, structurally validated by note name/type/length; no
srcversion, symbol, relocation, instruction or data masking. Standard strip-debug removes
only debug information. No runtime validation is claimed.
