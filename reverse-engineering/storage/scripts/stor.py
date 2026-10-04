#!/usr/bin/env python3
"""Storage isolated-rebuild harness: reuses lieppos/glue/glue.py with storage SPECS.
usage: stor.py NAME [--keep]   (K overridable with STOR_K=<kdm tree>)"""
import sys, os
sys.path.insert(0, '/home/armol/kernel-work/gki-12901745-workspace/lieppos/glue')
import glue
glue.L = '/home/armol/kernel-work/gki-12901745-workspace/lieppos/storage'
if os.environ.get('STOR_K'):
    glue.K = os.environ['STOR_K']
LNK = ['include', 'drivers/misc', 'drivers/clk', 'drivers/devfreq', 'drivers/soc', 'drivers/power', 'drivers/thermal',
       'drivers/tee', 'drivers/iommu', 'drivers/gpu', 'drivers/pinctrl', 'drivers/scsi', 'drivers/regulator', 'drivers/phy', 'drivers/char', 'drivers/mmc', 'drivers/ufs']
def links(*own):
    return [l for l in LNK if not any(o == l or o.startswith(l + '/') for o in own)]
glue.SPECS = {
    'ufs-mediatek-mod': dict(mode='mirror', dir='drivers/ufs/vendor', copydirs=['drivers/ufs'], links=links('drivers/ufs'),
                             include_makefile=True, inc=[],
                             objs='../ufs-mediatek.o ../ufs-mediatek-sysfs.o ../ufs-mediatek-mimic.o ../ufs-mediatek-btag.o ../ufs-mediatek-rpmb.o ../ufs-mediatek-ise-dummy.o'),
    'ufs-mediatek-dbg': dict(mode='mirror', dir='drivers/ufs', copydirs=['drivers/ufs'], links=links('drivers/ufs'),
                             include_makefile=True, inc=[], objs='ufs-mediatek-dbg.o'),
    'phy-mtk-ufs': dict(mode='mirror', dir='drivers/phy/mediatek', copydirs=['drivers/phy/mediatek'], links=links('drivers/phy') + ['drivers/ufs'],
                        include_makefile=True, inc=[], objs='phy-mtk-ufs.o'),
    'rpmb': dict(mode='mirror', dir='drivers/char/rpmb', copydirs=['drivers/char/rpmb'], links=links('drivers/char') + ['drivers/ufs', 'drivers/mmc'],
                 include_makefile=True, inc=[], objs='core.o cdev.o'),
    'rpmb-mtk': dict(mode='mirror', dir='drivers/char/rpmb', copydirs=['drivers/char/rpmb'], links=links('drivers/char') + ['drivers/ufs', 'drivers/mmc'],
                     include_makefile=True, inc=[], objs='rpmb-mtk.o'),
    'mtk-mmc': dict(mode='mirror', dir='drivers/mmc/host', copydirs=['drivers/mmc'], links=links('drivers/mmc'),
                    include_makefile=True, inc=[], objs='mtk-mmc.o'),
    'mtk-mmc-dbg': dict(mode='mirror', dir='drivers/mmc/host', copydirs=['drivers/mmc'], links=links('drivers/mmc'),
                        include_makefile=True, inc=[], objs='mtk-mmc-dbg.o'),
    'mtk-wp': dict(mode='mirror', dir='drivers/mmc/host', copydirs=['drivers/mmc'], links=links('drivers/mmc'),
                   include_makefile=True, inc=[], objs='mtk-wp.o'),
    'cqhci': dict(mode='mirror', dir='drivers/mmc/host', copydirs=['drivers/mmc'], links=links('drivers/mmc'),
                  include_makefile=True, inc=[], objs='cqhci-core.o cqhci-crypto.o'),
    'blocktag': dict(mode='mirror', dir='drivers/misc/mediatek/blocktag', copydirs=['drivers/misc/mediatek/blocktag'],
                     links=[l for l in LNK if l != 'drivers/misc'] + ['drivers/misc/mediatek/include', 'drivers/misc/mediatek/aee', 'drivers/misc/mediatek/mrdump'],
                     include_makefile=True, inc=[], objs='blocktag-mictx.o blocktag-core.o blocktag-earaio.o blocktag-ufs.o blocktag-mmc.o'),
}
for _s in glue.SPECS.values():
    _s['links'] = list(dict.fromkeys(_s['links']))
glue.main()
