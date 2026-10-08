#!/usr/bin/env python3
"""Relocate copied camera Markdown links after the established DONE-pack sync.

Usage: relocate-pack-links.py RESEARCH_DIR [--check]
Top-level research documents are copied into notes/ by the promotion utilities.
Only copied camera documents and their current manifest hashes are adapted.
Generated indexes/provenance and all other components are left untouched.
"""
import argparse
import csv
import hashlib
import os
from pathlib import Path
import re
from urllib.parse import unquote

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('research_dir', type=Path)
parser.add_argument('--check', action='store_true', help='check without writing')
args = parser.parse_args()
research = args.research_dir.resolve()
assert research.name == 'CAMERA-ISP-KERNEL', research
repo = research.parents[2]
workspace = repo.parent
pack = workspace / 'Reverse Engineer - DONE/CAMERA-ISP-KERNEL'
assert pack.is_dir(), pack
manifest = workspace / 'COPY-MANIFEST.tsv'
with manifest.open(newline='') as f:
    reader = csv.DictReader(f, delimiter='\t')
    fields, rows = reader.fieldnames, list(reader)
generated = {'evidence/EVIDENCE-INDEX.md', 'notes/PROVENANCE.md',
             'notes/CLASSIFICATION-CHANGE.md'}
pairs = []
for row in rows:
    if row['component'] != research.name or row['artifact_origin'] != 'research-derived':
        continue
    src = Path(row['original_path'])
    dst = workspace / row['local_path']
    if src.is_relative_to(research) and src.is_file():
        assert dst.is_relative_to(pack), dst
        relative = src.relative_to(research)
        expected = (str(relative) if len(relative.parts) > 1 else
                    {'README.md': 'README.md', 'SOURCE.md': 'SOURCE.md',
                     'STATUS.md': 'notes/research-STATUS.md',
                     'stale-claims.md': 'notes/stale-claims.md'}.get(src.name, 'notes/' + src.name))
        # Historical root-level copies retain their old source hashes/provenance.
        # They are not the documents copied by the current synchronization mapping.
        if str(dst.relative_to(pack)) == expected:
            pairs.append((src, dst, row))
# Prefer sync-done-pack.py's root SOURCE.md over the older promoted notes/SOURCE.md.
mapping = {src.resolve(): dst for src, dst, row in pairs}
if (pack / 'SOURCE.md').exists():
    mapping[(research / 'SOURCE.md').resolve()] = pack / 'SOURCE.md'
changes = []
pending = []
errors = []
for src, dst, row in pairs:
    if src.suffix != '.md' or str(dst.relative_to(pack)) in generated:
        continue
    content = src.read_bytes()
    assert hashlib.sha256(content).hexdigest() == row['original_sha256'], src

    def relocate(match):
        target = match.group(1)
        if target.startswith(('http:', 'https:', 'mailto:', '#')):
            return match.group(0)
        path, sep, anchor = target.partition('#')
        operand = (src.parent / unquote(path.strip('<>'))).resolve()
        destination = mapping.get(operand, operand)
        if not destination.exists():
            errors.append(f'{src}: {target}')
        relative = os.path.relpath(destination, dst.parent)
        if ' ' in relative:
            relative = '<' + relative + '>'
        return '](' + relative + (sep + anchor if sep else '') + ')'

    adapted = re.sub(r'\]\(([^)]+)\)', relocate, content.decode()).encode()
    if dst.read_bytes() != adapted:
        changes.append(str(dst.relative_to(pack)))
        pending.append((dst, row, adapted))
assert not errors, errors
if not args.check and changes:
    for dst, row, adapted in pending:
        dst.write_bytes(adapted)
        row['current_sha256'] = hashlib.sha256(adapted).hexdigest()
        row['bytes'] = str(len(adapted))
        if '; Markdown links relocated for pack layout' not in row['kind_or_provenance']:
            row['kind_or_provenance'] += '; Markdown links relocated for pack layout'
    with manifest.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
print(f'CAMERA-ISP-KERNEL: {len(changes)} link-adapted documents; generated files untouched')
if args.check:
    assert not changes, changes
