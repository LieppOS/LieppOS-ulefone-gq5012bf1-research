# Category-C closure checkpoint — 8 accepted, 12 unresolved

**The expanded 20-target mission is not complete.** All 18 original identities and the
separate two-DRM amendment are tracked; 8 have independent strict
Category-A evidence, none are relabeled B, and 12 retain C blockers.
No canonical audit, phone, stock image, firmware/calibration, runtime module, secure world,
or remote Git repository was modified. This is an isolated local research checkpoint.

## All selected identities

“Initial C (pending)” refers to a canonical G row that becomes C under its pending family
delta; it is not claimed to have already been canonically integrated.

| Module | Initial | Exact remaining issue | Source reconstruction/fix | B1/B2 | Whole stock | Final |
|---|---|---|---|---|---|---|
| charger_class.ko | C | srcversion only (90/90 functions, data 20/21: __UNIQUE_ID_srcversion) | No stock srcversion hits for four scanned modules; tcpc_class retains inherited traced source-provenance blocker. | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |
| cmdq-platform-mt6878.ko | C | GNU build-ID only (allowed) | Microtrust visibility/config correction | PASS independent B1/B2; GNU20-normalized identity | PASS | A |
| cmdq-sec-drv.ko | C | GNU build-ID only (allowed) | Microtrust visibility/config correction | PASS independent B1/B2; GNU20-normalized identity | PASS | A |
| cmdq-test.ko | C | GNU build-ID only (allowed) | Microtrust visibility/config correction | PASS independent B1/B2; GNU20-normalized identity | PASS | A |
| focaltech_touch_spi_ft3680.ko | C | 40 functions size-different; opcode/call-boundary differences; recipe incomplete | Bounded experiments complete; genuine residual retained | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |
| mtk-cmdq-drv-ext.ko | C | GNU build-ID only (allowed) | Microtrust visibility/config correction | PASS independent B1/B2; GNU20-normalized identity | PASS | A |
| mtk_chg_type_det.ko | C | srcversion only (8/8 functions, data 20/21) | No stock srcversion hits for four scanned modules; tcpc_class retains inherited traced source-provenance blocker. | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |
| rt_pd_manager.ko | C | srcversion only (11/11 functions, data 19/20) | No stock srcversion hits for four scanned modules; tcpc_class retains inherited traced source-provenance blocker. | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |
| st21nfc.ko | C | 22/24 raw function matches; relocation/semantic acceptance not demonstrated; recipe incomplete | Historical object baseline reproduced 24/24; 28 authentic blob pairs tested (4 compile, 24 incompatible I2C probe API); no ioctl/ping hits. | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |
| tcpc_class.ko | C | srcversion only after closure (709/709 functions, 113/114 data, 54 timers exact) | No stock srcversion hits for four scanned modules; tcpc_class retains inherited traced source-provenance blocker. | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |
| tcpc_mt6375.ko | C | srcversion + __COUNTER__-numbered .modinfo/addressable objects (66/66 functions, data 21/28) | No stock srcversion hits for four scanned modules; tcpc_class retains inherited traced source-provenance blocker. | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |
| thermal-generic-adc.ko | C | GNU build-ID only (allowed) | Public-source OEM split-BTF base | PASS independent B1/B2; GNU20-normalized identity | PASS | A |
| tkcore.ko | C | only 5/19 consumer CRC edges reproduced; 14 private-type CRC edges | ZTE3.2p3 layout rejects drop-in;two pinned Vivo3.2p8 trees retain all10 old struct blocks;UMIDIGI/kernel/vendor scopes yield no matching newer header;eight stock provider/consumer occurrences have no BTF/debug sections. | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |
| yft_devinfo.ko | C | 10 exported device_add CRCs + 11 KCFI IDs differ; provider enum/type graph; probe/sysfs codegen | Bounded experiments complete; genuine residual retained | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |
| aw883xx_driver.ko | C (pending) | 235/236 raw functions exact; aw883xx_dev_cfg_load 3560 B stock vs 3564 B best experimental build; complete ELF remains unaccepted | 90 type-grid candidates plus targeted structural variants: no acceptance | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |
| bluetooth.ko | C (pending) | GNU build-ID only (allowed) | Public-source OEM split-BTF base | PASS independent B1/B2; GNU20-normalized identity | PASS | A |
| cfg80211.ko | C (pending) | GNU build-ID only (allowed) | Public-source OEM split-BTF base | PASS independent B1/B2; GNU20-normalized identity | PASS | A |
| mac80211.ko | C (pending) | GNU build-ID only (allowed) | Public-source OEM split-BTF base | PASS independent B1/B2; GNU20-normalized identity | PASS | A |
| drm_display_helper.ko | C (pending) | Split-BTF type/name references only; all non-BTF/GNU20 bytes exact in Codex B1/B2 | Verified amendment at source425ffd; shared OEM BTF reconstruction is the new executable hypothesis; not certified yet. | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |
| drm_dma_helper.ko | C (pending) | Split-BTF type/name references only; all non-BTF/GNU20 bytes exact in Codex B1/B2 | Verified amendment at source425ffd; shared OEM BTF reconstruction is the new executable hypothesis; not certified yet. | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |

