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

## Workspace

Moved `Reverse Engineer - PARTIAL/TKCORE-DRV` → `Reverse Engineer - DONE/` on 2026-10-07
(index totals 76/54/3 → 77/53/3). Earlier notes and stock inventories kept; the September
behavioural source moved to `source/legacy-behavioural/`; closure files copied with
provenance (45 manifest rows); README, EVIDENCE-INDEX, PROVENANCE regenerated;
`notes/CLASSIFICATION-CHANGE.md` added; the TKCORE-DRV links in the BLOCKED
TRUSTKERNEL-TEE / TRUSTKERNEL-ABI-ISLAND READMEs re-pointed (only drift caused by the move).
manifest-audit: 3921/3921 rows resolve, trees 77/53/3, no drift in TKCORE-DRV (pre-existing
drift in 5 unrelated packs untouched).

## Note for STORAGE (not edited)

`reverse-engineering/storage/binary-analysis/teed-rpmb-ioctls.md` swaps two labels: the
`0xc008b301`/`0xc048b300` rows are the eMMC `MMC_IOC_MULTI_CMD`/`MMC_IOC_CMD` path and
`0xc01874a5`/`0xc01874a7` are tkcore `TEE_ALLOC_SHM_IOC`/`TEE_GET_FD_FOR_RPC_SHM_IOC`
(see `rpmb-boundary.md`).
