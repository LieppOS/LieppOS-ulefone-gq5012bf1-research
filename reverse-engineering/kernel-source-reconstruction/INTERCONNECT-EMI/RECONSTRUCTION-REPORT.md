# INTERCONNECT-EMI — source reconstruction result

Device: Ulefone Armor29 Pro Thermal / GQ5012BF1 / MT6878T.
Stock:6.1.115-android14-11-g945dff7bc1bf. **All three targets source-certified A**:
complete packaged stock ELF equality except parsed GNU build-ID descriptors; zero
unexplained executable, data, ABI, KCFI, relocation, symbol or section differences.
No component promotion is implied; existing owner is COVERED-GENERIC, status N/A.

| Module | Functions exact | Data exact | Imports / exports | CRC / KCFI | Relocations | Residual |
|---|---:|---:|---:|---|---:|---|
| mmqos-common.ko |129/129|208/208|137/30|exact /8 IDs|3708/3708|GNU ID only|
| mmqos-mt6878.ko |2/2|20/20|5/0|exact /2 IDs|192/192|GNU ID only|
| mtk-emi.ko |8/8|88/88|22/0|exact /2 IDs|244/244|GNU ID only|

These are symbol occurrences, including any aliases/generated trace helpers, not guessed
unique source bodies. See MODULE-PARITY.tsv, FUNCTION-PARITY.tsv, DATA-PARITY.tsv and
complete acceptance axis ledgers. Section counts including NULL:52 /37 /42. Common's
30 exports are GPL; the other two export none. Imports total164:129 core slots,33 real
external providers and2 platform-to-common slots. Source-derived CRCs AND export licence
sections agree for all33 external slots;32 function callee prefixes and one tracepoint
data boundary are checked per actual symbols (see witness ledger for exact counts/types).

## Reconstructed source and build

Maintained recipe: `android_kernel_modules_interconnect_emi_ulefone_gq5012bf1`.
Accepted commit: `e03fc92f55b2976c54b3461741fdcf55f870a3b9`.
All six compiled C files are unchanged ALPS5e415e public source. Two complete Kbuild-only
patches isolate owned modules and resolve local trace headers for absolute external builds.
No C delta, object copying, binary patching, signature manipulation or fake ABI stub.
Producer filename stems (hyphens preserved) generate the exact stock depends strings.

The committed independent clone bootstrapped from immutable public-source mirrors into
an empty workspace. Original development directory was unavailable throughout bootstrap,
B1, B2 and stock acceptance. B2 destroyed/recreated source, kout and provider outputs;
raw and stripped modules, all10 target objects,12 provider objects, symvers/config and
source-tree identities are identical. Actual stock acceptance is independent of determinism.
Fourteen verifier mutation cases pass, including export CRC and all three module operands.

## Raw differences and classification

GNU descriptor ranges: common **0x16350+20**, platform **0x3d10+20**, EMI **0x4050+20**.
All20 bytes differ in each accepted clean build. Every byte outside those ranges matches
stock. Raw offsets, before/after hashes and IDs are retained in acceptance.json.
Only the structurally checked NT_GNU_BUILD_ID descriptor is normalized. Debug sections
are stripped with llvm-strip --strip-debug as stock packaging requires; both unstripped
and packaged B1/B2 artifacts are independently deterministic. No srcversion/modinfo,
relocation, string or symbol normalization. No appended stock module signatures.
Executable/data/ABI coverage is BYTE_EXACT; residual is BUILD_METADATA_ONLY. There is no
COMPILER_ONLY, PROVEN_SEMANTIC_EQUIVALENT or UNRESOLVED behavioral claim.

## Board and ABI contracts

166 node records:1 common,9 common ports,24 logical larbs,132 master ports; every
compiler-expanded source field agrees with compiled stock. Typed graph is acyclic.
MT6878 EMI OF match selects the38-entry mt6873_icc table, not a guessed new controller.
97 board paths resolve (87 private MMQoS,10 Linux EMI);133 IOMMU specifiers are decoded
with domain/table bits preserved;21 physical larb suppliers plus1 common are explicit.
1152 selected static/live properties agree and551 fdtget crosschecks pass.

Seven actual reverse imports match CRC/licence/full target function/KCFI: four DRM,
one camera, two platform-to-common. Sixteen completed camera/MDP/VCodec transport slots
through mtk-icc-core have source-derived CRC and stock/source callee-prefix agreement.
Neither that separate framework nor the other provider modules is certified by this work.

## Limits and deferred runtime work

Recorded module loading is not successful probing or active bandwidth voting. No measured
frequency, throughput, channel/rank count or DRAM type is invented. Dormant EMI GPU/APU/
storage/USB/connectivity entries are not board wiring proof. MMQoS VCP host code is exact;
firmware implementation/execution remains separate. Controlled runtime/Slot B validation,
fault recovery, votes, clocks/regulators, suspend/resume and observability are deferred.
No device access, register/frequency/voltage change, stress test, flash, reboot or push.
