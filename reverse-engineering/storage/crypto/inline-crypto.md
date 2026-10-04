# Storage inline crypto (kernel side)

## Kernel components (no vendor crypto module ships)

| layer | provider | GQ5012BF1 config |
|---|---|---|
| fscrypt | GKI built-in | `CONFIG_FS_ENCRYPTION=y`, `_ALGS=y`, `_INLINE_CRYPT=y` |
| blk-crypto | GKI built-in | `CONFIG_BLK_INLINE_ENCRYPTION=y` and `_FALLBACK=y` (software fallback if no keyslot is available) |
| dm-default-key (metadata encryption) | GKI built-in | `CONFIG_DM_DEFAULT_KEY=y` |
| UFS crypto profile / keyslot manager | GKI `ufshcd-crypto.c` | `CONFIG_SCSI_UFS_CRYPTO=y`. Keyslots and capabilities come from the UFSHCI 2.1 crypto registers (`CCAP`/`CRYPTOCAP`) of the host at `0x112b0000` |
| MTK enablement | `ufs-mediatek-mod` (exact) | `hba->caps |= UFSHCD_CAP_CRYPTO`. On host enable, SiP `UFS_MTK_SIP_CRYPTO_CTRL`(1) asks ATF to enable the engine; if it fails, the cap is cleared and blk-crypto falls back to software. `crypto_rst` is part of every host reset. Clocks: `ufs_fde` (`CLK_TOP_AES_UFSFDE_SEL`), `ufshci_aes`, `ufshci_aes_axi` |
| MTK crypto boost | `ufs-mediatek-mod` | **off** (no `mediatek,ufs-boost-crypt`) |
| MMC/SD crypto | GKI `CONFIG_MMC_CRYPTO=y`; `cqhci-crypto.o` in `cqhci.ko`; `mtk-mmc` `set_crypto_enable_in_sw = true` for mt6878 | SD (MSDC1) has no `crypto_clk` in DT. Adoptable-storage keys go through blk-crypto; whether MSDC1 has a hardware engine is not proven, so the fallback is likely |

Keys are programmed by the generic `ufshcd_crypto_keyslot_program()` (MMIO keyslot write), which is **standard (non-wrapped) inline encryption**. Nothing in the shipped UFS module implements hardware-wrapped keys (`derive_sw_secret` / `BLK_CRYPTO_KEY_TYPE_HW_WRAPPED`).

## Algorithms in use (stock fstab, props)

- `/data`: `fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized`. Contents use AES-256-XTS on the UFS inline engine (IV_INO_LBLK_64 policy flag from `inlinecrypt_optimized`). Filenames use AES-256-CTS in software (`ro.crypto.volume.filenames_mode=aes-256-cts`).
- `/data` metadata encryption: `keydirectory=/metadata/vold/metadata_encryption` with no `metadata_encryption=` option, so the Android default (aes-256-xts) applies through **dm-default-key**. Live evidence: `/dev/block/mapper/userdata -> /dev/block/dm-57` and `ro.crypto.metadata.enabled=true`.
- `ro.crypto.type=file`, `ro.crypto.state=encrypted`.

See [`fbe-boundary.md`](fbe-boundary.md) for the trust boundary.
