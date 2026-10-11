# Four legacy identities — no artificial DONE → A inference

The frozen inventory selects these exact filenames/hashes, not inferred subsystem names:
`focaltech_touch_spi_ft3680.ko`, `yft_devinfo.ko`, `st21nfc.ko`, `tkcore.ko`.
All four remain C. The following are bounded findings and inherited blockers, not fresh
whole-module acceptance or claims of missing firmware/trusted-world reconstruction.

## ST21 NFC: new bounded experiment

The preserved full historical module has 22/24 raw functions exact; ioctl and ping differ,
and stock srcversion is `B6AF553DA6B3CC90D31F110`, versus reconstruction
`228FE134076AA5BBB4F04FA`. The historical ping is 656 bytes versus stock 644;
ioctl has equal size 1440 but differing bytes.

An initial build under the current generic vendor CMDQ environment produced only 6/24
raw matches (25 emitted functions); it is not a meaningful regression of the historical
reconstruction. The configuration/flags differ. Replaying the preserved historical
compiler command with pinned clang and **private source/dependency/object outputs**
reproduced all 24/24 historical object bodies. No historical files were changed.
That baseline still has 22/24 stock bodies exact.

All distinct public C/header combinations from the fetched NothingOSS/MiCode histories
were tested under that reproduced command: union 7 C blobs × 4 headers = 28 pairs.
Four compiled; 24 were rejected because their one-argument I2C probe does not match the
historical two-argument kernel API. No compiling pair matched either ioctl or ping.
The object-level results contain full blob/commit provenance and diagnostics. They do
not constitute full linked module acceptance. A separate modpost fingerprint scan found
no stock digest in 20 NothingOSS + 28 MiCode pairs.

Evidence: `evidence/st21nfc/`. Next: recover a new authentic OEM/ST revision or matching
historical API/configuration lineage; then close both bodies and natural metadata and
preserve a complete independent module recipe. Do not silently suppress the probe ABI
warning to certify a module.

## FT3680

Inherited blocker: 40 function sizes differ, with real opcode/call-boundary differences.
The historical reconstruction is incomplete at the current source-acceptance standard.
Its YFT provider dependency also remains unresolved. No new source candidate is promoted.
Next: locate an authentic FocalTech FT3680 SPI OEM release and compare all functions/data,
not an upstream I2C implementation or a firmware payload.

## YFT device information

Inherited blocker: ten exported device_add CRCs and eleven KCFI IDs differ, plus provider
enum/type graph and probe/sysfs code generation. The earlier enormous enum-tag search is
preserved as rejected evidence; repeat spelling brute force is not a new source recovery.
Next: recover the actual ODM enum/type header from an authentic release or a demonstrable
new consumer constraint. No stock CRC or KCFI constant injection.

## TrustKernel core

The historical normal-world source island is statically complete and source-built
consumers can use its **island** ABI. That is not historical stock ABI equivalence.
Only 5/19 consumer edges retain stock CRCs; fourteen private-type/member-spelling edges
remain. Genksyms hashes identifier spellings not recoverable merely from stripped layout.

The CMDQ Microtrust configuration fix does not close this TrustKernel blocker: CMDQ has
real public declarations, whereas reconstructed TrustKernel private definitions have
unrecovered original names. No matching tkcore source path was found in the inspected
NothingOSS/MiCode trees. This is not a claim that every possible release was searched.
Next: recover authentic TrustKernel normal-world private headers. Trusted-world, HAL,
KeyMint/Gatekeeper and firmware behavior remain outside the proof and were not exercised.

### New public declaration release recovered, not a compatible replacement

A subsequent external search located actual TrustKernel normal-world source in
`deadman96385/android_kernel_zte_mt6761`, pinned at
`b0c0f1ec4cb6d616090e7879a7df0785a1323c5d`. The `tkcore` core/include/armtz source
is preserved under `evidence/legacy-source-search/zte-tkcore/`, with original GPL-2.0
copyright/license notices. All 52 downloaded blobs were checked against their Git blob
IDs and are recorded with SHA256 in `zte-tkcore-manifest.json`. An API quota interruption
on the final version header was resolved by fetching the commit-pinned raw URL and
checking the same blob ID; no source substitution was made.

This is version `3.2p3` (2015–2018), not the stock module's read-only-observed
`tkcore_nsdrv_version` / modinfo version `6:1.1-k6.6`. The authenticated source contains
real `tee_core_priv.h`, `tee_core.h`, `tee_shm.h` and RPC/private headers. Their presence
is direct source evidence, unlike an indexed Kconfig-only reference.

A compile-only probe under the prepared pinned kernel environment measures:

