#!/usr/bin/env python3
"""Fail-closed static verifier for GQ5012BF1 yft_gpio_keys reconstruction."""
import hashlib, os, re, subprocess, sys, tempfile
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
STOCK=os.path.join(ROOT,'workspace/phase4-yft-gpio-keys/oracle/yft_gpio_keys.ko')
CANON=os.path.join(ROOT,'workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/yft_gpio_keys.ko')
RECON=os.path.join(ROOT,'workspace/phase4-yft-gpio-keys/yft_gpio_keys.rebuilt.ko')
SRC='/home/armol/kernel-work/gki-12901745-workspace/lieppos/yft-gpio-keys-recon/yft_gpio_keys.c'
DONOR='/home/armol/kernel-work/gki-12901745-workspace/common/drivers/input/keyboard/gpio_keys.c'
DTS=os.path.join(ROOT,'workspace/phase4-fingerprint/oracle/vendor_boot.entry0.dtb.dts')
LOG=os.path.join(ROOT,'workspace/phase4-yft-gpio-keys/recon-build-final.log')
RE='/usr/lib/llvm/23/bin/llvm-readelf'; OC='/usr/lib/llvm/23/bin/llvm-objcopy'
checks=[]
def ck(name,cond,detail=''):
 checks.append((name,bool(cond),detail));
def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
def out(*a): return subprocess.check_output(a,text=True,errors='replace')
def sections(p):
 b=open(p,'rb').read();d={}
 for l in out(RE,'-SW',p).splitlines():
  m=re.match(r'\s*\[\s*(\d+)\]\s+(\S+)\s+\S+\s+\S+\s+(\S+)\s+(\S+)',l)
  if m:d[int(m[1])]=(m[2],int(m[3],16),int(m[4],16))
 return b,d
def parse(p):
 b,ss=sections(p);f={};o={};u=set()
 for l in out(RE,'-sW',p).splitlines():
  m=re.match(r'\s*\d+:\s+([0-9a-f]+)\s+(\d+)\s+(\S+)\s+(\S+)\s+\S+\s+(\S+)\s*(.*)',l)
  if not m:continue
  val,z,t,bind,ndx,n=int(m[1],16),int(m[2]),m[3],m[4],m[5],m[6].strip()
  if ndx=='UND' and n:u.add(n)
  if ndx.isdigit() and t in ('FUNC','OBJECT') and n:
   sn,fo,_=ss[int(ndx)];raw=b[fo+val:fo+val+z];q={'size':z,'sec':sn,'raw':raw,'hash':hashlib.sha256(raw).hexdigest(),'kcfi':b[fo+val-4:fo+val] if t=='FUNC' and val>=4 else b''}
   (f if t=='FUNC' else o)[n]=q
 raw=b''
 for sn,fo,z in ss.values():
  if sn=='__versions':raw=b[fo:fo+z]
 v={}
 for i in range(0,len(raw),64):v[raw[i+8:i+64].split(b'\0')[0].decode()]=int.from_bytes(raw[i:i+8],'little')
 secraw={sn:b[fo:fo+z] for sn,fo,z in ss.values()}
 return f,o,u,v,secraw
