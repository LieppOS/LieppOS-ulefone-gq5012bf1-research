#!/usr/bin/env python3
"""Offline FDT/property helpers, derived from accepted REGULATORS map-power.py.
Never interprets an arbitrary integer as a phandle: callers supply typed property rules.
"""
import struct,tarfile,csv,sys,re,shlex,subprocess
sys.dont_write_bytecode=True
from pathlib import Path
def cells(b):
 assert len(b)%4==0
 return list(struct.unpack('>'+str(len(b)//4)+'I',b))
def strings(b):return b.rstrip(b'\0').decode(errors='replace').split('\0') if b else []
def decode(b):
 if not b:return True
 if b[0]!=0 and b.endswith(b'\0') and all(c==0 or 32<=c<127 for c in b):return strings(b)
 return [hex(x) for x in cells(b)] if len(b)%4==0 else b.hex()
def fdt(path):
 b=Path(path).read_bytes();h=struct.unpack_from('>10I',b);assert h[0]==0xd00dfeed;i=h[2];st=b[h[3]:h[3]+h[8]];stack=[];out={}
 while True:
  tag,=struct.unpack_from('>I',b,i);i+=4
  if tag==1:
   e=b.index(0,i);name=b[i:e].decode();i=(e+4)&~3;stack.append(name);out['/'+'/'.join(stack[1:])]={}
  elif tag==2:stack.pop()
  elif tag==3:
   n,k=struct.unpack_from('>II',b,i);i+=8;name=st[k:st.index(0,k)].decode();out['/'+'/'.join(stack[1:])][name]=b[i:i+n];i=(i+n+3)&~3
  elif tag==4:continue
  elif tag==9:break
  else:raise ValueError(tag)
 return out
def live(path):
 out={};prefix='sys/firmware/devicetree/base'
 with tarfile.open(path) as tf:
  for m in tf:
   n=m.name.lstrip('./')
   if not n.startswith(prefix) or not m.isfile():continue
   p,_,key=n[len(prefix):].rpartition('/');out.setdefault(p or '/',{})[key]=tf.extractfile(m).read()
 return out
def status(nodes,p):
 while True:
  v=strings(nodes.get(p,{}).get('status',b'okay'))
  if v and v[0] not in ['okay','ok']:return v[0]+'@'+p
  if p=='/':return 'okay'
  p=p.rpartition('/')[0] or '/'
def tab(p,head,rows):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(head);w.writerows(rows)
def block(s,start):
 i=s.index('{',start);depth=0
 for j in range(i,len(s)):
  if s[j]=='{':depth+=1
  elif s[j]=='}':
   depth-=1
   if depth==0:return s[i+1:j]
 raise ValueError('unclosed block')
def split_top(s):
 parts=[];depth=0;quote=False;start=0
 for i,c in enumerate(s):
  if c=='"' and (i==0 or s[i-1]!='\\'):quote=not quote
  if quote:continue
  if c in '({[':depth+=1
  elif c in ')}]':depth-=1
  elif c==',' and depth==0:parts.append(s[start:i].strip());start=i+1
 if s[start:].strip():parts.append(s[start:].strip())
 return parts
def number(s):
 if s.strip() in ['false','true']:return int(s.strip()=='true')
 s=re.sub(r'(?<=[0-9a-fA-F])[uUlL]+\b','',s.strip())
 if re.fullmatch(r'[0-9a-fA-FxX()+*/<>|&~ \t\n-]+',s):return int(eval(s,{'__builtins__':{}},{}))
 return s
def export_values(ko):
 """Authoritative CRC symbol offsets, never positional ksymtab/function pairing."""
 out={}
 for y in ko.syms:
  if not y['n'].startswith('__crc_') or not 0<y['shndx']<len(ko.secs):continue
  sec=ko.secs[y['shndx']]
  if 'kcrctab' not in sec['n']:continue
  out[y['n'][6:]]=('EXPORT_SYMBOL_GPL' if '_gpl' in sec['n'] else 'EXPORT_SYMBOL',struct.unpack_from('<I',ko.b,sec['off']+y['val'])[0])
 assert len(out)*4==sum(s['size'] for s in ko.secs if 'kcrctab' in s['n'])
 return out

def clang_command(W,mod):
 T=W/'src/kdm';line=(T/f'drivers/interconnect/mediatek/.{mod}.o.cmd').read_text().splitlines()[0].split(':=',1)[1];args=shlex.split(line);args[0]=str(W/'prebuilts/clang/host/linux-x86/clang-r487747c/bin/clang');out=[];i=0
 while i<len(args):
  if args[i]=='-o':i+=2;continue
  if args[i]=='-c' or args[i].startswith('-Wp,-MMD,'):i+=1;continue
  out.append(args[i]);i+=1
 return out
