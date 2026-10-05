#!/bin/bash
# build-all.sh TREE TAG : rebuild every GQ5012BF1 USB vendor module from TREE, parity into par/<mod>-TAG
cd /home/armol/kernel-work/gki-12901745-workspace/lieppos/usb
T=$1; TAG=$2; ONLY=$3
while read m s o; do
  [ -z "$m" ] && continue
  [ -n "$ONLY" ] && ! echo " $ONLY " | grep -q " $m " && continue
  case $m in xhci-mtk-hcd-v2|usb_logger) X="-I$PWD/$T/$s";;
    rt_pd_manager|tcpci_late_sync) X="-DCONFIG_MTK_TYPEC_WATER_DETECT=1";; *) X="";; esac
  r=$(XCCFLAGS="$X" MPW=${MPW_ALL:-} ./sb.sh $T $m $s "$o" $TAG 2>&1 | grep -E '^functions|^sections|error' | head -2 | sed -E 's/byte-identical-or.*//; s/functions: //' | tr '\n' ' ')
  echo "$m: $r"
done <<'EOL'
mtu3 drivers/usb/mtu3 mtu3_plat.o mtu3_trace.o mtu3_host.o mtu3_core.o mtu3_gadget_ep0.o mtu3_gadget.o mtu3_qmu.o mtu3_dr.o mtu3_debugfs.o
xhci-mtk-hcd-v2 drivers/misc/mediatek/usb/usb_xhci xhci.o xhci-mem.o xhci-ext-caps.o xhci-ring.o xhci-hub.o xhci-dbg.o xhci-trace.o xhci-mtk.o xhci-mtk-sch.o quirks.o xhci-debugfs.o
phy-mtk-xsphy drivers/phy/mediatek phy-mtk-xsphy.o
extcon-mtk-usb drivers/misc/mediatek/extcon extcon-mtk-usb.o
usb_meta drivers/misc/mediatek/usb/usb_meta usb_meta.o
usb_boost drivers/misc/mediatek/usb/usb_boost usb_boost_common.o usb_boost_plat.o
usb_logger drivers/misc/mediatek/usb/usb_logger u_logger.o u_logger_trace.o
mux_switch drivers/misc/mediatek/typec/mux mux_switch.o
rt_pd_manager drivers/misc/mediatek/typec/tcpc rt_pd_manager.o
tcpci_late_sync drivers/misc/mediatek/typec/tcpc tcpci_late_sync.o
mtk_u_ether drivers/misc/mediatek/usb/usb_rndis u_ether.o
mtk_usb_f_rndis drivers/misc/mediatek/usb/usb_rndis f_rndis.o rndis.o
usb_offload drivers/misc/mediatek/usb/usb_offload usb_offload_common.o usb_offload_mem.o
EOL
