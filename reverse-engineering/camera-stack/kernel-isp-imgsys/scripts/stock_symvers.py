#!/usr/bin/env python3
"""Build a Module.symvers from the exports of every stock vendor module.

CRCs come from the stock exporters' __kcrctab, so consumers rebuilt against
this file record exactly the stock modversions.  Module column = file stem
(what modpost writes into depends=).  Overrides (symbol -> module) let
us model build-time providers that were not shipped (e.g. the
mtk_ccu / mtk_ccu_mssv remoteproc modules whose names appear in stock
depends= although only mtk_ccuv.ko ships).

usage: stock_symvers.py <out.symvers> <dups.tsv> [--override sym=mod ...] <ko>...
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from elfmini import Elf  # noqa: E402
import ko_inventory as I  # noqa: E402


def main():
    out, dups = sys.argv[1], sys.argv[2]
    ov = {}
    kos = []
    for a in sys.argv[3:]:
        if a.startswith("--override="):
            s, m = a.split("=", 1)[1].split(":")
            ov[s] = m
        else:
            kos.append(a)
    table = {}
    seen = {}
    for p in kos:
        try:
            e = Elf(p)
        except Exception:
            continue
        # modpost writes the *path stem* of the provider (Module.symvers module
        # column) into depends=, e.g. "custom-ldo" although modinfo name is custom_ldo
        name = os.path.basename(p)[:-3]
        gpl = "__ksymtab_gpl" in e.secbyname
        for sym, crc in I.exports(e):
            seen.setdefault(sym, []).append(name)
            # export type: look for the symbol in __ksymtab_gpl via section of __ksymtab_<sym>
            et = "EXPORT_SYMBOL_GPL"
            ks = next((s for s in e.symbols if s.name == "__ksymtab_" + sym), None)
            if ks is not None and 0 < ks.shndx < 0xFF00:
                sec = e.sections[ks.shndx].name
                et = "EXPORT_SYMBOL_GPL" if "gpl" in sec else "EXPORT_SYMBOL"
            elif not gpl:
                et = "EXPORT_SYMBOL"
            table.setdefault(sym, (crc, name, et))
    for s, m in ov.items():
        if s in table:
            c, _, et = table[s]
            table[s] = (c, m, et)
    with open(out, "w") as f:
        for s in sorted(table):
            c, m, et = table[s]
            f.write(f"{(c or 0):#010x}\t{s}\t{m}\t{et}\t\n")
    with open(dups, "w") as f:
        f.write("symbol\texporters\n")
        for s, ms in sorted(seen.items()):
            if len(ms) > 1:
                f.write(f"{s}\t{','.join(ms)}\n")
    print(len(table), "symbols;", sum(1 for v in seen.values() if len(v) > 1), "multiply exported")


if __name__ == "__main__":
    main()
