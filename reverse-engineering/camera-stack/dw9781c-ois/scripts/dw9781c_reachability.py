#!/usr/bin/env python3
"""Static proof of who can make the stock DW9781C driver touch the bus.

Offline; reads only stock images already extracted under workspace/ and the
NothingOSS hf_manager header.  Output: a human summary on stdout and TSVs in
../evidence/.

Part K  (stock dw9781c.ko, binary call graph from objdump -d -r):
        every function, its callers' entry kind, and whether it can reach
        i2c_transfer.
Part U  (stock vendor userspace):
        U1 libcameracustom.lens.so ois_list_0..5 contents
        U2 libmtkcam_metastore.so availableOisModes (0x80070004) per sensor
        U3 availableOisModes -> NSCam::Utils::eSensorType  (+10 for 3..6)
           in featurepolicy / EIS / P1 node
        U4 libcam.utils.sensorprovider.so mapSensorType jump table
           (eSensorType -> hf_manager SENSOR_TYPE_*)
        U5 dw9781c.ko support_sensors[0].sensor_type
        U6 every SensorProvider::{enableSensor,lockOisAsync,...} call site in
           /vendor with a literal sensor-type argument
"""
import collections
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))
from elfmini import Elf  # noqa: E402

PART = os.path.join(REPO, "workspace/gq5012bf1/stock/partitions")
KO = os.path.join(PART, "vendor_dlkm/lib/modules/dw9781c.ko")
V64 = os.path.join(PART, "vendor/lib64/mt6878")
HF_H = os.environ.get("HF_SENSOR_TYPE_H", os.path.join(
    REPO, "..", "kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/sensor/2.0/core/hf_sensor_type.h"))
EVD = os.path.join(HERE, "..", "evidence")
OBJDUMP = os.environ.get("OBJDUMP", "llvm-objdump")


def objdump(path, *extra):
    return subprocess.run([OBJDUMP, "-d", "--no-show-raw-insn", *extra, path],
                          capture_output=True, text=True, check=True).stdout.splitlines()


# ---------------------------------------------------------------- Part K
def part_k():
    e = Elf(KO)
    funcs = {s.name for s in e.symbols if s.type == 2 and s.shndx}
    calls = collections.defaultdict(set)      # fn -> callees (local + imports)
    taken = collections.defaultdict(set)      # fn -> functions whose address it materialises
    text_syms = {}
    for s in e.symbols:
        if s.type == 2 and s.shndx:
            text_syms[(e.sections[s.shndx].name, s.value)] = s.name
    cur = None
    for line in objdump(KO, "-r"):
        m = re.match(r"^[0-9a-f]+ <(\w+)>:", line)
        if m:
            cur = m.group(1)
            continue
        m = re.search(r"\bbl?\s+0x[0-9a-f]+ <(\w+)>$", line)
        if m and cur and m.group(1) in funcs and m.group(1) != cur:
            calls[cur].add(m.group(1))
        m = re.search(r"R_AARCH64_(CALL26|JUMP26)\s+(\w+)$", line)
        if m and cur:
            calls[cur].add(m.group(2))
        m = re.search(r"R_AARCH64_ADD_ABS_LO12_NC\s+(\.text|\.init\.text|\.exit\.text)\+0x([0-9a-f]+)$", line)
        if m and cur:
            t = text_syms.get((m.group(1), int(m.group(2), 16)))
            if t:
                taken[cur].add(t)
    # function pointers stored in data objects (ops tables, driver struct)
    slots = collections.defaultdict(list)
    for tgt, lst in e.relocs.items():
        tn = e.sections[tgt].name
        if tn.startswith(".rela") or "text" in tn:
            continue
        for r in lst:
            s = r.sym
            fn = None
            if s.type == 2:
                fn = s.name
            elif s.type == 3:
                fn = text_syms.get((e.sections[s.shndx].name, s.value + r.addend))
            if fn:
                holder = e.containing(tgt, r.off)
                hn = holder.name if holder else tn
                slots[fn].append(f"{hn}+{r.off - (holder.value if holder else 0):#x}")

    def reaches(fn, seen=None):
        seen = seen or set()
        if fn == "i2c_transfer":
            return True
        if fn in seen:
            return False
        seen.add(fn)
        return any(reaches(c, seen) for c in calls.get(fn, ()))

    ENTRY = {
        "init_module": "module load",
        "cleanup_module": "module unload",
        "dw9781c_probe": "i2c_driver.probe_new (DT bind 4-000e)",
        "dw9781c_remove": "i2c_driver.remove",
        "dw9781c_ois_suspend": "runtime-PM suspend",
        "dw9781c_ois_resume": "runtime-PM resume",
        "dw9781c_open": "v4l2-subdev open (/dev/v4l-subdevN)",
        "dw9781c_close": "v4l2-subdev close",
        "dw9781c_ops_core_ioctl": "v4l2-subdev ioctl (VIDIOC_MTK_S_OIS_INIT/UNINIT reach I2C)",
        "dw9781c_enable": "hf_manager enable(SENSOR_TYPE_OIS1)",
        "dw9781c_batch": "hf_manager batch",
        "dw9781c_sample": "hf_manager poll sample (only while enabled)",
        "dw9781c_custom_cmd": "hf_manager custom_cmd",
        "ois_init_fx": "workqueue queued by dw9781c_enable(en=1)",
    }
    rows = []
    for fn in sorted(funcs, key=lambda n: (n not in ENTRY, n)):
        how = ENTRY.get(fn, "internal")
        rows.append((fn, how, "YES" if reaches(fn) else "no",
                     ",".join(sorted(calls.get(fn, ()))),
                     ",".join(sorted(taken.get(fn, ()))),
                     ",".join(slots.get(fn, ()))))
    return rows, e


