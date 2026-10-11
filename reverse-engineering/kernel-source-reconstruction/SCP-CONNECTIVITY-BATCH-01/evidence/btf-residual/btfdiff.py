#!/usr/bin/env python3
"""Classify split-BTF differences between a stock and a rebuilt module (diagnostic only).

Parses both .BTF sections, walks every type record, and for every type-reference field
records (stock_id, rebuilt_id). Reports whether module-local records/strings are identical
and whether the differences are confined to references into the vmlinux base.
Usage: btfdiff.py <stock.ko> <rebuilt.ko> <base-vmlinux>
"""
import sys, struct, subprocess, collections, json

def section(path, name):
    out = subprocess.run(['llvm-objcopy', '--dump-section', f'{name}=/dev/stdout', path], capture_output=True, check=True).stdout
    return out

def parse(b):
    magic, ver, flags, hlen, toff, tlen, soff, slen = struct.unpack_from('<HBBIIIII', b, 0)
    assert magic == 0xeb9f
    t = b[hlen + toff: hlen + toff + tlen]; s = b[hlen + soff: hlen + soff + slen]
    recs = []; i = 0
    while i < len(t):
        name, info, sz = struct.unpack_from('<III', t, i)
        kind = (info >> 24) & 0x1f; vlen = info & 0xffff
        refs = []; start = i; i += 12
        if kind in (2, 7, 8, 9, 10, 11, 12, 18):  # ptr fwd? typedef volatile const restrict func type_tag: 'type' field
            if kind != 7: refs.append(start + 8)
        if kind == 1: i += 4                       # int
        elif kind == 3:                            # array: type, index_type, nelems
            refs += [i, i + 4]; i += 12
        elif kind in (4, 5):                       # struct/union members: name, type, offset
            for k in range(vlen): refs.append(i + 4); i += 12
        elif kind == 6: i += 8 * vlen              # enum
        elif kind == 13:                           # func_proto params: name, type
            refs.append(start + 8)
            for k in range(vlen): refs.append(i + 4); i += 8
        elif kind == 14: refs.append(start + 8); i += 4   # var
        elif kind == 15:                           # datasec: type, offset, size
            for k in range(vlen): refs.append(i); i += 12
        elif kind == 16: pass                      # float
        elif kind == 17: refs.append(start + 8); i += 4   # decl_tag
        elif kind == 19: i += 12 * vlen            # enum64
        recs.append((start, i, kind, name, refs))
    return dict(hdr=(ver, flags, hlen, toff, tlen, soff, slen), t=t, s=s, recs=recs)

def base_count(vmlinux):
    b = section(vmlinux, '.BTF'); p = parse(b); return len(p['recs']), p

A = parse(section(sys.argv[1], '.BTF')); B = parse(section(sys.argv[2], '.BTF'))
nbase, base = base_count(sys.argv[3])
res = dict(header_equal=A['hdr'] == B['hdr'], strings_equal=A['s'] == B['s'], records=(len(A['recs']), len(B['recs'])), public_base_types=nbase)
pairs = collections.Counter(); other = 0; kinds_equal = True
for ra, rb in zip(A['recs'], B['recs']):
    if (ra[0], ra[1], ra[2], ra[3]) != (rb[0], rb[1], rb[2], rb[3]): kinds_equal = False
    refset = set(ra[4])
    for off in range(ra[0], ra[1], 4):
        va, = struct.unpack_from('<I', A['t'], off); vb, = struct.unpack_from('<I', B['t'], off)
        if va == vb: continue
        if off in refset: pairs[(va, vb)] += 1
        else: other += 1
res['record_layout_names_kinds_equal'] = kinds_equal
res['non_reference_word_differences'] = other
res['differing_reference_fields'] = sum(pairs.values())
res['distinct_reference_pairs'] = len(pairs)
loc = [p for p in pairs if p[0] > nbase or p[1] > nbase]
res['pairs_touching_module_local_ids'] = len(loc)
fa = collections.defaultdict(set); fb = collections.defaultdict(set)
for a, b in pairs: fa[a].add(b); fb[b].add(a)
res['stock_to_public_mapping_is_function'] = all(len(v) == 1 for v in fa.values())
res['public_to_stock_mapping_is_function'] = all(len(v) == 1 for v in fb.values())
deltas = collections.Counter(a - b for a, b in pairs)
res['top_id_deltas'] = deltas.most_common(8)
res['stock_max_ref'] = max((struct.unpack_from('<I', A['t'], o)[0] for r in A['recs'] for o in r[4]), default=0)
res['public_max_ref'] = max((struct.unpack_from('<I', B['t'], o)[0] for r in B['recs'] for o in r[4]), default=0)
print(json.dumps(res, indent=1))
