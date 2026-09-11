#!/usr/bin/env python3
"""Fail-closed offline verifier for the leds_ln2403 reconstruction."""
import csv, hashlib, os, re, subprocess, sys

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
ORACLE=os.path.join(ROOT,'workspace/phase4-leds-ln2403/oracle/leds-ln2403.ko')
REBUILT=os.path.join(ROOT,'workspace/phase4-leds-ln2403/build/leds_ln2403.rebuilt.ko')
PSTOCK=os.path.join(ROOT,'workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/mtk-pwm.ko')
PBUILD=os.path.join(ROOT,'workspace/phase4-leds-ln2403/provider/mtk-pwm.source-built.ko')
SRC=os.path.join(ROOT,'kernel/phase4-leds-ln2403-recon/leds_ln2403.c')
GSRC='/home/armol/kernel-work/gki-12901745-workspace/lieppos/leds-ln2403-recon/leds_ln2403.c'
PSRC=os.path.join(ROOT,'kernel/phase4-mtk-pwm-provider')
GPSRC='/home/armol/kernel-work/gki-12901745-workspace/lieppos/mtk-pwm-provider'
PROVIDER_FILES=['mtk_pwm.c','pwm_v2/mtk_pwm_hal.c','include/mt-plat/mtk_pwm.h','include/mt-plat/mtk_pwm_hal.h','include/mt-plat/mtk_pwm_hal_pub.h','pwm_v2/include/mach/mtk_pwm_prv.h']
READELF='/usr/lib/llvm/23/bin/llvm-readelf'
checks=[]
def check(name, value):
    checks.append((name,bool(value)))
def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
def rows(p):
    with open(os.path.join(ROOT,p),newline='') as f: return list(csv.DictReader(f,delimiter='\t'))
def run(*a): return subprocess.check_output(a,text=True,errors='replace')
def funcs(p):
    b=open(p,'rb').read(); sec={}
    for l in run(READELF,'-SW',p).splitlines():
        m=re.match(r'\s*\[\s*(\d+)\]\s+(\S+)\s+\S+\s+\S+\s+(\S+)\s+(\S+)',l)
        if m: sec[int(m[1])]=(m[2],int(m[3],16),int(m[4],16))
    out={}
    for l in run(READELF,'-sW',p).splitlines():
        m=re.match(r'\s*\d+:\s+([0-9a-f]+)\s+(\d+)\s+FUNC\s+\S+\s+\S+\s+(\d+)\s+(\S+)',l)
        if m:
            v,z,nx,n=int(m[1],16),int(m[2]),int(m[3]),m[4]
            if z and nx in sec:
                fo=sec[nx][1]; out[n]=b[fo+v:fo+v+z]
    return out