# ---------------------------------------------------------------- Part U
def u1_ois_list():
    p = os.path.join(V64, "libcameracustom.lens.so")
    blob_all = open(p, "rb").read()
    sec = subprocess.run(["llvm-readelf", "-S", "-W", p], capture_output=True, text=True).stdout
    m = re.search(r"\]\s+\.data\s+PROGBITS\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)", sec)
    d_addr, d_off = int(m.group(1), 16), int(m.group(2), 16)
    dynsym = {}
    out = subprocess.run(["llvm-nm", "-D", p], capture_output=True, text=True).stdout
    for line in out.splitlines():
        a, t, n = line.split(None, 2) if len(line.split()) == 3 else (None, None, None)
        if n and n.startswith(("ois_list_", "vcm_list_")):
            dynsym[n] = int(a, 16)
    rows = []
    for n in sorted(k for k in dynsym if k.startswith("ois_list_")):
        off = dynsym[n] - d_addr + d_off
        size = 0x39C  # 21 entries x 0x2C (distance between consecutive ois_list_N symbols)
        blob = blob_all[off:off + size]
        entries = []
        for i in range(0, size, 0x2C):  # sensor id (u32) .. name
            sid, = struct.unpack_from("<I", blob, i)
            name = blob[i + 12:i + 44].split(b"\0")[0].decode(errors="replace")
            if sid or name:
                entries.append(f"{sid:#x}:{name}")
        rows.append((n, ";".join(entries) if entries else "<empty>"))
    return rows


def u2_available_ois_modes():
    p = os.path.join(V64, "libmtkcam_metastore.so")
    dis = objdump(p)
    rows = []
    fn = None
    regs = {}
    for i, line in enumerate(dis):
        m = re.match(r"^[0-9a-f]+ <(\w+)>:", line)
        if m:
            fn, regs = m.group(1), {}
            continue
        m = re.search(r"\smov\s+w(\d+), #0x([0-9a-f]+)", line)
        if m:
            regs[m.group(1)] = int(m.group(2), 16)
        if re.search(r"movk\s+w1, #0x8007, lsl #16", line) and fn:
            # value pushed right after IEntry ctor: str wN,[sp,#..] or mov w8,#imm; str w8
            val = None
            for x in dis[i + 1:i + 9]:
                mm = re.search(r"\smov\s+w8, #0x([0-9a-f]+)", x)
                if mm:
                    val = int(mm.group(1), 16)
                    break
                mm = re.search(r"\sstr\s+w(\d+), \[sp", x)
                if mm:
                    val = regs.get(mm.group(1))
                    break
            drv = fn.replace("constructCustStaticMetadata_PLATFORM_VENDOR_", "")
            rows.append((drv, val))
    return rows