## Resolved root causes

1. Four CMDQ modules: Microtrust header visibility from a generic vendor configuration
   contaminated recursive genksyms type graphs. The recovered board config removes it;
   Trustonic stays enabled for genuine provider source. Natural CRC/counter metadata match.
2. Four BTF modules: public GKI base was the wrong split-BTF lineage. Pinned NothingOSS MTK
   ACK, vendor configuration, Kleaf flags, OEM release-string length and pahole reproduce
   exact base BTF. No BTF copying, rewriting or extra normalization.

Source changes and exact tested/final commits: SOURCE-CHANGES.tsv and SOURCE-PINS.tsv.
Fresh-clone/source/bundle and intermediate comparisons: BUILD-REPRODUCTION.md.
Raw/semantic function/data/ABI/section/relocation evidence: evidence/ family ledgers.

## Checks

- CMDQ 35/35 joint B1/B2 accepts, 40/40 mutation checks; 120 debug-stripped objects exact.
- Connectivity 17/17 B1/B2 accepts, 44/44 mutation checks; 577 raw objects exact.
- Thermal 34/34 B1/B2 accepts, 11/11 mutation checks; 130 debug-stripped vendor objects
  and separately checked native intermediates; BTF identical, not complete base vmlinux.
- All compared configs and natural symvers match (text workspace-path normalization only).
- Recovery bundles verified; documentation-only post-build commits distinguished explicitly.
- Unchanged isolated inventory validator: 458 identities / 471 occurrences, zero errors;
  its 14 mutation/regression checks pass. evidence/inventory-validation.json records the
  canonical baseline counts, not a silently promoted audit.

## Unresolved findings and next actions

Public NothingOSS/MiCode searches found no stock fingerprints in 1100 + 4443 four-module
USB candidate combinations. This is a bounded history/one-file-variation search, not all
possible OEM source or a full multi-input Cartesian product. TCPC's 709/709 code and 54
recovered timers remain intact; srcversion/counter/source composition remain blockers.
AW883XX's diagnostic best still has one mismatching function (3564 vs stock3560), despite
235/236 raw matches and equal total file size. All 90 grid attempts and 97 source variants
are preserved, not certified. Historical ST21 flags reproduce its preserved object, but
neither the public blob scan nor natural fingerprint scan closes ioctl/ping/OEM tokens.
FT3680, YFT private enum/type graph and TrustKernel private CRC declarations remain open;
no new accepted source release was recovered for them. A public ZTE TKCore 3.2p3 release
was recovered at b0c0f1ec4cb6d616090e7879a7df0785a1323c5d (52 verified source blobs).
A compile-only layout probe proves it is not the newer stock 6:1.1-k6.6 declaration
lineage: tee 0x158 versus stock0x138, context0xc8 versus stock0xd0. It supplies authentic
historical constraints, not an accepted replacement. A further two pinned Vivo3.2p8
publications preserve the same10 core struct blocks (57 recovered blobs); the inspected
UMIDIGI kernel/vendor scopes supply no matching newer normal-world header. Four stock
provider/consumer identities (eight occurrences) have no BTF/debug sections to expose
member names. No redundant layout build or C promotion followed; see
LEGACY-C-RECONSTRUCTION.md and scripts/validate-legacy-search.py.

