#!/usr/bin/env python3
"""Test thermal ADC acceptance on private rebuilt operands only.
Usage: thermal-btf-mutation-test.py RECIPE BUILD_DIR STOCK_DIR REPORT_JSON
The stock tree is read-only. Only the rebuilt module is copied and mutated.
"""
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

recipe, build, stock, report = map(lambda s: Path(s).resolve(), sys.argv[1:])
sys.path.insert(0, str(recipe / 'scripts'))
from normalize import kpp, normalized

module = 'thermal-generic-adc'
source = build / (module + '.stripped')
k = kpp.KO(source)
bt = k.sec('.BTF')
assert bt and bt['size'] > 24
hl, = struct.unpack_from('<I', k.b, bt['off'] + 4)
toff, = struct.unpack_from('<I', k.b, bt['off'] + 8)
soff, = struct.unpack_from('<I', k.b, bt['off'] + 16)
first = bt['off'] + hl + toff
_, build_id, build_id_size = normalized(k)
assert build_id_size == 20

def at(section, relative=0):
    s = k.sec(section)
    assert s and s['size'] > relative, (section, relative)
    return s['off'] + relative

cases = {
    'function_text': at('.text', 16),
    'rodata': at('.rodata.str1.1'),
    'data': at('.data'),
    'import_crc': at('__versions'),
    'modinfo': at('.modinfo'),
    'relocation_addend': at('.rela.text', 16),
    'btf_header': bt['off'],
    'btf_name_offset_reference': first,
    'btf_type_id_reference': first + 8,
    'btf_string_table': bt['off'] + hl + soff + 1,
    'build_id': build_id,
}
env = dict(os.environ, LIEPPOS_VERIFY_JOINT='1',
           LIEPPOS_VERIFY_MODULE=module, PYTHONDONTWRITEBYTECODE='1')
results = []
with tempfile.TemporaryDirectory(prefix='thermal-btf-mut-') as tmp:
    dest = Path(tmp) / source.name
    shutil.copyfile(source, dest)
    command = [sys.executable, str(recipe / 'scripts/verify.py'), tmp, str(stock)]
    baseline = subprocess.run(command, env=env, capture_output=True, text=True)
    assert baseline.returncode == 0, baseline.stderr
    for axis, offset in cases.items():
        b = bytearray(source.read_bytes())
        b[offset] ^= 1
        dest.write_bytes(b)
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        expected_pass = axis == 'build_id'
        ok = (result.returncode == 0) == expected_pass
        results.append(dict(module=module, axis=axis, offset=offset,
                            expected='PASS' if expected_pass else 'REJECT',
                            verify_exit=result.returncode, result='OK' if ok else 'FAIL'))
        print(axis, result.returncode, 'OK' if ok else 'FAIL')
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(json.dumps(dict(baseline_exit=baseline.returncode,
    cases=results, all_detected=all(r['result'] == 'OK' for r in results)), indent=2) + '\n')
assert all(r['result'] == 'OK' for r in results), 'mutation not detected'
print(f'{len(results)} cases passed; only GNU build-ID normalization allowed')
