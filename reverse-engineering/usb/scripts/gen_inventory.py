#!/usr/bin/env python3
"""gen_inventory.py OUT.tsv : GQ5012BF1 USB-related kernel module inventory (stock .ko + parity dirs).
Static and read-only. It reads the stock modules and the parity output that sb.sh/build-all.sh wrote to $W/par."""
import subprocess, hashlib, os, re, sys

W = '/home/armol/kernel-work/gki-12901745-workspace/lieppos/usb'
STOCK = '/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/workspace/gq5012bf1/stock'
LLVM = '/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin/'
VR = 'vendor-ramdisks/platform-extracted/lib/modules'
VD = 'partitions/vendor_dlkm/lib/modules'
SD = 'partitions/system_dlkm/lib/modules'
B = 'MTK ALPS 5e415e059253 (unmodified)'
REL = {  # module -> (class, dir, source candidate, revision, runtime role, parity dir | None, scope)
    'mtu3': ('MEDIATEK VENDOR', VR, 'KDM drivers/usb/mtu3/{plat,trace,host,core,gadget_ep0,gadget,qmu,dr,debugfs}.c (DUAL_ROLE)', B,
             'ACTIVE: 11201000.usb0 dual-role controller (UDC + usb_role_switch provider; populates/depopulates xhci0 child)', 'mtu3-B2', 'USB-CONTROLLER-KERNEL'),
    'xhci-mtk-hcd-v2': ('MEDIATEK VENDOR', VR, 'KDM drivers/misc/mediatek/usb/usb_xhci/{xhci,xhci-mem,-ext-caps,-ring,-hub,-dbg,-trace,-mtk,-mtk-sch,quirks,-debugfs}.c', B,
                        'ACTIVE in host role: 11200000.xhci0 (single USB2 root hub; bound only while host)', 'xhci-mtk-hcd-v2-B2', 'USB-CONTROLLER-KERNEL'),
    'phy-mtk-xsphy': ('MEDIATEK VENDOR', VR, 'KDM drivers/phy/mediatek/phy-mtk-xsphy.c', B,
                      'ACTIVE: 11f40000.usb-phy0 USB2 port (U2 only; U3 code paths dormant: no U3 child)', 'phy-mtk-xsphy-B2', 'USB-PHY'),
    'extcon-mtk-usb': ('MEDIATEK VENDOR (GQ5012BF1-modified)', VR, 'KDM drivers/misc/mediatek/extcon/extcon-mtk-usb.c + YFT OTG/UVC patch', 'MTK ALPS 5e415e059253 + reconstructed YFT patch 0002',
                       'ACTIVE: /extcon-usb: TCPC->usb_role_switch bridge, OTG VBUS regulator, GPIO 28/37/55/152, tiny2c_mode/uvc_insert_status', 'extcon-mtk-usb-B2', 'EXTCON-MTK-USB'),
    'rt_pd_manager': ('MEDIATEK VENDOR (TCPC 2.0.31 + GQ5012BF1)', VR, 'KDM drivers/misc/mediatek/typec/tcpc/rt_pd_manager.c (+2.0.31 inc/ headers)', 'MTK ALPS 5e415e059253 + reconstructed patch 0001 (srcversion residual)',
                      'ACTIVE: /rt-pd-manager: Type-C class port (typec_port0), partner/altmode registration, mux/orientation forwarding', 'rt_pd_manager-B2', 'USB-TYPEC-ROLE-KERNEL'),
    'tcpci_late_sync': ('MEDIATEK VENDOR', VR, 'KDM drivers/misc/mediatek/typec/tcpc/tcpci_late_sync.c', B,
                        'ACTIVE: late_initcall tcpc_schedule_init_work for registered TCPCs', 'tcpci_late_sync-B2', 'USB-TYPEC-ROLE-KERNEL'),
    'mux_switch': ('MEDIATEK VENDOR', VR, 'KDM drivers/misc/mediatek/typec/mux/mux_switch.c', B,
                   'LOADED, PASS-THROUGH: /soc/typec-mux-switch (DTBO-added) registers typec_switch/typec_mux; no mux IC driver registers below it', 'mux_switch-B2', 'USB-TYPEC-ROLE-KERNEL'),
    'usb_meta': ('MEDIATEK VENDOR', VR, 'KDM drivers/misc/mediatek/usb/usb_meta/usb_meta.c', B,
                 'ACTIVE: /usb-meta (udc=usb0): legacy android_usb class (iSerial) for MTK META/factory mode', 'usb_meta-B2', 'USB-GADGET-KERNEL'),
    'usb_boost': ('MEDIATEK VENDOR', VR, 'KDM drivers/misc/mediatek/usb/usb_boost/{usb_boost_common,usb_boost_plat}.c', B,
                  'ACTIVE: /usb-boost-manager: CPU/vcore DVFS boost on USB traffic (vcore 725 mV, small-core 1.25 GHz, usb-audio)', 'usb_boost-B2', 'USB-CONTROLLER-KERNEL'),
    'usb_logger': ('MEDIATEK VENDOR', VR, 'KDM drivers/misc/mediatek/usb/usb_logger/{u_logger,u_logger_trace}.c', B,
                   'ACTIVE: /usb-logger: MTU3/xHCI trace hooks', 'usb_logger-B2', 'USB-CONTROLLER-KERNEL'),
    'mtk_u_ether': ('MEDIATEK VENDOR', VD, 'KDM drivers/misc/mediatek/usb/usb_rndis/u_ether.c', B,
                    'CONFIGURED: RNDIS ethernet core (sys.usb.config=rndis[,adb]); GKI CONFIG_USB_CONFIGFS_RNDIS is off', 'mtk_u_ether-B2', 'USB-GADGET-KERNEL'),
    'mtk_usb_f_rndis': ('MEDIATEK VENDOR', VD, 'KDM drivers/misc/mediatek/usb/usb_rndis/{f_rndis,rndis}.c', B,
                        'CONFIGURED: configfs function mtk_rndis.gs4 (USB tethering)', 'mtk_usb_f_rndis-B2', 'USB-GADGET-KERNEL'),
    'usb_offload': ('MEDIATEK VENDOR', VD, 'KDM drivers/misc/mediatek/usb/usb_offload/{usb_offload_common,usb_offload_mem}.c', B,
                    'ACTIVE in host role with USB audio: /soc/usb-offload (xhci-host=xhci0, sram v3, ADSP low-power)', 'usb_offload-B2', 'USB-CONTROLLER-KERNEL'),
    # closed elsewhere (not rebuilt here)
    'tcpc_class': ('MEDIATEK VENDOR (closed elsewhere)', VR, 'TCPC 2.0.31_MTK core', 'see DONE/TCPC-CLASS', 'ACTIVE: TCPC/PD core, type_c_port0', None, 'TCPC-CLASS'),
    'tcpc_mt6375': ('MEDIATEK VENDOR (closed elsewhere)', VR, 'tcpc_mt6375.c', 'see DONE/TCPC-MT6375', 'ACTIVE: MT6375 TCPC (CC, VBUS, VCONN, WD)', None, 'TCPC-MT6375'),
    'pd_dbg_info': ('MEDIATEK VENDOR (closed elsewhere)', VR, 'pd_dbg_info.c', 'see DONE/PD-DBG-INFO', 'ACTIVE: PD debug buffer', None, 'PD-DBG-INFO'),
    'mt6375-charger': ('MEDIATEK VENDOR (closed elsewhere)', VR, 'mt6375-charger.c', 'see power-charging research', 'ACTIVE: usb-otg-vbus regulator, BC1.2 via usb2-phy, yft_usb_flag export', None, 'power-charging'),
    'mtk_chg_type_det': ('MEDIATEK VENDOR (closed elsewhere)', VR, 'mtk_chg_type_det.c', 'see power-charging research', 'ACTIVE: charger-type detection consumer of TCPC', None, 'power-charging'),
    'yft_tiny2c_usb': ('BOARD-SPECIFIC (closed elsewhere)', VD, 'yft_tiny2c_usb.c', 'see DONE/YFT-TINY2C-USB', 'ACTIVE: thermal-camera rails GPIO 192/191/149', None, 'YFT-TINY2C-USB'),
    'c2k_usb': ('MEDIATEK VENDOR (closed elsewhere)', VD, 'c2k_usb rawbulk', 'see modem research (DONE)', 'CONFIGURED: via_* gadget functions (sys.usb.config=via_bypass)', None, 'modem'),
}
GKI = ['usbnet', 'usbserial', 'cdc-acm', 'cdc_ether', 'cdc_eem', 'cdc_ncm', 'r8152', 'r8153_ecm', 'rtl8150', 'asix', 'ax88179_178a', 'aqc111', 'ftdi_sio']


