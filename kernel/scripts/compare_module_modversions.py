#!/usr/bin/env python3

import argparse
import subprocess
import sys


def dump(path):
    out = subprocess.check_output(
        ["modprobe", "--dump-modversions", path],
        text=True,
    )

    symbols = {}
    for line in out.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            crc, symbol = parts
            symbols[symbol] = crc.lower()

    return symbols


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stock")
    parser.add_argument("rebuilt")
    args = parser.parse_args()

    stock = dump(args.stock)
    rebuilt = dump(args.rebuilt)

    stock_names = set(stock)
    rebuilt_names = set(rebuilt)
    common = stock_names & rebuilt_names

    crc_diff = [
        s for s in sorted(common)
        if stock[s] != rebuilt[s]
    ]

    print(f"stock symbols:   {len(stock)}")
    print(f"rebuilt symbols: {len(rebuilt)}")
    print(f"common symbols:  {len(common)}")
    print(f"stock-only:      {len(stock_names - rebuilt_names)}")
    print(f"rebuilt-only:    {len(rebuilt_names - stock_names)}")
    print(f"CRC mismatches:  {len(crc_diff)}")

    if stock_names - rebuilt_names:
        print("\n===== STOCK ONLY =====")
        for symbol in sorted(stock_names - rebuilt_names):
            print(stock[symbol], symbol)

    if rebuilt_names - stock_names:
        print("\n===== REBUILT ONLY =====")
        for symbol in sorted(rebuilt_names - stock_names):
            print(rebuilt[symbol], symbol)

    if crc_diff:
        print("\n===== CRC MISMATCHES =====")
        for symbol in crc_diff:
            print(
                f"{symbol}\t"
                f"stock={stock[symbol]}\t"
                f"rebuilt={rebuilt[symbol]}"
            )

    if stock_names == rebuilt_names and not crc_diff:
        print("\nMODVERSION CONTRACT: EXACT MATCH")
        return 0

    print("\nMODVERSION CONTRACT: DIFFERENT")
    return 1


if __name__ == "__main__":
    sys.exit(main())
