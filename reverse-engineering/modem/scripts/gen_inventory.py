#!/usr/bin/env python3
"""Generate modem kernel/module-inventory.tsv, kernel/source-map.tsv and aggregated parity TSVs."""
import csv, hashlib, os, re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "binary-analysis/per-module"
ST = Path(os.environ['ST']); VD = ST/'partitions/vendor_dlkm/lib/modules'; VR = ST/'vendor-ramdisks/platform-extracted/lib/modules'
KDM = "NothingOSS android_kernel_device_modules_6.1_nothing_mt6878"
C = "fae67a9257dc (MTK [ALPS09525334], 2024-12-11; = 6df320423600 without the Nothing MODEM_DUMP_FLAG hunk)"
CB = "957dac1 (NothingOSS Tetris-U baseline; tree identical at 6df320423600)"
M = [
("ccci_util_lib","CCCI","CCCI utility library: LK tag/boot-arg parsing, MD image check-header, reserved/shared-memory layout, md_sta broadcast, pin_sta, /sys/kernel/ccci, /proc/ccci_dump|ccci_log|ccci_sib","ACTIVE","drivers/misc/mediatek/ccci_util/",C,"+ include/mt-plat/mtk_ccci_common.h 415e7e6c (fae67a9257dc; SMEM_USER_MD_POST_DUMP=46)"),
("ccci_md_all","CCCI","CCCI core: modem_sys1 (MD1, gen 6299), FSM (boot handshake/EE/monitor/poller), port layer (95-entry port table: char/tty/ipc/rpc/net/smem/sys/ctl/udc), skb pool, UDC, mdee_dumper_v6","ACTIVE","drivers/misc/mediatek/eccci/ (ccci_md_all-y)",C,"tree id ca75801a = fae67a9257dc:eccci"),
("ccci_auxadc","CCCI","MD AUXADC channel bridge (ccci_get_adc_*) for md_auxadc DT node","ACTIVE","drivers/misc/mediatek/eccci/ccci_auxadc.c",C,""),
("ccci_ccif","CCCI-HIF","CCIF HIF: AP<->MD control/command channels (all non-network ports), ring-buffer SRAM, 2 IRQs","ACTIVE","drivers/misc/mediatek/eccci/hif/ (ccci_ringbuf, ccci_hif_ccif)",C,""),
("ccci_dpmaif","DPMAIF","DPMAIF v3 HIF: network data path for ccmni (4 TXQ x 2048 DRB, 1 RXQ, BAT 16384, LRO off by DT cap=4), resv-mem, net speed/DVFS, page pool","ACTIVE","drivers/misc/mediatek/eccci/hif/ (ccci_dpmaif-y)",C,""),
("ccci_fsm_scp","CCCI","CCCI <-> SCP bridge (ccci_md_scp node, CCIF2), MD state to SCP over tinysys IPI","ACTIVE","drivers/misc/mediatek/eccci/fsm/ccci_fsm_scp_c.c",C,""),
("ccmni","CCMNI","CCMNI pure-IP netdevs ccmni0..ccmni20 (21), NAPI/WQ-GRO, RPS","ACTIVE","drivers/misc/mediatek/ccmni/",CB,""),
("rps_perf","CCMNI","set_rps_map helper (RPS CPU mask for ccmni / rndis)","ACTIVE","drivers/misc/mediatek/rps/",CB,""),
("mddp","MODEM-DATA-PATH","MD direct path (Wi-Fi tethering/WFPM offload); closed in the connectivity pass","ACTIVE","drivers/misc/mediatek/mddp/",CB,"same tree as connectivity research"),
("mtk_mdpm","MODEM-POWER","MD power meter (MD section power levels to PBM)","ACTIVE","drivers/misc/mediatek/mdpm/",CB,""),
("md_cooling_all","MODEM-POWER","MD thermal cooling devices (TX power / MUTT / SCG-off) via exec_ccci_kern_func","ACTIVE","drivers/thermal/mediatek/md_cooling*.c",CB,""),
("c2k_usb","C2K-USB","C2K rawbulk USB gadget core (modem AT/ETS/data over USB, factory/debug)","CONFIGURED","drivers/misc/mediatek/usb/c2k_usb/",CB,""),
("c2k_usb_f_via_atc","C2K-USB","rawbulk ATC function","CONFIGURED","drivers/misc/mediatek/usb/c2k_usb/",CB,""),
("c2k_usb_f_via_ets","C2K-USB","rawbulk ETS function","CONFIGURED","drivers/misc/mediatek/usb/c2k_usb/",CB,""),
("c2k_usb_f_via_modem","C2K-USB","rawbulk modem function","CONFIGURED","drivers/misc/mediatek/usb/c2k_usb/",CB,""),
("mtk_md_power_throttling","power-dependency","MD power throttling (low-battery/OC/BP notify -> MD)","ACTIVE","drivers/misc/mediatek/power_throttling/","6df320423600 (connectivity pass, KDM 05f8044)","dependency closure"),
]
def run(*a): return subprocess.run(a, capture_output=True, text=True).stdout
def find(name):
    for base in (VR, VD):
        p = base/(name+'.ko')
        if p.exists(): return p