def run(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout


def kv(summary, key):
    for l in summary.splitlines():
        if l.startswith(key):
            return l.split(':', 1)[1].strip()
    return ''


g = lambda pat, s: (re.search(pat, s).group(1) if re.search(pat, s) else '')
cols = ['filename', 'class', 'path', 'sha256', 'size', 'vermagic', 'depends', 'imports(__versions)', 'exports', 'modversions(import CRC)',
        'KCFI', 'functions', 'data', 'sections', 'relocations', 'build-ID', 'source candidate', 'source revision', 'runtime role',
        'parity A vs B', 'workspace scope']
out = ['\t'.join(cols)]
rows = list(REL.items()) + [(m, ('GENERIC GKI', SD, 'ACK 6b18f0b574ab', 'GKI 12901745 signed system_dlkm module', 'host-mode class driver (USB serial/net/ACM)', None, 'GKI-KMI-BASELINE')) for m in GKI]
for m, (cls, rel, src, rev, role, pd, scope) in rows:
    p = f'{STOCK}/{rel}/{m}.ko'
    raw = open(p, 'rb').read()
    mi = run(LLVM + 'llvm-readelf', '-p', '.modinfo', p)
    vm = re.search(r'vermagic=([^\n]*)', mi); dep = re.search(r'depends=([^\n]*)', mi)
    bid = re.search(r'Build ID: ([0-9a-f]+)', run(LLVM + 'llvm-readelf', '-n', p))
    nsec = len(re.findall(r'^\s*\[\s*\d+\]', run(LLVM + 'llvm-readelf', '-SW', p), re.M)) - 1
    if pd:
        S = open(f'{W}/par/{pd}/SUMMARY.txt').read()
        fn, da, im, ex, rl = (kv(S, k) for k in ('functions', 'data objects', 'imports', 'exports', 'relocation entries'))
        sec = open(f'{W}/par/{pd}.secdiff').read().strip()
        b12 = open(f'{W}/par/{pd.replace("-B2", "-B1")}.ko', 'rb').read() == open(f'{W}/par/{pd}.ko', 'rb').read()
        if "differing: ['.note.gnu.build-id']" in sec:
            par = 'EXACT (all sections equal except .note.gnu.build-id' + ('; B1==B2)' if b12 else ')')
        elif "differing: ['.modinfo', '.note.gnu.build-id']" in sec:
            par = 'EXACT CODE/DATA; .modinfo differs only in srcversion (source-text MD4), build-id' + ('; B1==B2' if b12 else '')
        else:
            par = 'PARTIAL: ' + sec
        cells = [g(r'A=(\d+)', im), g(r'A=(\d+)', ex), g(r'name\+CRC-equal=(\d+)', im) + '/' + g(r'A=(\d+)', im),
                 g(r'kcfi-equal=(\d+)', fn) + '/' + g(r'A=(\d+)', fn), g(r'byte-identical=(\d+)', fn) + '/' + g(r'A=(\d+)', fn),
                 g(r'bytes-equal=(\d+)', da) + '/' + g(r'A=(\d+)', da), str(nsec),
                 (g(r'A=(\d+)', rl) + ' A / ' + g(r'B=(\d+)', rl) + ' B') if rl else '']
    else:
        nimp = len(re.findall(r' U ', run(LLVM + 'llvm-nm', p)))
        nf = len(re.findall(r' [tT] ', run(LLVM + 'llvm-nm', p)))
        cells = [str(nimp), '', '', '', f'{nf} (text syms)', '', str(nsec), '']
        par = 'n/a here (closed in ' + scope + ')' if cls.endswith('elsewhere)') else 'n/a (generic GKI module, not rebuilt)'
    out.append('\t'.join([m + '.ko', cls, rel + '/' + m + '.ko', hashlib.sha256(raw).hexdigest(), str(len(raw)),
                          vm.group(1) if vm else '', dep.group(1) if dep else ''] + cells +
                         [bid.group(1) if bid else '', src, rev, role, par, scope]))
open(sys.argv[1], 'w').write('\n'.join(out) + '\n')
print('\n'.join(l.split('\t')[0] + '  ' + l.split('\t')[-2] for l in out))
