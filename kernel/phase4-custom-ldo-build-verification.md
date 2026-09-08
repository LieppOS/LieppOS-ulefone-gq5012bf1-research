# `custom_ldo.ko` exact-GKI build verification

## Build

* Workspace: `/home/armol/kernel-work/gki-12901745-workspace`
* Kernel: `//common:kernel_aarch64`
* Common commit: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`
* Target: `//lieppos/custom-ldo-recon:custom_ldo_recon`
* Provider target: `//lieppos/custom-ldo-wl2868-recon/stock-name:custom_ldo_wl2868_stock_name`
* Result: `BUILD_RC=0`
* Compiler warnings: 0
* Modpost warnings: 0
* Unresolved symbols: 0
* `check_no_remaining`: emitted

No handwritten or patched `Module.symvers`, fake provider, fake CRC,
`KBUILD_MODPOST_WARN`, or CRC post-processing was used. Kleaf's `deps` stages
the provider's genuinely generated symvers, and the Makefile supplies that file
through `KBUILD_EXTRA_SYMBOLS`.

The provider is the existing reconstructed source built under the stock output
basename `custom-ldo-wl2868.ko`; this preserves the stock generated
`depends=custom-ldo-wl2868` metadata naturally. Its generated exports are:

```text
0x23ec3223 will_ldo_vout .../custom-ldo-wl2868 EXPORT_SYMBOL_GPL
0xdd9b9ea1 will_ldo_en   .../custom-ldo-wl2868 EXPORT_SYMBOL_GPL
```

The consumer's generated exports are:

```text
0xfda530e0 custom_ldo_vout .../custom_ldo EXPORT_SYMBOL
0x239d3df2 custom_ldo_en   .../custom_ldo EXPORT_SYMBOL
```

Both export CRCs and all three imported MODVERSION CRCs match stock exactly.

The build emits two OpenSSL/sign-file diagnostics because the local workspace
has no `common/certs/signing_key.pem`. They are signing-provenance diagnostics,
not compiler warnings, modpost warnings, or unresolved symbols.

## Final artifact

* Module: `workspace/phase4-custom-ldo/recon-custom_ldo.ko`
* SHA-256: `eac87172f411a3f60b7f0f060086521ceea4cf22377dd63b190594fd50de373e`
* Size: 10,288 bytes
* Build ID: `7d0307cb6e73a79b7b13cdfe0706d4e0f89c8338`
* Log: `workspace/phase4-custom-ldo/recon-build.log`
* Consumer symvers: `workspace/phase4-custom-ldo/recon-Module.symvers`
* Provider symvers: `workspace/phase4-custom-ldo/provider-Module.symvers`
* Structural verification: `workspace/phase4-custom-ldo/verify-recon-vs-stock.txt`
