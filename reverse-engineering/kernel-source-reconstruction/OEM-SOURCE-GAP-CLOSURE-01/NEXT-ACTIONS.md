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
