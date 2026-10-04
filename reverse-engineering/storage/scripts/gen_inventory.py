#!/usr/bin/env python3
"""gen_inventory.py OUT.tsv : GQ5012BF1 storage module inventory from stock .ko + parity dirs.
Static, read-only: reads stock modules and the parity outputs written by sb.sh/build-all.sh."""
import subprocess, hashlib, os, re, sys

W = '/home/armol/kernel-work/gki-12901745-workspace/lieppos/storage'
STOCK = '/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/workspace/gq5012bf1/stock'
LLVM = '/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin/'
REL = {  # module -> (class, stock path rel, source candidate, revision, runtime role, parity dir)
    'ufs-mediatek-mod': ('MEDIATEK VENDOR MODULE', 'vendor-ramdisks/platform-extracted/lib/modules',
                         'KDM drivers/ufs/{ufs-mediatek,-sysfs,-mimic,-btag,-rpmb,-ise-dummy}.c (non-iSE variant, no ufsfeature/ufshid)',
                         'MTK ALPS 5e415e059253 + MTK ACK ufshcd.h/ufshcd-priv.h debug-vops hunks (line layout only)',
                         'ACTIVE: UFSHCI host variant for soc/112b0000.ufshci (boot device); RPMB raw-dev provider', 'ufs-mediatek-mod-B2'),
    'ufs-mediatek-dbg': ('MEDIATEK VENDOR MODULE', 'vendor-ramdisks/platform-extracted/lib/modules',
                         'KDM drivers/ufs/ufs-mediatek-dbg.c', 'MTK ALPS 5e415e059253 + 69-line layout pad (proven by __LINE__)',
                         'ACTIVE: cmd history, /proc/ufs_debug, AEE error hooks', 'ufs-mediatek-dbg-B2'),
    'phy-mtk-ufs': ('MEDIATEK VENDOR MODULE', 'vendor-ramdisks/platform-extracted/lib/modules',
                    'KDM drivers/phy/mediatek/phy-mtk-ufs.c', 'MTK ALPS 5e415e059253 (unmodified)',
                    'ACTIVE: M-PHY for soc/ufsphy@112a0000', 'phy-mtk-ufs-B2'),
    'rpmb': ('MEDIATEK VENDOR MODULE', 'vendor-ramdisks/platform-extracted/lib/modules',
             'KDM drivers/char/rpmb/core.o only (no cdev.o: CONFIG_RPMB_INTF_DEV off)', 'MTK ALPS 5e415e059253 (unmodified)',
             'ACTIVE: RPMB class core (rpmb_dev_register by ufs-mediatek-mod)', 'rpmb-B2'),
    'rpmb-mtk': ('MEDIATEK VENDOR MODULE (GQ5012BF1-modified)', 'vendor-ramdisks/platform-extracted/lib/modules',
                 'KDM drivers/char/rpmb/rpmb-mtk.c + GQ5012BF1 TrustKernel patch (raw-frame ioctls 10..14, netlink off, Trustonic off)',
                 'MTK ALPS 5e415e059253 + reconstructed ODM patch (no public source); built against ufs-mediatek-mod-ise symvers',
                 'ACTIVE: /dev/rpmb0 char device (RPMB transport for the TrustKernel TEE daemon)', 'rpmb-mtk-B2'),
    'mtk-mmc': ('MEDIATEK VENDOR MODULE', 'vendor-ramdisks/platform-extracted/lib/modules',
                'KDM drivers/mmc/host/mtk-mmc.c', 'MTK ALPS 5e415e059253 (unmodified)',
                'ACTIVE: MSDC1 microSD host soc/mmc@11240000 (MSDC0 eMMC node disabled)', 'mtk-mmc-B2'),
    'mtk-mmc-dbg': ('MEDIATEK VENDOR MODULE', 'vendor-ramdisks/platform-extracted/lib/modules',
                    'KDM drivers/mmc/host/mtk-mmc-dbg.c', 'MTK ALPS 5e415e059253 (unmodified)', 'ACTIVE: MSDC debug/history', 'mtk-mmc-dbg-B2'),
    'cqhci': ('MEDIATEK VENDOR MODULE (KDM copy of upstream CQHCI)', 'vendor-ramdisks/platform-extracted/lib/modules',
              'KDM drivers/mmc/host/cqhci-core.c + cqhci-crypto.c', 'MTK ALPS 5e415e059253 (unmodified)',
              'LOADED, UNUSED on this board (only MSDC0/eMMC has supports-cqe and it is disabled)', 'cqhci-B2'),
    'mtk-wp': ('MEDIATEK VENDOR MODULE', 'vendor-ramdisks/platform-extracted/lib/modules',
               'KDM drivers/mmc/host/mtk-wp.c', 'MTK ALPS 5e415e059253 (unmodified)',
               'LOADED: block write-protect policy via wp_boot1/wp_boot2/wp_user module params (none set in modules.load/bootconfig evidence)', 'mtk-wp-B2'),
    'blocktag': ('MEDIATEK VENDOR MODULE', 'vendor-ramdisks/platform-extracted/lib/modules',
                 'KDM drivers/misc/mediatek/blocktag/{mictx,core,earaio,ufs,mmc}.c (no fuse/pm/fscmd tracers)', 'MTK ALPS 5e415e059253 (unmodified)',
                 'ACTIVE: block I/O tracer, /proc/blocktag, EARA-IO boost hints', 'blocktag-B2'),
    'zram': ('GENERIC GKI', 'partitions/system_dlkm/lib/modules', 'ACK 6b18f0b574ab drivers/block/zram', 'GKI 12901745 (system_dlkm, signed GKI module)',
             'ACTIVE: swap (vendor/etc/fstab.enableswap zram0 zramsize=100%)', None),
    'zsmalloc': ('GENERIC GKI', 'partitions/system_dlkm/lib/modules', 'ACK 6b18f0b574ab mm/zsmalloc.c', 'GKI 12901745', 'ACTIVE: zram allocator', None),
}


