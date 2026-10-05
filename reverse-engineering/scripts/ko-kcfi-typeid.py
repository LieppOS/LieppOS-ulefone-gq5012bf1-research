#!/usr/bin/env python3
"""Clang KCFI type-id oracle (Android clang 17 / -fsanitize=kcfi).

A KCFI-instrumented function is preceded by the 32-bit constant

    type_id = xxHash64(itanium_mangled_type_string) & 0xffffffff

where the mangled string for a C function type `R f(A, B)` is
`_ZTSF<R><A><B>E` (parameter *names* are not part of it).  That makes every
indirect-call-target prologue in a stock .ko an independent 32-bit constraint
on the *exact* prototype of that function - including the spelling of named
enum / struct / union parameter types, which MODVERSION CRCs cannot isolate.

Verified against the stock GQ5012BF1 yft_devinfo.ko:
    _ZTSFiPciE            -> 0x4d9b0091   int  f(char *, int)
    _ZTSFiP10i2c_driveriE -> 0xd21592a3   int  f(struct i2c_driver *, int)
    _ZTSFvPciE            -> 0x6a3c623b   void f(char *, int)      (stock)
    _ZTSFvP8seq_fileE     -> 0x9831c2fc   void f(struct seq_file *)(stock)

Usage:  from kcfi_typeid import kcfi; hex(kcfi("_ZTSFiPciE"))
"""
M=(1<<64)-1
P1=11400714785074694791;P2=14029467366897019727;P3=1609587929392839161;P4=9650029242287828579;P5=2870177450012600261
def rotl(x,r): return ((x<<r)|(x>>(64-r)))&M
def rnd(acc,inp): acc=(acc+inp*P2)&M; acc=rotl(acc,31); return (acc*P1)&M
def merge(acc,val): val=rnd(0,val); acc^=val; return (acc*P1+P4)&M
def xxh64(b,seed=0):
    import struct
    n=len(b); i=0
    if n>=32:
        v1=(seed+P1+P2)&M; v2=(seed+P2)&M; v3=seed; v4=(seed-P1)&M
        while i+32<=n:
            a,bb,c,d=struct.unpack_from('<4Q',b,i); v1=rnd(v1,a); v2=rnd(v2,bb); v3=rnd(v3,c); v4=rnd(v4,d); i+=32
        h=(rotl(v1,1)+rotl(v2,7)+rotl(v3,12)+rotl(v4,18))&M
        h=merge(h,v1);h=merge(h,v2);h=merge(h,v3);h=merge(h,v4)
    else: h=(seed+P5)&M
    h=(h+n)&M
    while i+8<=n:
        k=struct.unpack_from('<Q',b,i)[0]; h^=rnd(0,k); h=(rotl(h,27)*P1+P4)&M; i+=8
    if i+4<=n:
        k=struct.unpack_from('<I',b,i)[0]; h^=(k*P1)&M; h=(rotl(h,23)*P2+P3)&M; i+=4
    while i<n:
        h^=(b[i]*P5)&M; h=(rotl(h,11)*P1)&M; i+=1
    h^=h>>33; h=(h*P2)&M; h^=h>>29; h=(h*P3)&M; h^=h>>32
    return h
def kcfi(s): return xxh64(s.encode())&0xffffffff
