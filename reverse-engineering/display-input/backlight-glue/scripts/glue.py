#!/usr/bin/env python3
"""Isolated M= rebuild + parity harness for small KDM display-glue modules.

usage: glue.py NAME            (spec in SPECS)
Copies the listed KDM sources into lieppos/glue/NAME/src, writes a Kbuild,
builds against the CI-12901745 kout, strips debug, runs ko-parity-tsv.py.
"""
import os, shutil, subprocess, sys, glob

G = '/home/armol/kernel-work/gki-12901745-workspace'
K = G + '/kernel_device_modules-6.1'
L = G + '/lieppos/glue'
R = '/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research'
STOCK = R + '/workspace/gq5012bf1/stock'
PARITY = R + '/reverse-engineering/display-input/rear-display-input/scripts/ko-parity-tsv.py'
CLANG = G + '/prebuilts/clang/host/linux-x86/clang-r487747c/bin'

SPECS = {
    'mtk-pwm': dict(files=['drivers/misc/mediatek/pwm/mtk_pwm.c', 'drivers/misc/mediatek/pwm/pwm_v2/mtk_pwm_hal.c'],
                    objs='mtk_pwm.o pwm_v2/mtk_pwm_hal.o',
                    inc=['drivers/misc/mediatek/include/', 'drivers/misc/mediatek/pwm/pwm_v2/include/']),
    'pwm-mtk-disp': dict(files=['drivers/pwm/pwm-mtk-disp.c'], inc=[]),
    'leds-mtk': dict(files=['drivers/leds/leds-mtk.c', 'drivers/leds/leds-mtk.h'],
                     inc=['drivers/misc/mediatek/flashlight', 'drivers/misc/mediatek/power_throttling', 'drivers/leds/'],
                     extra=['ccflags-y += -I$(srctree)/drivers/power/supply']),
    'leds-mtk-disp': dict(files=['drivers/leds/leds-mtk-disp.c', 'drivers/leds/leds-mtk.h'],
                          inc=['drivers/leds/', 'drivers/gpu/drm/mediatek/mediatek_v2/', 'drivers/misc/mediatek/include/',
                               'drivers/misc/mediatek/include/mt-plat/', 'drivers/gpu/drm/panel/']),
    'backlight_cooling': dict(files=['drivers/thermal/mediatek/backlight_cooling.c'],
                              inc=['drivers/thermal/mediatek/', 'drivers/leds/']),
    'mediatek-drm-gateic': dict(mode='mirror', dir='drivers/gpu/drm/panel', copydirs=['drivers/gpu/drm/panel'],
                                links=['drivers/gpu/drm/mediatek', 'drivers/misc', 'drivers/leds', 'include'],
                                inc=['drivers/misc/mediatek/include/mt-plat', 'drivers/leds/', 'include'],
                                objs='mtk_drm_panel_i2c.o mtk_drm_gateic_rt4801h.o mtk_drm_gateic_rt4831a.o mtk_drm_gateic.o'),
    'mediatek-drm-panel-drv': dict(mode='mirror', dir='drivers/gpu/drm/panel',
                                copydirs=['drivers/gpu/drm/panel', 'drivers/gpu/drm/mediatek/mediatek_v2'],
                                overrides={'/home/armol/kernel-work/gki-12901745-workspace/lieppos/disp/stockhdr/mtk_panel_ext.h':
                                           'drivers/gpu/drm/mediatek/mediatek_v2/mtk_panel_ext.h'},
                                links=['drivers/gpu/drm/mediatek/mml', 'drivers/misc', 'drivers/leds', 'include'],
                                inc=['drivers/misc/mediatek/include/mt-plat', 'drivers/leds/', 'include'],
                                objs='mtk_round_corner/mtk_drm_rc.o mtk_drm_panel_helper.o mtk_drm_panel_helper_dbi.o mtk_drm_panel_helper_dpi.o mtk_drm_panel_helper_dsi.o mtk_drm_panel_drv_dbi.o mtk_drm_panel_drv_dpi.o mtk_drm_panel_drv_dsi.o mtk_drm_panel_drv.o'),
    'mtk_disp_sec': dict(mode='mirror', dir='drivers/gpu/drm/mediatek/mediatek_v2',
                         copydirs=['drivers/gpu/drm/mediatek/mediatek_v2'],
                         links=['drivers/misc', 'drivers/iommu', 'drivers/dma-buf', 'drivers/gpu/drm/panel', 'drivers/leds',
                                'include', 'drivers/soc', 'drivers/devfreq', 'drivers/gpu/drm/mediatek/mml'],
                         inc=['include'], objs='mtk_disp_sec.o', include_makefile=True),
    'rt4831a_drv': dict(files=['drivers/misc/mediatek/gate_ic/rt4831a_drv.c', 'drivers/misc/mediatek/gate_ic/gate_i2c.h'],
                        inc=['drivers/leds/']),
    'regulator-vibrator': dict(files=['drivers/leds/regulator-vibrator.c'], inc=['drivers/leds/']),
    'aw36518': dict(files=['drivers/misc/mediatek/flashlight/aw36518.c', 'drivers/misc/mediatek/flashlight/flashlight.h',
                           'drivers/misc/mediatek/flashlight/flashlight-core.h', 'drivers/misc/mediatek/flashlight/flashlight-dt.h'],
                    srcdir='/home/armol/kernel-work/gki-12901745-workspace/lieppos/aw36518-recon/recon',
                    inc=['drivers/misc/mediatek/flashlight/']),
    'aw36518_v2': dict(files=['drivers/misc/mediatek/flashlight/aw36518_v2.c', 'drivers/misc/mediatek/flashlight/flashlight.h',
                           'drivers/misc/mediatek/flashlight/flashlight-core.h', 'drivers/misc/mediatek/flashlight/flashlight-dt.h'],
                    srcdir='/home/armol/kernel-work/gki-12901745-workspace/lieppos/aw36518-v2-recon',
                    inc=['drivers/misc/mediatek/flashlight/']),
    'mtk_irtx_pwm': dict(files=['drivers/misc/mediatek/irtx/mtk_irtx_pwm.c'],
                         inc=['drivers/misc/mediatek/include/', 'drivers/misc/mediatek/include/mt-plat/',
                              'drivers/misc/mediatek/pwm/pwm_v2/include/']),
}


