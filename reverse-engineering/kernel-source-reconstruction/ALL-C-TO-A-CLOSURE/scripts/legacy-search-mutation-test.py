#!/usr/bin/env python3
"""Exercise archived-search validation on temporary copies only.

Checks artifact integrity, not module parity. No stock binary or source checkout
is changed; each test has an independent copy of the archived diagnostic files.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parents[1]


def change_json(path, change):
    data = json.loads(path.read_text())
    change(data)
    path.write_text(json.dumps(data, indent=2) + '\n')


def main():
    cases = []
    with tempfile.TemporaryDirectory(prefix='allc-legacy-integrity-') as tmp:
        baseline = Path(tmp) / 'baseline'
        (baseline / 'scripts').mkdir(parents=True)
        shutil.copy2(P / 'scripts/validate-legacy-search.py', baseline / 'scripts/')
        shutil.copytree(P / 'evidence/legacy-source-search', baseline / 'evidence/legacy-source-search')

        def run(root):
            result = subprocess.run([sys.executable, str(root / 'scripts/validate-legacy-search.py')],
                                    capture_output=True, text=True,
                                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            return result

        control = run(baseline)
        assert control.returncode == 0, control.stderr
        for name in ['source_byte', 'candidate_pin', 'struct_verdict', 'debug_scope', 'tree_entry']:
            root = Path(tmp) / name
            shutil.copytree(baseline, root)
            data = root / 'evidence/legacy-source-search/newer-provider-search'
            if name == 'source_byte':
                path = data / 'Y21s-source/drivers/misc/mediatek/tkcore/include/linux/tee_core.h'
                path.write_bytes(path.read_bytes() + b'\n')
            elif name == 'candidate_pin':
                change_json(data / 'candidate-comparisons.json',
                            lambda rows: rows[0].update(commit='0' * 40))
            elif name == 'struct_verdict':
                change_json(data / 'struct-block-comparison.json',
                            lambda rows: rows[0].update(identical=False))
            elif name == 'debug_scope':
                change_json(data / 'stock-type-info-scope.json',
                            lambda obj: obj['stock_modules'][0].update(
                                debug_type_sections=[{'name': '.BTF', 'size': 1}]))
            else:
                path = data / 'Y21s-candidate-tree.txt'
                path.write_text('\n'.join(path.read_text().splitlines()[1:]) + '\n')
            result = run(root)
            assert result.returncode != 0 and 'AssertionError' in result.stderr, (name, result)
            cases.append({'name': name, 'exit': result.returncode, 'detected': True})
    record = {'scope': 'Archived diagnostic integrity only; not whole-module acceptance',
              'control_exit': control.returncode, 'cases': cases,
              'all_detected': all(case['detected'] for case in cases)}
    output = P / 'evidence/legacy-source-search/newer-provider-search/legacy-search-mutations.json'
    output.write_text(json.dumps(record, indent=2) + '\n')
    print(f'PASS legacy diagnostic integrity: {len(cases)}/{len(cases)} mutations detected; '
          'temporary copies only; no module acceptance claim')


if __name__ == '__main__':
    main()
