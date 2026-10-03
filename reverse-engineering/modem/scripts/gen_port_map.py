#!/usr/bin/env python3
"""kernel/ccci-port-map.tsv = decoded stock port table (dump_ports.py) + node/SELinux/consumer evidence.
Consumers come from vendor_file_contexts + vendor_sepolicy.cil allow rules + binary string references
(userspace/dependency-map.tsv). 'kernel' consumers come from in-kernel callers (mtk_ccci_request_port etc.)."""
import csv, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
raw = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT/'binary-analysis/md_ccci_ports.stock.tsv'
rows = list(csv.DictReader(raw.open(), delimiter='\t'))
HIF = {'0': 'CLDMA', '1': 'CCIF', '2': 'DPMAIF'}
# name -> (selinux type, consumer, purpose)
C = {
 'ccci_aud': ('ccci_aud_device', 'audio HAL (mtk_hal_audio): audio.primary.mediatek.so', 'speech control/PCM messages for modem voice (SpeechDriver)'),
 'ccci_raw_audio': ('ccci_aud_device', 'audio HAL (mtk_hal_audio)', 'speech shared-memory ring (SMEM_USER_RAW_AUDIO) for voice PCM/params'),
 'ccci_md_log_ctrl': ('ccci_mdl_device', 'mdlogger/emdlogger (system_ext)', 'modem logging control'),
 'ttyC0': ('gsm0710muxd_device', 'mtkfusionrild (legacy AT URC path), factory/meta', 'AT command channel (UART2)'),
 'ccci_fs': ('ccci_device', 'ccci_mdinit (ccci_fsd thread)', 'modem NVRAM file system service: /mnt/vendor/nvdata/md, md_cmn, protect_f/s/md'),
 'ttyC2': ('agps_device', 'mtk_agpsd', 'AGPS IPC-UART (control-plane LPP/RRLP to GNSS)'),
 'ttyC3': ('icusb_device', '- (no stock consumer found)', 'IC-USB SIM (legacy)'),
 'ttyC1': ('mdlog_device', 'mdlogger/emdlogger, mnld (log)', 'modem log stream (MD_LOG)'),
 'ccci_imsv': ('ccci_device', 'no specific stock opener found (allowed for rild/ccci_device domains; AP-side IMS daemons absent - IMS stack runs in MD)', 'IMS video (VT) control'),
 'ccci_imsc': ('ccci_device', 'no specific stock opener found (allowed for rild/ccci_device domains; AP-side IMS daemons absent - IMS stack runs in MD)', 'IMS control'),
 'ccci_imsa': ('ccci_device', 'no specific stock opener found (allowed for rild/ccci_device domains; AP-side IMS daemons absent - IMS stack runs in MD)', 'IMS audio control'),
 'ccci_imsdc': ('ccci_device', 'vtservice (libvt_avsync.so)', 'IMS data channel (ViLTE A/V sync)'),
 'ccci_imsem': ('ccci_device', 'no specific stock opener found (allowed for rild/ccci_device domains; AP-side IMS daemons absent - IMS stack runs in MD)', 'IMS event monitor'),
 'ccci_imsm': ('ccci_device', 'no specific stock opener found (allowed for rild/ccci_device domains; AP-side IMS daemons absent - IMS stack runs in MD)', 'IMS manager'),
 'ccci_ioctl0': ('ccci_device', 'ccci_mdinit', 'control ioctl node (MD state, reset, SIM type, etc.)'),
 'ccci_ioctl1': ('ccci_device', 'ccci_device clients via libccci_util (index chosen at runtime)', 'control ioctl node'),
 'ccci_ioctl2': ('ccci_device', 'ccci_device clients via libccci_util (index chosen at runtime)', 'control ioctl node'),
 'ccci_ioctl3': ('ccci_device', 'ccci_device clients via libccci_util (index chosen at runtime)', 'control ioctl node'),
 'ccci_ioctl4': ('ccci_device', 'ccci_device clients via libccci_util (index chosen at runtime)', 'control ioctl node'),
 'ccci_it': ('ccci_device', '- (test)', 'internal throughput test'),
 'ccci_lb_it': ('ccci_device', '- (test)', 'loopback test'),
 'ccci_mdl_monitor': ('ccci_mdmonitor_device', 'md_monitor', 'modem monitor (MDM) control'),
 'ccci_rpc': ('ccci_device', 'ccci_rpcd', 'modem RPC to AP (e.g. md1img/GPIO/ADC queries)'),
 'ccci_rpc_k': ('-', 'kernel (port_rpc.c)', 'in-kernel RPC handler (GPIO/ADC/EINT/DRAM info)'),
 'ccci_woa': ('ccci_device', 'no specific stock opener found (allowed for rild/ccci_device domains; AP-side IMS daemons absent - IMS stack runs in MD)', 'Wi-Fi offload agent (WO) for ePDG'),
 'ccci_c2k_ppp': ('ccci_device', '- (C2K PPP, no stock consumer)', 'CDMA2000 PPP data'),
 'ccci_c2k_agps': ('agps_device', 'mtk_agpsd', 'CDMA2000 AGPS'),
 'ccci_ss_xcap': ('ccci_device', 'no specific stock opener found (allowed for rild/ccci_device domains; AP-side IMS daemons absent - IMS stack runs in MD)', 'supplementary services over XCAP'),
 'ccci_bip': ('ccci_device', 'bip_ap', 'SIM Bearer Independent Protocol (STK BIP)'),
 'ttyC5': ('nwkopt_device', 'mtk_hal_nwk_opt domain (SELinux allow; binary not in stock vendor)', 'TCHE (traffic/QoS hints)'),
 'ttyC6': ('nlop_device', 'mtkfusionrild (libmtk-ril.so)', 'DISP (network-location / display hint) channel'),
 'ccci_udc': ('-', 'kernel (port_udc.c)', 'UDC (uplink data compression) control'),
 'ccci_wifi_proxy': ('ccci_wifi_proxy_device', 'rild (libwpfa.so, Wi-Fi packet filter agent)', 'MD<->AP Wi-Fi proxy (VoWiFi packet filtering/WPFA)'),
 'ccci_vts': ('ccci_vts_device', 'rild', 'video telephony stream'),
 'ccci_0_200': ('-', 'kernel: mddp.ko (MDDP_IPC_TTY_NAME)', 'MD direct control (MDDP/WFPM tethering offload IPC)'),
 'ccci_0_202': ('-', '- (time sync)', 'MD time channel'),
 'ccci_0_204': ('-', '-', 'GARB channel'),
 'ccci_ikeraw': ('ccci_device', 'no specific stock opener found (allowed for rild/ccci_device domains; AP-side IMS daemons absent - IMS stack runs in MD)', 'IKE raw packets for ePDG (VoWiFi)'),
 'ccci_epdg1': ('ccci_device', 'no specific stock opener found (allowed for rild/ccci_device domains; AP-side IMS daemons absent - IMS stack runs in MD)', 'ePDG tunnel 1'),
 'ccci_epdg2': ('ccci_device', 'no specific stock opener found (allowed for rild/ccci_device domains; AP-side IMS daemons absent - IMS stack runs in MD)', 'ePDG tunnel 2'),
 'ccci_epdg3': ('ccci_device', 'no specific stock opener found (allowed for rild/ccci_device domains; AP-side IMS daemons absent - IMS stack runs in MD)', 'ePDG tunnel 3'),
 'ccci_epdg4': ('ccci_device', 'no specific stock opener found (allowed for rild/ccci_device domains; AP-side IMS daemons absent - IMS stack runs in MD)', 'ePDG tunnel 4'),
 'ttyCMIPC0': ('gsm0710muxd_device', 'vendor.mediatek.hardware.nvram-service (libmipc.so)', 'MIPC: NVRAM/OSLK service'),
 'ttyCMIPC1': ('gsm0710muxd_device', 'mtkfusionrild (libmipc.so)', 'MIPC: main RIL control channel'),
 'ttyCMIPC2': ('gsm0710muxd_device', 'atcid', 'MIPC: AT command interface daemon'),
 'ttyCMIPC3': ('-', '- (no stock consumer)', 'MIPC spare'),
 'ttyCMIPC4': ('-', '- (no stock consumer)', 'MIPC spare'),
 'ttyCMIPC5': ('gsm0710muxd_device', 'mnld (GNSS)', 'MIPC: GNSS assistance / location'),
 'ttyCMIPC6': ('-', '- (no stock consumer)', 'MIPC spare'),
 'ttyCMIPC7': ('-', '- (no stock consumer)', 'MIPC spare'),
 'ttyCMIPC8': ('-', '- (no stock consumer)', 'MIPC spare'),
 'ttyCMIPC9': ('gsm0710muxd_device', 'thermal_core', 'MIPC: modem thermal/TX-power control'),
 'ccci_ipc_1220_0': ('ccci_device', 'mtk_agpsd', 'IPC task AP_IPC_AGPS (0)'),
 'ccci_ipc_2': ('ccci_device', 'GNSS (mnld)', 'IPC task AP_IPC_GPS (2)'),
 'ccci_ipc_3': ('-', 'kernel (CONFIG_MTK_CONN_MD unset: inactive)', 'IPC task AP_IPC_WMT (3), conn_md bridge not built'),
 'ccci_ipc_4': ('ccci_device', 'MISCTA clients', 'IPC task AP_IPC_MISCTA (4)'),
 'ccci_ipc_5': ('ccci_device', 'ccci_mdinit', 'IPC task AP_IPC_CCCIIPC (5): time/clib requests'),
 'ccci_ipc_6': ('-', '-', 'IPC task AP_IPC_GF (6), no char node'),
 'ccci_ipc_7': ('-', '-', 'IPC task AP_IPC_PKTTRC (7), no char node'),
 'ccci_ipc_8': ('-', '-', 'IPC task AP_IPC_USB (8), no char node'),
 'ccci_ipc_9': ('ccci_device', 'LWA proxy', 'IPC task AP_IPC_LWAPROXY (9)'),
 'ccci_sys': ('-', 'kernel (port_sysmsg.c)', 'system messages (MD->AP: SIM type, RF temp, TX power, etc.)'),
 'ccci_ctrl': ('-', 'kernel (port_ctlmsg.c)', 'control messages (handshake, exception)'),
 'ccci_poll': ('-', 'kernel (port_poller.c)', 'MD status poller'),
 'ccci_raw_dbm': ('-', 'kernel', 'SMEM RAW_DBM (low-power debug mem)'),
 'ccci_ccb_ctrl': ('ccci_ccb_device', 'ccci_mdinit / emdlogger / md_monitor', 'CCB (circular buffer in cache smem) control'),
 'ccci_ccb_dhl': ('ccci_mdl_device', 'mdlogger/emdlogger', 'CCB DHL (modem trace) buffer'),
 'ccci_raw_dhl': ('ccci_mdl_device', 'mdlogger/emdlogger', 'raw DHL smem'),
 'ccci_raw_netd': ('ccci_device', 'netd agent / mddp (SMEM_USER_RAW_NETD)', 'data usage counters smem'),
 'ccci_raw_usb': ('ccci_device', 'mddp (SMEM_USER_RAW_USB)', 'MDDP IPC buffer smem'),
 'ccci_raw_lwa': ('-', '-', 'LWA smem (no node)'),
 'ccci_raw_mdm': ('ccci_mdmonitor_device', 'md_monitor', 'modem monitor smem'),
 'ccci_ccb_md_monitor': ('ccci_mdmonitor_device', 'md_monitor', 'CCB modem monitor buffer'),
 'ccci_ccb_meta': ('ccci_device', 'meta_tst (factory META)', 'CCB META buffer'),
 'ccci_md_post_dump': ('ccci_device', 'ccci_mdinit / md_monitor / libmtk-ril (post-EE dump)', 'SMEM_USER_MD_POST_DUMP (id 46)'),
}
out = ROOT/'kernel/ccci-port-map.tsv'
with open(out, 'w') as o:
    o.write('idx\tname\tdevice\ttx_ch\trx_ch\tchannel_names\thif\ttxq\trxq\ttxq_exp\trxq_exp\tflags\tops\tminor\tselinux_type\tconsumer\tpurpose\n')
    for r in rows:
        n = r['name']; ops = r['ops']; fl = r['flags']
        if ops == 'net_port_ops': dev = f'netdev {n}'; se, cons, pur = '-', 'netd/ConnectivityService via RIL data call (IRadioData setupDataCall)', 'CCMNI pure-IP data interface'
        else:
            dev = f'/dev/{n}' if 'WITH_CHAR_NODE' in fl else '(kernel only)'
            se, cons, pur = C.get(n, ('?', '?', '?'))
        o.write('\t'.join([r['idx'], n, dev, r['tx_ch'], r['rx_ch'], f"{r['tx_ch_name']}/{r['rx_ch_name']}", HIF.get(r['hif'], r['hif']),
                r['txq'], r['rxq'], r['txq_exp'], r['rxq_exp'], fl, ops, r['minor'], se, cons, pur]) + '\n')
print(out)