BLOCKERS.tsv has a next experiment for every remaining C. C-CLOSURE-STATE.json is the
resumption checkpoint. Continue a genuinely new authentic source/header/helper-composition
investigation; do not repeat completed grids or normalize missing OEM metadata.

## Audit status and staged reconciliation

Original canonical baseline f61ebf03 is retained for the unchanged owner-CAS delta.
The resume record compares actual canonical and both Codex staging commits by immutable
identity. No staging research or canonical audit is merged or edited here. The eight
previous promotions and any DRM promotions are applied only to the staged identity map
for the projected counts below, not silently to the canonical table. Owner integration
must regenerate field preconditions against its actual HEAD; no stale audit replacement.

Verified Codex staged baseline: {'commit': '437ebd5762afa2512fe1ba10102e6b4f4d6beba9', 'counts': {'A': 323, 'D': 60, 'G': 54, 'C': 20, 'B': 1}, 'existing_A_overlap': [], 'closure_classes': {'charger_class.ko@0c5bd394088d109c569cf5803a82edd0f182bad53714c284f99a797c76cf4e94': 'C', 'cmdq-platform-mt6878.ko@b19db2ed44e9102e58851d2a9faba599e899fabc52071b65fcc1b069908df625': 'C', 'cmdq-sec-drv.ko@3ac1eab54f0e9d9455cb3d184bc07edd2fb02924a6db408b2b1db323105e0ae3': 'C', 'cmdq-test.ko@0b89a6428bed00b661f00296ca22cf6a5e69edafbcd4b201fe4b73942902e668': 'C', 'focaltech_touch_spi_ft3680.ko@6629ec6148ac361a5f0085b8b19efa9d591426679f58262c4998345f41931162': 'C', 'mtk-cmdq-drv-ext.ko@b23648bcd8e09e4eff391e59eee17a7400896fb040967a83908dd95691542a49': 'C', 'mtk_chg_type_det.ko@8b8922f5bd6a2aea2f512e9b38bae19475f62ae27492bd9ea74c19cb1d4e4a5d': 'C', 'rt_pd_manager.ko@b82517127d6360f600e60d2b39d4970c61eab4263e7da67ee28fc5c94cb6715a': 'C', 'st21nfc.ko@5c5945457f8e3f37744c95a98075278134a328590d27e00d38dd8de8261078e8': 'C', 'tcpc_class.ko@2426edb571f5f8c2c1317b618fe6c10a095a59cf17acdd4d17ef583f63b5b5c5': 'C', 'tcpc_mt6375.ko@30abac643ebc7428a5ff350741d22b0f4bdcf65a5a071f55ec7ba78d862ca750': 'C', 'thermal-generic-adc.ko@d1a827e499d45203cfbb30fe8b8c6d7d8e60a6f60c42f5754d7ebd3e6dabc3dd': 'C', 'tkcore.ko@03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226': 'C', 'yft_devinfo.ko@0d5e547e3e6c313c88695b2c8f9aae04398e3c8822f16d57dff6aea011f821fe': 'C', 'aw883xx_driver.ko@3bc4722c6550abb9cfd75d06602c2a1bff8d0b6af58708324479ef6a0d22c9b4': 'C', 'bluetooth.ko@2df021ea9d5b0563ad21029a8cab1ba43d392b12af460ff3f0f7c36372b282fa': 'C', 'cfg80211.ko@cb214010dffb3975f5330d9c263b955e353f25f69f6a083922f0de326b179851': 'C', 'mac80211.ko@7496ce42c408268b91dacf7a1114edda761902d6f620633f48753bddfc53aced': 'C', 'drm_display_helper.ko@5abc061d76bd3120f94d8c94811714765590a57a1a129672672bb6c3948f5ccf': 'C', 'drm_dma_helper.ko@241827fc5faafc7bb47ca7d43fe1f318d4aec2d71793a0c3b365dcfa1f30145c': 'C'}}

Projected staged counts after this closure only: {'A': 331, 'D': 60, 'G': 54, 'C': 12, 'B': 1}

Accepted source proof and recovery inputs: BUILD-REPRODUCTION.md; additive scope receipt: C-CLOSURE-MANIFEST-AMENDMENT.tsv; recovered context: RESUME-DAEF94C6.md.
