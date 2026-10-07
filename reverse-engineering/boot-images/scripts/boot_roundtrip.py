#!/usr/bin/env python3
"""Round-trip stock boot/init_boot/vendor_boot images through AOSP unpack_bootimg/mkbootimg
and verify (1) the repacked image equals the stock image body byte-for-byte, (2) the stock AVB
hash footer digest = sha256(salt || body) for the partition, i.e. the footer is reproducible.
usage: roundtrip.py <mkbootimg-dir> <workdir> <img>...
"""
import hashlib, os, shlex, struct, subprocess, sys

T, W = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else (None, None)


def avb(img):
    b = open(img, "rb").read()
    f = b[-64:]
    if f[:4] != b"AVBf":
        return None
    orig, vbo, vbs = struct.unpack(">QQQ", f[12:36])
    vb = b[vbo:vbo + vbs]
    assert vb[:4] == b"AVB0"
    alg, = struct.unpack(">I", vb[28:32])
    auth, aux = struct.unpack(">QQ", vb[12:28])
    doff, dsz = struct.unpack(">QQ", vb[96:112])
    d = vb[256 + auth + doff: 256 + auth + doff + dsz]
    descs = []
    p = 0
    while p < len(d):
        tag, nb = struct.unpack(">QQ", d[p:p + 16])
        body = d[p + 16:p + 16 + nb]
        if tag == 2:  # hash descriptor
            isz, = struct.unpack(">Q", body[0:8])
            halg = body[8:40].rstrip(b"\0").decode()
            pnl, sl, dl, fl = struct.unpack(">IIII", body[40:56])
            o = 56 + 60
            pn = body[o:o + pnl].decode(); o += pnl
            salt = body[o:o + sl]; o += sl
            dig = body[o:o + dl]
            descs.append(dict(image_size=isz, alg=halg, part=pn, salt=salt, digest=dig))
        p += 16 + nb
    return dict(orig=orig, vbmeta_alg=alg, descs=descs, blob=b)


for img in (sys.argv[3:] if not os.environ.get("VBMETA_CHECK") else []):
    name = os.path.basename(img)[:-4]
    out = os.path.join(W, name)
    subprocess.run(["rm", "-rf", out], check=True)
    args = subprocess.check_output(["python3", f"{T}/unpack_bootimg.py", "--boot_img", img, "--out", out,
                                    "--format=mkbootimg"], text=True)
    rep = os.path.join(W, name + ".repack")
    subprocess.check_call(["python3", f"{T}/mkbootimg.py"] + shlex.split(args) +
                          (["--vendor_boot", rep] if "--vendor_" in args else ["--output", rep]))
    r = open(rep, "rb").read()
    a = avb(img)
    s = a["blob"] if a else open(img, "rb").read()
    body_eq = s[:len(r)] == r
    pad_zero = (a is not None) and set(s[len(r):a["orig"]]) <= {0}
    line = f"{name:16s} repack={len(r):>9} body_identical={body_eq}"
    if a:
        line += f" avb_orig={a['orig']} pad_zero_to_orig={pad_zero} vbmeta_alg={a['vbmeta_alg']}"
        for d in a["descs"]:
            calc = hashlib.new(d["alg"], d["salt"] + s[:d["image_size"]]).digest()
            line += f" | hashdesc part={d['part']} size={d['image_size']} digest_match={calc == d['digest']}"
    print(line)
    print("    args:", args.strip()[:400])


def vbmeta_descs(path):
    b = open(path, "rb").read()
    assert b[:4] == b"AVB0"
    auth, aux = struct.unpack(">QQ", b[12:28])
    alg, = struct.unpack(">I", b[28:32])
    doff, dsz = struct.unpack(">QQ", b[96:112])
    d = b[256 + auth + doff:256 + auth + doff + dsz]
    out, p = [], 0
    while p < len(d):
        tag, nb = struct.unpack(">QQ", d[p:p + 16]); body = d[p + 16:p + 16 + nb]
        if tag == 2:
            isz, = struct.unpack(">Q", body[0:8]); halg = body[8:40].rstrip(b"\0").decode()
            pnl, sl, dl, fl = struct.unpack(">IIII", body[40:56]); o = 116
            pn = body[o:o + pnl].decode(); o += pnl; salt = body[o:o + sl]; o += sl
            out.append(("hash", pn, isz, halg, salt, body[o:o + dl]))
        elif tag == 4:
            rli, pnl = struct.unpack(">II", body[0:8])
            out.append(("chain", body[76:76 + pnl].decode(), rli))
        elif tag == 1:
            out.append(("hashtree?", None))
        p += 16 + nb
    return alg, out


if __name__ == "__main__" and os.environ.get("VBMETA_CHECK"):
    D = os.environ["VBMETA_CHECK"]
    for s in "ab":
        alg, ds = vbmeta_descs(f"{D}/vbmeta_{s}.img")
        print(f"vbmeta_{s}: alg={alg} chains={[x[1:] for x in ds if x[0] == 'chain']}")
        for x in ds:
            if x[0] == "hash":
                pn, isz, halg, salt, dig = x[1:]
                p = f"{D}/{pn}_{s}.img"
                ok = hashlib.new(halg, salt + open(p, "rb").read()[:isz]).digest() == dig if os.path.exists(p) else "n/a"
                print(f"   hash {pn:12s} size={isz:>9} matches {pn}_{s}.img: {ok}")