def u3_mapping():
    pats = {
        "libmtkcam_hal_core_featurepolicy.so": "FeatureSettingPolicy::emplaceStreamData",
        "libfeature_eis.so": "EisHalImp::Init",
        "libmtkcam_p1node.so": "P1NodeImp::check_config",
    }
    rows = []
    for lib, fn in pats.items():
        dis = subprocess.run([OBJDUMP, "-d", "-C", "--no-show-raw-insn", os.path.join(V64, lib)],
                             capture_output=True, text=True).stdout.splitlines()
        inside = False
        for i, line in enumerate(dis):
            if line.endswith(">:"):
                inside = fn in line
                continue
            if inside and re.search(r"\sadd\s+w\d+, w\d+, #0xa$", line):
                ctx = " | ".join(x.split(":", 1)[1].strip() for x in dis[i - 4:i + 1] if ":" in x)
                if re.search(r"sub\s+w\d+, w\d+, #0x[34]", ctx):
                    rows.append((lib, fn, line.split(":")[0].strip(), ctx))
                    break
    return rows


def u4_map_sensor_type():
    p = os.path.join(V64, "libcam.utils.sensorprovider.so")
    sym = "_ZN5NSCam5Utils21SensorProviderService13mapSensorTypeENS0_11eSensorTypeE"
    dis = objdump(p, f"--disassemble-symbols={sym}")
    ins = {}
    for line in dis:
        m = re.match(r"\s+([0-9a-f]+):\s+(.*)", line)
        if m:
            ins[int(m.group(1), 16)] = m.group(2).strip()
    addrs = sorted(ins)
    # locate: adr x10, TABLE ; mov w20, #DEFAULT ; adr x11, BASE ; ldrb ; add ; br
    table = base = default = None
    nmax = None
    for a in addrs:
        t = ins[a]
        m = re.match(r"cmp\s+w1, #0x([0-9a-f]+)", t)
        if m and nmax is None:
            nmax = int(m.group(1), 16)
        m = re.match(r"adr\s+x10, 0x([0-9a-f]+)", t)
        if m and table is None:
            table = int(m.group(1), 16)
        m = re.match(r"mov\s+w20, #0x([0-9a-f]+)", t)
        if m and default is None:
            default = int(m.group(1), 16)
        m = re.match(r"adr\s+x11, 0x([0-9a-f]+)", t)
        if m and base is None:
            base = int(m.group(1), 16)
    blob = open(p, "rb").read()
    rows = []
    for st in range(nmax + 1):
        tgt = base + blob[table + st] * 4
        t = ins.get(tgt, "")
        m = re.match(r"mov\s+w20, #0x([0-9a-f]+)", t)
        if m:
            rows.append((st, int(m.group(1), 16)))
        elif t.startswith("mov\tw8") or t.startswith("mov w8") or tgt not in ins or "w20" not in t:
            rows.append((st, default if t.startswith("mov") and "w8" in t else None))
    return rows


def hf_enum():
    body = open(HF_H).read()
    body = body[body.find("SENSOR_TYPE_INVALID"):]
    body = body[:body.find("}")]
    v, out = -1, {}
    for line in body.split("\n"):
        line = re.sub(r"/\*.*?\*/|//.*", "", line).strip().rstrip(",")
        if not line:
            continue
        m = re.match(r"(\w+)\s*=\s*(\w+)", line)
        if m:
            v, n = int(m.group(2), 0), m.group(1)
        else:
            v, n = v + 1, line
        out[v] = n
    return out


def u6_call_sites():
    rows = collections.Counter()
    for f in sorted(os.listdir(V64)):
        p = os.path.join(V64, f)
        if not f.endswith(".so") or os.path.islink(p) or b"SensorProvider" not in open(p, "rb").read():
            continue
        dis = objdump(p)
        for i, line in enumerate(dis):
            m = re.search(r"<_ZN5NSCam5Utils\d+SensorProvider\w*?(enableSensor|lockOisAsync|customCmd|"
                          r"getLatestSensorData|getAllSensorData|disableSensor)\w*@plt>", line)
            if not m or not re.search(r"\sbl\s", line):
                continue
            arg = "dynamic"
            for x in reversed(dis[max(0, i - 12):i]):
                mm = re.search(r"\s(?:mov|orr)\s+w1, (#0x[0-9a-f]+|#\d+|wzr)", x)
                if mm:
                    arg = "0" if mm.group(1) == "wzr" else str(int(mm.group(1)[1:], 0))
                    break
                if re.search(r"\s(?:mov|ldr|add)\s+w1,", x):
                    break
            rows[(f, m.group(1), arg)] += 1
    return rows


