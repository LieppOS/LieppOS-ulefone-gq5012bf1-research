# TKCORE-DRV — STATUS (2026-10-07)

**DONE (static, named scope: normal-world `tkcore_drv.ko` — TrustKernel TZ backend/transport —
and its DT, SMC/FF-A, shared-memory, RPC and ABI contract).**

`tkcore_drv.ko`: **50/50 functions byte-identical**, 18/18 data objects (29/29 incl. modinfo
symbols except srcversion), 66/66 imports, 67/67 modversion CRCs, 0/0 exports, KCFI 46/46
(all named), 717/717 relocations, 43/43 `__bug_table` entries incl. line numbers, strings
65+581 identical, `.modinfo` identical except `srcversion`; B1 == B2.
Whole-file difference: 41 bytes (srcversion 21, build-id 20).

Source: public TrustKernel 7:2.2 tree (anvil-kernel 8e1a0f39478f / 6b94428f) + reconstructed
6:1.1-era delta (`patches/0001`). Classification DONOR + PATCHES (srcversion not reproduced).

| closure item | state |
|---|---|
| stock module set | tkcore_drv.ko (this) + tkcore.ko (provider, TRUSTKERNEL-TEE) + ffa_v10.ko (FFA-V10); teeperf not TKCore (`module-set.tsv`) |
| source / reconstruction | complete, deterministic (`scripts/build_tkcore_drv.sh`) |
| functions / data / ABI / KCFI / relocations | exact (`parity/`) |
| DT / platform contract | `hardware-contract.md` — FF-A transport proven by SP manifest in `tee.img` + DT |
| ioctl → backend → secure call map | `ioctl-map.tsv`, `smc-map.tsv`, `normal-world-interface.md` |
| shared memory | `shared-memory.md` |
| userspace clients / RPMB | `userspace-clients.tsv`, `rpmb-boundary.md` |
| secure-world boundary | `secure-world-boundary.md` |
| YFT deltas | none (`yft-tkcore-deltas.md`) |
| residuals | srcversion (PATH/PROVENANCE), build-id, DWARF (`parity/residuals.md`) |

Not part of this scope (unchanged status): `tkcore.ko` reconstruction (BLOCKED components),
TrustKernel secure OS/TAs (proprietary), runtime validation (FF-A probe, SMC latency, RPMB
traffic) — none is a static blocker.
