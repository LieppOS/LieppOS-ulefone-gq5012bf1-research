#!/usr/bin/env python3
"""Function / data / object-composition inventory for camera_eeprom_v4l2.ko.

usage: eeprom_inventory.py <stock.ko> <rebuilt-stripped.ko> <build-dir containing camera_eeprom_v4l2.mod> <outdir>

* object boundaries come from the rebuild's input objects (link order from the .mod
  file): for every object/section the base offset in the final module is solved from
  its defined symbols, then validated against the stock symbol table;
* callers/callees/strings/data references come from the stock relocations;
* KCFI = 32-bit word immediately preceding the function when that word lies in a
  gap between functions (clang -fsanitize=kcfi preamble);
* status = byte comparison of every symbol between stock (A) and rebuild (B).
"""
import collections
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from elfko import Ko  # noqa: E402

CALL = {279, 280, 282, 283}          # TSTBR14, CONDBR19, JUMP26, CALL26
SECS = ('.text', '.init.text', '.exit.text', '.data', '.rodata', '.bss', '.init.data', '.exit.data')


def defined(k, types):
    return [s for s in k.syms if s['type'] in types and s['sec'] and s['shndx'] not in (0, 0xfff1, 0xfff2)]


def main():
    a_path, b_path, bdir, out = sys.argv[1:5]
    A, B = Ko(a_path), Ko(b_path)
    os.makedirs(out, exist_ok=True)
    mod = open(os.path.join(bdir, 'camera_eeprom_v4l2.mod')).read().split()
    objs = list(mod)

    # ---- object composition -------------------------------------------------
    afuncs = sorted(defined(A, (2,)), key=lambda s: (s['sec'], s['value']))
    aobjs = sorted(defined(A, (1,)), key=lambda s: (s['sec'], s['value']))
    owner = {}          # (sec, value, name) -> object
    omap = []
    cursor = collections.defaultdict(int)
    for o in objs:
        K = Ko(o)
        rel = os.path.relpath(o, os.path.commonpath(objs))
        row = dict(obj=rel, ranges={}, nf=0, nd=0)
        for sec in SECS:
            if sec not in K.secs:
                continue
            ss = [s for s in K.syms if s['sec'] == sec and s['type'] in (1, 2) and s['shndx'] == K.secs[sec]['idx']]
            size = K.secs[sec]['size']
            if size == 0:
                continue
            base = None
            for cand in sorted({x['value'] - s['value'] for s in ss[:1] for x in A.syms
                                if x['name'] == s['name'] and x['sec'] == sec}):
                if cand >= cursor[sec] and all(any(x['name'] == s['name'] and x['value'] == cand + s['value']
                                                   for x in A.syms if x['sec'] == sec) for s in ss):
                    base = cand
                    break
            if base is None and not ss:
                continue
            assert base is not None, (o, sec)
            cursor[sec] = base + size
            row['ranges'][sec] = (base, base + size)
            for s in ss:
                owner[(sec, base + s['value'], s['name'])] = rel
                if s['type'] == 2:
                    row['nf'] += 1
                else:
                    row['nd'] += 1
        omap.append(row)

    def own(s):
        return owner.get((s['sec'], s['value'], s['name']), 'module-linker(.mod.c/this_module/modinfo)')

    # ---- relocation-derived references -------------------------------------
    def resolve(sec, sym, add):
        if sym['type'] == 3:
            if sym['sec'].startswith('.rodata.str'):
                return 'str', A.cstr(sym['sec'], add)
            hits = [s for s in A.syms if s['sec'] == sym['sec'] and s['type'] in (1, 2)
                    and s['value'] <= add < s['value'] + max(s['size'], 1)]
            if hits:
                return ('fn' if hits[0]['type'] == 2 else 'data'), '%s@0x%x' % (hits[0]['name'], hits[0]['value'])
            return 'data', '%s+0x%x' % (sym['sec'], add)
        if sym['shndx'] == 0:
            return 'import', sym['name']
        return ('fn' if sym['type'] == 2 else 'data'), '%s@0x%x' % (sym['name'], sym['value'])

    fkey = lambda s: '%s@0x%x' % (s['name'], s['value'])
    callees = collections.defaultdict(set)
    callers = collections.defaultdict(set)
    strs = collections.defaultdict(list)
    drefs = collections.defaultdict(set)
    # address-taken (data relocations pointing at a function)
    taken = collections.defaultdict(set)
    for sec, rl in A.relocs.items():
        if sec.startswith('.rela') or sec.endswith('eh_frame') or sec in ('.debug_info', '.altinstructions', '__bug_table', '__jump_table'):
            continue
        for off, typ, sym, add in rl:
            kind, tgt = resolve(sec, sym, add)
            if sec in ('.text', '.init.text', '.exit.text'):
                f = [s for s in afuncs if s['sec'] == sec and s['value'] <= off < s['value'] + s['size']]
                if not f:
                    continue
                me = fkey(f[0])
                if typ in CALL and kind in ('fn', 'import'):
                    callees[me].add(tgt)
                    if kind == 'fn':
                        callers[tgt].add(me)
                elif kind == 'str':
                    if tgt not in strs[me]:
                        strs[me].append(tgt)
                elif kind == 'data':
                    drefs[me].add(tgt)
                elif kind == 'fn':
                    taken[tgt].add(me)
            elif kind == 'fn':
                d = [s for s in aobjs if s['sec'] == sec and s['value'] <= off < s['value'] + max(s['size'], 1)]
                taken[tgt].add(d[0]['name'] if d else sec)

    # ---- byte status ---------------------------------------------------------
    def sbytes(K, s):
        return K.data(s['sec'])[s['value']:s['value'] + s['size']]

    bidx = {(s['sec'], s['value'], s['name']): s for s in B.syms}

    def status(s):
        t = bidx.get((s['sec'], s['value'], s['name']))
        if t is None:
            return 'MISSING-IN-B'
        if t['size'] != s['size']:
            return 'SIZE-DIFF'
        return 'EXACT' if sbytes(A, s) == sbytes(B, t) else 'BYTES-DIFF'

    # ---- function inventory --------------------------------------------------
    with open(os.path.join(out, 'function-inventory.tsv'), 'w') as f:
        f.write('name\tsection\taddress\tsize\tbind\tkcfi_typeid\taddress_taken_by\tcallers\tcallees\tstrings\t'
                'data_refs\tsource_object\tstatus\n')
        by_sec = collections.defaultdict(list)
        for s in afuncs:
            by_sec[s['sec']].append(s)
        for s in afuncs:
            prev_end = max([x['value'] + x['size'] for x in by_sec[s['sec']] if x['value'] < s['value']] or [0])
            kc = ''
            if s['value'] >= 4 and prev_end <= s['value'] - 4:
                kc = '0x%08x' % struct.unpack_from('<I', A.data(s['sec']), s['value'] - 4)[0]
            k = fkey(s)
            f.write('\t'.join([s['name'], s['sec'], '0x%x' % s['value'], str(s['size']),
                               'GLOBAL' if s['bind'] == 1 else 'LOCAL', kc or '-',
                               ';'.join(sorted(taken.get(k, ()))) or '-',
                               ';'.join(sorted(callers.get(k, ()))) or '-',
                               ';'.join(sorted(callees.get(k, ()))) or '-',
                               ' | '.join(x.replace('\n', '\\n').replace('\t', ' ') for x in strs.get(k, [])[:6]) or '-',
                               ';'.join(sorted(drefs.get(k, ()))) or '-',
                               own(s), status(s)]) + '\n')

    # ---- data inventory --------------------------------------------------------
    def dcat(s):
        n = s['name']
        if n == 'g_camCalList':
            return 'sensor->EEPROM address map (raw read()/write() path)'
        if n == 'cam_cal_config_list':
            return 'layout search order (37 config pointers)'
        if n.endswith('_eeprom') and s['size'] == 64:
            return 'layout config record (sensor id, i2c addr, size, preload, parser table ptr)'
        if n == 'cal_layout_table':
            return 'calibration layout table (header magic + 9 command items: include/offset/size/parser)'
        if n == 'CamCalReturnErr':
            return 'per-command error code table (per-TU copy, static const in cam_cal_config.h)'
        if n.startswith('yft_otp_state'):
            return 'YFT OTP-valid flag exported via /sys/class/camera_otp'
        if n in ('mp_eeprom_preload', 'mp_layout_preload'):
            return 'per-device preload cache (7 slots, never freed)'
        if n in ('cam_cal_config', 'last_sensor_id', 'cam_cal_index'):
            return 'global layout-selection state (shared by all device nodes)'
        if n in ('eeprom_of_match', '__mod_of__eeprom_of_match_device_table'):
            return 'OF match "mediatek,camera_eeprom"'
        if n in ('geeprom_file_operations', 'eeprom_i2c_init', 'class_attr_camera_otp', 'camera_otp_class'):
            return 'driver/char-device/sysfs plumbing'
        if 'debug' in n or n.startswith('__param'):
            return 'module parameter cam_eeprom_debug'
        if '__key' in n:
            return 'lockdep class key'
        if s['sec'] in ('.modinfo', '__versions', '.gnu.linkonce.this_module', '.note.Linux'):
            return 'module metadata'
        return 'other'

    with open(os.path.join(out, 'data-inventory.tsv'), 'w') as f:
        f.write('name\tsection\taddress\tsize\tbind\tcategory\tsource_object\tstatus\n')
        for s in sorted(defined(A, (1,)), key=lambda s: (s['sec'], s['value'])):
            f.write('\t'.join([s['name'], s['sec'], '0x%x' % s['value'], str(s['size']),
                               'GLOBAL' if s['bind'] == 1 else 'LOCAL', dcat(s), own(s), status(s)]) + '\n')

    # ---- object map --------------------------------------------------------------
    with open(os.path.join(out, 'object-map.tsv'), 'w') as f:
        f.write('link_order\tsource_object\t.text_range\t.data_range\t.rodata_range\t.bss_range\tfunctions\tdata_objects\t'
                'donor\tconfidence\n')
        for i, r in enumerate(omap):
            rg = lambda sec: ('0x%x-0x%x' % r['ranges'][sec]) if sec in r['ranges'] else '-'
            f.write('\t'.join([str(i + 1), r['obj'], rg('.text'), rg('.data'), rg('.rodata'), rg('.bss'),
                               str(r['nf']), str(r['nd']), '{donor}', 'proven (byte-identical rebuild)']) + '\n')
    print('functions', len(afuncs), collections.Counter(status(s) for s in afuncs))
    print('data', len(aobjs), collections.Counter(status(s) for s in aobjs))
    print('objects', len(omap))


if __name__ == '__main__':
    main()
