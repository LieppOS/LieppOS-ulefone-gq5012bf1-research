# Independent clean-checkout build reproduction

Maintained commit:33130d53c94404f65e1661ffa4113bde21cb4b08.
Final fresh clone:/home/armol/kernel-work/regulators-final-cleancheck/repo; empty ws beside it.
Initial b6aaaf3 recipe clone ran with original development directory moved away throughout
bootstrap/B1/B2/stock acceptance; initial proof log remains separately preserved. Generated
Python bytecode was removed in33130d5 with no C/build-logic change, then that exact commit
passed another fresh clone and empty workspace using the separate regulator recovery mirror.
No old kout, module.o, hand-edited symvers or environment shim was available as a recipe input.

## Inputs and exact settings

- All full public hashes/tree identities:SOURCE.md / SOURCE-PINS.tsv.
- clang-r487747c, Android clang17.0.2/build10087095; LLVM=1 LLVM_IAS=1 ARCH=arm64.
- GKI build12901745 public vmlinux.symvers; SHA-bound reference recovery copy.
- Fresh gki_defconfig +957dac mgk_64_k61_defconfig via KCONFIG_EXT_PREFIX; resulting
  config SHA2568f9d1d2901dfbc77062764b4f9e21bc1000097392a36f8ba1eebd9c47d35f50e.
- Stock release6.1.115-android14-11-g945dff7bc1bf; module_scmversion empty.
- KCFLAGS:-D__ANDROID_COMMON_KERNEL__ -faddrsig
  -fmacro-prefix-map=<target-source>/=../kernel_device_modules-6.1/.
- Original vendor include ordering/-Werror, no header overlay. Fixed userlieppos,
  hostregulators-build, version1, timestampThu Oct8 12:00:00UTC2026.
- DEVICE_MODULES_REGULATOR_MT6315=m, REGULATOR_MT6363=m,
  DEVICE_MODULES_REGULATOR_MTK_DVFSRC=m, DEVICE_MODULES_REGULATOR_RT6160=m and MTK_DVFSRC=m
  from the accepted regenerated config. Scope-only patches suppress all non-target output.
- Host glibc qualifier-warning demotion in modules_prepare affects host resolve_btfids,
  not module compilation; identical to the accepted infrastructure recipe.

## Run

```sh
export LIEPPOS_REGULATORS_MIRROR=/home/armol/kernel-work/regulators-pin-mirror
/path/to/fresh-recipe/scripts/bootstrap.sh /space-free/empty-ws
/path/to/fresh-recipe/scripts/b1b2.sh /space-free/empty-ws /path/to/extracted-stock/lib/modules
```

Every mirror input is checked by immutable source/compiler tree id or GKI symvers SHA256.
bootstrap supports public URLs for later recovery, but no network retrieval was used here.
Each build independently deletes/recreates target/witness trees and kout, regenerates config
and prepares headers, compiles real mtk-dvfsrc.c, checks four source-derived genksyms CRCs
and actual export licence buckets, then builds exactly four modules with no diagnostics.
No final-target unresolved modpost symbol is tolerated. Initial discovery of two omitted
tracepoint exports was fixed by adding both to the **source-generated** provider witnesses,
not by suppressing modpost or fabricating symbols.

**B1=B2** for4 raw.ko,4 stripped.ko, all8 target.o including generated.mod.o,
provider.o, target/core/external symvers, CRC witnesses, configuration and both full source
identities. Full stock acceptance is separate and passes all4. Raw IDs are deterministic
within the same rebuilt workspace; cross-workspace DWARF paths affect raw IDs, so the
stock equivalence claim is on standard strip-debug outputs.

Evidence: evidence/build/B{1,2}-* and b1b2-clean-checkout.log; complete acceptance.json and
axis ledgers. The exact provider compile command/dependencies/#SYMVER records are preserved
verbatim in evidence/build/provider-object.cmd.xz (compression keeps Kbuild's original
whitespace without rewriting provenance). Both stock operands and reference-only acceptance
are SHA-bound. Nine negative
verifier tests reject real content/ABI/KCFI changes while allowing only the GNU descriptor.
No ELF patching, srcversion deletion, signature masking or stock-code transplantation occurs.
