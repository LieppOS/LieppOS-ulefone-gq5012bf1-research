# GQ5012BF1 TinySys messaging transport: `mtk_rpmsg_mbox` + `mtk_tinysys_ipi`

This work was offline and static only. No adb, no IPI or mailbox traffic, no firmware contact. Inputs were stock modules, the existing live-DT capture, and public MTK/NothingOSS sources.

`mtk-mbox.ko` (the layer below) is already closed as DIRECT_SOURCE_MATCH (commit `a33f4e2`). It was **not** redone; it appears here only as a provider in the graph.

## Result

| module | functions | data | imports (CRC) | exports (CRC) | KCFI | relocations | sections | whole file |
|---|---|---|---|---|---|---|---|---|
| `mtk_rpmsg_mbox.ko` | **8/8** byte-identical | 11/11 (canonical) | 14/14 | 3/3 GPL | 8/8 | 57/57, raw-byte identical | 36/36, all content exact except build-id | identical after the 20-byte build-id is transplanted |
| `mtk_tinysys_ipi.ko` | **12/12** byte-identical | 11/11 | 28/28 | 10/10 | 12/12 | 279/279, raw-byte identical | 35/35 | identical after the build-id is transplanted |

- **Source:** unmodified MTK ALPS mt6878 `5e415e059253`; source blobs `82ec9c50d3` and `1acca98c7c`.
- **Lineage:** pinned by full-section parity. A later MiCode variant that is `.text`-identical is excluded by `__bug_table` line numbers.
- **Classification:** **DIRECT_SOURCE_MATCH, no YFT delta.** A clean rebuild B2 equals B1.
- **Remaining build-provenance difference:** `.note.gnu.build-id` only. Everything else matches exactly:
  - `__FILE__` strings, reproduced with `-fmacro-prefix-map`;
  - `vermagic` and the rest of `.modinfo`;
  - `.llvm_addrsig` (`-faddrsig`);
  - `.symtab`/`.strtab`, with symbol-index order equal, so RELA is raw-byte equal;
  - DWARF, which is stripped in both.

  The differing build-id is a hash over the pre-strip link output, which includes the DWARF `comp_dir` paths.

## Roles

- **`mtk_rpmsg_mbox`** wraps each TinySys processor's `mtk_mbox_device` as a GKI `rpmsg_device` with one endpoint per IPI id. Each endpoint resolves its id to a (mailbox, SRAM slot, size, IRQ pin) tuple. The module provides the one non-blocking TX primitive: busy-check → SRAM write → `mb()` → doorbell. It has **no RX path**, no IRQ, no PM and no init.
- **`mtk_tinysys_ipi`** is the IPI framework used by SCP, VCP, GPUEB and MCUPM. It provides:
  - per-id registration of receive buffers and callbacks;
  - WAIT (mutex, sleepable) and POLLING (spinlock, IRQs off) send modes, with busy-retry up to a deadline;
  - `send_compl` request/ACK on paired pins;
  - `recv`/`recv_reply`;
  - an ISR hook installed into mtk-mbox;
  - the IPIMonitor timestamps and timeout dumps.

## Map

| topic | document |
|---|---|
| inventory | [`kernel/module-inventory.tsv`](kernel/module-inventory.tsv) (14 TinySys-adjacent modules), [`kernel/source-map.tsv`](kernel/source-map.tsv) |
| rpmsg layer, function by function | [`kernel/mtk_rpmsg_mbox.md`](kernel/mtk_rpmsg_mbox.md) |
| IPI framework, function by function | [`kernel/mtk_tinysys_ipi.md`](kernel/mtk_tinysys_ipi.md) |
| parity (A = stock, B = rebuild) | [`kernel/parity/`](kernel/parity/) (canonical `ko-pair-parity`/`ko-residue-diff`/`ko-str-refs` + per-axis TSVs), [`kernel/parity/lineage-and-whole-file.txt`](kernel/parity/lineage-and-whole-file.txt) |
| dependency graph (102 edges, CRC + KCFI) | [`dependency-graph.md`](dependency-graph.md), [`kernel/dependency-edges.tsv`](kernel/dependency-edges.tsv) |
| processors: capability vs enablement | [`processors.md`](processors.md) |
| wire/shared-memory structures | [`protocol/ipc-structures.md`](protocol/ipc-structures.md) |
| channel map (SCP 36, VCP 28, GPUEB 11, MCUPM 8 ids) | [`protocol/ipi-channel-map.md`](protocol/ipi-channel-map.md), [`protocol/ipi-channel-map.tsv`](protocol/ipi-channel-map.tsv), [`protocol/callsite-census.tsv`](protocol/callsite-census.tsv) |
| YFT deltas | [`yft-tinysys-deltas.md`](yft-tinysys-deltas.md) |
| rebuild recipe, exact sources | [`reconstruction/`](reconstruction/), [`scripts/`](scripts/) |
