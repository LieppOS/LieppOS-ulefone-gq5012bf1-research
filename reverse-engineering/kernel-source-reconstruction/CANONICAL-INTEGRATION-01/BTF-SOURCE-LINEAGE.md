# OEM split-BTF base lineage (six identities)

thermal-generic-adc, cfg80211, mac80211, vendor bluetooth, drm_display_helper and drm_dma_helper
are BTF-encoded against a base vmlinux built from public source, never from stock BTF:
NothingOSS `android_kernel_6.1_nothing_mt6878` c364c39ae8d83dfb5d72802a7718b756c238b07e
(tree fb0bf39188577b248bb2bc537856964e13e1746c, MTK ACK merge of GKI 6b18f0b5) with the pinned
vendor configuration and Kleaf flags recorded in each recipe's `scripts/make-btf-base.sh` and
`reference/gq5012bf1-vendor.config`, OEM release `6.1.115-android14-11-g945dff7bc1bf`, clang r487747c,
pahole 1.23 (build-tools e905be25). Every recipe rebuilds it and requires `.BTF` SHA256
`cafe5987ff236b6385fb8ec2101d4ee27a4a11f0c6d366b3b3608e69e272202f` (`reference/oem-btf-base.btf.sha256`). Official GKI 12901745 vmlinux.symvers supplies core CRCs separately via KBUILD_MIXED_TREE.

Recipes: connectivity 40bf4296, thermal ff6e97b3 (built 9e0e1a0d), audio_shared_infrastructure
4697eac3. Canonical re-verification against the integration operands: connectivity 17/17,
thermal 34/34, DRM 12/12 strict PASS in both builds; BTF reference mutations are rejected
(connectivity 44, thermal 11, DRM 34 cases per build). No BTF byte was copied, shifted or stripped.
Full investigation: `ALL-C-TO-A-CLOSURE/OEM-BTF-BASE-INVESTIGATION.md`.