def ioctl_cmds():
    """cmd constants compared in dw9781c_ops_core_ioctl and whether the arm reaches I2C."""
    dis = objdump(KO, "--disassemble-symbols=dw9781c_ops_core_ioctl")
    ins = [(int(m.group(1), 16), m.group(2).strip()) for m in
           (re.match(r"\s+([0-9a-f]+):\s+(.*)", x) for x in dis) if m]
    cmds = {}
    for i, (a, t) in enumerate(ins):
        m = re.match(r"mov\s+w(\d+), #0x([0-9a-f]+)", t)
        if m and i + 1 < len(ins):
            m2 = re.match(r"movk\s+w%s, #0x([0-9a-f]+), lsl #16" % m.group(1), ins[i + 1][1])
            if m2:
                cmds[(int(m2.group(1), 16) << 16) | int(m.group(2), 16)] = a
    return cmds


def u7_ioctl_users(cmds):
    """movz/movk (or literal) materialisations of the subdev ioctl numbers in /vendor and /odm ELFs."""
    hits = collections.defaultdict(set)
    for part in ("vendor", "odm"):
        for d, _, fs in os.walk(os.path.join(PART, part)):
            for f in fs:
                p = os.path.join(d, f)
                if os.path.islink(p):
                    continue
                b = open(p, "rb").read()
                if b[:4] != b"\x7fELF" or b[18] != 0xB7:  # EM_AARCH64 only
                    continue
                words = struct.unpack_from("<%dI" % (len(b) // 4), b)
                for t in cmds:
                    lo, hi = t & 0xFFFF, t >> 16
                    movz = 0x52800000 | (lo << 5)
                    for i, w in enumerate(words):
                        if (w & 0x7FFFFFE0) == movz:
                            rd = w & 31
                            if any((x & 0x7FFFFFFF) == (0x72A00000 | (hi << 5) | rd) for x in words[i + 1:i + 4]):
                                hits[t].add(os.path.relpath(p, PART))
                                break
    return hits


def main():
    os.makedirs(EVD, exist_ok=True)
    krows, e = part_k()
    with open(os.path.join(EVD, "dw9781c-kernel-reachability.tsv"), "w") as fo:
        fo.write("function\tentry\treaches_i2c_transfer\tcallees\taddress_taken\tstored_in\n")
        for r in krows:
            fo.write("\t".join(r) + "\n")
    print("== K: stock dw9781c.ko — paths to i2c_transfer")
    for r in krows:
        print(f"  {r[0]:24s} {r[2]:4s} {r[1]}")

    ss = [s for s in e.symbols if s.name == "support_sensors"][0]
    st, = struct.unpack_from("<i", e.bytes_of(ss), 0)
    name = e.bytes_of(ss)[8:24].split(b"\0")[0].decode()
    hf = hf_enum()
    print(f"\n== U5: support_sensors[0].sensor_type = {st} ({hf.get(st)}), name '{name}'")

    print("\n== U1: libcameracustom.lens.so ois_list_N")
    u1 = u1_ois_list()
    for n, v in u1:
        print(f"  {n}: {v}")

    print("\n== U2: availableOisModes (0x80070004) static metadata per sensor driver")
    u2 = u2_available_ois_modes()
    for d, v in u2:
        print(f"  {d:40s} {v}")
    stock = ["SENSOR_DRVNAME_IMX989_MIPI_RAW", "SENSOR_DRVNAME_OV64B_MIPI_RAW",
             "SENSOR_DRVNAME_S5KJN1_MIPI_RAW", "SENSOR_DRVNAME_S5KJN1MAIN2_MIPI_RAW"]
    u2d = dict(u2)

    print("\n== U3: availableOisModes -> eSensorType mapping sites")
    u3 = u3_mapping()
    for r in u3:
        print(f"  {r[0]} {r[1]} @{r[2]}: {r[3]}")

    print("\n== U4: SensorProviderService::mapSensorType (eSensorType -> hf SENSOR_TYPE)")
    u4 = dict(u4_map_sensor_type())
    for k in range(13, 17):
        print(f"  eSensorType {k} -> {u4.get(k)} ({hf.get(u4.get(k))})")

    print("\n== U6: literal sensor-type arguments at SensorProvider call sites in /vendor/lib64/mt6878")
    u6 = u6_call_sites()
    lit = collections.Counter()
    for (f, call, arg), n in sorted(u6.items()):
        lit[arg] += n
    print("  literal-arg histogram:", dict(sorted(lit.items())))
    with open(os.path.join(EVD, "dw9781c-userspace-reachability.tsv"), "w") as fo:
        fo.write("item\tkey\tvalue\n")
        for n, v in u1:
            fo.write(f"U1_ois_list\t{n}\t{v}\n")
        for d, v in u2:
            fo.write(f"U2_availableOisModes\t{d}\t{v}\n")
        for r in u3:
            fo.write(f"U3_mode_to_eSensorType\t{r[0]}:{r[1]}@{r[2]}\t{r[3]}\n")
        for k, v in sorted(u4.items()):
            fo.write(f"U4_mapSensorType\teSensorType {k}\t{v} {hf.get(v, '')}\n")
        fo.write(f"U5_dw9781c_support_sensors\tsensor_type\t{st} {hf.get(st)}\n")
        for (f, call, arg), n in sorted(u6.items()):
            fo.write(f"U6_call_site\t{f}:{call}\targ={arg} x{n}\n")

    print("\n== U7: subdev ioctl numbers handled by dw9781c_ops_core_ioctl, users in /vendor + /odm")
    cmds = ioctl_cmds()
    i2c_cmds = {0xC00456C7: "VIDIOC_MTK_S_OIS_INIT -> dw9781c_init (I2C)",
                0xC00456C8: "VIDIOC_MTK_S_OIS_UNINIT -> dw9781c_release (I2C)",
                0xC00856C2: "VIDIOC_MTK_S_OIS_MODE (log only)",
                0xC00856C3: "VIDIOC_MTK_G_OIS_POS_INFO (memset+copy_to_user, no I2C)"}
    u7 = u7_ioctl_users(cmds)
    with open(os.path.join(EVD, "dw9781c-userspace-reachability.tsv"), "a") as fo:
        for c in sorted(cmds):
            users = sorted(u7.get(c, ()))
            print(f"  {c:#010x} {i2c_cmds.get(c, '?'):55s} users: {users or 'none'}")
            fo.write(f"U7_ioctl\t{c:#010x} {i2c_cmds.get(c, '?')}\t{','.join(users) or 'none'}\n")

    # ---------------- verdict
    ois1 = [k for k, v in hf.items() if v == "SENSOR_TYPE_OIS1"][0]
    est_for_ois1 = sorted(k for k, v in u4.items() if v == ois1)
    modes_for_ois1 = [k - 10 for k in est_for_ois1 if 13 <= k <= 16]
    stock_modes = {d: u2d.get(d) for d in stock}
    eff = {d: (v if v is not None else "absent->13") for d, v in stock_modes.items()}
    checks = [
        ("probe/runtime-PM/open/close do no I2C",
         all(r[2] == "no" for r in krows if r[0] in ("dw9781c_probe", "dw9781c_ois_resume", "dw9781c_ois_suspend",
                                                      "dw9781c_open", "dw9781c_close", "dw9781c_power_on",
                                                      "dw9781c_power_off", "init_module"))),
        ("I2C reachable only via ioctl/hf enable,sample,custom_cmd/ois_init_fx",
         {r[0] for r in krows if r[2] == "YES" and r[1] != "internal"} <=
         {"dw9781c_ops_core_ioctl", "dw9781c_enable", "dw9781c_sample", "dw9781c_custom_cmd", "ois_init_fx"}),
        ("dw9781c hf type is SENSOR_TYPE_OIS1", st == ois1),
        ("every ois_list_N is only the Dummy entry", all(v == "0xffff:Dummy" for _, v in u1)),
        ("OIS1 is reachable only from availableOisModes value(s)", modes_for_ois1),
        ("no stock sensor selects an OIS1 mode",
         all(stock_modes[d] not in modes_for_ois1 for d in stock)),
        ("no literal OIS1 eSensorType at any SensorProvider call site",
         all(arg not in [str(x) for x in est_for_ois1] for (_, _, arg) in u6)),
        ("ioctl table is exactly the four known commands", set(cmds) == set(i2c_cmds)),
        ("no /vendor or /odm binary encodes S_OIS_INIT/UNINIT",
         not u7.get(0xC00456C7) and not u7.get(0xC00456C8)),
    ]
    print("\n== verdict")
    print("  stock sensors' availableOisModes:", eff)
    ok = True
    for c, v in checks:
        good = bool(v) if not isinstance(v, list) else len(v) > 0
        ok &= good
        print(f"  [{'OK' if good else 'FAIL'}] {c}: {v}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
