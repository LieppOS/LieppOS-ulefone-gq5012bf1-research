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
