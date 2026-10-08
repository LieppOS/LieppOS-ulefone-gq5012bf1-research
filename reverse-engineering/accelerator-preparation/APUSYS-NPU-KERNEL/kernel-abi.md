# Kernel and userspace ABI — APUSYS-NPU-KERNEL

Binary acceptance proves the exact stock ABI, not merely matching prototypes:

* `apu_top.ko`: 180 import CRCs, 21 exports/buckets/CRCs, 19 KCFI IDs and 9,752 relocations exact;
* `apusys.ko`: 375 import CRCs, 11 exports/buckets/CRCs, 152 KCFI IDs and 46,647 relocations exact;
* every `.modinfo` record, alias, dependency, symbol/string table and compiler/vermagic record exact.

Thirteen non-GKI vendor import CRCs are generated from the actual public provider declarations during every clean build and checked against stock. Provider ownership remains external; see `dependencies.md` and `dependency-edges.tsv`. No CRC or KCFI constant is stamped into a built object.

The principal userspace surface is `/dev/apusys`, with native/compat `_IOWR('A',32..35)` handshake, memory, command and utility layouts. Its dma-buf/map/submit/fence/completion/error lifetime and the negotiated RPMsg firmware protocol are documented in `source-to-userspace-contract.md`. Exact source and full ELF equality together prove these layouts and handlers correspond to stock. Existence still does not prove a shipped service successfully executed them on this phone.

Complete occurrence-aware function/data, ABI, section and relocation ledgers are under `evidence/reconstruction/acceptance/`; the original preparation inventories remain as independent stock baselines.