def run(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout


def kv(summary, key):
    for l in summary.splitlines():
        if l.startswith(key):
            return l.split(':', 1)[1].strip()
    return ''


cols = ['filename', 'class', 'path', 'sha256', 'size', 'vermagic', 'depends', 'imports(__versions)', 'exports', 'modversions',
        'KCFI', 'functions', 'data', 'sections', 'relocations', 'build-ID', 'source candidate', 'source revision', 'runtime role',
        'parity A vs B']
out = ['\t'.join(cols)]
for m, (cls, rel, src, rev, role, pd) in REL.items():
    p = f'{STOCK}/{rel}/{m}.ko'
    raw = open(p, 'rb').read()
    mi = run(LLVM + 'llvm-readelf', '-p', '.modinfo', p)
    vm = re.search(r'vermagic=([^\n]*)', mi); dep = re.search(r'depends=([^\n]*)', mi)
    note = run(LLVM + 'llvm-readelf', '-n', p)
    bid = re.search(r'Build ID: ([0-9a-f]+)', note)
    nsec = len(re.findall(r'^\s*\[\s*\d+\]', run(LLVM + 'llvm-readelf', '-SW', p), re.M)) - 1
    S = open(f'{W}/par/{pd}/SUMMARY.txt').read() if pd else ''
    fn = kv(S, 'functions'); da = kv(S, 'data objects'); im = kv(S, 'imports'); ex = kv(S, 'exports'); rl = kv(S, 'relocation entries')
    g = lambda pat, s: (re.search(pat, s).group(1) if re.search(pat, s) else '')
    if pd:
        sec = open(f'{W}/par/{pd}.secdiff').read().strip() if os.path.exists(f'{W}/par/{pd}.secdiff') else ''
        par = 'EXACT (all sections equal except .note.gnu.build-id; B1==B2)' if "differing: ['.note.gnu.build-id']" in sec else 'PARTIAL: ' + fn.split(' kcfi')[0]
    else:
        par = 'n/a (generic GKI module, not rebuilt)'
    fnn = len(re.findall(r' [tT] ', run(LLVM + 'llvm-nm', p)))
    out.append('\t'.join([m + '.ko', cls, rel + '/' + m + '.ko', hashlib.sha256(raw).hexdigest(), str(len(raw)),
                          vm.group(1) if vm else '', dep.group(1) if dep else '',
                          (g(r'A=(\d+)', im) or str(len(raw) and 0)) if pd else '',
                          g(r'A=(\d+)', ex) if pd else '',
                          (g(r'name\+CRC-equal=(\d+)', im) + '/' + g(r'A=(\d+)', im) + ' CRC-equal') if pd else '',
                          (g(r'kcfi-equal=(\d+)', fn) + '/' + g(r'A=(\d+)', fn)) if pd else '',
                          (g(r'byte-identical=(\d+)', fn) + '/' + g(r'A=(\d+)', fn) + ' byte-identical') if pd else f'{fnn} (text syms)',
                          (g(r'bytes-equal=(\d+)', da) + '/' + g(r'A=(\d+)', da)) if pd else '',
                          str(nsec), (g(r'A=(\d+)', rl) + ' A / ' + g(r'B=(\d+)', rl) + ' B') if pd else '',
                          bid.group(1) if bid else '', src, rev, role, par]))
open(sys.argv[1], 'w').write('\n'.join(out) + '\n')
print('\n'.join(l.split('\t')[0] + '  ' + l.split('\t')[-1] for l in out))
