#!/usr/bin/env python3
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse, csv, os, re, subprocess

ap = argparse.ArgumentParser()
ap.add_argument('image')
ap.add_argument('tree')
ap.add_argument('dump')
ap.add_argument('outdir')
ap.add_argument('--jobs', type=int, default=8)
a = ap.parse_args()
image, tree, dump, out = map(Path, (a.image, a.tree, a.dump, a.outdir))
out.mkdir(parents=True, exist_ok=True)
paths = ['.'] + [p.relative_to(tree).as_posix() for p in sorted(tree.rglob('*'))]

def one(rel):
    image_path = '/' if rel == '.' else '/' + rel
    cp = subprocess.run([str(dump), '--path=' + image_path, str(image)],
                        check=True, text=True, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
    text = cp.stdout
    def g(pattern):
        m = re.search(pattern, text, re.M)
        if not m:
            raise RuntimeError(f'{rel}: missing {pattern!r}\n{text}\n{cp.stderr}')
        return m.group(1)
    size_line = g(r'^Size: (.+)$')
    size = re.match(r'(\d+)', size_line).group(1)
    type_name = size_line.rsplit('  ', 1)[-1]
    xattrs = []
    for name, value in re.findall(r'^Xattr: ([^=]+)=([0-9a-f]*)$', text, re.M):
        xattrs.append((name, value))
    host_path = tree if rel == '.' else tree / rel
    link_target = os.readlink(host_path) if host_path.is_symlink() else ''
    return {
        'path': rel,
        'type': type_name,
        'size': size,
        'nid': g(r'^NID: (\d+)'),
        'nlink': g(r'Links: (\d+)'),
        'inode_size': g(r'^Inode size: (\d+)'),
        'xattr_size': g(r'Xattr size: (\d+)'),
        'uid': g(r'^Uid: (\d+)'),
        'gid': g(r'Gid: (\d+)'),
        'mode': g(r'Access: ([0-7]+)'),
        'timestamp': g(r'^Timestamp: (.+)$'),
        'symlink_target': link_target,
        'xattrs': xattrs,
    }

with ThreadPoolExecutor(max_workers=a.jobs) as ex:
    rows = list(ex.map(one, paths))
rows.sort(key=lambda r: (r['path'] != '.', r['path']))
fields = ['path','type','size','nid','nlink','inode_size','xattr_size','uid','gid',
          'mode','timestamp','symlink_target']
with (out/'system-ext-source-metadata.tsv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
    w.writeheader()
    for r in rows:
        w.writerow({k:r[k] for k in fields})
with (out/'system-ext-source-xattrs.tsv').open('w', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n')
    w.writerow(['path','name','value_hex'])
    for r in rows:
        for name, value in r['xattrs']:
            w.writerow([r['path'],name,value])
with (out/'system-ext-fs-config.txt').open('w') as f:
    for r in rows:
        p = '/' if r['path']=='.' else '/system_ext/' + r['path']
        f.write(f"{p} {r['uid']} {r['gid']} {r['mode']} capabilities=0x0\n")
by_nid = {}
for r in rows:
    if r['type'] == 'regular file':
        by_nid.setdefault(r['nid'], []).append(r['path'])
with (out/'system-ext-hardlink-groups.tsv').open('w') as f:
    f.write('nid\tnlink\tpaths\n')
    for nid, members in sorted(by_nid.items(), key=lambda x:int(x[0])):
        expected = int(next(r['nlink'] for r in rows if r['nid']==nid))
        if expected > 1 or len(members)>1:
            f.write(f"{nid}\t{expected}\t{'|'.join(sorted(members))}\n")
print(f'PATHS={len(rows)}')
print(f'XATTRS={sum(len(r["xattrs"]) for r in rows)}')
print(f'NON_SELINUX_XATTRS={sum(name != "security.selinux" for r in rows for name,_ in r["xattrs"])}')
print(f'HARDLINK_INODES={sum(len(v)>1 for v in by_nid.values())}')
print(f'NLINK_GT1_INODES={sum(int(next(r["nlink"] for r in rows if r["nid"]==nid))>1 for nid in by_nid)}')
