#!/usr/bin/env python3
"""Approximate subsystem buckets over resolved-load-order.tsv (load-order-summary.md)."""
import re, sys
from collections import defaultdict
rows = [l.rstrip('\n').split('\t') for l in open(sys.argv[1] if len(sys.argv) > 1 else 'resolved-load-order.tsv')][1:]
cats = [('debug/aee/boot-profiling', r'^(bootprof|mrdump|aee_|monitor_hang|dbgtop|irq_dbg|cache_parity|bus_parity|last_bus|log_store|mtk_printk|dbg_error|sec$|emi_mpu|smpu|device_apc)'),
 ('clock/power-domain/pinctrl/PMIC/regulator', r'^(clk_|clkbuf|mtk_scpsys|pd_chk|pinctrl|mt63|mt6315|mtk_spmi|spmi_|mtk_pmic|mtk_dvfsrc|mtk_icc|regulator|rt5133|rt6160|custom_ldo|mt6685|mtk_pm_domain|fhctl|mtk_dcm|mt6878_dcm|nvmem)'),
 ('storage (UFS/MMC/RPMB/blocktag)', r'^(ufs|phy_mtk_ufs|cqhci|mtk_mmc|rpmb|blocktag)'),
 ('display/GPU/MM', r'^(mediatek_drm|drm_|panel_|mtk_panel|mtk_disp|leds_mtk|pwm_mtk_disp|mtk_dpc|mtk_smi|mtk_iommu|iommu|mtk_mm|mmqos|cmdq|mtk_cmdq|mali|ged|gpueb|mtk_gpu|spi_tiny_co5300|rt4831|mtk_mml|mdp_drv|mtk_sync|mmprofile)'),
 ('input/touch/keys/fp', r'^(mtk_pmic_keys|yft_gpio_keys|yft_tpd|focaltech|hynitron|tui_common|microarray|fingerprint|touch_boost|mtk_ioctl_touch)'),
 ('power/charging/battery/TypeC', r'^(mt6375|sh366003|sc85|mtk_charger|mtk_pep|mtk_pd|charger_|adapter_class|tcpc|rt_pd|pd_dbg|pmic_lbat|mtk_battery|mtk_low_battery|mtk_dynamic_loading|mtk_bp_thl|mtk_pbm|mtk_mdpm|extdev_io|yft_devinfo|mtk_chg|mtk_peak|mtk_.*throttling|mtk_cg_peak)'),
 ('USB', r'^(mtu3|xhci|phy_mtk_xsphy|extcon_mtk_usb|usb_|mtk_usb|mtk_u_ether|c2k_usb|yft_tiny2c|usbnet|cdc_|r815|asix|ax88|aqc|rtl8150|usbserial|ftdi)'),
 ('camera/ISP/flash/codec', r'^(imgsensor|mtk_cam|camera_|main\d?_vcm|sub_vcm|dw9781c|aw3651|mtk_imgsys|mtk_hcp|mtk_ccu|mtk_aie|mtk_ipesys|mtk_jpeg|flashlight|mtk_vmm|mtk_ccd|mtk_vcodec|mtk_vcu)'),
 ('audio', r'^(snd_|mtk_afe|audio_ipi|adsp|mtk_scp_|mtk_vow|aw883|mt6369_accdet|mtk_sp_spk|mtk_btcvsd)'),
 ('connectivity', r'^(conn|wlan|bt_drv|bluetooth|btbcm|btqca|btsdio|hci_uart|hidp|rfcomm|gps|fmradio|wmt_|cfg80211|mac80211|st21nfc|nfc|uarthub)'),
 ('modem/CCCI', r'^(ccci|ccmni|mddp|md_cooling|mtk_md_power|wwan)'),
 ('sensors/SCP', r'^(scp|sensorhub|hf_manager|mtk_mbox|mtk_rpmsg|mtk_tinysys|tinysys|mcupm|sspm|vcp)'),
 ('TEE/security', r'^(gz_|tkcore|tmem|teeperf|widevine|sec_rng|mtk_sec_heap|tipc|ffa)')]
agg = defaultdict(list)
for r in rows:
    for n, p in cats:
        if re.search(p, r[1]): agg[n].append((int(r[0]), r[2])); break
    else: agg['other'].append((int(r[0]), r[2]))
for n, _ in cats + [('other', '')]:
    v = agg[n]; ph = defaultdict(int)
    for s, p in v: ph[p] += 1
    print(f'| {n} | {len(v)} | {min(s for s,_ in v)}-{max(s for s,_ in v)} | ' + ', '.join(f'{k} {c}' for k, c in ph.items()) + ' |')
