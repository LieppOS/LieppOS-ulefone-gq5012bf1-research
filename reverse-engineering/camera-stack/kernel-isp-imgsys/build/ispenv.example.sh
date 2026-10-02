. /tmp/camenv.sh
export ST="/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/workspace/gq5012bf1/stock"
export KI="$RS/kernel-isp-imgsys"
export K="/home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878"
export VD="$ST/partitions/vendor_dlkm/lib/modules"
export VR="$(dirname "$(find "$ST/vendor-ramdisks" -name mtk-smi.ko | head -1)")"
MODS_VD="mtk-cam-isp7sp mtk_imgsys_isp7sp mtk_imgsys_v4l2 mtk_imgsys_cmdq mtk_hcp mtk_ccuv mtk_aie mtk_aie_debug_7sp_2 camera_dpe_isp7sp pda_drv_mt6878 ccd_rpmsg mtk_rpmsg_mbox mtk-vmm-isp71-regulator mtk-vmm-notifier camera_eeprom_v4l2 camera_af_media imgsensor-glue imgsensor"
MODS_VR="mtk-vmm-spm clk-mt6878-cam clk-mt6878-img clk-mt6878-ccu mtk-smi mtk_iommu mmqos-mt6878 mtk-mmdvfs-v3 mtk-mbox mtk_tinysys_ipi"
export KO=$G/lieppos/camera-isp/kout
export MC=$G/vendor/mediatek/kernel_modules/mtkcam
export DM=$G/kernel_device_modules-6.1
export SYS="$ST/partitions/system_dlkm"
