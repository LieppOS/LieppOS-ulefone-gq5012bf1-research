#!/usr/bin/env python3
"""Validate archived candidate blobs/type comparisons, not source acceptance.

No network, ELF mutation, build, or device operation. These diagnostics cannot
promote a C module. Publication origin is distinguished from matching OEM source.
"""
import hashlib
import json
from pathlib import Path
import re

P = Path(__file__).resolve().parents[1]
E = P / 'evidence/legacy-source-search'
N = E / 'newer-provider-search'


def definition(text, tag):
    match = re.search(r'\bstruct\s+' + re.escape(tag) + r'\s*\{', text)
    assert match, tag
    depth, index = 1, match.end()
    while depth:
        depth += (text[index] == '{') - (text[index] == '}')
        index += 1
    return text[match.start():index + 1]


def main():
    baseline = json.loads((E / 'zte-tkcore-manifest.json').read_text())
    baseline_blobs = {f['path']: f['git_blob'] for f in baseline['files']}
    candidates = json.loads((N / 'candidate-comparisons.json').read_text())
    expected = {
        'Y21s': 'c6f6fa957459b2b5d435c816113f1743bb6f4549',
        'V23_5G': 'caadc867e01508e6b5ccf1905e6b65122d85a3e0',
    }
    assert len(candidates) == len(expected)
    tags = ['tee', 'tee_context', 'tee_session', 'tee_shm_dma_buf',
            'tee_shm_resv', 'tee_shm_ns', 'tee_shm', 'tee_data', 'tee_cmd', 'tee_ops']
    comparisons = json.loads((N / 'struct-block-comparison.json').read_text())
    assert [x['tag'] for x in comparisons] == tags
    original = (E / 'zte-tkcore/include/linux/tee_core.h').read_text()
    recovered = 0
    for candidate in candidates:
        name = candidate['repo'].split('/')[-1]
        assert candidate['commit'] == expected.pop(name)
        assert candidate['comparison_base'] == baseline['commit']
        assert candidate['version'] == r'3.2p8.4.14p2\n'
        rows = (N / (name + '-candidate-tree.txt')).read_text().splitlines()
        tree = {}
        for row in rows:
            meta, path = row.split('\t', 1)
            mode, kind, blob = meta.split()
            assert kind == 'blob' and path not in tree
            tree[path] = blob
        assert len(tree) == candidate['candidate_files'] == 52
        differences = {path for path, blob in tree.items()
                       if blob != baseline_blobs.get(path)}
        assert differences == {x['path'] for x in candidate['changed_vs_zte']}
        files = candidate['recovered_files']
        assert len(files) == len({x['path'] for x in files})
        assert differences.issubset({x['path'] for x in files})
        for item in files:
            data = (N / (name + '-source') / item['path']).read_bytes()
            assert hashlib.sha256(data).hexdigest() == item['sha256']
            blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            assert blob == item['git_blob'] == tree[item['path']]
            recovered += 1
        header = N / (name + '-source/drivers/misc/mediatek/tkcore/include/linux/tee_core.h')
        for item in comparisons:
            old = definition(original, item['tag'])
            new = definition(header.read_text(), item['tag'])
            assert old == new and item['identical']
            assert hashlib.sha256(old.encode()).hexdigest() == item['old_sha256'] == item['new_sha256']
    assert not expected
    for name, commit in [
        ('UMIDIGI-Official-F2', '3b998eaba611932b7cc2b451eb7eb3ab5d2fbf0b'),
        ('Hadenix-F2', 'e494bc66f92dfacf9494a7ac8a40c225cca87181'),
    ]:
        pin = json.loads((N / (name + '-pin.json')).read_text())
        scope = json.loads((N / (name + '-tree-scope.json')).read_text())
        assert pin['commit'] == commit and pin['candidate_files'] == 0
        assert not (N / (name + '-candidate-tree.txt')).read_text().strip()
        assert scope['tracked_blobs'] > 50000 and scope['archive_paths'] == []
    vendor = json.loads((N / 'Hadenix-GitLab-vendor-pin.json').read_text())
    assert vendor['commit'] == '84bf3f5e0b1fe0e35bf603d5aec284b11bfed92a'
    assert vendor['tracked_objects'] == 145500
    inventory = (N / 'Hadenix-GitLab-vendor-candidate-tree.txt').read_text().splitlines()
    assert len(inventory) == vendor['candidate_files'] == 173
    assert not any(line.split('\t', 1)[1].split('/')[-1] in
                   ['tee_core.h', 'tee_core_priv.h', 'tee_log.c', 'yft_devinfo.h', 'focaltech_fhp.c']
                   for line in inventory)
    debug = json.loads((N / 'stock-type-info-scope.json').read_text())['stock_modules']
    assert len(debug) == 8
    assert {Path(x['path']).name for x in debug} == {
        'tkcore.ko', 'tkcore_drv.ko', 'tmem_ffa.ko', 'microarray_fp_tee.ko'}
    assert all(x['debug_type_sections'] == [] for x in debug)
    print(f'VALID legacy search: {recovered} recovered blobs, two 3.2p8 trees, '
          'ten unchanged struct definitions, three other pinned tree scopes; '
          'no C-to-A inference')


if __name__ == '__main__':
    main()