| Declaration | Public 3.2p3 | Stock reconstructed anchor |
|---|---:|---:|
| sizeof(struct tee) | 0x158 | 0x138 |
| tee.priv / ops / dev | 0x68 / 0x70 / 0x78 | 0x88 / 0x90 / 0x98 |
| tee.rpc | 0xd0 | 0xb0 |
| sizeof(struct tee_context) | 0xc8 | 0xd0 |
| tee_context.refcount | 0xc0 | 0xc0 |

The public release embeds one `miscdevice`; stock uses a list at 0xa0 and has added
version/logging fields. Its context lacks the extra stock pointer at 0xc8. These are
actual declaration/layout differences: do not drop the old header into the modern
island and assume correct CRCs. The public tee_session retains implicit padding and
provides useful original member-name constraints, but the recursively referenced tee
and context graphs are still unclosed. No source correction, CRC acceptance or runtime
claim follows from this successful layout probe.

Next concrete search: find the newer `6:1.1-k6.6` normal-world source release/fork,
constrained by the known added version/log fields, misc-device-list conversion and
extra context member. Do not repeat unconstrained spelling brute force.

The exact FT V4.2 20240407 banner is also visible in a TI support-thread boot log, but
that I2C example is not the GQ5012BF1 SPI source release. No source file or immutable
matching FT/YFT release was recovered from the bounded indexed searches; this is not
proof of global nonexistence. No unrelated generic driver is promoted.

### Follow-up: newer publication dates do not imply newer private declarations

A constrained follow-up fetched Git trees directly after the GitHub API returned an
HTTP403 quota limit. The accessible Git transport allowed immutable tree/blob checks;
the quota failure is not treated as source absence. Source-tree evidence, recovered GPL
normal-world driver files, and comparisons are under
`evidence/legacy-source-search/newer-provider-search/`.

| Publication | Immutable commit | Finding |
|---|---|---|
| vivo-source-mirror/Y21s | c6f6fa957459b2b5d435c816113f1743bb6f4549 | TKCore 3.2p8.4.14p2; 52 TKCore paths, 28 changed blobs vs ZTE |
| vivo-source-mirror/V23_5G | caadc867e01508e6b5ccf1905e6b65122d85a3e0 | Same TKCore version/header; 52 paths, 29 changed blobs vs ZTE |
| UMIDIGI-Official/UMIDIGI-F2-Kernel-Source-Code | 3b998eaba611932b7cc2b451eb7eb3ab5d2fbf0b | 50,588 tracked blobs; zero selected TKCore/private-header/FT/YFT paths |
| Hadenix/kernel_umidigi_f2_mt6771_4.14 | e494bc66f92dfacf9494a7ac8a40c225cca87181 | 50,583 tracked blobs; zero selected paths; README links vendor source |
| gitlab.com/Hadenix1/umidigi_open_source_code_mtk | 84bf3f5e0b1fe0e35bf603d5aec284b11bfed92a | Followed the README link; 145,500 tracked paths, no matching normal-world private-header filename |

`vivo-source-mirror` and Hadenix are community publications, not verified direct OEM
releases for this board. An immutable Git blob proves the retrieved text's identity,
not that it is the GQ5012BF1 source. The linked vendor tree includes ATF/userspace/TEE
artifact paths and camera `MTKCore` false positives; these are not Linux TKCore private
headers. Only its Git filename inventory was inspected. No trusted applications,
firmware, production-line payloads or keys were fetched, built, incorporated or executed.
This is a bounded filename/tree search, not exhaustive content/history proof.

The 57 recovered Vivo blobs retain their original license notices. Both newer header
files differ from 3.2p3 only by two added function declarations. All ten extracted private
struct definition blocks (`tee`, context/session/shm variants, data/cmd/ops) are
**byte-identical** to the rejected 3.2p3 definitions. The low-level header's SMC dispatch
changes to an arm-smccc macro, not the missing version/log/list/context fields. Rebuilding
the same struct blocks would not recover those fields, so the completed layout experiment
was not repeated. No full-module build or CRC acceptance is claimed for these candidates.

A read-only ELF section inventory also checked four stock provider/consumer filenames:
`tkcore.ko`, `tkcore_drv.ko`, `tmem_ffa.ko`, `microarray_fp_tee.ko`. All eight occurrences
in the frozen operand set lack `.BTF` and `.debug*` sections. That route cannot supply
original member spellings from these files. SHA256s and section results are archived in
`stock-type-info-scope.json`; stock operands were not modified.

