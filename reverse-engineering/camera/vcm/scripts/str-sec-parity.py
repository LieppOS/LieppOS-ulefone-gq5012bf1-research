#!/usr/bin/env python3
"""str-sec-parity.py A.ko B.ko OUTDIR

Writes OUTDIR/string-parity.tsv  (every NUL-terminated string in each
SHF_STRINGS / .modinfo section, positional, with equality) and
OUTDIR/section-parity.tsv (every section: type, size, sha256 of bytes, equal).
"""
import hashlib, os, re, subprocess, sys

RE = os.environ.get('LLVM_READELF', 'llvm-readelf')


def sections(p):
    raw = open(p, 'rb').read()
    out = {}
    for l in subprocess.run([RE, '-SW', p], capture_output=True, text=True).stdout.splitlines():
        m = re.match(r'\s*\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+[0-9a-f]+\s+([0-9a-f]+)\s+([0-9a-f]+)\s+\S+\s+(\S*)', l)
        if m:
            n, t, off, sz, fl = m.group(2), m.group(3), int(m.group(4), 16), int(m.group(5), 16), m.group(6)
            data = b'' if t == 'NOBITS' else raw[off:off + sz]
            out[n] = (t, sz, fl, data)
    return out


def main():
    a, b, od = sys.argv[1:4]
    os.makedirs(od, exist_ok=True)
    sa, sb = sections(a), sections(b)
    with open(f'{od}/section-parity.tsv', 'w') as f:
        f.write('section\ttype\tA_size\tB_size\tA_sha256\tB_sha256\tequal\n')
        for n in sorted(set(sa) | set(sb)):
            x, y = sa.get(n), sb.get(n)
            ha = hashlib.sha256(x[3]).hexdigest()[:16] if x else ''
            hb = hashlib.sha256(y[3]).hexdigest()[:16] if y else ''
            f.write(f"{n}\t{(x or y)[0]}\t{x[1] if x else ''}\t{y[1] if y else ''}\t{ha}\t{hb}\t"
                    f"{'yes' if x and y and x[3] == y[3] and x[1] == y[1] else 'no'}\n")
    eq = tot = 0
    with open(f'{od}/string-parity.tsv', 'w') as f:
        f.write('section\tindex\tA\tB\tequal\n')
        for n in sorted(set(sa) | set(sb)):
            x, y = sa.get(n), sb.get(n)
            if not ((x and 'S' in x[2]) or n == '.modinfo'):
                continue
            la = [s.decode('latin1') for s in (x[3] if x else b'').split(b'\0') if s]
            lb = [s.decode('latin1') for s in (y[3] if y else b'').split(b'\0') if s]
            for i in range(max(len(la), len(lb))):
                u = la[i] if i < len(la) else ''
                v = lb[i] if i < len(lb) else ''
                tot += 1
                eq += u == v
                f.write(f"{n}\t{i}\t{u}\t{v}\t{'yes' if u == v else 'no'}\n")
    print(f'strings {eq}/{tot} equal; sections '
          f"{sum(1 for n in sa if n in sb and sa[n][3] == sb[n][3])}/{len(set(sa) | set(sb))} byte-equal")


if __name__ == '__main__':
    main()
