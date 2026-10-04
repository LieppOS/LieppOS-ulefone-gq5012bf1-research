# FBE → inline-crypto → secure-world boundary (interfaces only)

No keys, key blobs or per-user material were read. The chain is reconstructed from stock fstab, init/vintf, the module ABI and existing property captures.

```text
Android (vold)                                   user space, AOSP
  │  fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized
  │  metadata: keydirectory=/metadata/vold/metadata_encryption
  │
  ├─► KeyMint HAL  android.hardware.security.keymint@3.0-service.trustkernel   ← PROPRIETARY
  │     (also gatekeeper-service.trustkernel)                                     TrustKernel
  │        └─► /dev/tkcore* ─► tkcore.ko / tkcore_drv.ko ─► SMC ─► TrustKernel TEE (t6)
  │     KeyMint wraps/unwraps vold's storage keys. Raw per-file/metadata keys are
  │     returned to vold (standard keys, not hardware-wrapped).
  │
  ├─► FS_IOC_ADD_ENCRYPTION_KEY ─► fscrypt (GKI) ─► blk-crypto (GKI)
  │                                            └─► dm-default-key (GKI) for metadata
  │
  └─► blk-crypto keyslot manager ─► ufshcd-crypto (GKI) ─► UFSHCI crypto keyslots
                                      (MMIO @0x112b0000, AES-256-XTS)
                                      engine enabled by ufs-mediatek-mod via
                                      SiP UFS_MTK_SIP_CRYPTO_CTRL ─► ATF (MTK BL31)
```

| boundary | Linux-side code | status |
|---|---|---|
| fscrypt / blk-crypto / dm-default-key | GKI built-in (ACK `6b18f0b574ab`, exact GKI binary identity proven elsewhere) | generic, no vendor patch |
| UFS keyslot programming | GKI `ufshcd-crypto` | generic |
| UFS crypto engine enable / reset / clocks | `ufs-mediatek-mod.ko` | **source-exact** (this work) |
| ATF SiP `UFS_MTK_SIP_CRYPTO_CTRL` | MTK BL31 | proprietary firmware; interface = SMC function id + arg 1 |
| KeyMint / Gatekeeper | `*.trustkernel` HALs + TrustKernel TAs | proprietary; out of scope |
| TEE kernel driver | `tkcore.ko`, `tkcore_drv.ko` | separate component (TrustKernel), not part of storage |

Hardware-wrapped keys are **not used**. The UFS module has no wrapped-key operations, and the fstab has no `wrappedkey_v0` flag. Encryption keys therefore exist in kernel memory and are programmed into UFSHCI keyslots by Linux. This document intentionally stops at the interface.