SF,SO,SU,SV,SS=parse(STOCK);RF,RO,RU,RV,RS=parse(RECON)
sm=out('modinfo',STOCK);rm=out('modinfo',RECON);src=open(SRC).read();donor=open(DONOR).read();dts=open(DTS).read();log=open(LOG,errors='replace').read()
ck('frozen stock SHA',sha(STOCK)=='53c2957db5a2866d27f8dda5910ba2ddda0200ab36fa50b7a97bb87436897cec')
ck('canonical stock SHA',sha(CANON)==sha(STOCK))
ck('stock size',os.path.getsize(STOCK)==37136)
ck('reconstruction source SHA',sha(SRC)=='b9b81dac6a81b0b9e23cac0a41f3d4d6e04855036d00c84d0cb1e138e38aaa41')
ck('pinned donor SHA',sha(DONOR)=='22b787ef4dcd0bfb1fa3b5c693baf793da69642f604b0d1f82188e1b2bfd4b79')
ck('stock function count',len(SF)==23)
ck('rebuild function count',len(RF)==23)
ck('function set exact',set(SF)==set(RF))
ck('function sizes exact',all(SF[n]['size']==RF[n]['size'] for n in SF))
ck('KCFI set exact',all(SF[n]['kcfi']==RF[n]['kcfi'] for n in SF))
ck('function bytes exact',all(SF[n]['raw']==RF[n]['raw'] for n in SF))
ck('text/init/exit exact',all(SS[x]==RS[x] for x in ['.text','.init.text','.exit.text']))
ck('stock import ABI count',len(SV)==65 and len(SU)==64)
ck('rebuild import ABI count',len(RV)==65 and len(RU)==64)
ck('undefined import set exact',SU==RU)
ck('MODVERSION map exact',SV==RV)
ck('no exports',not any(x.startswith('__ksymtab') for x in SS))
ck('module name exact','name:           yft_gpio_keys' in sm and 'name:           yft_gpio_keys' in rm)
ck('module aliases exact',all(x in rm for x in ['alias:          platform:gpio-keys','alias:          of:N*T*Cyft-gpio-keys','alias:          of:N*T*Cyft-gpio-keysC*']))
ck('driver and OF identity','name\t= "yft-gpio-keys"' in src and 'compatible = "yft-gpio-keys"' in src)
ck('exact DT parent/path',re.search(r'(?m)^\s*yft-gpio-keys \{\s*\n\s*compatible = "yft-gpio-keys";',dts) is not None)
ck('exact two-button set',dts.count('key-custom1 {')==1 and dts.count('key-custom2 {')==1)
ck('GPIO mapping',re.search(r'key-custom1 \{.*?gpios = <0x89 0x0d 0x01>;',dts,re.S) and re.search(r'key-custom2 \{.*?gpios = <0x89 0x08 0x01>;',dts,re.S))
ck('F1/F2 keycodes',re.search(r'key-custom1 \{.*?linux,code = <0x3b>;',dts,re.S) and re.search(r'key-custom2 \{.*?linux,code = <0x3c>;',dts,re.S))
ck('active-low polarity',dts.count('gpios = <0x89 0x0d 0x01>;')==1 and dts.count('gpios = <0x89 0x08 0x01>;')==1)
ck('DT debounce and implementation',dts.count('debounce-interval = <0x10>;')==2 and 'button->debounce_interval = 16;' in src and 'gpiod_set_debounce' in src and 'msecs_to_jiffies' in src)
ck('IRQ trigger/flags','IRQF_TRIGGER_RISING | IRQF_TRIGGER_FALLING' in src and 'irqflags |= IRQF_SHARED' in src)
ck('YFT IRQ mask/re-enable','disable_irq_nosync(irq);' in src and 'enable_irq(bdata->irq);' in src)
ck('YFT edge rearm','irq_set_irq_type(bdata->irq, IRQ_TYPE_EDGE_RISING);' in src and 'irq_set_irq_type(bdata->irq, IRQ_TYPE_EDGE_FALLING);' in src)
ck('wakeup DT and PM',re.search(r'key-custom1 \{.*?wakeup-source;',dts,re.S) is not None and re.search(r'key-custom2 \{.*?wakeup-source;',dts,re.S) is not None and 'device_init_wakeup(dev, wakeup);' in src and 'enable_irq_wake' in src and 'disable_irq_wake' in src)
ck('suspend/resume callbacks','SIMPLE_DEV_PM_OPS(gpio_keys_pm_ops, gpio_keys_suspend, gpio_keys_resume);' in src)
ck('input device ABI',all(x in src for x in ['input->phys = "gpio-keys/input0"','input->id.bustype = BUS_HOST','input->id.vendor = 0x0001','input->id.product = 0x0001','input->id.version = 0x0100']))
ck('event reporting','input_event(input, type, *bdata->code, state);' in src and 'input_sync(bdata->input);' in src)
ck('exact YFT diagnostic strings',all(x in src for x in ['[%s]  button=%s,state=%d\\n','%s: key %s. \\n','"pressed"','"released"']))
ck('lifecycle',all(x in src for x in ['platform_driver_register(&gpio_keys_device_driver)','platform_driver_unregister(&gpio_keys_device_driver)','shutdown\t= gpio_keys_shutdown']))
ck('important data/rodata exact',all(SS[x]==RS[x] for x in ['.data','.rodata','.rodata.str1.1','__versions']))
ck('clean final build','Build completed successfully' in log and 'Build completed successfully, 9 total actions' in log)
compiler=[l for l in log.splitlines() if re.search(r'\bwarning:',l,re.I) and 'SSL error' not in l]
modpost=[l for l in log.splitlines() if 'modpost' in l.lower() and 'warning' in l.lower()]
unres=[l for l in log.splitlines() if re.search(r'undefined!|undefined symbol|unresolved symbol',l,re.I)]
ck('compiler warnings zero',len(compiler)==0)
ck('modpost warnings zero',len(modpost)==0)
ck('unresolved symbols zero',len(unres)==0)
failed=[x for x in checks if not x[1]]
for n,ok,d in checks:print(('PASS' if ok else 'FAIL')+'\t'+n+(('\t'+d) if d else ''))
print(f'{len(checks)-len(failed)}/{len(checks)} CHECKS PASSED')
sys.exit(1 if failed else 0)
