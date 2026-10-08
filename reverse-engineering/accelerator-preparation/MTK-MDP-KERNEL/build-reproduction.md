# Build reproduction — MTK-MDP-KERNEL

Everything below was executed offline; no device was contacted.

## 1. Procedure actually run

```sh
git clone <local>/android_kernel_modules_mdp_ulefone_gq5012bf1 repo   # @ 060689b
export LIEPPOS_MDP_MIRROR=<offline pin mirror>      # or omit to fetch upstream
repo/scripts/bootstrap.sh ws                        # verifies each pin by tree id / sha256
repo/scripts/b1b2.sh      ws <stock-dir>            # B1, B2, compare, full acceptance
```

`bootstrap.sh` verified: `common` tree `710eb8595138…`, clang tree `8eb8e3afb00a…`
(`clang --version` carries `based on r487747c`), `kdm` tree `05f9c65d40ef…`,
`alps5e41` tree `9c61acc3cb0d…`, GKI 12901745 `vmlinux.symvers`
sha256 `61933b61252e…`.

Each build then, from scratch:

1. `assemble.sh` — re-extracts both source trees from the pinned commit, asserts the base
   tree id, applies the patch with `git apply --index`, asserts the patched tree id
   (`src/kdm` `d715f99efb3e…`, `src/prov` `98fe646c134c…`).
2. `make-kout.sh` — `gki_defconfig` + vendor `mgk_64_k61_defconfig` via
   `KCONFIG_EXT_PREFIX`, asserts `.config` sha256
   `8f9d1d2901dfbc77062764b4f9e21bc1000097392a36f8ba1eebd9c47d35f50e`, runs
   `modules_prepare`, stamps `UTS_RELEASE`/`kernel.release` to
   `6.1.115-android14-11-g945dff7bc1bf`, installs the GKI `vmlinux.symvers` as
   `Module.symvers`.
3. `derive-provider-crcs.sh` — compiles the provider witness scope and asserts
   `111/111 source-derived provider CRCs equal stock consumer references`.
4. `build.sh` — builds `drivers/clk/mediatek`, `drivers/misc/mediatek/mdp`,
   `drivers/gpu/drm/mediatek/mml` in that order and **rejects** any `error:`,
   `WARNING: modpost` or `ERROR: modpost` line. All three directories built clean.

Compiler invocation (`scripts/kb.sh`): `ARCH=arm64 LLVM=1 LLVM_IAS=1 module_scmversion=`,
`DEVICE_MODULES_PATH=<src/kdm>`, `DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1`,
`KCFLAGS="-D__ANDROID_COMMON_KERNEL__ -faddrsig -fmacro-prefix-map=<src>/=../kernel_device_modules-6.1/"`.
`-faddrsig` is required (stock carries `.llvm_addrsig`); the prefix map reproduces the
`__FILE__` spelling baked into stock strings. `KBUILD_BUILD_{USER,HOST,VERSION,TIMESTAMP}`
are fixed so nothing in `.modinfo` is host-dependent.

## 2. B1 == B2

Compared and equal: `SHA256SUMS` (4 raw + 4 stripped modules + provider symvers),
`INTERMEDIATE-SHA256SUMS` (**54** target objects, including the three `.mod.o` and the
composite `mtk-mml.o` / `mdp_drv_mt6878.o`), `provider-crc-witnesses.tsv`,
`config.sha256`, `SOURCE-TREE` (both tree ids).

B1 stripped-module hashes (identical in B2):

```
1ad5705a05a0da0d38d31c31038ab02a672571aa81b7e3078149ef63862049d5  clk-mt6878-mdpsys
8519a714f368d91d597287a46e906e38ccdb4d438805ab092ed07357e68e4e5a  mdp_drv_mt6878
ca04e2f38967e9e565bbcf258d3f2628bee27a342e2488ba7f6a3175775726e7  mtk-mml
ed0c432f0a5f9b9d11f8911a56ba129b4514519aca1e02ca95c90cefb7892d6c  mtk-mml-mt6878
```

## 3. Stock comparison

`verify.py` compares the stripped rebuild against stock on every axis and asserts that the
only differing bytes fall in the module's recorded build-ID range:

```
clk-mt6878-mdpsys PASS  bytes 15176     raw_differing_bytes 20  unresolved 0
mdp_drv_mt6878    PASS  bytes 763384    raw_differing_bytes 20  unresolved 0
mtk-mml           PASS  bytes 1894280   raw_differing_bytes 20  unresolved 0
mtk-mml-mt6878    PASS  bytes 23128     raw_differing_bytes 20  unresolved 0
```

Normalized (build-ID-zeroed) sha256 of rebuild == stock for all four:
`ed066364722b…`, `8adcb07234ee…`, `2e3e2ccd44ac…`, `6bd4eca64e84…`.

The two builds choose different build IDs, so the *count* of literally differing bytes in
any single comparison can be 19 or 20 out of the 20-byte descriptor (a byte may coincide);
the descriptor itself is always the whole and only difference.

## 4. No dependency on earlier scratch trees

The clean checkout used only: the cloned repository, the pin mirror and the stock modules.
It did not read `/home/armol/kernel-work/mdp-reconstruction` (the development workspace),
any prepared `kout`, or any other component's workspace.

## 5. Transcripts

`evidence/reconstruction/build/`: `clean-checkout-bootstrap.log`,
`b1b2-clean-checkout.log`, `B1-SHA256SUMS.txt`, `B2-SHA256SUMS.txt`,
`B1-INTERMEDIATE-SHA256SUMS.txt`, `natural-external-provider.symvers`,
`provider-crc-witnesses.tsv`, `source-tree-ids.txt`.
