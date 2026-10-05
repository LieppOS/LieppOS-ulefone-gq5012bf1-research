#!/usr/bin/env python3
"""chanmap.py DEVICETREE_TAR KDM_TREE STOCK_KO_DIR CALLSITES_TSV OUT_TSV

Authoritative GQ5012BF1 TinySys IPI channel map, offline:
  * SCP / VCP / GPUEB pin tables from the stock live device tree (send-table/recv-table),
    with slot offsets and pin indices recomputed by the exact stock algorithm
    (scp_wrapper_ipi.c / vcp_helper.c mbox_setup_pin_table; gpueb_ipi.c sequential layout);
  * MCUPM pin table decoded from the static .data of the stock mcupm.ko;
  * symbolic names from scp.h / vcp.h / mcupm_ipi_id.h (KDM 5e415e059253) and the DT
    gpueb send-/recv-name-table;
  * kernel users from the static call-site census (ipi_callsites.py) of stock modules.
"""
import io, os, re, struct, sys, tarfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from elfmini import Elf
TAR, KDM, KO, CS, OUT = sys.argv[1:6]
BASE = 'sys/firmware/devicetree/base/'
tf = tarfile.open(TAR)
def prop(node, name):
    try:
        return tf.extractfile(BASE + node + '/' + name).read()
    except KeyError:
        return None
