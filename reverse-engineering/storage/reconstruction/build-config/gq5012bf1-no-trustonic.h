/* GQ5012BF1 board config: the stock rpmb-mtk.ko imports no mc_* (Trustonic
 * MobiCore) symbols, so it was built with CONFIG_TRUSTONIC_TEE_SUPPORT unset
 * (this device uses TrustKernel tkcore). The shared kout .config has it =m. */
#undef CONFIG_TRUSTONIC_TEE_SUPPORT
#undef CONFIG_TRUSTONIC_TEE_SUPPORT_MODULE
