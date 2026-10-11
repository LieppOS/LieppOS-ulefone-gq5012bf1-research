# Category-C closure checkpoint — 8 accepted, 10 unresolved

**The 18/18 mission is not complete.** All 18 frozen identities are tracked; eight have
independent strict Category-A evidence, none are relabeled B, and ten retain C blockers.
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
| tkcore.ko | C | only 5/19 consumer CRC edges reproduced; 14 private-type CRC edges | Recovered pinned ZTE public TKCore 3.2p3 source (52 verified blobs); layout probe shows tee 0x158/context 0xc8 versus stock 0x138/0xd0; not a compatible drop-in. | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |
| yft_devinfo.ko | C | 10 exported device_add CRCs + 11 KCFI IDs differ; provider enum/type graph; probe/sysfs codegen | Bounded experiments complete; genuine residual retained | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |
| aw883xx_driver.ko | C (pending) | 235/236 raw functions exact; aw883xx_dev_cfg_load 3560 B stock vs 3564 B best experimental build; complete ELF remains unaccepted | 90 type-grid candidates plus targeted structural variants: no acceptance | Inherited only; no new accepted B1/B2 | NOT ACCEPTED | C |
| bluetooth.ko | C (pending) | GNU build-ID only (allowed) | Public-source OEM split-BTF base | PASS independent B1/B2; GNU20-normalized identity | PASS | A |
| cfg80211.ko | C (pending) | GNU build-ID only (allowed) | Public-source OEM split-BTF base | PASS independent B1/B2; GNU20-normalized identity | PASS | A |
| mac80211.ko | C (pending) | GNU build-ID only (allowed) | Public-source OEM split-BTF base | PASS independent B1/B2; GNU20-normalized identity | PASS | A |

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
historical constraints, not an accepted replacement; see LEGACY-C-RECONSTRUCTION.md.

BLOCKERS.tsv has a next experiment for every remaining C. C-CLOSURE-STATE.json is the
resumption checkpoint. Continue a genuinely new authentic source/header/helper-composition
investigation; do not repeat completed grids or normalize missing OEM metadata.

## Audit status and projected counts

Canonical at f61ebf03 remains A244 B1 C14 D91 E0 F0 G108: 245 certified / 213 remaining.
With the pending audio/connectivity deltas and these eight closures, projected only:
A289 B1 C10 D91 E0 F0 G67: 290 certified / 168 remaining / 458 total.
Concurrent other-family work is excluded until reconciled. AUDIT-DELTA.tsv supplies exact
field preconditions for eight identities; it is not applied. MERGE-INSTRUCTIONS.md requires
inventory repair/validation, current-HEAD reconciliation, owner-reviewed regeneration and
unchanged validator/mutation acceptance. No stale audit replacement or push.