def stock_ko(name):
    for l in open(L + '/stock-kos.txt'):
        if os.path.basename(l.strip()) == name + '.ko':
            return l.strip()
    raise SystemExit('no stock ' + name)


def mirror(name, sp):
    """Mirror mode: copy whole KDM dir(s) at their KDM-relative path, symlink others."""
    d = f'{L}/{name}/src'
    if '--keep' not in sys.argv:
        shutil.rmtree(d, ignore_errors=True)
        for sub in sp['copydirs']:
            shutil.copytree(f'{K}/{sub}', f'{d}/{sub}', symlinks=True,
                            ignore=shutil.ignore_patterns('*.o', '*.ko', '.*.cmd'))
        for src_, dst_ in sp.get('overrides', {}).items():
            os.makedirs(os.path.dirname(f'{d}/{dst_}'), exist_ok=True)
            shutil.copy2(src_, f'{d}/{dst_}')
        for sub in sp.get('links', []):
            os.makedirs(os.path.dirname(f'{d}/{sub}'), exist_ok=True)
            os.symlink(f'{K}/{sub}', f'{d}/{sub}')
    sub = sp['dir']
    open(f'{d}/Kbuild', 'w').write(f'obj-m += {sub}/\nKBUILD_EXTRA_SYMBOLS += {L}/stock-all.symvers\n')
    kb = [f'ccflags-y += -I$(DEVICE_MODULES_PATH)/{i}' for i in sp.get('inc', [])] + sp.get('extra', [])
    if sp.get('include_makefile'):
        kb = ['include $(src)/Makefile', 'obj-y :=', 'obj-m :='] + kb
    if sp['objs'] == name + '.o':
        kb += [f'obj-m += {name}.o']
    else:
        kb += [f'obj-m += {name}.o', f'{name}-y := {sp["objs"]}']
    open(f'{d}/{sub}/Kbuild', 'w').write('\n'.join(kb) + '\n')
    return d, f'{d}/{sub}/{name}', f'-fmacro-prefix-map={d}/=../kernel_device_modules-6.1/'


