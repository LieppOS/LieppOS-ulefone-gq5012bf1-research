# Candidate vdcmd opcode recovery from the AC020 payload libraries

Tool: [`tools/extract-vdcmd-opcodes.py`](../tools/extract-vdcmd-opcodes.py)
Evidence: [`evidence/binaries/vdcmd-opcodes/`](../evidence/binaries/vdcmd-opcodes/)
Inputs (hash-pinned in [`evidence/binaries/SHA256SUMS.txt`](../evidence/binaries/SHA256SUMS.txt),
copied to `/tmp/ac020/` for analysis, verified byte-identical to the in-repo
stock copies under `workspace/gq5012bf1/stock/partitions/`):

| library | sha256 (first 16) | rows | candidate values | singly-claimed |
|---|---|---|---|---|
| `libircmd020.so` | `0aa7d5c751379281` | 63 | 13 | 2 |
| `libAC020sdk.so` | `332764f014cb4f26` | 47 | 13 | 3 |
| `libadvirtempac020.so` | `96af2cb2a087a8d3` | 16 | 7 | 2 |

Nothing here was observed on a device. `_get`/`_set` in a `helper` name is the
vendor's own export name, not an observed transaction direction.

## What a row claims — and what it does not

A row is **one candidate value per (exported helper, immediate)**: the helper
materialises that value from an immediate (`mov Wd, #imm`, `movw`, or the AArch64
`orr/add Wd, wzr, #imm` spelling) and the value's def-chain reaches a store inside
the helper. `status=unique` means exactly one exported helper in that library
reaches that value; `ambiguous` means several do.

That is the whole claim. **The row does not say which descriptor field the value
fills.** The vdcmd descriptor layout (u16 LE class at `+0x00`, u8 op with bit 7 as
read/write at `+0x02`, CRC16 slot at `+0x10`) is reconstructed separately in
[`re/protocol/vdcmd-uvc-transport.md`](../re/protocol/vdcmd-uvc-transport.md); a
store reached by this walk is not tied to a slot offset, so a row can equally be a
length, a gain, a mode value or an enum. `confidence` measures walk length only
(≤6 hops = high, ≤24 = medium, else low) and never runtime behaviour.

## Why the earlier table was thrown away

Three iterations of this extractor ran against the same pinned binaries, and the
first two over-claimed:

* **v1** (`out/opcodes-libircmd020.json`, `/tmp/ac020/out/opcodes.tsv`, 236 rows,
  `class/op/symbol/builder`) attached a class and an op to every row from a linear
  scan of wrapper prologues. The scan could not tell a descriptor store from any
  other store, so the pair column carried more confidence than the evidence did.
* **v2 first cut** emitted 286 rows for `libircmd020.so`, **248 of them from load
  terminals** — i.e. "the register this helper *loaded* was once written from an
  immediate", which proves nothing about a command being sent. Spot checks were
  unambiguous false positives: `adv_output_frame_rate 0x003C` from
  `cmp w21, #0x3c`, `adv_baudrate 0x00E1` from `cmp w1, #0xe1, lsl #12`,
  `basic_preview_info 0x000F` from `and w9, w9, #0xf`, and `0x0010` from
  `add x13, x29, #0x10` (a frame-pointer address computation).
* **v2 final** (committed) drops loads as terminals, records them as
  `load-terminal` notes, and adds def rules so a flag-setting op
  (`cmp`/`tst`/`subs`/…), a bit-test branch (`tbz`/`tbnz`, whose immediate is a bit
  index), or arithmetic on a live register (`offset-arithmetic`) can never close a
  chain. `mov`/`sxtw`-style value-preserving copies are followed through instead of
  stopping the walk, so recall did not collapse with the precision fix.

Boundary counts are the audit trail for that conservatism — for `libircmd020.so`:
3453 `load-terminal`, 610 `no-immediate-source`, 421 `value-from-memory`,
208 `offset-arithmetic`, 23 `opaque-def-add`, 18 `flag-setting-not-a-def`,
7 `partial-constant-movk`, 9 other `opaque-def-*` (6383 notes on
`libadvirtempac020.so`, 3406 on `libAC020sdk.so`). A chain that stops is written
down instead of becoming a claim.

## The only name-attributed candidates

Seven values are reached by exactly one exported helper in their library:

| value | library | sole exporting helper |
|---|---|---|
| `0x000E` | libircmd020 | `basic_device_info` |
| `0x0100` | libircmd020 | `basic_mirror_and_flip_status` |
| `0x000C` | libAC020sdk | `iruvc_usb_data_read` |
| `0x0050` | libAC020sdk | `probe_devices` |
| `0x0150` | libAC020sdk | `probe_devices` |
| `0x0280` | libadvirtempac020 | `new_ktbt_recal_double_point_calculate_in_change_lens` |
| `0x00C8` | libadvirtempac020 | `multi_point_calc_new_nuc_table_in_change_lens` |

The three in `libAC020sdk.so` and the two in `libadvirtempac020.so` sit in
transport/probe/KT-BT paths, where a stored immediate is more likely a size, table
index or scale than a command ID — which is exactly why the table above is a
shortlist for device-side correlation and not a command list. Do not put these in a
header as `VDCMD_OPCODE_*` constants; regenerate them from the binaries if a schema
is ever needed (see *Parked* below for why no generator is committed).

## Reproduce

```sh
L=../../workspace/gq5012bf1/stock/partitions/system/app/FactoryMode/lib/arm64
O=evidence/binaries/vdcmd-opcodes
for n in libircmd020 libAC020sdk libadvirtempac020; do
  M=$(md5sum $L/$n.so | cut -d' ' -f1)
  for f in tsv json; do
    python3 tools/extract-vdcmd-opcodes.py $L/$n.so --out $O/$n-opcodes.$f --format $f \
      --source system/app/FactoryMode/lib/arm64/$n.so --source-md5 "$M" --notes $O/$n-notes.json
  done
done
```

`llvm-objdump`/`llvm-nm` must be on `PATH` (this host: `/opt/bin`). The tool
refuses nothing on empty input, so check the printed row/id counts against the table
above rather than trusting a silent zero.

## Parked: two libraries this module cannot analyse yet

`analysis/wip/` holds work-in-progress that **is not evidence and is not wired into
the pipeline**, kept only so the method is not lost:

* `analyzer-opcodes.py` + `rms-device-analyzer.tsv` target `librms-device-analyzer.so`
  (`ProcessOpCodeReport`, the `rms.ic.<n>` / `rms.config.*` report dispatcher). That
  library is **not present** anywhere on this machine (checked: the whole `TIER3`,
  `SSD` and `WDBlue` trees, the in-repo `workspace/` stock partitions, the extracted
  FactoryMode APK payload set under `evidence/`), so the manifest's entry points could
  not be re-verified against `nm`. The tool refuses to run on a manifest it cannot
  check, and its hardcoded addresses stay untrusted until the binary is re-acquired.
* `gen-vdcmd-opcodes-header.py` and `gen-vdm-opcode-registry.py` generate headers that
  nothing compiles against, and the first one's preamble cited
  `libvdcmd_codec.so` (ELF 32-bit LSB, BuildID `fd84421b…`) — a library likewise
  **absent** from every corpus location, so its claims were unverifiable by
  construction. Its dense table also degenerates: with 7 defined names over a 12-bit
  ID space it would emit ~4090 hole comments, which is documentation noise, not a
  registry.

Both are blocked on inputs or a consumer, not on effort. Until then the TSV/JSON pair
plus this note are the whole artifact set.
