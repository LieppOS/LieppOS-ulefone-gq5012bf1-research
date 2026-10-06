import subprocess,re,sys,difflib,os,itertools
W='/home/armol/kernel-work/gki-12901745-workspace/lieppos/thermal-fm78100'; G='/home/armol/kernel-work/gki-12901745-workspace'
import shlex
FL=shlex.split(open(W+'/cc.flags').read())
ENV=dict(os.environ,PATH=G+'/prebuilts/clang/host/linux-x86/clang-r487747c/bin:'+os.environ['PATH'])
HDR0='''#include <linux/delay.h>
#include <linux/device.h>
#include <linux/gpio.h>
#include <linux/i2c.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/of_gpio.h>
#include <linux/platform_device.h>
#include <linux/slab.h>
int chip_id_unused;
'''
def dis(o,sym):
    out=subprocess.run(['llvm-objdump','-d','--no-show-raw-insn',o,'--disassemble-symbols='+sym],capture_output=True,text=True).stdout
    return [re.sub(r'<.*>','',re.sub(r'^\s*[0-9a-f]+:\s*','',l)).strip() for l in out.splitlines()[6:] if l.strip()]
def stock(sym): return dis(W+'/stock/yft_tiny2c_usb.ko',sym)
HDR=''
def compile(body,tag='t'):
    c=f'/tmp/t2c/fast_{tag}.c'; o=f'/tmp/t2c/fast_{tag}.o'
    open(c,'w').write(HDR+body)
    r=subprocess.run(['clang']+FL+['-c','-o',o,c],cwd=G+'/lieppos/camera-isp/kout',env=ENV,capture_output=True,text=True)
    if r.returncode: print(r.stderr[-1500:]); return None
    return o
def score(body,sym,tag='t',show=False):
    o=compile(body,tag)
    if not o: return 999
    A=stock(sym); B=dis(o,sym)
    d=[l for l in difflib.unified_diff(A,B,lineterm='',n=0) if l[:1] in '+-' and l[:3] not in('+++','---')]
    if show: print('\n'.join(d))
    return len(d)
