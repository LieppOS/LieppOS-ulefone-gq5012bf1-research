#!/usr/bin/env python3
"""FDT node/property reader retaining parent properties after nested child nodes.
Uses the audit decoder for values, but maintains a stack of node records.
"""
import struct

def walk(path, decode):
 b=open(path,'rb').read();magic,total,start,strings=struct.unpack_from('>4I',b)
 assert magic==0xd00dfeed
 p=start;stack=[];out=[]
 def string(off):
  end=b.index(b'\0',off);return b[off:end].decode(errors='replace'),end+1
 while p<total:
  tag,=struct.unpack_from('>I',b,p);p+=4
  if tag==9:break
  if tag==1:
   name,p=string(p);p=(p+3)&~3
   parent=stack[-1]['path'] if stack else '/'
   node=dict(path=(parent.rstrip('/')+'/'+name) or '/',name=name,parent=parent,props={})
   if not name and not stack:node['path']='/'
   stack.append(node);out.append(node)
  elif tag==2:stack.pop()
  elif tag==3:
   size,off=struct.unpack_from('>2I',b,p);p+=8;name,_=string(strings+off)
   stack[-1]['props'].setdefault(name,[]).extend(decode(name,b[p:p+size]));p+=size;p=(p+3)&~3
  elif tag==4:continue
  else:raise ValueError('bad FDT token '+str(tag))
 return out
