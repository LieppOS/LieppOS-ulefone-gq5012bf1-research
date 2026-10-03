#!/usr/bin/env python3
"""List MediaTek MKIMG (0x58881688) sub-images in a partition image: name, offset, size, sha256."""
import sys,struct,hashlib
d=open(sys.argv[1],'rb').read(); off=0
while off+512<=len(d):
    magic,size=struct.unpack_from('<II',d,off)
    if magic!=0x58881688: break
    name=d[off+8:off+40].split(b'\0')[0].decode(errors='replace')
    hsz=struct.unpack_from('<I',d,off+0x34)[0] if struct.unpack_from('<I',d,off+0x30)[0]==0x58891689 else 512
    body=d[off+hsz:off+hsz+size]
    ver=b''
    import re
    m=re.search(rb't-neptune[\x20-\x7e]{10,120}',body)
    print(f"{name}\toffset=0x{off:x}\thdr={hsz}\tsize={size}\tsha256={hashlib.sha256(body).hexdigest()}\t{(m.group(0).decode() if m else '')}")
    off+=hsz+size
    off=(off+15)&~15
    # align: images are aligned to 16 bytes
