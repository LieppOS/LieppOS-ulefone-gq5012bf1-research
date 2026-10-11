#!/usr/bin/env python3
"""Fail-closed restoration of signature-stripped system_dlkm analysis copies.

Dry-run by default.  With --apply it changes ONLY files under
TARGET_ROOT/workspace/gq5012bf1/stock/partitions/system_dlkm whose current bytes are
exactly the authenticated stock bytes minus their appended module signature.

Trust anchors (never modified, never rewritten to fit the files):
  * expected identity: the committed audit table ALL-457-MODULES.tsv, cross-checked
    against evidence/stock-identities.json and kernel/stock-module-master.csv in TARGET_ROOT;
  * source bytes: system_dlkm_a.img whose SHA-256 must equal IMAGE_SHA256 (recorded as
    "factory V15 exact" in research commit f037fed2, 2026-09-16, before either incident),
    extracted by this script into a fresh private directory.

Any destination that is neither intact nor exactly signature-stripped aborts the
whole run before a single write.
"""
import argparse, csv, hashlib, json, os, shutil, struct, subprocess, sys, tempfile, time
from pathlib import Path

IMAGE_SHA256 = '300f24c5550be110d0161583fa56d3c36ae61b8b2da4b44c128350c6e22b9f2a'
MAGIC = b'~Module signature appended~\n'
REL_ROOT = Path('workspace/gq5012bf1/stock/partitions/system_dlkm')
sha = lambda b: hashlib.sha256(b).hexdigest()

def unsigned_len(b):
    if not b.endswith(MAGIC):
        return None
    sig_len, = struct.unpack('>I', b[-len(MAGIC) - 4:-len(MAGIC)])
    id_type = b[-len(MAGIC) - 12 + 2]
    return len(b) - sig_len - 12 - len(MAGIC) if id_type == 2 else None

