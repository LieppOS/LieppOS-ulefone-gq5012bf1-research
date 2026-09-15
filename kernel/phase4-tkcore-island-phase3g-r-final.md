# GQ5012BF1 TrustKernel Phase 3G-R — final result

## PHASE

1. classification: `PHASE3G_R_C0_LOCAL_VBMETA_BOOT_BLOCKED`
2. starting research HEAD: `8e53f501e14b6e391ac4758deed6a4a064595b91`
3. final research HEAD: report from final committed repository state

## PREVIOUS TRIAL

4. previous candidate retired: **YES**
5. source tkcore in previous candidate: **YES**
6. source tkcore_drv in previous candidate: **NO — STOCK**
7. source tmem_ffa in previous candidate: **YES**
8. previous candidate static ABI-valid: **NO — stock tkcore_drv incompatible on 7/11 tkcore edges**

## C0

9. C0 vbmeta SHA: `46a6ec3b1572db72fb090e2fe68dbb0297a64b7dac825bf94ff488aff3640b18`
10. C0 descriptor semantic differences count: `0`
11. C0 changed payload modules count: `0`
12. C0 write result: **PASS — exact candidate readback; later restored stock-exact**
13. C0 boot result: **FAIL — no ADB/Fastboot in 300 seconds; manual bootloader recovery required**
14. C0 Slot-B identity proven: **NO**
15. local top-level test-key accepted: **NO**

## C1 ARTIFACTS

16. packaged tkcore SHA: **NOT BUILT — C0 FAIL**
17. packaged tkcore_drv SHA: **NOT BUILT — C0 FAIL**
18. packaged tmem_ffa SHA: **NOT BUILT — C0 FAIL**
19. executable parity result: **BLOCKED — C0 FAIL**
20. 19-edge result: **BLOCKED — C0 FAIL**
21. blocked edges: **NOT MEASURED FOR C1; C1 FORBIDDEN**
22. stock tkcore witnesses: **NOT MEASURED FOR C1; C1 FORBIDDEN**

## C1 IMAGES

23. vendor_boot SHA: **NOT CONSTRUCTED**
24. vendor_dlkm SHA: **NOT CONSTRUCTED**
25. vbmeta SHA: **NOT CONSTRUCTED**
26. changed module payload count: **N/A**
27. changed module names: **N/A**
28. load-order result: **NOT PERFORMED**
29. AVB verification result: **NOT PERFORMED**

## C1 DEVICE

30. C1 writes verified: **NO — NO C1 WRITES**
31. B boot result: **NOT ATTEMPTED**
32. actual boot slot: **N/A**
33. A preserved: **YES**
34. B fallback occurred: **N/A FOR C1; C0 required manual bootloader recovery**

## G1

35. tkcore loaded: **NOT TESTED**
36. tkcore_drv loaded: **NOT TESTED**
37. tmem_ffa loaded: **NOT TESTED**
38. loaded artifact hashes exact: **NOT TESTED**
39. Unknown symbol count: **NOT OBSERVED / G1 NOT REACHED**
40. version-disagreement count: **NOT OBSERVED / G1 NOT REACHED**
41. module-load failure count: **NOT OBSERVED / G1 NOT REACHED**

## SAFETY

42. A partition writes: `0`
43. super resize: `0`
44. verification disabled: **NO**
45. bootloader relocked: **NO**
46. RPMB writes: `0`
47. NVRAM/persist/calibration writes: `0`
48. boot attempts C0: `1`
49. boot attempts C1: `0`

## ROLLBACK

50. final active slot: **A**
51. A bootable/successful: **YES / YES**
52. B final status: **bootable / not successful**
53. stock backups retained: **YES**

Final restored hashes:

- `vendor_boot_b`: `c8953d16b7a47976362aa23b53d0a08dde451f25cab4c552fa70c43e56ee0756`
- `vendor_dlkm_b`: `fce7acfb64956126a03929f085050ab1b300272333e84abf27b9e708aaa40297`
- `vbmeta_b`: `e14e11e184950d487b31def17a349f4f161e34988825bf35d85fc9bd6c3bde93`

## RESEARCH

54. authoritative reports:
    - `kernel/phase4-tkcore-island-phase3g-r-diagnosis.md`
    - `kernel/phase4-tkcore-island-phase3g-r-c0-vbmeta.md`
    - `kernel/phase4-tkcore-island-phase3g-r-c0-descriptor-diff.tsv`
    - `kernel/phase4-tkcore-island-phase3g-r-C0-result.md`
    - `kernel/phase4-tkcore-island-phase3g-r-c0-blocker.md`
    - `kernel/phase4-tkcore-island-phase3g-r-results.tsv`
    - `kernel/phase4-tkcore-island-phase3g-r-final.md`
55. final research commit: report from final committed repository state

## Required terminal classification

**PHASE 3G-R: LOCAL TOP-LEVEL VBMETA BOOT CONTROL FAILED**

**TRUSTKERNEL RUNTIME: NOT TESTED**

**CORRECTED C1: NOT ATTEMPTED**

**NEXT: AVB / SLOT-B BOOT-CHAIN DIAGNOSIS**

**STOP.**