def u32s(b): return list(struct.unpack('>%dI' % (len(b) // 4), b)) if b else []
def strs(b): return [x.decode() for x in b.split(b'\0') if x] if b else []
def enum(path, start_pat, end_pat):
    t = open(os.path.join(KDM, path)).read()
    s = t[re.search(start_pat, t).start():]; s = s[:re.search(end_pat, s).start()]
    d = {}
    for n, v in re.findall(r'^\s*(IPI_\w+)\s*=\s*(\d+)', s, re.M): d[int(v)] = n
    return d
SCPN = enum('drivers/misc/mediatek/scp/include/scp.h', r'IPI_OUT_AUDIO_VOW_1', r'SCP_IPI_COUNT')
VCPN = enum('drivers/misc/mediatek/vcp/include/vcp.h', r'IPI_OUT_VDEC_1', r'VCP_IPI_COUNT')
MCUN = {int(v): n for n, v in re.findall(r'#define\s+(CH_\w+)\s+(\d+)', open(os.path.join(KDM, 'drivers/misc/mediatek/mcupm/include/mcupm_ipi_id.h')).read())}
rows = []
def setup(send, recv, nmbox, is64d):
    # exact port of mbox_setup_pin_table() (scp_wrapper_ipi.c:247 / vcp_helper.c:2937)
    for mb in range(nmbox):
        last_ofs = last_idx = last_slot = last_sz = 0
        for tbl in (send, recv):
            for p in tbl:
                if p['mbox'] == mb:
                    p['offset'] = last_ofs + last_slot; p['pin_index'] = last_idx + last_sz
                    last_idx = p['pin_index']
                    if is64d:
                        last_sz = (p['size'] + 1) // 2; last_ofs = last_sz * 2; last_slot = last_idx * 2
                    else:
                        last_sz = p['size']; last_ofs = last_sz; last_slot = last_idx
                elif mb < p['mbox']:
                    break
def dt_tables(node, recv_cells):
    st = u32s(prop(node, 'send-table')); rt = u32s(prop(node, 'recv-table'))
    send = [dict(id=st[i], mbox=st[i + 1], size=st[i + 2]) for i in range(0, len(st), 3)]
    recv = []
    for i in range(0, len(rt), recv_cells):
        c = rt[i:i + recv_cells]
        d = dict(id=c[0], mbox=c[1], size=c[2], recv_opt=c[3])
        if recv_cells == 7: d.update(lock=c[4], buf_full_opt=c[5], cb_ctx_opt=c[6])
        if recv_cells == 5: d.update(cb_ctx_opt=c[4])
        recv.append(d)
    return send, recv
procs = {}
# SCP
n = 'scp@1c400000'; rcm = u32s(prop(n, '#recv-cells-mode')); cells = 7 if rcm and rcm[0] == 1 else 4
s, r = dt_tables(n, cells); nm = u32s(prop(n, 'mbox-count'))[0]; setup(s, r, nm, 1)
procs['SCP'] = (s, r, SCPN, 'DT /scp@1c400000 (mbox-count %d, #recv-cells-mode %s, slot 64 x u32, is64d=1)' % (nm, rcm[0] if rcm else '-'))
# VCP
n = 'soc/vcp@1ea00000'; rcm = u32s(prop(n, '#recv-cells-mode')); cells = 7 if rcm and rcm[0] == 1 else 4
s, r = dt_tables(n, cells); nm = u32s(prop(n, 'mbox-count'))[0]; setup(s, r, nm, 1)
procs['VCP'] = (s, r, VCPN, 'DT /soc/vcp@1ea00000 (mbox-count %d, slot 64, is64d=1)' % nm)
# GPUEB: send 3 cells, recv 5 cells (id, mbox, size, recv_opt, cb_ctx_opt); pin_index = chan_id; offsets sequential
n = 'soc/gpueb@13c00000'; s, r = dt_tables(n, 5); nm = u32s(prop(n, 'mbox-count'))[0]
sn, rn = strs(prop(n, 'send-name-table')), strs(prop(n, 'recv-name-table'))
for mb in range(nm):
    ofs = 0
    for tbl in (s, r):
        for p in tbl:
            if p['mbox'] == mb: p['offset'] = ofs; p['pin_index'] = p['id']; ofs += p['size']
GN = {p['id']: sn[i] for i, p in enumerate(s)}
procs['GPUEB'] = (s, r, GN, 'DT /soc/gpueb@13c00000 (mbox-count %d, mbox-size %d slots, is64d=0, MBOX_OPT_SMEM; names from send-/recv-name-table)' % (nm, u32s(prop(n, 'mbox-size'))[0]))
# MCUPM: static tables in stock mcupm.ko .data
e = Elf(os.path.join(KO, 'mcupm.ko'))
def arr(name, esz):
    sym = e.sym(name)[0]; b = e.bytes_of(sym); return [b[i:i + esz] for i in range(0, len(b), esz)]
s = []; r = []
for b in arr('mcupm_mbox_pin_send', 104):
    w0, sz, pi, cid = struct.unpack_from('<IIII', b)
    s.append(dict(id=cid, mbox=w0 & 0xf, offset=(w0 >> 4) & 0xfffff, send_opt=(w0 >> 24) & 3, lock=(w0 >> 26) & 3, size=sz, pin_index=pi))
for b in arr('mcupm_mbox_pin_recv', 120):
    w0, sz, pi, cid = struct.unpack_from('<IIII', b)
    r.append(dict(id=cid, mbox=w0 & 0xf, offset=(w0 >> 4) & 0xfffff, recv_opt=(w0 >> 24) & 3, lock=(w0 >> 26) & 3,
                  buf_full_opt=(w0 >> 28) & 3, cb_ctx_opt=(w0 >> 30) & 3, size=sz, pin_index=pi))
ext = u32s(prop('mcupm@c540000', 'mbox-extend')); MCU_N = ext[0] if ext else 8
procs['MCUPM'] = (s, r, MCUN, 'stock mcupm.ko .data mcupm_mbox_pin_send[16]/_recv[16]; mtk_ipi_init(): DT mbox-extend %s -> mbox_total_number=%d, so send/recv_count=%d and the ipi table has %d entries' % ('absent' if not ext else ext[0], MCU_N, MCU_N, MCU_N))
# kernel users from the call-site census
DEV = {'&scp_ipidev': 'SCP', '&sap_ipidev': 'SAP', '&vcp_ipidev': 'VCP', 'ret:vcp_get_ipidev': 'VCP', '&mcupm_ipidev': 'MCUPM',
       'ret:get_mcupm_ipidev': 'MCUPM', '&gpueb_ipidev': 'GPUEB', 'ret:get_gpueb_ipidev': 'GPUEB'}
MODDEV = {'mmqos-common': 'VCP', 'mtk-mmdvfs-v3': 'VCP'}
users = collections.defaultdict(set)
gpueb_name_var = collections.defaultdict(dict)
lines = [l.rstrip('\n').split('\t') for l in open(CS)]
pinvar = {}
for m, f, api, *x in lines:
    if api.startswith('gpueb_get_') and x[0].startswith('"'):
        gpueb_name_var[(m, f)][api] = x[0].strip('"')
    if api == 'PINVAR' and x[1].startswith('"'):
        pinvar[(m, x[0])] = x[1].strip('"')
for m, f, api, *x in lines:
    if not api.startswith('mtk_ipi_') or api == 'mtk_ipi_device_register' or m in ('mtk_tinysys_ipi',): continue
    dev = DEV.get(x[0]) or MODDEV.get(m)
    ident = x[1]
    if dev is None: continue
    if not ident.lstrip('-').isdigit():
        nmz = gpueb_name_var.get((m, f), {})
        pv = pinvar.get((m, ident.lstrip('&*')))
        if dev == 'GPUEB' and (pv or len(set(nmz.values())) == 1):
            nmv = pv or list(nmz.values())[0]
            ident = next((str(k) for k, v in GN.items() if v == nmv), None)
            if ident is None:
                users[(dev, 'NAME:' + nmv)].add('%s:%s %s (name "%s" not in DT name table)' % (m, f, api, nmv)); continue
        else:
            continue
    a = api.replace('mtk_ipi_', '')
    det = ''
    if api in ('mtk_ipi_send', 'mtk_ipi_send_compl'):
        det = '(opt=%s len=%s tmo=%s)' % ({'0': 'WAIT', '1': 'POLLING'}.get(x[2], x[2]), x[4], x[5])
    users[(dev, int(ident))].add('%s:%s %s%s' % (m, f, a, det))
# source-attested users with non-constant ids (call site passes a variable)
SRC = {('SCP', 29): 'sensorhub:ipi_comm_noack/ipi_transfer_messages send (ipi_comm.c:52 id=IPI_OUT_SENSOR_CTRL via ipi_comm.c:274)',
       ('SCP', 31): 'sensorhub:ipi_comm_noack/ipi_transfer_messages send (ipi_comm.c:52 id=IPI_OUT_SENSOR_NOTIFY via ipi_comm.c:279)',
       ('SCP', 0): 'mtk-vow:vow_ipi_send send (vow_scp.c:162 IPI_OUT_AUDIO_VOW_1)'}
for k, v in SRC.items(): users[k].add(v + ' [source]')
hdr = ['processor', 'ipi_id', 'symbolic_name', 'direction', 'mbox', 'slot_offset_u32', 'pin_index', 'payload_slots', 'payload_bytes',
       'recv_opt', 'cb_ctx', 'ack_behaviour', 'kernel_users', 'board_state', 'table_source', 'confidence']
out = []
for P, (s, r, names, src) in procs.items():
    sids = {p['id']: p for p in s}; rids = {p['id']: p for p in r}
    for cid in sorted(set(sids) | set(rids)):
        nmv = names.get(cid, '?')
        for kind, p in (('AP->%s' % P, sids.get(cid)), ('%s->AP' % P, rids.get(cid))):
            if not p: continue
            ro = p.get('recv_opt')
            if kind.startswith('AP'):
                ack = 'send_compl-capable: ACK arrives on recv pin of same id' if cid in rids and rids[cid].get('recv_opt') == 1 else (
                      'send_compl-capable: paired recv pin is MESSAGE-type, so any inbound message on it completes notify' if cid in rids else 'fire-and-forget (no recv pin with this id)')
            else:
                ack = {0: 'MBOX_RECV_MESSAGE: unsolicited message, completes pin->notify (mtk_ipi_recv/recv_reply)',
                       1: 'MBOX_RECV_ACK: completion only while holder>0 (reply to send_compl)'}.get(ro, '?')
            cb = p.get('cb_ctx_opt')
            uu = users.get((P, cid), set())
            if kind.startswith('AP'):
                uu = {x for x in uu if not re.search(r' (un)?register', x)}
            else:
                uu = {x for x in uu if re.search(r' ((un)?register|send_compl|recv_reply|recv)\b', x)}
            u = '; '.join(sorted(uu)) or '-'
            conf = 'high (table=%s; name=%s; users=%s)' % ('DT' if P != 'MCUPM' else 'stock .data',
                    'DT string' if P == 'GPUEB' else 'header enum', 'static call sites' if u != '-' else 'none found')
            out.append([P, str(cid), nmv, kind, str(p['mbox']), str(p.get('offset', '?')), str(p.get('pin_index', '?')), str(p['size']),
                        str(p['size'] * 4), '-' if ro is None else str(ro), '-' if cb is None else {0: 'ISR', 1: 'process'}.get(cb, str(cb)),
                        ack, u, ('INACTIVE: static entry beyond mbox_total_number=%d' % MCU_N) if (P == 'MCUPM' and cid >= MCU_N) else 'active', src, conf])
for (P, k), v in users.items():
    if isinstance(k, str): out.append([P, '-', k[5:], 'AP->%s' % P, '-', '-', '-', '-', '-', '-', '-', 'unresolvable: name absent from DT', '; '.join(sorted(v)), 'INERT: gpueb_get_send_PIN_ID_by_name()=-1, caller returns early', 'call site', 'high (static)'])
    elif P == 'SAP' or (P in procs and k not in {p['id'] for p in procs[P][0]} | {p['id'] for p in procs[P][1]}):
        nm_ = procs[P][2].get(k, '?') if P in procs else '?'
        why = 'SAP ipidev never registered (no SAP DT node): IPI_DEV_ILLEGAL' if P == 'SAP' else 'id not in board pin table: register/send return IPI_UNAVAILABLE (-3)'
        out.append([P, str(k), nm_, 'unconfigured', '-', '-', '-', '-', '-', '-', '-', why, '; '.join(sorted(v)), 'INERT', 'call site', 'high (static)'])
with open(OUT, 'w') as f:
    f.write('\t'.join(hdr) + '\n')
    for o in out: f.write('\t'.join(o) + '\n')
for P, (s, r, n, src) in procs.items(): print(P, 'send', len(s), 'recv', len(r), 'ids', len({p['id'] for p in s} | {p['id'] for p in r}))
print('rows', len(out))
