# DW9781C-OIS — status

**DONE (static, 2026-10-07).** Closure: `README.md`; corrections: `stale-claims.md`.

| criterion | result |
|---|---|
| lineage | DIRECT_SOURCE_MATCH (NothingOSS MT6878 `dw9781c.c`, unmodified) |
| parity | stripped stock `.ko` identical except 20-byte build-id; B1==B2 |
| interfaces | DT, I2C 0x0A, regulators/pins/clocks, V4L2 subdev ioctls, hf_manager OIS1 mapped |
| stock consumers | none reach the chip (Dummy `ois_list`; no `availableOisModes`=5; no S_OIS_INIT/UNINIT users) |
| boundary | physical population/lens (hardware only); on-chip firmware |

## Workspace move (2026-10-07)

`Reverse Engineer - PARTIAL/DW9781C-OIS` → `Reverse Engineer - DONE/DW9781C-OIS`
(moved, not copied). README regenerated; `notes/{research-README,stale-claims,CLASSIFICATION-CHANGE}.md`,
`binary-analysis/{dw9781c-parity.*,b1-b2-build.txt,dw9781c-*-reachability.*}`
and `scripts/` copied in; `notes/ois-vcm-lens-mapping.md` and
`notes/dw9781c-ois-exact-source-and-ownership.md` refreshed from research.
`REVERSE-ENGINEERING-STATUS.md`: PARTIAL row replaced by DONE row, log entry,
totals **81 DONE / 49 PARTIAL / 3 BLOCKED / 0 TODO** (133). `COPY-MANIFEST.tsv`:
the 4 old rows re-pathed and re-hashed, 17 rows added (including the 5 pack files
that had never been registered). `manifest-audit.py`: rows 4000/4000 resolved,
hash/size drift unchanged at the 19 pre-existing rows in 5 other components,
unregistered 495→490 (DW9781C-OIS now 0), status counts 81/49/3/0.
