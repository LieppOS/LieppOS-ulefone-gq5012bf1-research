# Next actions

1. **Owner: integrate tmem_ffa C→A** via `MERGE-INSTRUCTIONS.md`, giving 422/458 certified.
2. **User: review and decide on sending the request drafts.**
   - Before sending, check the device packaging and Ulefone's website for an existing GPL source offer.
   - The highest-yield request is the Ulefone full vendor-module tree, which covers up to 24 modules.
3. **Codex batch-02:** read `HANDOFF-TO-CODEX.md`. The TrustKernel provider CRCs for `tkcore_drv` and
   `microarray_fp_tee` are now natural with patch 0002. Whether the armtz `named_shm` use is also absent in stock
   `tkcore_drv` is Codex's to verify.
4. **Highest-value next source-recovery assignment:** `tkcore.ko`.
   - The declarations are closed, and 103/122 functions plus 25/25 exports already match.
   - The remaining 19 functions need authentic 6:1.x text.
   - Watch for any other TrustKernel 5.x/6.x public import. A useful search key is
     `tkcore_nsdrv_version "6:` or `"5:`, plus `large_cluster_id` / `plat_cpu_is_big`.
   - Test only declarations and functions such a release actually contains, using `scripts/tk-genksyms.py` and
     the build1 recipe.
5. **Richtek/MediaTek srcversion family** (5 C rows): any authentic exact copy of the shipped files closes them
   immediately. Test srcversion only; the code is already exact.
6. **No further generic searching** for flashlight, the shipped objects or the 11 unowned G drivers without a
   new, distinct source lead.

## Reconciliation with Codex batch-02 (observed at end of session; read-only)

Codex committed `aa212a88`, "complete12 non-display sources, 7 independent A / 5 honest C". It uses the same
manifest `6f78615b`, and its AUDIT-DELTA covers exactly its 12 identities. It does **not** touch `tmem_ffa` or
`tkcore`, so it is disjoint from this package's 14-field delta.

| Class | A | B | C | D | E | F | G | Certified |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Canonical now (`4e47a5b9`) | 420 | 1 | 11 | 3 | 0 | 0 | 23 | 421 |
| + this package (tmem_ffa C→A) | 421 | 1 | 10 | 3 | 0 | 0 | 23 | 422 |
| + Codex batch-02 (7 G→A, 5 G→C), identity-disjoint | 428 | 1 | 15 | 3 | 0 | 0 | 11 | **429/458** |

Codex reports `tkcore_drv` as C with 50/50 functions and import CRC residuals on `__tee_get`/`tee_core_add`/….
Those are the `tkcore.ko` exports this package reproduces naturally (25/25), so applying patch 0002 to Codex's
provider witness is the direct next test (`HANDOFF-TO-CODEX.md`).
