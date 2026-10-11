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
