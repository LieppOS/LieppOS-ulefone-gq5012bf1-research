# Actual Ulefone KeyMint backend

Working Slot A proves the phone uses:

    android.hardware.security.keymint@3.0-service.trustkernel

The process runs in:

    u:r:hal_keymint_default:s0

The registered AIDL service is:

    android.hardware.security.keymint.IKeyMintDevice/default

The vendor VINTF manifest declares the TrustKernel KeyMint 3.0 implementation.

Therefore generic NXP Javacard and AOSP Trusty KeyMint implementations found
during broad source searching are not evidence of this device's runtime
backend.

Keystore2 early_boot_ended() performs boot-level-cache setup before propagating
earlyBootEnded() to KeyMint, so the TrustKernel HAL is not yet proven to be
the blocking component.

PHONE_MODIFIED=0
