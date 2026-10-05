#!/usr/bin/env python3
"""gen_inventory.py STOCKROOT OUT.tsv MOD... : static inventory of shipped TinySys messaging modules."""
import hashlib, os, re, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from elfmini import Elf
root, out, mods = sys.argv[1], sys.argv[2], sys.argv[3:]
places = ['partitions/vendor_dlkm/lib/modules', 'vendor-ramdisks/platform-extracted/lib/modules']
def modinfo(e):
    s = e.secbyname['.modinfo']; d = e.blob[s.off:s.off + s.size].split(b'\0')
    kv = {}
    for x in d:
        if b'=' in x:
            k, v = x.decode().split('=', 1); kv.setdefault(k, v)
    return kv
rows = []
for m in mods:
    paths = [os.path.join(p, m + '.ko') for p in places if os.path.exists(os.path.join(root, p, m + '.ko'))]
    f = os.path.join(root, paths[0]); b = open(f, 'rb').read(); e = Elf(f)
    shas = {hashlib.sha256(open(os.path.join(root, p), 'rb').read()).hexdigest() for p in paths}
    mi = modinfo(e)
    vs = e.secbyname.get('__versions'); nimp = vs.size // 64 if vs else 0
    exps = sorted(s.name[10:] for s in e.symbols if s.name.startswith('__ksymtab_') and s.shndx and s.name not in ('__ksymtab_gpl', '__ksymtab_strings') and s.type != 3)
    gpl = e.secbyname.get('__ksymtab_gpl')
    funcs = [s for s in e.symbols if s.type == 2 and s.shndx]
    data = [s for s in e.symbols if s.type == 1 and s.shndx and not s.name.startswith(('__UNIQUE_ID', '__crc_', '__kstrtab', '__ksymtab'))]
    und = [s for s in e.symbols if s.shndx == 0 and s.name]
    nrel = sum(len(v) for v in e.relocs.values())
    bid = e.secbyname.get('.note.gnu.build-id'); bidhex = b[bid.off + 16: bid.off + bid.size].hex() if bid else '-'
    # KCFI: functions whose preamble word (func-4) is a type id; count functions with a __cfi typeid preamble = all global/addr-taken
    srcs = sorted(set(x.decode() for x in re.findall(rb'\.\./kernel_device_modules-6\.1/[\w./-]+\.[ch]', b)))
    rows.append([m, ' + '.join(paths), ','.join(sorted(shas)), str(len(b)), mi.get('vermagic', '-'), mi.get('depends', '-') or '(none)',
                 mi.get('license', '-'), mi.get('description', '-'),
                 str(nimp), str(len(und)), str(len(exps)) + (' (GPL)' if gpl and gpl.size else ''), ','.join(exps),
                 str(len(funcs)), str(len(data)), str(len(e.sections)), str(nrel), bidhex, ';'.join(srcs) or '-'])
hdr = ['module', 'stock_paths', 'sha256', 'bytes', 'vermagic', 'depends', 'license', 'description', 'modversions_imports',
       'undefined_symbols', 'exports', 'export_names', 'functions', 'data_objects', 'sections', 'relocations', 'build_id', 'source_path_strings']
with open(out, 'w') as fo:
    fo.write('\t'.join(hdr) + '\n')
    for r in rows: fo.write('\t'.join(r) + '\n')
for r in rows: print(r[0], r[3], r[5], 'imp', r[8], 'exp', r[10], 'fn', r[12], 'data', r[13], 'sec', r[14], 'rel', r[15], r[17])
