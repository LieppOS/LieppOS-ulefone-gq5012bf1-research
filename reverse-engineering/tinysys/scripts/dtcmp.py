#!/usr/bin/env python3
"""dtcmp.py DTS DEVICETREE_TAR : compare TinySys pin tables in the MTK reference mt6878.dts with the stock live DT."""
import re, struct, sys, tarfile
dts, tarp = sys.argv[1:3]
t = open(dts).read()
t = re.sub(r'/\*.*?\*/', '', t, flags=re.S); t = re.sub(r'//[^\n]*', '', t)
tf = tarfile.open(tarp); B = 'sys/firmware/devicetree/base/'
def live(node, p):
    try: return tf.extractfile(B + node + '/' + p).read()
    except KeyError: return None
for key, node, sc, rc in (('scp@1c400000', 'scp@1c400000', 3, 7), ('vcp@1ea00000', 'soc/vcp@1ea00000', 3, 4), ('gpueb@13c00000', 'soc/gpueb@13c00000', 3, 5)):
    i = t.find(key + ' {'); seg = t[i:i + 40000]
    for p, n in (('send-table', sc), ('recv-table', rc)):
        m = re.search(r'\n\s*' + re.escape(p) + r'\s*=\s*([^;]*);', seg)
        sv = [int(x, 0) for x in re.findall(r'0x[0-9a-fA-F]+|\d+', m.group(1))]
        lv = live(node, p); lv = list(struct.unpack('>%dI' % (len(lv) // 4), lv))
        S = [tuple(sv[k:k + n]) for k in range(0, len(sv), n)]; L = [tuple(lv[k:k + n]) for k in range(0, len(lv), n)]
        print('%s %s: reference %d entries, live %d entries, %s' % (key, p, len(S), len(L), 'IDENTICAL (same order)' if S == L else 'DIFFERENT'))
        if S != L:
            print('   only in reference:', sorted(set(S) - set(L))); print('   only in live     :', sorted(set(L) - set(S)))
            if set(S) == set(L): print('   same set, different order')