def die(msg):
    print('REFUSED:', msg, file=sys.stderr); sys.exit(2)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--target-root', type=Path, required=True)
    ap.add_argument('--image', type=Path, required=True)
    ap.add_argument('--fsck-erofs', type=Path, required=True)
    ap.add_argument('--quarantine', type=Path, required=True, help='new directory for damaged copies (must not exist)')
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    root = a.target_root.resolve(); dest_root = root / REL_ROOT
    if not dest_root.is_dir() or dest_root.is_symlink():
        die(f'{dest_root} is not a real directory')
    audit = root / 'reverse-engineering/kernel-source-parity-audit'
    rows = [r for r in csv.DictReader((audit / 'ALL-457-MODULES.tsv').open(), delimiter='\t') if 'system_dlkm' in r['partitions'].split(';')]
    frozen = json.loads((audit / 'evidence/stock-identities.json').read_text())
    master = {(r['filename'], r['sha256']) for r in csv.DictReader((root / 'kernel/stock-module-master.csv').open())}
    if len(rows) != 60:
        die(f'expected 60 system_dlkm identities in the committed audit, found {len(rows)}')
    for r in rows:
        f = frozen.get(r['module_id'])
        if r['partitions'] != 'system_dlkm' or not f or f['stock_sha256'] != r['stock_sha256'] or int(f['stock_size']) != int(r['stock_size']) \
           or (r['filename'], r['stock_sha256']) not in master or r['module_id'] != r['filename'] + '@' + r['stock_sha256']:
            die('audit/frozen/master disagree for ' + r['module_id'])
    img = a.image.read_bytes()
    if sha(img) != IMAGE_SHA256:
        die(f'image sha256 {sha(img)} != recorded {IMAGE_SHA256}')
    work = Path(tempfile.mkdtemp(prefix='restore-operands-'))
    try:
        (work / 'image.img').write_bytes(img)
        x = work / 'extract'
        subprocess.run([str(a.fsck_erofs), f'--extract={x}', str(work / 'image.img')], check=True, capture_output=True)
        if len(list(x.rglob('*.ko'))) != 60:
            die('extracted image does not contain exactly 60 modules')
        plan = []
        for r in sorted(rows, key=lambda r: r['filename']):
            rel = Path(r['stock_paths'])
            if ';' in r['stock_paths'] or not rel.is_relative_to(REL_ROOT):
                die('unexpected path ' + r['stock_paths'])
            src = (x / rel.relative_to(REL_ROOT)).read_bytes()
            if sha(src) != r['stock_sha256'] or len(src) != int(r['stock_size']):
                die('image member does not match committed identity: ' + r['module_id'])
            n = unsigned_len(src)
            if n is None:
                die('image member is not a signed module: ' + r['module_id'])
            d = root / rel
            if d.is_symlink() or not d.is_file():
                die(f'destination is not a regular file: {d}')
            cur = d.read_bytes(); st = d.stat()
            if cur == src:
                state = 'ALREADY_INTACT'
            elif cur == src[:n]:
                state = 'SIGNATURE_STRIPPED'
            else:
                die(f'{rel}: unknown state sha256={sha(cur)} size={len(cur)}; not a pure signature strip, refusing')
            plan.append(dict(module_id=r['module_id'], filename=r['filename'], destination=str(rel), state=state,
                             before_sha256=sha(cur), before_size=len(cur), before_inode=st.st_ino,
                             before_mtime=time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(st.st_mtime)),
                             unsigned_prefix_sha256=sha(src[:n]), signature_trailer_bytes=len(src) - n,
                             source='system_dlkm_a.img@' + IMAGE_SHA256[:16] + ':' + str(rel.relative_to(REL_ROOT)),
                             expected_sha256=r['stock_sha256'], expected_size=int(r['stock_size']), _src=src))
        todo = [p for p in plan if p['state'] == 'SIGNATURE_STRIPPED']
        print(json.dumps(dict(target=str(dest_root), identities=len(plan), already_intact=len(plan) - len(todo), to_restore=len(todo), apply=a.apply)))
        if a.apply and todo:
            a.quarantine.mkdir(parents=True, exist_ok=False)
            for p in todo:
                d = root / p['destination']
                q = a.quarantine / p['filename']
                shutil.copy2(d, q)
                if sha(q.read_bytes()) != p['before_sha256']:
                    die('quarantine copy mismatch ' + p['filename'])
                tmp = d.with_name('.' + d.name + '.restore-tmp')
                with open(tmp, 'xb') as fh:
                    fh.write(p['_src']); fh.flush(); os.fsync(fh.fileno())
                if sha(tmp.read_bytes()) != p['expected_sha256']:
                    tmp.unlink(); die('temporary copy mismatch ' + p['filename'])
                os.replace(tmp, d)
                p['quarantine'] = str(q); p['quarantine_sha256'] = sha(q.read_bytes())
        for p in plan:
            cur = (root / p['destination']).read_bytes()
            p['after_sha256'] = sha(cur); p['after_size'] = len(cur)
            p['action'] = ('RESTORED' if a.apply else 'WOULD_RESTORE') if p['state'] == 'SIGNATURE_STRIPPED' else 'NONE'
            if a.apply and p['after_sha256'] != p['expected_sha256']:
                die('post-check failed ' + p['destination'])
        cols = ['module_id', 'filename', 'destination', 'state', 'action', 'before_sha256', 'before_size', 'before_inode', 'before_mtime',
                'unsigned_prefix_sha256', 'signature_trailer_bytes', 'expected_sha256', 'expected_size', 'after_sha256', 'after_size',
                'source', 'quarantine', 'quarantine_sha256']
        a.manifest.parent.mkdir(parents=True, exist_ok=True)
        with a.manifest.open('w', newline='') as f:
            w = csv.DictWriter(f, cols, delimiter='\t', lineterminator='\n', extrasaction='ignore', restval='')
            w.writeheader(); w.writerows(plan)
        print(json.dumps(dict(result='APPLIED' if a.apply else 'DRY_RUN', restored=sum(p['action'] == 'RESTORED' for p in plan),
                              intact_after=sum(p['after_sha256'] == p['expected_sha256'] for p in plan))))
    finally:
        shutil.rmtree(work)

if __name__ == '__main__':
    main()
