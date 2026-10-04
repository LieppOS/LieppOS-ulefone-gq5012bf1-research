#!/usr/bin/env python3
# symbytes.py KO SYMBOL -> hex bytes of a data/func symbol (section file contents)
import sys, subprocess, re
ko, sym = sys.argv[1], sys.argv[2]
sh = subprocess.run(['llvm-readelf', '-S', '-W', ko], capture_output=True, text=True).stdout
secs = {}
for m in re.finditer(r'\[\s*(\d+)\]\s+(\S+)\s+\S+\s+[0-9a-f]+\s+([0-9a-f]+)\s+([0-9a-f]+)', sh):
    secs[m.group(1)] = (m.group(2), int(m.group(3), 16), int(m.group(4), 16))
for l in subprocess.run(['llvm-readelf', '-s', '-W', ko], capture_output=True, text=True).stdout.splitlines():
    p = l.split()
    if len(p) >= 8 and p[7] == sym and p[6] in secs:
        name, off, size = secs[p[6]]
        v, sz = int(p[1], 16), int(p[2], 0)
        data = open(ko, 'rb').read()[off + v: off + v + sz]
        fmt = sys.argv[3] if len(sys.argv) > 3 else 'u32'
        if fmt == 'u32':
            import struct
            print(sym, name, sz, ' '.join(str(x) for x in struct.unpack('<%dI' % (sz // 4), data[:sz // 4 * 4])))
        else:
            print(sym, name, sz, data.hex())
        break