def main():
    name = sys.argv[1]
    sp = SPECS[name]
    if sp.get('mode') == 'mirror':
        d, kobase, pmap = mirror(name, sp)
        return build(name, d, kobase, pmap)
    d = f'{L}/{name}/src'
    if '--keep' not in sys.argv:
        shutil.rmtree(d, ignore_errors=True)
        for f in sp['files']:
            base = os.path.relpath(f, os.path.dirname(sp['files'][0]))
            os.makedirs(os.path.dirname(f'{d}/{base}') or d, exist_ok=True)
            rev = os.environ.get('GLUE_REV')
            if rev:
                repo, h = rev.split(':')
                data = subprocess.run(['git', '-C', repo, 'show', f'{h}:{f}'], capture_output=True, check=True).stdout
                open(f'{d}/{base}', 'wb').write(data)
            elif sp.get('srcdir'):
                shutil.copy2(f"{sp['srcdir']}/{os.path.basename(f)}", f'{d}/{base}')
            else:
                shutil.copy2(f'{K}/{f}', f'{d}/{base}')
        for hp in os.environ.get('GLUE_HDRS', '').split():
            repo, h = os.environ['GLUE_REV'].split(':')
            data = subprocess.run(['git', '-C', repo, 'show', f'{h}:{hp}'], capture_output=True, check=True).stdout
            dst = f'{d}/ovl/' + hp.split('include/', 1)[1]
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, 'wb').write(data)
    mod = name.replace('-', '_') if False else name
    kb = [f'ccflags-y += -I{d}/ovl'] if os.path.isdir(f'{d}/ovl') else []
    kb = [f'ccflags-y += -I{d}'] + kb + ['ccflags-y += -I$(DEVICE_MODULES_PATH)/include'] + [f'ccflags-y += -I$(DEVICE_MODULES_PATH)/{i}' for i in sp['inc']]
    kb += sp.get('extra', [])
    if 'objs' in sp:
        kb += [f'obj-m += {mod}.o', f'{mod}-objs := {sp["objs"]}']
    else:
        kb += [f'obj-m += {os.path.basename(sp["files"][0])[:-2]}.o']
    kb += [f'KBUILD_EXTRA_SYMBOLS += {L}/stock-all.symvers']
    open(f'{d}/Kbuild', 'w').write('\n'.join(kb) + '\n')
    kdir = os.path.dirname(sp['files'][0])
    return build(name, d, f'{d}/{name}', f'-fmacro-prefix-map={d}/=../kernel_device_modules-6.1/{kdir}/')


def build(name, d, kobase, pmap):
    env = dict(os.environ, PATH=CLANG + ':' + os.environ['PATH'])
    # stock KDM is built as one external module rooted at ../kernel_device_modules-6.1,
    # so __FILE__ strings are '../kernel_device_modules-6.1/<dir>/<file>.c'
    flags = (os.environ.get('GLUE_KCFLAGS', '-faddrsig') + ' ' + pmap).strip()
    cmd = ['make', f'O={G}/lieppos/nfc/kout', f'M={d}', 'ARCH=arm64', 'LLVM=1', 'LLVM_IAS=1',
           'KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/', 'DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1',
           'DEVICE_MODULES_PATH=$(srctree)/$(DEVICE_MODULES_REL_DIR)', 'module_scmversion=', '-j16', 'modules']
    if flags:
        cmd.append('KCFLAGS=' + flags)
    r = subprocess.run(cmd, cwd=G + '/common', env=env, capture_output=True, text=True)
    open(f'{d}/build.log', 'w').write(r.stdout + r.stderr)
    errs = [l for l in (r.stdout + r.stderr).splitlines() if 'error' in l.lower() or 'warning: modpost' in l.lower() or 'WARNING' in l]
    print('\n'.join(errs[:25]))
    if r.returncode:
        print('BUILD FAILED'); sys.exit(1)
    ko = kobase + '.ko'
    subprocess.run([CLANG + '/llvm-strip', '--strip-debug', '-o', f'{kobase}.stripped.ko', ko], check=True)
    shutil.copy2(f'{kobase}.stripped.ko', f'{L}/{name}/{name}.stripped.ko')
    out = f'{L}/{name}/parity'
    p = subprocess.run(['python3', PARITY, stock_ko(name), f'{kobase}.stripped.ko', out], env=env,
                       capture_output=True, text=True)
    print(p.stdout.split('\nA = ')[0])
    p2 = subprocess.run(['python3', L + '/secdiff.py', stock_ko(name), f'{kobase}.stripped.ko'], env=env,
                        capture_output=True, text=True)
    print(p2.stdout.strip())
    if p.returncode:
        print(p.stderr[-2000:])


if __name__ == '__main__':
    main()
