# Independent clean-checkout build reproduction

Accepted maintained commit: **e03fc92f55b2976c54b3461741fdcf55f870a3b9**.
Clone:/home/armol/kernel-work/interconnect-cleancheck/repo; initially empty workspace
beside it. Development directory was moved away throughout bootstrap/B1/B2/stock
acceptance and restored only afterward. Source/ABI inputs came solely from the separately
preserved public /home/armol/kernel-work/interconnect-pin-mirror. No copied objects,
old kout, private header overlay, temporary environment shim or device interaction.

```sh
RECIPE='/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_interconnect_emi_ulefone_gq5012bf1'
git clone "$RECIPE" /home/armol/kernel-work/interconnect-repro/repo
cd /home/armol/kernel-work/interconnect-repro/repo
export LIEPPOS_INTERCONNECT_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror
export JOBS=12 PYTHONDONTWRITEBYTECODE=1
scripts/bootstrap.sh /home/armol/kernel-work/interconnect-repro/ws
scripts/b1b2.sh /home/armol/kernel-work/interconnect-repro/ws \
 '/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules'
```

Or clone source/android_kernel_modules_interconnect_emi_ulefone_gq5012bf1.bundle and
verify HEAD against source/COMMIT. Bundle contains no required build artifacts. The
public source/compiler mirror can be regenerated using archive-pins.sh from verified
pristine inputs; its Git objects/tree IDs and compiler archive/content tree are fixed.
Upstream source URLs are preserved but task bootstrap requires local mirror/offline IO.

## Exact build settings

GKI12901745 compiler: Android clang17.0.2 build10087095 (r487747c), pinned lld/LLVM,
ARCH=arm64 LLVM=1 LLVM_IAS=1. GKI gki_defconfig plus957dac mgk_64_k61_defconfig yields
.config **8f9d1d2901dfbc77062764b4f9e21bc1000097392a36f8ba1eebd9c47d35f50e**.
Regenerate modules_prepare headers and stamp stock kernel release; use hash-bound public
12901745 vmlinux.symvers. Actual compiler/link commands retain KCFI/modversions, stock
-faddrsig, __ANDROID_COMMON_KERNEL__, native includes and public __FILE__ prefix mapping.
No ACK_DIR is permitted. User/host/version/timestamp fixed in build.sh. Only glibc
qualifier warning in host bpf tools is demoted; no target warning is ignored.

Provider compilation is twelve exact .o goals, not extra delivered modules. Every
required source #SYMVER is unique, CRC-identical and correct licence bucket. Correct
producer basename reproduces .modinfo depends; core GKI metadata and reference hashes
are assertions, not fabricated implementations. Neither ELF code nor data is edited.
Exact twelve provider commands/dependencies are compressed verbatim under
provider-commands; target commands/config/source and all object hashes are retained.

## Determinism and separate stock acceptance

Each build removes/recreates source trees, kout/config/generated headers and provider
outputs. B1/B2 comparisons cover three raw debug KOs, three stock-packaged stripped KOs,
all10 target .o files (six units, one common aggregate, three .mod.o), twelve provider
.o files, all symvers/CRC witnesses, .config and source-tree identities. All match.
Stock shipped modules are stripped; llvm-strip --strip-debug is the packaging operation,
not a behavioral normalization. The complete packaged ELF is compared byte-for-byte.
Only parsed20-byte GNU descriptors differ: offsets0x16350 /0x3d10 /0x4050. Raw offsets,
hashes and descriptor bytes are stored before normalization. No srcversion, modinfo,
section, symbol/string, data, KCFI or relocation normalization.

verify.py also materializes all139 functions,316 data objects,164 import slots,30
export CRC/licence records,12 absolute KCFI IDs and4144 raw/semantic relocations.
Fourteen disposable mutation cases pass: metadata-only GNU change accepted; instructions,
node/policy data, import/export CRCs, module metadata, relocations, symbol names and CFI
changes rejected, including platform and EMI operands. Stock files are never mutated.

## Research evidence regeneration (host only)

```sh
python3 scripts/map-topology.py <accepted-ws> <stock-merged.dtb> <saved-devicetree.tar> <evidence/hardware>
python3 scripts/finish-evidence.py <recipe> <accepted-ws>
python3 scripts/test-acceptance.py <recipe> <accepted-ws>/out/B1
```

Those scripts validate source/compiled field layouts, typed references, cross-component
CRC/CFI boundaries and immutable public snapshots. prepare-reference.py is the historical
pre-build identity/scope generator, not a required hidden build input. Final source/evidence
checksums and Git commits preserve results. Hardware deployment/validation is deferred.
