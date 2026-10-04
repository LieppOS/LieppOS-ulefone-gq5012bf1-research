#!/usr/bin/env python3
"""dtnode.py BASE NODE... : dump /proc/device-tree style nodes (from a read-only devicetree.tar capture)
with string/u32 decoding and phandle -> node-path resolution."""
import os, sys, struct
B = sys.argv[1]
ph = {}
for dp, dn, fn in os.walk(B):
    if 'phandle' in fn:
        v = open(os.path.join(dp, 'phandle'), 'rb').read()
        if len(v) == 4:
            ph[struct.unpack('>I', v)[0]] = os.path.relpath(dp, B)
def fmt(name, v):
    if not v:
        return '<true>'
    if all(32 <= c < 127 or c == 0 for c in v) and v.endswith(b'\0') and b'\0\0' not in v and v[0] != 0:
        return ' | '.join(x.decode() for x in v.rstrip(b'\0').split(b'\0'))
    if len(v) % 4 == 0:
        cells = struct.unpack('>%dI' % (len(v) // 4), v)
        s = ' '.join('0x%x' % c for c in cells)
        if name in ('clocks', 'resets', 'phys', 'pinctrl-0', 'pinctrl-1', 'pinctrl-2', 'power-domains', 'interrupt-parent', 'iommus', 'nvmem-cells') or name.endswith('-supply') or name.endswith('-gpios') or name.endswith('-gpio') or name in ('cd-gpios',):
            s += '   [' + ', '.join(ph.get(c, '') for c in cells if c in ph) + ']'
        return s
    return v.hex()
for n in sys.argv[2:]:
    d = os.path.join(B, n)
    print('### ' + n)
    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        if os.path.isdir(p):
            print('  [%s/]' % f)
        else:
            print('  %s = %s' % (f, fmt(f, open(p, 'rb').read())))