def main():
    required=[ORACLE,REBUILT,PSTOCK,PBUILD,SRC]+[os.path.join(PSRC,p) for p in PROVIDER_FILES]
    check('required binaries/source exist',all(os.path.isfile(p) for p in required))
    check('oracle SHA256 frozen',sha(ORACLE)=='211bda35ee3476c107d7e495a0463c27bbef114a031a6b81b8bb718bbe54ee94')
    check('oracle size frozen',os.path.getsize(ORACLE)==39344)
    check('rebuilt SHA256 frozen',sha(REBUILT)=='9ba9d6fef5d1e364aae07692169cde076eb4c3db509d9032c1265e78351db526')
    check('rebuilt size frozen',os.path.getsize(REBUILT)==36976)
    note=run(READELF,'-n',ORACLE); rnote=run(READELF,'-n',REBUILT)
    check('stock Build ID', '589cce1de2565302414117d6e650f26aa98c4a46' in note)
    check('rebuilt Build ID', 'eff0083a51ae66750cdc35f57c4340d83f06a9d3' in rnote)
    check('stock PAC property','aarch64 feature: PAC' in note)
    check('rebuilt PAC property','aarch64 feature: PAC' in rnote)
    rb=open(REBUILT,'rb').read(); ob=open(ORACLE,'rb').read()
    check('module name exact',b'name=leds_ln2403\0' in rb)
    check('provider dependency exact',b'depends=mtk-pwm\0' in rb)
    check('OF alias base exact',b'alias=of:N*T*Cmediatek,yft_camplight\0' in rb)
    check('OF alias wildcard exact',b'alias=of:N*T*Cmediatek,yft_camplightC*\0' in rb)
    check('description exact',b'description=Module For PWM LN2403\0' in rb)
    check('author exact',b'author=yuanliang, <yuanliang@dazhi.sh.cn>\0' in rb)
    check('license exact',b'license=GPL\0' in rb)
    expected={'cleanup_module','init_module','mt_camplight_mode_show','mt_camplight_mode_store','leds_ctl_show','leds_ctl_store','camplight_set_brightness_show','camplight_set_brightness_store','ln2403_gpio_ctrl_apply','ln2403_pwm_work','gpio_ctrl_timer_handler','set_leds','camplight_probe','camplight_remove','redblue_led_timer_func','ln2403_get_gpio'}
    fp=rows('kernel/phase4-leds-ln2403-function-parity.tsv')
    check('function set 16/16',{x['function'] for x in fp}==expected and len(fp)==16)
    check('rebuilt has no extra function',set(funcs(REBUILT))==expected)
    check('function size parity count',sum(x['size_identical']=='yes' for x in fp)==8)
    check('function byte parity count',sum(x['byte_identical']=='yes' for x in fp)==7)
    ka=[x for x in fp if x['kcfi_applicable']=='yes']
    check('KCFI applicable count',len(ka)==12)
    check('KCFI exact 12/12',all(x['stock_kcfi_or_preword']==x['rebuild_kcfi_or_preword'] for x in ka))
    check('all function residuals explained',all(x['residual_explanation']!='unresolved' for x in fp))
    imp=rows('kernel/phase4-leds-ln2403-import-delta.tsv')
    check('import set 32/32',len(imp)==32 and all(x['presence']=='shared' for x in imp))
    check('MODVERSION CRC 32/32',all(x['crc_match']=='yes' and x['status']=='EXACT' for x in imp))
    check('mt_pwm_disable CRC',any(x['symbol']=='mt_pwm_disable' and x['stock_crc']=='0xd602ce35' and x['rebuild_crc']==x['stock_crc'] for x in imp))
    check('pwm_set_spec_config CRC',any(x['symbol']=='pwm_set_spec_config' and x['stock_crc']=='0xa54c8591' and x['rebuild_crc']==x['stock_crc'] for x in imp))
    check('target has zero exports',b'__ksymtab_' not in rb)
    sf,pf=funcs(PSTOCK),funcs(PBUILD)
    check('provider mt_pwm_disable bytes exact',sf.get('mt_pwm_disable')==pf.get('mt_pwm_disable') and len(sf.get('mt_pwm_disable',b''))==160)
    check('provider pwm_set_spec_config bytes exact',sf.get('pwm_set_spec_config')==pf.get('pwm_set_spec_config') and len(sf.get('pwm_set_spec_config',b''))==744)
    op=rows('kernel/phase4-leds-ln2403-object-parity.tsv')
    exact_objects={'ln2403_mode_str','ln2403_leds_str','dev_attr_camplight_mode','dev_attr_leds_ctl','dev_attr_camplight_set_brightness','camplight_of_match','camplight_driver','camplight_duty'}
    check('critical object bytes exact',all(any(x['object']==n and x['classification']=='BYTE_IDENTICAL' for x in op) for n in exact_objects|{'mt_sysfs_attributes'}))
    check('objects have no unresolved label',all('unresolved' not in x['explanation'].lower() for x in op))
    src=open(SRC).read()
    check('source snapshot synchronized',os.path.isfile(GSRC) and open(GSRC).read()==src and all(os.path.isfile(os.path.join(GPSRC,p)) and open(os.path.join(GPSRC,p),'rb').read()==open(os.path.join(PSRC,p),'rb').read() for p in PROVIDER_FILES))
    check('five GPIO properties',all(x in src for x in ['ln2403-en-gpio','ln2403-power-gpio','leds-power-gpio','leds-red-gpio','leds-blue-gpio']))
    check('three pinctrl states',all(x in src for x in ['ln2403_pwmoff_high','ln2403_pwmoff_low','ln2403_pwmon']))
    check('three sysfs attributes',all(x in src for x in ['DEVICE_ATTR(camplight_mode','DEVICE_ATTR(leds_ctl','DEVICE_ATTR(camplight_set_brightness']))
    check('PWM channel and cap', '#define PWM_NO 3' in src and 'conf.pwm_no = PWM_NO' in src and 'camplight_duty >= 94' in src)
    check('fixed PWM percentages',all(x in src for x in ['ln2403_pwm_work(1, 97, 17)','ln2403_pwm_work(1, 73, 17)','ln2403_pwm_work(1, 11, 17)']) and 'if (mode >= 6)' in src and 'mode >= ARRAY_SIZE' not in src)
    check('timer constants',all(x in src for x in ['NS_40MS 40000000LL','NS_50MS 50000000LL','NS_200MS 200000000LL','NS_500MS 500000000LL','NS_1S 1000000000LL']))
    check('no PM/shutdown hooks',all(x not in src for x in ['.shutdown =','.suspend =','.resume =','.pm =']))
    remove_body=src.split('static int camplight_remove',1)[1].split('}',1)[0]
    check('remove preserves no-teardown defect','device_remove_file' not in remove_body and 'hrtimer_cancel' not in remove_body and 'mt_pwm_disable' not in remove_body and 'return 0;' in remove_body)
    dts=open(os.path.join(ROOT,'workspace/phase4-leds-ln2403/dt/vendor-dtb-00.dts')).read()
    check('DT node and compatible','yft_camplight {' in dts and 'compatible = "mediatek,yft_camplight"' in dts)
    check('DT GPIO values',all(re.search(rf'{re.escape(n)} = <0x[0-9a-f]+ 0x{v:x} 0x00>;',dts) for n,v in [('ln2403-power-gpio',74),('ln2403-en-gpio',91),('leds-power-gpio',153),('leds-red-gpio',20),('leds-blue-gpio',21)]))
    check('DT pinctrl state strings',all(x in dts for x in ['"ln2403_pwmoff_high"','"ln2403_pwmoff_low"','"ln2403_pwmon"']))
    blog=open(os.path.join(ROOT,'workspace/phase4-leds-ln2403/build/final-build.log'),errors='replace').read()
    check('build succeeded','Build completed successfully' in blog)
    check('compiler warning free',not re.search(r'(^|\s)warning:',blog,re.M|re.I))
    check('modpost warning free','modpost: WARNING' not in blog)
    check('no undefined symbols','undefined!' not in blog and 'undefined symbol' not in blog.lower())
    docs=['stock-oracle.txt','RED.md','source-candidates.md','provider-abi.md','dt-contract.md','hardware-contract.md','pwm-contract.md','camplight-mode-contract.md','brightness-contract.md','redblue-contract.md','async-contract.md','struct-layout.md','probe-contract.md','lifecycle-contract.md','sysfs-contract.md','userspace-contract.md','safety-contract.md','build-parity.md','reconstruction.md']
    check('required closure documents',all(os.path.isfile(os.path.join(ROOT,'kernel/phase4-leds-ln2403-'+x)) for x in docs))
    check('no placeholder language',all(not re.search(r'\b(TODO|TBD|FIXME)\b',open(os.path.join(ROOT,'kernel/phase4-leds-ln2403-'+x),errors='replace').read(),re.I) for x in docs))
    failed=[n for n,v in checks if not v]
    for n,v in checks: print(('PASS' if v else 'FAIL')+': '+n)
    print(f'{len(checks)-len(failed)}/{len(checks)} CHECKS PASSED')
    if failed: print('FAILED: '+'; '.join(failed),file=sys.stderr); return 1
    return 0
if __name__=='__main__':
    try: sys.exit(main())
    except Exception as e:
        print('FAIL-CLOSED: '+repr(e),file=sys.stderr); sys.exit(2)
