# UFS kernel stack: exact reconstruction

## Modules (A = stock vendor_ramdisk `.ko`, B = isolated rebuild, debug-stripped)

| module | functions | data | imports (CRC) | exports | export CRCs | KCFI | relocs | ELF sections |
|---|---|---|---|---|---|---|---|---|
| `ufs-mediatek-mod.ko` | **98/98** | 69/69 | 201/201 | 10/10 | 9/9 | 98/98 | 1907/1907 | 61/61 except build-id |
| `ufs-mediatek-dbg.ko` | **32/32** | 31/31 | 43/43 | 11/11 | 10/10 | 32/32 | 1044/1044 | 47/47 except build-id |
| `phy-mtk-ufs.ko` | **11/11** | 19/19 | 24/24 | 0 | — | 11/11 | 90/90 | 40/40 except build-id |

All three modules have identical modinfo, vermagic `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` and `__versions` order. Their symbol tables are identical once `__UNIQUE_ID` counters are normalised, and two clean rebuilds are file-identical (B1==B2). Per-symbol tables are in [`parity/`](parity/), and the whole-module proof is [`../kernel/parity/full-module-proof.txt`](../kernel/parity/full-module-proof.txt).

## Source lineage (proven, not branch-tip similarity)

- **Base:** MTK ALPS MT6878 `5e415e059253ce0d2e61c97108e5f5785d71f06f` (2025-02-25, NothingOSS `android_kernel_device_modules_6.1_nothing_mt6878` history). This is the same snapshot proven exact for `mediatek-drm.ko`. With no edits it already gives 98/98 for `ufs-mediatek-mod` (functions), 11/11 for `phy-mtk-ufs`, and 29/32 for `ufs-mediatek-dbg`.
- **Object set** (`drivers/ufs/vendor/Makefile`, non-iSE variant `ufs-mediatek-mod`): `ufs-mediatek.o`, `ufs-mediatek-sysfs.o`, `ufs-mediatek-mimic.o`, `ufs-mediatek-btag.o`, `ufs-mediatek-rpmb.o` and `ufs-mediatek-ise-dummy.o`. Not built: `ufsfeature`/`ufsshpb`/`ufstw`/`ufshid`/`ufsringbuf`. Their symbols are absent from stock even though the shared `kout` `.config` has `CONFIG_UFSFEATURE=y` and `CONFIG_UFSHID=y`.
- **Header layout from MTK's own ACK:** stock `__bug_table` line numbers for the inline `ufshcd_get_variant()` `BUG_ON` are 1338/1328, against 1333/1323 in the Google ACK `6b18f0b574ab`. The +5 lines are MTK's ACK hunk adding `check_bus_status`/`dbg_dump` to `struct ufs_hba_variant_ops` under `CONFIG_MTK_UFS_DEBUG_BUILD`, plus matching `ufshcd-priv.h` helpers, exactly as carried in `NothingOSS android_kernel_6.1_nothing_mt6878` (`d6343dbbb`). `CONFIG_MTK_UFS_DEBUG_BUILD` is off, so only line numbers change: [`../reconstruction/build-config/`](../reconstruction/build-config/).
- **ufs-mediatek-dbg:** the three residual functions differ only in the `__LINE__` immediates of `ufs_mtk_aee_warning()`, 136/160/189 in stock against 67/91/120 here. That proves 69 extra source lines before `ufs_mtk_eh_abort`, and the padding patch [`0001`](../reconstruction/kdm-patches/) inserts exactly those (text not recoverable).
- `phy-mtk-ufs`: unmodified ALPS.

No GQ5012BF1 functional change exists in the UFS host, PHY or debug code.

## Documents

- [`dt-contract.md`](dt-contract.md): DT properties, to driver caps, to effect.
- [`power-state-machine.md`](power-state-machine.md): link startup, hibern8, runtime and system PM, refclk, regulators, MTCMOS, reset, error recovery.
- [`feature-map.md`](feature-map.md): ENABLED/DISABLED/AVAILABLE-BUT-UNUSED features.
- [`health-thermal.md`](health-thermal.md): health descriptor, EOL, temperature and throttling.
- [`../crypto/inline-crypto.md`](../crypto/inline-crypto.md), [`../rpmb/boundary.md`](../rpmb/boundary.md).
