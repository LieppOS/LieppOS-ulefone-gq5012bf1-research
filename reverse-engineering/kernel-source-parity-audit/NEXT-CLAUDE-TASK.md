# NEXT CLAUDE TASK — source-close the six-module MT6878 boot clock core

> **STATUS: COMPLETED 2026-10-09.** All six modules D → A (byte-exact except GNU build ID,
> independent clean-checkout B1/B2). Result: `../kernel-source-reconstruction/BOOT-CLOCK-CORE/`;
> source: `android_kernel_modules_boot_clock_ulefone_gq5012bf1`. The assignment below is
> retained as the historical brief. Two of its statements were corrected by the work:
> the pinned public source alone did **not** reproduce stock (a display-PWM clock delta was
> required for `clk-mt6878` and `clk-mt6878-peri`), and `clk-fmeter-mt6878` sits at normal
> loader position 50 (recovery 49), not 51.
>
> **Follow-up PRESERVE:STORAGE: COMPLETED 2026-10-09** (ten storage modules G → A,
> `../kernel-source-reconstruction/STORAGE/`).
>
> **Follow-up PINCTRL: COMPLETED 2026-10-09** (four pinctrl/GPIO/EINT modules D → A,
> `../kernel-source-reconstruction/PINCTRL/`; 121 certified / 337 uncertified of 458).
>
> **Follow-up REGULATORS: COMPLETED 2026-10-09** (four modules D → A,
> `../kernel-source-reconstruction/REGULATORS/`; 125 certified / 333 uncertified of 458).
> RT6160 actual load-order metadata corrected133→124 (recovery122); stock lists unchanged.
> Current queue head: `CANDIDATE:device_modules:drivers/interconnect/mediatek`:
> `mmqos-common`, `mmqos-mt6878`, `mtk-emi`; no new assignment has been written yet.

## Mission

Create an independently reproducible, stock-compatible source package for **only**:

1. `clk-common.ko`
2. `clk-mt6878.ko`
3. `clk-mt6878-bus.ko`
4. `clk-mt6878-peri.ko`
5. `clk-mt6878-vlp.ko`
6. `clk-fmeter-mt6878.ko`

All six are D in the frozen source-gap audit, are listed in the stock first-stage loader,
and have public source candidates under one clock-provider tree. This is the highest-priority
new source integration project, not an instruction to rebuild already closed accelerators,
GKI, storage, USB, audio, connectivity or camera drivers.

Workspace: `/home/armol/androido_dalykai/LieppOS custom ROM/`.
Research: `/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research`.
Kernel: `6.1.115-android14-11`; arm64 / MediaTek MT6878(T).

## Exact existing operands

### Stock

All six binaries are in:

`workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/`

Use each complete SHA256/size/path set from
`reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv`.
Do not substitute a same-name binary from another image. Initial read-only extraction:

```sh
cd '/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research'
python3 - <<'PY'
import csv
from pathlib import Path
p=Path('reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv')
rows=list(csv.DictReader(p.open(),delimiter='\t'))
for r in rows:
    if r['source_group']=='BOOT-CLOCK-CORE':
        print(r['filename'],r['stock_sha256'],r['stock_size'],r['stock_paths'])
        print('source:',r['candidate_path'],'pin:',r['source_commit'])
        print('providers:',r['provider_dependencies'])
PY
```

The retained loader resolves them at sequences 22 (common), 23 (SoC), 28 (peri),
29 (bus), 31 (VLP), 51 (fmeter). Treat those as existing load order, not observed probe success.

### Public source

- Existing checkout:
  `/home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878/device_modules`
- Candidate directory: `drivers/clk/mediatek/`.
- Pinned public baseline:
  `957dac185efe46cbf6336b0fff9516d84c8cd78f`, NothingOSS
  `android_kernel_device_modules_6.1_nothing_mt6878`.
- Additional ALPS comparison revision already used by other exact closures:
  `5e415e059253ce0d2e61c97108e5f5785d71f06f`.
- Existing public history mirror:
  `/home/armol/kernel-work/public-mtk/nt6878.git`.
- Candidate target/config evidence: `kernel/nothing-module-index.csv` and the six
  `candidate_configs`/`candidate_files` records in the audit. Read actual Kbuild targets;
  index presence is not a stock-compatible build proof.
- The existing `drivers/clk/mediatek/Makefile` selects `clk-common.o` with
  `CONFIG_DEVICE_MODULES_COMMON_CLK_MEDIATEK`; its composite object order is
  `clk-mtk.o clk-pll.o clk-gate.o clk-apmixed.o clk-cpumux.o reset.o clk-mux.o clkchk.o
  clk-fmeter.o mtk-pd-chk.o clkdbg.o`. There is **no `clk-common.c`**.
- `CONFIG_COMMON_CLK_MT6878` selects both `clk-mt6878.o` and the unrelated `clk-bringup.o`
  and also `clk-fmeter-mt6878.o`; restrict the owned outputs explicitly rather than
  blindly enabling that entire target. BUS/PERI/VLP use their respective
  `CONFIG_COMMON_CLK_MT6878_{BUS,PERI,VLP}` selectors.
