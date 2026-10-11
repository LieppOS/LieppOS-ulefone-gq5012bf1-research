#!/usr/bin/env python3
"""Private-copy CMDQ ELF mutation tests; no writes to stock or build operands.
Usage: cmdq-mutation-test.py RECIPE BUILD_DIR STOCK_DIR REPORT_JSON
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
recipe, build, stock, report = map(lambda s: Path(s).resolve(), sys.argv[1:])
sys.path.insert(0, str(recipe/'scripts'))
from normalize import kpp, normalized
modules = ['cmdq-platform-mt6878', 'cmdq-sec-drv', 'cmdq-test', 'mtk-cmdq-drv-ext']
results, absent = [], []
for m in modules:
    source = build/(m+'.stripped')
    k = kpp.KO(source)
    def at(section, relative=0):
        s = k.sec(section)
        return s['off'] + relative if s and s['size'] > relative else None
    _, bid, length = normalized(k)
    assert length == 20
    targets = dict(function_text=at('.text',16), data=at('.data'),
                   rodata=at('.rodata') or at('.rodata.str1.1'), import_crc=at('__versions'),
                   modinfo=at('.modinfo'), relocation_addend=at('.rela.text',16),
                   symbol_table=at('.symtab',24), symbol_name=at('.strtab',1), build_id=bid)
    crc = next((s for s in k.secs if 'kcrctab' in s['n'] and s['size']), None)
    targets['export_crc'] = crc['off'] if crc else None
    symtab = next(s for s in k.secs if s['type'] == 2)
    kcfi = next((i for i,s in enumerate(k.syms) if s['n'].startswith('__kcfi_typeid_')), None)
    targets['kcfi_absolute_id'] = symtab['off'] + kcfi*24 + 8 if kcfi is not None else None
    env = dict(os.environ, LIEPPOS_VERIFY_JOINT='1', LIEPPOS_VERIFY_MODULE=m,
               PYTHONDONTWRITEBYTECODE='1')
    with tempfile.TemporaryDirectory(prefix='cmdq-mut-') as tmp:
        dest = Path(tmp)/source.name
        shutil.copyfile(source, dest)
        command = [sys.executable, str(recipe/'scripts/verify.py'), tmp, str(stock)]
        baseline = subprocess.run(command, env=env, capture_output=True, text=True)
        assert baseline.returncode == 0, baseline.stderr
        for axis, offset in targets.items():
            if offset is None:
                absent.append(dict(module=m, axis=axis))
                continue
            b = bytearray(source.read_bytes()); b[offset] ^= 1; dest.write_bytes(b)
            r = subprocess.run(command, env=env, capture_output=True, text=True)
            ok = (r.returncode == 0) == (axis == 'build_id')
            results.append(dict(module=m, axis=axis, offset=offset, verify_exit=r.returncode,
                                expected='PASS' if axis == 'build_id' else 'REJECT',
                                result='OK' if ok else 'FAIL'))
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(json.dumps(dict(cases=results, absent_axes=absent,
    all_detected=all(x['result']=='OK' for x in results)), indent=2)+'\n')
assert all(x['result']=='OK' for x in results)
print(len(results), 'cases passed; absent axes:', absent)
