#!/usr/bin/env python3
"""Generate connectivity kernel/module-inventory.tsv, kernel/source-map.tsv and aggregated parity TSVs."""
import csv, hashlib, os, re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "binary-analysis/per-module"
ST = Path(os.environ['ST']); VD = ST/'partitions/vendor_dlkm/lib/modules'; SYS = ST/'partitions/system_dlkm/lib/modules'
NKM = "NothingOSS android_kernel_modules_nothing_mt6878"
KDM = "NothingOSS android_kernel_device_modules_6.1_nothing_mt6878"
CMN = "GKI android14-6.1 common (vendor in-tree build, scm g945dff7bc1bf)"
# name, subsystem, role, board_state, stock_dir, source path, donor tree, donor commit, rebuild notes
M = [
("conninfra","conninfra","CONNINFRA/connv2 core: power/reset, A-die SPI, EMI, pre-cal, coredump, connsyslog, thermal","ACTIVE",VD,"connectivity/conninfra/",NKM,"2115d27 (alps-mp-u0.mp1-V9.9)","TARGET_BUILD_VARIANT unset (CONNINFRA_DBG_SUPPORT=1, BUILD_MODE=0)"),
("connadp","conninfra","connectivity build-in adapter + connsys power throttling","ACTIVE",VD,"drivers/misc/mediatek/connectivity/",KDM,"6df320423600 (Galaga-V3.2 sync)","needs power_throttling @6df320423600 (6-level LOW_BATTERY enum)"),
("connscp","conninfra","CONAP <-> SCP bridge (GNSS/geofence offload over tinysys IPI)","CONFIGURED",VD,"drivers/misc/mediatek/conn_scp/",KDM,"6df320423600",""),
("clkbuf","power/clock","clock-buffer (XO_BUF) control used by conninfra","ACTIVE",VD,"drivers/misc/mediatek/clkbuf/",KDM,"6df320423600",""),
("mt6685-core","power/clock","MT6685 clock/RTC PMIC MFD (32k/26M co-clock source, mt6685-consys child)","ACTIVE",VD,"drivers/mfd/mt6685-core.c",KDM,"957dac1 (NothingOSS Tetris-U2.6 baseline)",""),
("uarthub_drv","transport","UART hub (connv3/external-combo transport; platform capability)","DORMANT",VD,"drivers/misc/mediatek/uarthub/",KDM,"957dac1 (= 6df320423600 tree)","loaded, no MT6878 consumer on this board"),
("connfem","connfem","ConnFem front-end-module selection (ePA/eLNA) for Wi-Fi/BT","ACTIVE",VD,"connectivity/connfem/",NKM,"2115d27",""),
("wmt_chrdev_wifi_connac2","wifi","/dev/wmtWifi power-on char device + wlan reset glue","ACTIVE",VD,"connectivity/wlan/adaptor/build/connac2x/",NKM,"2115d27",""),
("wlan_drv_gen4m_6878","wifi","gen4m Wi-Fi driver, CONNAC2X SOC7_0, AXI HIF, cfg80211","ACTIVE",VD,"connectivity/wlan/core/gen4m/ (Kbuild.6878)",NKM,"2115d27 + 13 hunks from c3d070e (alps-mp-u0.mp1.rc-V11.24)","MODULE_NAME=wlan_drv_gen4m_6878 SEGMENT=SP DRIVER_BUILD_DATE=20251022145214"),
("wifi_cooling","wifi","thermal cooling device for Wi-Fi TX duty","ACTIVE",VD,"drivers/thermal/mediatek/wifi_cooling.c",KDM,"6df320423600",""),
("mddp","wifi","modem direct data path (Wi-Fi tethering offload to MD)","ACTIVE",VD,"drivers/misc/mediatek/mddp/",KDM,"957dac1 (NothingOSS Tetris-U2.6 baseline)",""),
("cfg80211","wifi","Linux wireless configuration API (vendor-built GKI-tree module)","ACTIVE",VD,"common/net/wireless/",CMN,"g945dff7bc1bf","M= build + intree_relink.sh"),
("mac80211","wifi","Linux softMAC stack (loaded; gen4m is fullMAC and does not use it)","DORMANT",VD,"common/net/mac80211/",CMN,"g945dff7bc1bf","M= build + intree_relink.sh"),
("bt_drv_6878","bluetooth","MT6878 BTIF/BGF Bluetooth driver, /dev/stpbt","ACTIVE",VD,"connectivity/bt/mt66xx/6878 (btif/)",NKM,"2115d27","TARGET_BUILD_VARIANT unset (FW_LOG_DEFAULT_ON=1, BUILD_QA_DBG=1)"),
("bluetooth","bluetooth","Linux Bluetooth core (vendor_dlkm copy; system_dlkm GKI copy loads first)","ACTIVE",VD,"common/net/bluetooth/",CMN,"g945dff7bc1bf","M= build + intree_relink.sh"),
("mtk-btcvsd","bluetooth","BT SCO CVSD/mSBC ALSA PCM (audio side of BT voice)","CONFIGURED",VD,"sound/soc/mediatek/common/mtk-btcvsd.c",KDM,"e38092245fb4 (audio pass rebase)",""),
("fmradio_drv_connac2x","fm","FM receiver driver (CONNAC2X, A-die FM core), /dev/fm","ACTIVE",VD,"connectivity/fmradio/Build/connac2x",NKM,"2115d27",""),
("gps_drv_dl_v051","gnss","GNSS data-link driver v051 (/dev/gpsdl0/1, gps_emi)","ACTIVE",VD,"connectivity/gps/data_link/plat/v051",NKM,"2115d27",""),
("gps_pwr","gnss","GNSS power/battery-level notify (/dev/gps_pwr)","ACTIVE",VD,"connectivity/gps/gps_pwr",NKM,"2115d27","insmod by init.gps_pwr.rc"),
("gps_scp","gnss","GNSS <-> SCP char device (/dev/gps2scp)","ACTIVE",VD,"connectivity/gps/gps_scp",NKM,"2115d27","insmod by init.gps_scp.rc"),
("mtk_low_battery_throttling","power-dependency","low-battery throttling (connadp/wlan dependency)","ACTIVE",None,"drivers/misc/mediatek/power_throttling/",KDM,"6df320423600","dependency closure"),
("pmic_lbat_service","power-dependency","PMIC LBAT service (wlan import)","ACTIVE",None,"drivers/misc/mediatek/power_throttling/",KDM,"6df320423600","dependency closure"),
]
DEP_ONLY = {"mtk_bp_thl","mtk_battery_oc_throttling","mtk_dynamic_loading_throttling","mtk_md_power_throttling","mtk_cpu_power_throttling","mtk_gpu_power_throttling","pmic_lvsys_notify"}

