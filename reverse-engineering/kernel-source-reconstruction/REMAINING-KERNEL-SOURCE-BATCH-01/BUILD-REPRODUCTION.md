# Build reproduction

## Development

D1 was built offline in `/home/armol/kernel-work/remaining-kernel-source-batch-01/dev/ws` with four CPUs and
`nice 10`. All four domains exited 0:

- NATIVE: reboot-mode and syscon-reboot-mode;
- EXT_HBT;
- EXT_SCHED;
- EXT_GPU.

Strict acceptance passed 5/5; 69/69 deliberate ELF mutations were rejected. The development workspace was then
renamed `quarantined-development` before independent proof.

## Path-determinism correction (preserved negative experiment)

Initial committed proof at `d331daa6` passed stock acceptance and 69/69 mutations in both fresh workspaces. The
native pair was raw-identical between workspaces. For the three external targets only their GNU build IDs differed:
workspace paths in DWARF affect the link-time build-ID even though debug sections are stripped. Every normalized
module was still equal to stock.

Commit `7e07384a` adds `-ffile-prefix-map` and `-fdebug-prefix-map` for the external roots. No target source or
accepted non-build-ID byte changed. The initial proof remains under `kernel-work/.../proof`; final proof is under
`proof-final`.

## Final independent proof

Bundle `bundles/remaining-kernel-source.bundle` (sha256
`9ceed647a22a7be496a22abcc9ae3a43048c2de0e7542b75bf3ede08ede990f0`) was verified, then cloned twice with
`--no-hardlinks`. Both clones:

1. checked out exact commit `7e07384a96580bef13ff3f075355c20b4305a4da` with no alternates;
2. passed `git fsck --full`;
3. bootstrapped exclusively from immutable offline mirrors;
4. generated vendor kout from GKI config + Nothing `mgk_64_k61_defconfig`;
5. built the OEM BTF base from public MTK ACK source, vendor config, clang r487747c and pahole 1.23;
6. built the five targets at four jobs / four pinned CPUs under `nice 10`;
7. ran strict whole-file stock acceptance and mutation controls.

| Check | B1 | B2 | Cross-build |
|---|---:|---:|---|
| build domains | 4/4 exit 0 | 4/4 exit 0 | — |
| whole-file stock acceptance | 5/5 | 5/5 | same normalized hashes |
| ELF mutation controls | 69/69 | 69/69 | — |
| raw `.ko` + stripped outputs | 10 files | 10 files | **10/10 byte-identical** |
| intermediate `.o` files | 13 | 13 | **13/13 byte-identical** |
| vendor/native config hashes | b826d842 / 841b4ed8 | same | identical content |
| native Module.symvers | 7,997 lines | same | byte-identical |
| assembled trees | 2 | same | byte-identical |
| source-built BTF base | `cafe5987…` | same | byte-identical |

The raw rebuild differs from stock at exactly one contiguous 20-byte range: the GNU build-ID descriptor. All
other bytes are exact, including complete module BTF for the reboot pair. `verify.py` additionally emits function,
data, section, relocation, import/export, KCFI and metadata ledgers.

Proof metadata is under `evidence/independent-proof/{B1,B2}`. Stock and rebuilt ELF operands are not committed.
