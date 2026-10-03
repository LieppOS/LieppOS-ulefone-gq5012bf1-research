#!/bin/bash
# rebuild_all.sh -- reproduce every connectivity module and run parity (stock vs rebuilt)
. /tmp/connenv.sh
set -e
# 1. KDM-hosted modules (kernel_device_modules-6.1 @ research commits, see source-map.tsv)
"$CR/scripts/build_kdm.sh" "drivers/misc/mediatek/connectivity/ drivers/misc/mediatek/conn_scp/ drivers/thermal/mediatek/ drivers/misc/mediatek/clkbuf/ drivers/misc/mediatek/uarthub/ drivers/misc/mediatek/mddp/ drivers/mfd/ drivers/misc/mediatek/power_throttling/ sound/soc/mediatek/" -k > /tmp/rb_kdm.log 2>&1 || true
# 2. vendor/mediatek/kernel_modules/connectivity (out-of-tree, TARGET_BUILD_VARIANT unset as in stock)
B(){ "$CR/scripts/build_ext.sh" "$@"; }
B conninfra > /tmp/rb_conninfra.log 2>&1
B connfem > /tmp/rb_connfem.log 2>&1
B wlan/adaptor/build/connac2x > /tmp/rb_wmt.log 2>&1
B wlan/core/gen4m MODULE_NAME=wlan_drv_gen4m_6878 SEGMENT=SP DRIVER_BUILD_DATE=20251022145214 > /tmp/rb_wlan.log 2>&1
B bt/mt66xx/6878 > /tmp/rb_bt.log 2>&1
B fmradio/Build/connac2x > /tmp/rb_fm.log 2>&1
B gps/data_link/plat/v051 > /tmp/rb_gpsdl.log 2>&1
B gps/gps_pwr > /tmp/rb_gpspwr.log 2>&1
B gps/gps_scp > /tmp/rb_gpsscp.log 2>&1
# 3. GKI-tree vendor modules (in-tree semantics restored by intree_relink.sh)
cd $G/common
for d in net/wireless net/mac80211 net/bluetooth; do
  mkdir -p $KOA/$d; ln -sf $G/common/$d/trace.h $KOA/$d/trace.h 2>/dev/null || true
done
ln -sf $G/common/net/wireless/reg.h $KOA/net/wireless/reg.h
for d in net/wireless net/mac80211 net/bluetooth; do
  make O=$KOA M=$d ARCH=arm64 LLVM=1 LLVM_IAS=1 KBUILD_MODPOST_WARN=1 module_scmversion= \
    KBUILD_EXTRA_SYMBOLS=$G/lieppos/camera-isp/stock-ext.symvers -j16 modules > /tmp/rb_$(basename $d).log 2>&1
done
"$CR/scripts/intree_relink.sh" net/wireless cfg80211
"$CR/scripts/intree_relink.sh" net/mac80211 mac80211
"$CR/scripts/intree_relink.sh" net/bluetooth bluetooth
set +e
KD=$G/lieppos/connectivity/kernel_device_modules-6.1
for m in connadp connscp wifi_cooling clkbuf uarthub_drv mddp mt6685-core mtk-btcvsd \
         mtk_low_battery_throttling pmic_lbat_service mtk_bp_thl mtk_battery_oc_throttling mtk_dynamic_loading_throttling \
         mtk_md_power_throttling mtk_cpu_power_throttling mtk_gpu_power_throttling pmic_lvsys_notify; do
  REBUILT=$(find $KD -name $m.ko | head -1) "$CR/scripts/parity_conn.sh" $m
done
for m in conninfra connfem wmt_chrdev_wifi_connac2 wlan_drv_gen4m_6878 bt_drv_6878 fmradio_drv_connac2x gps_drv_dl_v051 gps_pwr gps_scp; do
  REBUILT=$(find $CO -name $m.ko | head -1) "$CR/scripts/parity_conn.sh" $m
done
REBUILT=$KOA/net/wireless/cfg80211.ko "$CR/scripts/parity_conn.sh" cfg80211
REBUILT=$KOA/net/mac80211/mac80211.ko "$CR/scripts/parity_conn.sh" mac80211
REBUILT=$KOA/net/bluetooth/bluetooth.ko "$CR/scripts/parity_conn.sh" bluetooth