Validation: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-legacy-search.py` rechecks
all recovered blob/SHA256 identities, compares actual struct blocks against both
candidate headers, and verifies the recorded scope and section findings. A separate
`legacy-search-mutation-test.py` rejects five corrupted diagnostic fixtures (source
byte, pin, struct verdict, debug scope and tree entry), with a passing control. Those
5/5 checks run only on temporary copies and do not substitute for module-parity tests.
The main checkpoint validator includes the archive validator and checks the mutation
record. The mission remains 8 A / 10 C.

Next remains a genuinely different newer normal-world declaration/source lineage carrying
the proven added fields, not another publication of the 3.2 family. A matching OEM source
release or retained build/debug header artifacts would be useful; no request for unpublished source was
sent to an OEM and no source availability beyond the inspected scopes is asserted.

## Continuation from daef94c6 — modern 7:2.2 lineage already in the project

The "newer lineage" requirement above was already partly met by an existing local donor
that the closure checkpoint had not linked. `reverse-engineering/microarray-fp-tee/` and
`Reverse Engineer - DONE/TKCORE-DRV` use the public TrustKernel `drivers/tee/tkcore` from
anvil-kernel `8e1a0f39478f` (tree `6b94428fe0aae736e06693cda13bd284b88e93ed`,
`https://review.ozobot.com/plugins/gitiles/device/ozobot/anvil-kernel`, Zinwa Q25),
imported unmodified as local KDM commit `ff290548332880265d6bc920b1fb8011959db54e`.
It is `TKCORE_NSDRV_VER "7:2.2"`: newer than stock `6:1.1-k6.6`, but the first
public source with the stock structural features (version/log, `udevs` list, context
`config` pointer).

### Layout: all nine stock anchors match (evidence/tkcore-7.2.2/layout-result.json)

Compile-only probe of the unchanged 7:2.2 `include/linux/tee_tkcore.h` under the pinned
environment: `sizeof(struct tee)`0x138, name0x20, priv0x88, ops0x90, dev0x98, `udevs`0xa0,
rpc0xb0, `sizeof(struct tee_context)`0xd0, refcount0xc0 — 9/9 equal to stock. 3.2p3 matched
none of the moved fields. The private layout is therefore no longer the open question.

### Natural provider CRCs

Harness: the exact recorded `tee_core.c` compile command with `-E -D__GENKSYMS__`, piped to the
pinned `scripts/genksyms/genksyms` (argv in `genksyms-argv.json`); control reproduces the existing
7:2.2 natural `Module.symvers` exactly. No CRC value is written anywhere.

| Variant (authentic source basis) | Stock tkcore exports reproduced |
|---|---:|
| 7:2.2 unchanged | 11/25 |
| **H1**: undo 7:2.2's `tkcore_TEEC_*` prefix in the two alias blocks (3.2p3 and stock export unprefixed GP `TEEC_*`) | **14/25** (+TEEC_CloseSession, TEEC_InvokeCommand, TEEC_ReleaseSharedMemory) |
| H1 x {3.2p3 `tee_cmd` without login fields} x {3.2p3 layout-neutral `uint32_t test`} x {3.2p3 `tee_client_api.h` include} — 8 combinations | 14/25 each; rejected |

Consumer-edge effect (stock import CRCs that a 7:2.2+H1 provider would satisfy naturally):
tkcore_drv 6/11, tmem_ffa 3/7, microarray 1/1 → **10/19** (island: 5/19).

All four `tee_wait_queue_*` reproduce: the Phase-3F "include-context" residual for
sleep/wakeup is explained by the authentic `<linux/device.h>` include in the public header,
which the island header omitted.

### Localization of the remaining 11

Every remaining mismatch (`__tee_get`, `tee_core_{alloc,add,del,free}`, `tee_supp_cmd`,
`TEEC_{Initialize,Finalize}Context`, `TEEC_OpenSession`, `TEEC_{Register,Allocate}SharedMemory`)
reaches `struct tee` through genksyms' recursive expansion; no matching symbol does. Each type
has one expansion across all four translation units. The unknown is a same-layout spelling,
type alias or include-visibility difference inside the `struct tee` closure between 6:1.1 and
7:2.2 (18 private types plus GKI types reached via `tee_shm`/`tee_rpc`/`tee_device_config`).
No stock artifact exposes member names (no BTF/debug sections, verified above).

tkcore.ko remains **C**. H1 is a recorded source-level improvement for a future provider
rebuild, not an accepted recipe; no whole-module code/data parity was attempted here.
Next: recover a 6.x-era TrustKernel release (between 3.2p8 and 7:2.2) or the anvil-kernel
history preceding `8e1a0f39478f`; test only declarations it actually contains.
