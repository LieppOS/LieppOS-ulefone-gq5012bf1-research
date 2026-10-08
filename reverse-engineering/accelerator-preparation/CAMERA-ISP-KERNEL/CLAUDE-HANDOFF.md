# CAMERA-ISP-KERNEL handoff — DONE

The earlier PARTIAL reconstruction handoff has been completed. Do not restart donor triage
or the historical 133c6c1 graft workflow. Its complete original text is retained as
[notes/PREPARATION-HANDOFF.md.txt](notes/PREPARATION-HANDOFF.md.txt); this DONE handoff supersedes it.
The old preparation validator hard-codes a fourteen-section PARTIAL/no-reconstruction
handoff and is not a closure validator; accepted stock/source input and manifest checks
are recorded separately in the current reconstruction evidence.

## Authoritative result

Read, in order:

1. [STATUS.md](STATUS.md)
2. [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md)
3. [SOURCE.md](SOURCE.md) and [build-reproduction.md](build-reproduction.md)
4. [abi-parity.md](abi-parity.md)
5. [hardware-contract.md](hardware-contract.md),
   [firmware-boundary.md](firmware-boundary.md), and
   [source-to-userspace-contract.md](source-to-userspace-contract.md)
6. [evidence/EVIDENCE-INDEX.md](evidence/EVIDENCE-INDEX.md)

## State

* nineteen owned modules: static source/parity **DONE**;
* maintained local source repo: `android_kernel_modules_camera_isp_ulefone_gq5012bf1`,
  branch `main`, not pushed; bundle preserved under `source/`;
* aggregate acceptance: 2 971 functions (one bounded semantic-equivalence residue),
  2 474 data objects, 2 530 ABI rows, 978 sections, 71 991 relocations, zero unresolved;
* clean B1/B2 equality includes all 225 intermediate objects;
* runtime: **NOT TESTED**;
* proprietary HAL/3A/tuning/firmware algorithms: outside scope; parent remains PARTIAL.

## Only valid next action

Run the on-device acceptance list in
[source-to-userspace-contract.md](source-to-userspace-contract.md), or work the separate
`CAMERA-HAL-ISP` proprietary boundary. Any future source modification must rerun
`scripts/b1b2.sh` and preserve all machine ledgers; a successful compile alone is not
acceptance.
