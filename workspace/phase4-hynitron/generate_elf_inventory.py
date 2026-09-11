#!/usr/bin/env python3
"""Deterministic static inventory for the frozen GQ5012BF1 hynitron ELF."""
import csv, hashlib, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ELF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'workspace/phase4-hynitron/oracle/hynitron.stock.ko')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'kernel')
PREFIX = sys.argv[3] if len(sys.argv) > 3 else 'phase4-hynitron'
os.makedirs(OUT, exist_ok=True)
READELF = '/usr/lib/llvm/23/bin/llvm-readelf'
OBJCOPY = '/usr/lib/llvm/23/bin/llvm-objcopy'


def run(*args):
    return subprocess.check_output(args, text=True, errors='replace')


def tsv(name, header, rows):
    name = name.replace('phase4-hynitron', PREFIX, 1)
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(header)
        w.writerows(rows)

sec_out = run(READELF, '-SW', ELF)
sections = {}
for line in sec_out.splitlines():
    m = re.match(r'\s*\[\s*(\d+)\]\s+(\S+)\s+', line)
    if m:
        sections[int(m.group(1))] = m.group(2)

sym_out = run(READELF, '-sW', ELF)
symbols = []
for line in sym_out.splitlines():
    m = re.match(r'\s*(\d+):\s+([0-9a-fA-F]+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*(.*)$', line)
    if not m:
        continue
    num, value, size, typ, bind, vis, ndx, name = m.groups()
    symbols.append(dict(num=int(num), value=int(value, 16), size=int(size), typ=typ,
                        bind=bind, vis=vis, ndx=ndx, name=name.strip()))

section_data = {}
for idx, name in sections.items():
    if not name or name == 'NULL':
        continue
    path = os.path.join('/tmp', 'hynitron-stock-' + re.sub(r'[^A-Za-z0-9_.-]', '_', name) + '.bin')
    r = subprocess.run([OBJCOPY, '--dump-section', name + '=' + path, ELF],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if r.returncode == 0 and os.path.exists(path):
        with open(path, 'rb') as f:
            section_data[name] = f.read()

func_rows = []
for s in symbols:
    if s['typ'] != 'FUNC' or s['ndx'] == 'UND' or not s['name']:
        continue
    sec = sections.get(int(s['ndx'])) if s['ndx'].isdigit() else s['ndx']
    data = section_data.get(sec, b'')
    code = data[s['value']:s['value'] + s['size']]
    kcfi_bytes = data[s['value'] - 4:s['value']] if s['value'] >= 4 else b''
    kcfi = '0x' + kcfi_bytes[::-1].hex() if len(kcfi_bytes) == 4 else 'UNKNOWN'
    func_rows.append([s['name'], sec, f'0x{s["value"]:x}', s['size'], s['bind'], kcfi,
                      hashlib.sha256(code).hexdigest()])
func_rows.sort(key=lambda r: (r[1], int(r[2], 16), r[0]))
tsv('phase4-hynitron-functions.tsv',
    ['function', 'section', 'offset', 'size', 'binding', 'kcfi_id', 'sha256'], func_rows)

obj_rows = []
for s in symbols:
    if s['typ'] != 'OBJECT' or s['ndx'] == 'UND' or not s['name']:
        continue
    sec = sections.get(int(s['ndx'])) if s['ndx'].isdigit() else s['ndx']
    data = section_data.get(sec, b'')
    blob = data[s['value']:s['value'] + s['size']]
    role = 'module object'
    n = s['name']
    if 'driver' in n: role = 'I2C driver object'
    elif 'match' in n or '_id' in n: role = 'OF/I2C match table'
    elif 'fw' in n.lower() or 'firmware' in n.lower(): role = 'firmware object/table'
    elif 'gesture' in n.lower(): role = 'gesture state'
    elif 'work' in n.lower() or 'timer' in n.lower(): role = 'async state'
    elif sec == '.bss': role = 'global/state BSS'
    obj_rows.append([n, sec, f'0x{s["value"]:x}', s['size'], s['bind'], role,
                     hashlib.sha256(blob).hexdigest()])
obj_rows.sort(key=lambda r: (r[1], int(r[2], 16), r[0]))
tsv('phase4-hynitron-objects.tsv',
    ['object', 'section', 'offset', 'size', 'binding', 'evidence_role', 'sha256'], obj_rows)

versions = section_data['__versions']
version_rows = []
for off in range(0, len(versions), 64):
    crc = int.from_bytes(versions[off:off + 8], 'little')
    name = versions[off + 8:off + 64].split(b'\0')[0].decode()
    version_rows.append([name, f'0x{crc:08x}', f'0x{off:x}'])
tsv('phase4-hynitron-modversions.tsv', ['symbol', 'crc', 'versions_offset'], version_rows)

undef = {s['name'] for s in symbols if s['ndx'] == 'UND' and s['name']}
intermodule = {'second_touch_fw_version', 'yft_touchpanel_device_add', 'yft_set_touch_device_used'}
import_rows = []
for name, crc, off in version_rows:
    provider = 'stock yft_devinfo' if name in intermodule else ('module loader ABI' if name == 'module_layout' else 'GKI kernel')
    import_rows.append([name, crc, 'yes' if name in undef else 'version-only', provider])
tsv('phase4-hynitron-imports.tsv',
    ['symbol', 'crc', 'elf_undefined_symbol', 'provider_class'], import_rows)

kcrc = section_data['__kcrctab']
export_names = ['tiny_tp_gesture_contorl', 'tiny_tp_power_contorl']
func_by_name = {r[0]: r for r in func_rows}
export_rows = []
for i, name in enumerate(export_names):
    crc = int.from_bytes(kcrc[i * 4:i * 4 + 4], 'little')
    f = func_by_name.get(name)
    export_rows.append([name, f'0x{crc:08x}', 'EXPORT_SYMBOL', f[5] if f else 'UNKNOWN',
                        f[3] if f else 'UNKNOWN'])
tsv('phase4-hynitron-exports.tsv',
    ['symbol', 'crc', 'export_class', 'kcfi_id', 'function_size'], export_rows)

rel_out = run(READELF, '-rW', ELF)
rel_rows, relsec = [], ''
for line in rel_out.splitlines():
    m = re.match(r"Relocation section '(\S+)'", line)
    if m:
        relsec = m.group(1)
        continue
    m = re.match(r'\s*([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+(R_\S+)\s+([0-9a-fA-F]+)\s+(\S+)(?:\s+([+-])\s+(\S+))?', line)
    if m:
        off, info, typ, sval, sym, sign, add = m.groups()
        rel_rows.append([relsec, '0x' + off, typ, sym, (sign or '') + (add or '0')])
tsv('phase4-hynitron-relocations.tsv',
    ['relocation_section', 'offset', 'type', 'symbol', 'addend'], rel_rows)

str_rows = []
for line in run('strings', '-a', '-t', 'x', ELF).splitlines():
    m = re.match(r'\s*([0-9a-fA-F]+)\s+(.*)$', line)
    if m:
        value = m.group(2).replace('\t', '\\t')
        trailing = len(value) - len(value.rstrip(' '))
        if trailing:
            value = value[:-trailing] + '\\x20' * trailing
        str_rows.append(['0x' + m.group(1), value])
tsv('phase4-hynitron-strings.tsv', ['file_offset', 'string'], str_rows)

print(f'functions={len(func_rows)} objects={len(obj_rows)} modversions={len(version_rows)} '
      f'undefined={len(undef)} exports={len(export_rows)} relocations={len(rel_rows)} strings={len(str_rows)}')