def run(*a): return subprocess.run(a,capture_output=True,text=True).stdout
VR = ST/'vendor-ramdisks/platform-extracted/lib/modules'
def find(name, d):
    # same lookup order as parity_conn.sh: vendor ramdisk first, then vendor_dlkm
    for base in (VR, VD):
        p = base/(name+'.ko')
        if p.exists(): return p
def counts(path):
    rows=list(csv.DictReader(path.open(),delimiter='\t'))
    return sum(r['class']=='EXACT' for r in rows), sum(r['class']=='EXACT-CODE' for r in rows), len(rows)
def abi(name):
    rows=list(csv.DictReader((P/f'{name}.abi-parity.tsv').open(),delimiter='\t'))
    return 'EXACT' if all(r['result'].startswith('EXACT') for r in rows) else 'DIFF', {r['check']:f"{r['match']}/{r['total']}" for r in rows}
def secsizes(f):
    out={}
    for l in run('readelf','-SW',str(f)).splitlines():
        m=re.match(r'\s*\[\s*\d+\]\s+(\S+)\s+\S+\s+[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+)',l)
        if m and m.group(1) in ('.text','.data','.rodata','.bss','.init.text','.exit.text'): out[m.group(1)]=int(m.group(2),16)
    return ','.join(f"{k}={v}" for k,v in out.items())
hdr=['module','subsystem','role','board_state','stock_path','sha256','size','vermagic','depends','imports','exports','modversions','kcfi_typeids','functions_exact','functions_total','data_exact','data_total','abi','section_sizes','build_id','source_tree','source_path','source_commit','build_notes','status']
rows=[]
for name,sub,role,state,d,src,tree,commit,notes in M:
    f=find(name,d); b=f.read_bytes()
    mi=lambda k: run('modinfo','-F',k,str(f)).strip().replace('\n',',')
    syms=run('nm',str(f))
    kcfi=sum(1 for l in syms.splitlines() if '__kcfi_typeid_' in l)
    bid=re.search(r'Build ID:\s*([0-9a-f]+)',run('readelf','-n',str(f)))
    fe,fc,ft=counts(P/f'{name}.function-parity.tsv'); de,dc,dt=counts(P/f'{name}.data-parity.tsv')
    a,ad=abi(name)
    rows.append([name,sub,role,state,str(f.relative_to(ST)),hashlib.sha256(b).hexdigest(),len(b),mi('vermagic'),mi('depends'),
        ad.get('imports',''),ad.get('exports',''),ad.get('modversions',''),kcfi,fe,ft,de,dt,a,secsizes(f),bid.group(1) if bid else '-',
        tree,src,commit,notes,'DONE' if (fe==ft and de==dt and a=='EXACT') else 'PARTIAL'])
(ROOT/'kernel').mkdir(exist_ok=True)
with (ROOT/'kernel/module-inventory.tsv').open('w') as o:
    o.write('\t'.join(hdr)+'\n'); [o.write('\t'.join(map(str,r))+'\n') for r in rows]
with (ROOT/'kernel/source-map.tsv').open('w') as o:
    o.write('module\tsource_tree\tsource_path\tsource_commit\tresearch_build_tree\n')
    for name,sub,role,state,d,src,tree,commit,notes in M:
        bt = '$G/vendor/mediatek/kernel_modules/connectivity (git, see reconstruction/)' if tree==NKM else ('$G/kernel_device_modules-6.1 (git)' if tree==KDM else '$G/common')
        o.write(f'{name}\t{tree}\t{src}\t{commit}\t{bt}\n')
# aggregated parity tables
allm=[r[0] for r in M]+sorted(DEP_ONLY)
for kind in ('function','data','abi'):
    with (ROOT/f'binary-analysis/{kind}-parity.tsv').open('w') as o:
        first=True
        for m in allm:
            p=P/f'{m}.{kind}-parity.tsv'
            if not p.exists(): continue
            lines=p.read_text().splitlines()
            if first: o.write('module\t'+lines[0]+'\n'); first=False
            for l in lines[1:]: o.write(f'{m}\t{l}\n')
print('\n'.join(f"{r[0]}\t{r[13]}/{r[14]}\t{r[15]}/{r[16]}\t{r[17]}\t{r[24]}" for r in rows))
