# Remaining stock-vs-rebuild differences

## Result

All 16 modem-related stock modules reproduce exactly except for the 20-byte `.note.gnu.build-id`
descriptor in each file:

* **1,055 / 1,055 functions byte-identical**
* **730 / 730 data objects byte-identical**
* all imports, exports, modversions, export CRCs, `.modinfo`, vermagic and section sizes exact
* all KCFI instructions/type ids inside function bytes exact
* whole-file comparison: 20 differing bytes/module, **0 differing bytes outside build-id**

The stock build-id was computed before debug stripping and depends on build-host paths in DWARF.
Those paths are unavailable and have no runtime effect. This is a fully explained build artifact,
not a source/behavior difference.

## Source selection differences (resolved)

* CCCI/eccci must use MTK `fae67a9257dc`, not branch tip 957dac1.
* Nothing commit 6df320423600 adds a `MODEM_DUMP_FLAG` uevent block absent from stock. Applying
  `../reconstruction/eccci-6df320423600-revert-nothing-modem-dump-flag.patch` restores the MTK tree.
* `mtk_ccci_common.h` must include `SMEM_USER_MD_POST_DUMP=46` from the same MTK revision.
* ccmni/rps/mddp/mdpm/md_cooling/C2K USB use the older 957dac1 component trees.
* MD power throttling uses the newer 6df320423600 six-level implementation already reconstructed
  by the connectivity pass.

Per-module evidence is under `per-module/`; aggregate logs are `rebuild-all-parity.txt` and the
three TSVs in this directory.
