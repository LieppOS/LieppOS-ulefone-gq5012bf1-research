# Build reproduction — GPU-AI-AUX-KERNEL-INTERFACES

Everything below was executed offline; no device was contacted.

## 1. Procedure actually run

```sh
git clone <local>/android_kernel_modules_gpu_ai_aux_ulefone_gq5012bf1 repo   # @ aa21b33
export LIEPPOS_GPUAUX_MIRROR=<offline pin mirror>   # or omit to fetch upstream
repo/scripts/bootstrap.sh ws                        # verifies each pin by tree id / sha256
repo/scripts/b1b2.sh      ws <stock-dir>            # B1, B2, compare, full acceptance
```

`bootstrap.sh` verified: `common` tree `710eb8595138…`, clang tree `8eb8e3afb00a…`
(`clang --version` carries `based on r487747c`), `kdm` tree `05f9c65d40ef…`,
`alps5e41` tree `9c61acc3cb0d…`, GKI 12901745 `vmlinux.symvers` sha256 `61933b61252e…`.

Each build then, from scratch:

1. `assemble.sh` — re-extracts both source trees from the pinned commit, asserts the base
   tree id, applies the patch with `git apply --index`, asserts the patched tree id
   (`src/kdm` `d3a42d6e93f0…`, `src/prov` `3e04c795a4b8…`).
2. `make-kout.sh` — `gki_defconfig` + vendor `mgk_64_k61_defconfig` via
   `KCONFIG_EXT_PREFIX`, asserts `.config` sha256
   `8f9d1d2901dfbc77062764b4f9e21bc1000097392a36f8ba1eebd9c47d35f50e`, runs
   `modules_prepare`, stamps `kernel.release` to `6.1.115-android14-11-g945dff7bc1bf`,
   installs the GKI `vmlinux.symvers` as `Module.symvers`.
3. `derive-provider-crcs.sh` — compiles the provider witness scope and asserts
   `16/16 source-derived provider CRCs equal stock consumer references`.
4. `build.sh` — builds `drivers/misc/mediatek/vcp/rv` then `drivers/gpu/mediatek/gpueb`
   and **rejects** any `error:`, `WARNING: modpost` or `ERROR: modpost` line. Both
   directories built clean.

Compiler invocation (`scripts/kb.sh`): `ARCH=arm64 LLVM=1 LLVM_IAS=1 module_scmversion=`,
`DEVICE_MODULES_PATH=<src/kdm>`, `DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1`,
`KCFLAGS="-D__ANDROID_COMMON_KERNEL__ -faddrsig -fmacro-prefix-map=<src>/=../kernel_device_modules-6.1/"`.
The VCP Makefile's own `-D DEBUG_DO -fno-pic -mcmodel=large` is used unchanged.
`KBUILD_BUILD_{USER,HOST,VERSION,TIMESTAMP}` are fixed so nothing in `.modinfo` is
host-dependent.

## 2. B1 == B2

Compared and equal: `SHA256SUMS` (3 raw + 3 stripped modules + provider symvers),
`INTERMEDIATE-SHA256SUMS` (**22** target objects, including the three `.mod.o` and the
composite `gpueb.o` / `vcp.o`), `provider-crc-witnesses.tsv`, `config.sha256`,
`SOURCE-TREE` (both tree ids).

B1 stripped-module hashes (identical in B2):

```
e148f639fe77168c78872932d424e0390b9c92b9fdddd368d518f8b89fb71ba7  gpueb
748eb0eb2eb74cd4b40546cfa3b7525ee6af8784036281af2bba74893722a8a4  vcp
7b7a9bd3f92d3a64d1bb66124e0f7070eba05a1ebcde504fdeda58a886b42c0f  vcp_status
```

## 3. Stock comparison

```
gpueb      PASS  bytes 109016  raw_differing_bytes 20  unresolved 0
vcp        PASS  bytes 268776  raw_differing_bytes 20  unresolved 0
vcp_status PASS  bytes  22624  raw_differing_bytes 20  unresolved 0
```

Normalized (build-ID-zeroed) sha256 of the rebuild equals stock for all three:
`723a266ccb12…`, `79bd2cdf96c1…`, `0e2e0242280b…`. `verify.py` asserts that every
differing byte falls inside the module's recorded build-ID range, so a difference anywhere
else would abort rather than be reported as a pass.

## 4. No dependency on earlier scratch trees

The clean checkout used only the cloned repository, the pin mirror and the stock modules.
It did not read `/home/armol/kernel-work/gpuaux-reconstruction` (the development
workspace), any prepared `kout`, or any other component's workspace.

## 5. Transcripts

`evidence/reconstruction/build/`: `clean-checkout-bootstrap.log`,
`b1b2-clean-checkout.log`, `B1-SHA256SUMS.txt`, `B2-SHA256SUMS.txt`,
`B1-INTERMEDIATE-SHA256SUMS.txt`, `natural-external-provider.symvers`,
`provider-crc-witnesses.tsv`, `source-tree-ids.txt`.
