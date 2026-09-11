# yft_tiny2c_usb reconstruction source

This is the committed mirror of the exact-GKI working source at:

`/home/armol/kernel-work/gki-12901745-workspace/lieppos/yft-tiny2c-usb-recon/`

Build target: `//lieppos/yft-tiny2c-usb-recon:yft_tiny2c_usb_recon` against
`//common:kernel_aarch64` at common commit
`6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`.

The `provider-abi/` child is a **build-only ABI witness** for the stock MT6375 GPL data
export `int yft_usb_flag` (natural genksyms CRC `0x398e9c8b`). It must never be installed,
loaded, or shipped. The runtime provider is the stock/source-ported full
`mt6375-charger.ko`.

Authoritative behavioral and parity report:
`../phase4-yft-tiny2c-usb-reconstruction.md`.