- Inspect the actual `clk-mt6878*.c` / `clk-fmeter-mt6878.c` units and preserved Makefile;
  do not assume a filename-to-object one-to-one mapping or import later unrelated trees.

### Kernel and toolchain

- Common: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`, GKI CI build 12901745.
- Clang prebuilts: `7775eb113f960bc69a780b621d03a715914d4bca`, clang-r487747c.
- Full GKI pins/configuration/manifest:
  `kernel/phase4-gki-build-pins.tsv`, `kernel/phase4-gki-effective-manifest.xml`,
  `kernel/exact-gki-build-inputs.md`.
- Existing GKI workspace: `/home/armol/kernel-work/gki-12901745-workspace`.
  It may supply a read-only cache/reference, not unrecorded inputs to the final recipe.
- Reuse the maintained accelerator repositories' pinned bootstrap/build-input methods
  as references, especially camera/MDP source-derived provider CRC handling. Do not edit
  those repositories or rerun their module compilations.

## Known dependency boundary and exact missing proof

`clk-common` imports the stock AEE provider (`aee_aed.ko`); the other five depend on
`clk-common` exports. Kernel-core imports resolve against exact GKI. The complete required
symbols, CRCs and stock provider identities are in `DEPENDENCY-EDGES.tsv`; no dependency
identity is hidden by filename deduplication.

AEE itself is outside the six-module project and remains a separate source candidate.
Use its actual pinned public declarations to derive/import compatible ABI metadata; any
retained external provider operand must be explicit and bounded. Do not declare the AEE
implementation reconstructed merely because its consumer CRC matches. Do not forge CRC/KCFI
IDs, patch CRCs into rebuilt modules, or suppress unresolved symbols to create a green result.
If a provider prototype cannot naturally reproduce stock, record that exact blocker before
claiming source closure.

The missing proof is **a clean pinned source build + all stock parity axes**. The audit found
no demonstrated missing implementation, compiler failure or required OEM patch for these
six. First integrate and measure; only reconstruct source deltas actually established by
stock-versus-donor comparison.

## Execution sequence

1. Verify the six stock identities, source target composition, public tree pins and
   exact current import/export requirements. Keep this inventory frozen.
2. Create a new scoped maintained recipe, e.g.
   `android_kernel_modules_clock_core_ulefone_gq5012bf1`, with immutable input commits,
   complete patches if needed, explicit configuration and build scripts. No giant BSP tree
   or one repository per `.ko`.
3. Assemble into a new scratch workspace. Restrict Kbuild to these six modules and their
   necessary linked objects; exclude clk debug/bringup/domain clients from owned outputs.
   Keep ABI-compatible headers/resource definitions and exact source-layout strings.
4. Compile against exact GKI/toolchain/config. Compare the unchanged donor first. Record
   every real code/data/symbol/relocation/CRC/KCFI/modinfo/vermagic delta before editing source.
5. Resolve only demonstrated source/build/header differences. Freeze explicit patches and
   source-derived provider metadata; do not copy stock executable code into generated C.
6. Independently clone/bootstrap the maintained recipe and build B1/B2 from clean outputs.
   Hide the original development worktree to expose accidental dependencies. Compare raw
   and stripped modules, objects, symvers and configuration/source-tree hashes.
7. Preserve full machine ledgers and all build transcripts in the research repository.
   Record interfaces/DT clock-provider resources and future runtime qualification separately.
   Update this audit only from new measured evidence; do not alter other DONE source scopes.

## DONE criteria

For **each** of the six modules:

- Exact immutable stock identity and all shipped paths retained.
- Complete public-source pins, maintained source recipe and patches preserved.
- Successful independent clean source build; B1/B2 deterministic on declared axes.
- Every stock function and data object accounted for; zero unexplained behavior-bearing
  differences; any semantic exception has a specific complete proof.
- Import/export symbol sets, order where applicable, all CRCs, KCFI type IDs/callsites,
  modinfo/vermagic, section layout/content and all relocations accounted for.
- Metadata exceptions precisely bounded; do not conflate signing/build IDs with code.
- Provider dependencies and preserved external operands explicitly declared; no hidden
  old output tree, temporary environment shim or unknown source header.
- No live hardware claim: DT binding, oscillator/PLL behavior, clock-gate sequencing,
  suspend/resume and downstream functionality remain later runtime checks.

If these criteria cannot be met, preserve a sharply named exact blocker; do not promote a
scope or alter unrelated component records to conceal it.

## Safety and delivery

Offline only. No ADB, phone access, reboot, flashing, module loading, slot changes or pushes.
Preserve all existing source work and generated provenance. Do not reverse-engineer firmware
or Android HALs. Commit the scoped source recipe and research evidence locally; **DO NOT PUSH**.
Return the six-module acceptance table, source/pin/commit/build locations, precise residuals,
provider boundaries, runtime tests still needed and research commit IDs.
