#!/usr/bin/env python3
"""Locate and decode the USB/UVC descriptor tables embedded in the Tiny2-C module firmware
(firmware_EXT.bin from the stock M170infDlp whole-package). Prints only descriptor fields
(no firmware code/data is emitted)."""
import sys, re
d = open(sys.argv[1], 'rb').read()
u16 = lambda b, o: int.from_bytes(b[o:o+2], 'little')
u32 = lambda b, o: int.from_bytes(b[o:o+4], 'little')
dev = d.find(bytes.fromhex('12010002ef020140'))
b = d[dev:dev+18]
print(f'@{dev:#x} DEVICE bcdUSB={u16(b,2):#06x} class={b[4]:02x}/{b[5]:02x}/{b[6]:02x} bMaxPacketSize0={b[7]} '
      f'idVendor={u16(b,8):04x} idProduct={u16(b,10):04x} bcdDevice={u16(b,12):#06x} iManufacturer={b[14]} '
      f'iProduct={b[15]} iSerialNumber={b[16]} bNumConfigurations(template)={b[17]}')
q = d.find(bytes.fromhex('0a060002'), dev)
b = d[q:q+10]
print(f'@{q:#x} DEVICE_QUALIFIER bcdUSB={u16(b,2):#06x} class={b[4]:02x}/{b[5]:02x}/{b[6]:02x} bMaxPacketSize0={b[7]} bNumConfigurations(template)={b[8]}')
iad = d.find(bytes.fromhex('080b00020e030002'), dev)
o = iad; total = 0
VC = {1: 'VC_HEADER', 2: 'VC_INPUT_TERMINAL', 3: 'VC_OUTPUT_TERMINAL', 5: 'VC_PROCESSING_UNIT', 6: 'VC_EXTENSION_UNIT'}
VS = {1: 'VS_INPUT_HEADER', 4: 'VS_FORMAT_UNCOMPRESSED', 5: 'VS_FRAME_UNCOMPRESSED', 0x0d: 'VS_COLORFORMAT'}
cur_sub = None
pad = 0
while o < len(d):
    L = d[o]; t = d[o+1] if L > 1 else None
    if L == 0 and pad < 3:
        pad += 1; o += 1; continue
    if L < 2 or t not in (0x0b, 0x04, 0x05, 0x24, 0x25): break
    if pad: print(f'   ({pad} byte(s) padding: separate firmware descriptor block)')
    pad = 0
    b = d[o:o+L]; total += L
    if t == 0x0b:
        print(f'@{o:#x} IAD first={b[2]} count={b[3]} class={b[4]:02x}/{b[5]:02x}/{b[6]:02x} iFunction={b[7]}')
    elif t == 0x04:
        cur_sub = b[6]
        print(f'@{o:#x} INTERFACE if={b[2]} alt={b[3]} nEP={b[4]} class={b[5]:02x}/{b[6]:02x}/{b[7]:02x} iInterface={b[8]}')
    elif t == 0x05:
        mps = u16(b, 4)
        tt = ['control', 'isochronous', 'bulk', 'interrupt'][b[3] & 3]
        sync = ['none', 'async', 'adaptive', 'sync'][(b[3] >> 2) & 3]
        print(f'@{o:#x} ENDPOINT addr={b[2]:#04x} ({"IN" if b[2]&0x80 else "OUT"}) attr={b[3]:#04x} {tt}/{sync} '
              f'wMaxPacketSize={mps:#06x} (size {mps&0x7ff}, {((mps>>11)&3)+1}x/uframe) bInterval={b[6]}')
    elif t == 0x25:
        print(f'@{o:#x} CS_ENDPOINT subtype={b[2]} wMaxTransferSize={u16(b,3)}')
    elif t == 0x24 and cur_sub == 1:
        s = b[2]; n = VC.get(s, f'VC_{s}')
        if s == 1:
            print(f'@{o:#x} {n} bcdUVC={u16(b,3):#06x} wTotalLength={u16(b,5)} dwClockFrequency={u32(b,7)} bInCollection={b[11]} baInterfaceNr={list(b[12:12+b[11]])}')
        elif s == 2:
            print(f'@{o:#x} {n} id={b[3]} wTerminalType={u16(b,4):#06x} assoc={b[6]} iTerminal={b[7]} '
                  f'objFocalMin={u16(b,8)} objFocalMax={u16(b,10)} ocular={u16(b,12)} bControlSize={b[14]} bmControls={b[15:15+b[14]].hex() or "-"}')
        elif s == 3:
            print(f'@{o:#x} {n} id={b[3]} wTerminalType={u16(b,4):#06x} assoc={b[6]} source={b[7]} iTerminal={b[8]}')
        elif s == 5:
            print(f'@{o:#x} {n} id={b[3]} source={b[4]} wMaxMultiplier={u16(b,5)} bControlSize={b[7]} bmControls={b[8:8+b[7]].hex()} iProcessing={b[8+b[7]]}' + (f' bmVideoStandards={b[9+b[7]]:#04x}' if L > 9 + b[7] else ''))
        else:
            print(f'@{o:#x} {n} raw={b.hex()}')
    elif t == 0x24:
        s = b[2]; n = VS.get(s, f'VS_{s}')
        if s == 1:
            print(f'@{o:#x} {n} bNumFormats={b[3]} wTotalLength={u16(b,4)} bEndpointAddress={b[6]:#04x} bmInfo={b[7]} bTerminalLink={b[8]} '
                  f'bStillCaptureMethod={b[9]} bTriggerSupport={b[10]} bTriggerUsage={b[11]} bControlSize={b[12]} bmaControls={b[13:].hex()}')
        elif s == 4:
            g = b[5:21]
            print(f'@{o:#x} {n} formatIndex={b[3]} nFrames={b[4]} guid={g[:4].decode("latin1")}({g.hex()}) bpp={b[21]} defaultFrame={b[22]} aspect={b[23]}:{b[24]} interlace={b[25]} copyProtect={b[26]}')
        elif s == 5:
            n_int = b[25]
            ints = [u32(b, 26 + 4*i) for i in range(n_int)] if n_int else [u32(b, 26), u32(b, 30), u32(b, 34)]
            print(f'@{o:#x} {n} frameIndex={b[3]} caps={b[4]} {u16(b,5)}x{u16(b,7)} minBitRate={u32(b,9)} maxBitRate={u32(b,13)} '
                  f'maxVideoFrameBufferSize={u32(b,17)} defaultInterval={u32(b,21)} ({1e7/u32(b,21):.2f} fps) intervalType={n_int} intervals={ints}')
        elif s == 0x0d:
            print(f'@{o:#x} {n} primaries={b[3]} transfer={b[4]} matrix={b[5]}')
        else:
            print(f'@{o:#x} {n} raw={b.hex()}')
    o += L
print(f'descriptor bytes from IAD to end: {total}; + 9-byte configuration header (built at run time) = {total+9} = {total+9:#06x}')
for s in (b'Thermal Cam', b'202206223'):
    i = d.find(s); print(f'string @{i:#x}: {d[i:d.index(b"\0", i)].decode()}')