def counts(path):
    rows = list(csv.DictReader(path.open(), delimiter='\t'))
    return sum(r['class'] == 'EXACT' for r in rows), len(rows)
def abi(name):
    rows = list(csv.DictReader((P/f'{name}.abi-parity.tsv').open(), delimiter='\t'))
    return 'EXACT' if all(r['result'].startswith('EXACT') for r in rows) else 'DIFF', {r['check']: f"{r['match']}/{r['total']}" for r in rows}
def secsizes(f):
    out = {}
    for l in run('readelf', '-SW', str(f)).splitlines():
        m = re.match(r'\s*\[\s*\d+\]\s+(\S+)\s+\S+\s+[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+)', l)
        if m and m.group(1) in ('.text', '.data', '.rodata', '.bss', '.init.text', '.exit.text'): out[m.group(1)] = int(m.group(2), 16)
    return ','.join(f"{k}={v}" for k, v in out.items())
def srcpaths(f):
    s = run('strings', '-a', str(f))
    return ';'.join(sorted(set(re.findall(r'\.\./kernel_device_modules-6\.1/[\w/.-]+\.[ch]', s))))
hdr = ['module','scope','role','board_state','stock_path','sha256','size','vermagic','depends','imports','exports','modversions','export_crcs','kcfi_typeids','functions_exact','functions_total','data_exact','data_total','abi','section_sizes','build_id','file_bytes_differing','source_strings','source_tree','source_path','source_commit','build_notes','status']
rows = []
for name, scope, role, state, src, commit, notes in M:
    f = find(name); b = f.read_bytes()
    mi = lambda k: run('modinfo', '-F', k, str(f)).strip().replace('\n', ',')
    kcfi = sum(1 for l in run('nm', str(f)).splitlines() if '__kcfi_typeid_' in l)
    bid = re.search(r'Build ID:\s*([0-9a-f]+)', run('readelf', '-n', str(f)))
    fe, ft = counts(P/f'{name}.function-parity.tsv'); de, dt = counts(P/f'{name}.data-parity.tsv')
    a, ad = abi(name)
    rb = Path('/tmp/mstripped')/(name+'.ko')
    diff = '-'
    if rb.exists():
        r = rb.read_bytes()
        diff = str(sum(1 for x, y in zip(b, r) if x != y) + abs(len(b)-len(r))) if len(b) == len(r) else f'size {len(b)}/{len(r)}'
    rows.append([name, scope, role, state, str(f.relative_to(ST)), hashlib.sha256(b).hexdigest(), len(b), mi('vermagic'), mi('depends'),
        ad.get('imports',''), ad.get('exports',''), ad.get('modversions',''), ad.get('export-crcs',''), kcfi, fe, ft, de, dt, a, secsizes(f),
        bid.group(1) if bid else '-', diff + (' (build-id only)' if diff == '20' else ''), srcpaths(f) or '-', KDM, src, commit, notes,
        'DONE' if (fe == ft and de == dt and a == 'EXACT') else 'PARTIAL'])
(ROOT/'kernel').mkdir(exist_ok=True)
with (ROOT/'kernel/module-inventory.tsv').open('w') as o:
    o.write('\t'.join(hdr)+'\n'); [o.write('\t'.join(map(str, r))+'\n') for r in rows]
with (ROOT/'kernel/source-map.tsv').open('w') as o:
    o.write('module\tsource_tree\tsource_path\tsource_commit\tresearch_build_tree\tnotes\n')
    for name, scope, role, state, src, commit, notes in M:
        o.write(f'{name}\t{KDM}\t{src}\t{commit}\t$G/kernel_device_modules-6.1 (git; modem commit 67c7da4)\t{notes}\n')
for kind in ('function', 'data', 'abi'):
    with (ROOT/f'binary-analysis/{kind}-parity.tsv').open('w') as o:
        first = True
        for name, *_ in M:
            p = P/f'{name}.{kind}-parity.tsv'
            lines = p.read_text().splitlines()
            if first: o.write('module\t'+lines[0]+'\n'); first = False
            for l in lines[1:]: o.write(f'{name}\t{l}\n')
for r in rows: print(f"{r[0]}\t{r[14]}/{r[15]}\t{r[16]}/{r[17]}\t{r[18]}\t{r[21]}\t{r[27]}")
print('TOTAL', sum(r[15] for r in rows), sum(r[17] for r in rows))
