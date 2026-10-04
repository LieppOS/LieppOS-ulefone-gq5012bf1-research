# Build configuration for the exact storage rebuilds

- Kernel object tree: GKI `kout` for ACK `6b18f0b574ab` (android14-6.1-2024-12_r4) with `CONFIG_LTO_NONE`. Flags: `KCFLAGS=-faddrsig`, `-fmacro-prefix-map=<tree>/=../kernel_device_modules-6.1/`, clang-r487747c.
- Vendor source: MTK ALPS `5e415e059253`, plus [`../kdm-patches/`](../kdm-patches/).
- Isolated `M=` build per module: [`../../scripts/sb.sh`](../../scripts/sb.sh), with all modules in [`../../scripts/build-all.sh`](../../scripts/build-all.sh). Vendor provider CRCs come from stock-harvested `stock-all.symvers`.
- `ack-ufshcd-h-mtk-debug-vops.patch`, `ack-ufshcd-priv-h-mtk-debug-vops.patch`: MTK's ACK hunks (from NothingOSS `android_kernel_6.1_nothing_mt6878` `d6343dbbb`). They are prepended to the include path (`XLINUXINCLUDE`) for the UFS modules and change **only** line numbers (`CONFIG_MTK_UFS_DEBUG_BUILD` is off). The `-fmacro-prefix-map` for that directory makes `__FILE__` read `include/ufs/ufshcd.h`, as in stock.
- `gq5012bf1-no-trustonic.h`: force-included for `rpmb-mtk.o` only, and undefines `CONFIG_TRUSTONIC_TEE_SUPPORT{,_MODULE}`. The stock module imports no MobiCore symbols. The shared `kout` `.config` sets Trustonic `=m`; the GQ5012BF1 board does not ship a Trustonic driver.
- `rpmb-mtk` is built against symvers in which `ufs_mtk_rpmb_get_raw_dev` belongs to `ufs-mediatek-mod-ise`. This reproduces the stock `depends=ufs-mediatek-mod-ise,rpmb`; the CRC is unchanged (`0x4dfeeb1d`).
