# BOOT-DEPENDENCY-BATCH-01 — summary

**Result: 16/16 frozen first-stage Category D targets reconstructed and independently certified as
Category A.** Evidence: independent B1/B2 whole-stock ELF acceptance under the unchanged strict verifier,
where the only difference is the GNU20 build-ID descriptor. The canonical audit is not edited: an
identity-keyed CAS delta is proposed. Applied in a scratch copy, it yields **A349 / B1 / C10 / D44 / E0 /
F0 / G54 = 350 certified, 108 uncertified**, with validator PASS (0 errors) and 14/14 audit mutation tests.

- **Canonical start:** `21ec8901` (A333 B1 C10 D60 G54).
- **Frozen manifest:** `BATCH-MANIFEST.tsv` SHA256 `a527ea2a528eb0d896b82c8b6a5b86254c46ee55240010f7f8e803df79d4e56f`,
  committed at `3a5a3181` before any source work. Selection rule: `source_status=D ∧ priority=P0_BOOT`, giving exactly 16.
- **Maintained source:** `android_kernel_modules_boot_dependencies_ulefone_gq5012bf1` @ `8e7a66e130a5…`.
  Bundle `bundles/boot-dependencies.bundle` verified, cloned fresh twice, `fsck --full`.

| Module | Family | Functions | Data | Imports/Exports | KCFI IDs | Relocs | Source | Residual |
|---|---|---|---|---|---|---|---|---|
| timer-mediatek | timekeeping/IO | 26/26 | 26/26 | 29/0 | 3 | 177 | ALPS exact | none |
| 8250_mtk | timekeeping/IO | 59/59 | 29/29 | 114/32 | 0 | 1171 | ALPS exact | none |
| i2c-mt65xx | timekeeping/IO | 28/28 | 65/65 | 54/4 | 0 | 564 | ALPS + OEM DT literal | literal not in public history |
| reset-ti-syscon | timekeeping/IO | 7/7 | 19/19 | 13/0 | 0 | 51 | ALPS exact | none |
| rtc-mt6685 | timekeeping/IO | 29/29 | 51/51 | 63/0 | 0 | 817 | ALPS exact | none |
| regulator-vibrator | timekeeping/IO | 9/9 | 15/15 | 18/0 | 0 | 217 | ALPS + layout placeholder | 27 non-code lines' text unrecoverable |
| nvmem_mtk-devinfo | nvmem | 4/4 | 17/17 | 10/0 | 0 | 50 | ALPS exact | none |
| mtk-vmm-spm | mm/power | 16/16 | 21/21 | 17/0 | 0 | 281 | ALPS exact | none |
| mtk-mminfra-imax | mm/power | 7/7 | 41/41 | 23/0 | 0 | 524 | ALPS exact | none |
| mtk_dpc | mm/power | 67/67 | 118/118 | 81/18 | 0 | 3368 | ALPS exact | none |
| mtk-swpm-perf-arm-pmu | mm/power | 14/14 | 65/65 | 13/10 | 0 | 584 | ALPS exact | none |
| sec | security | 45/45 | 48/48 | 41/25 | 4 | 496 | ALPS exact | none |
| teeperf | security | 10/10 | 21/21 | 30/0 | 0 | 237 | ALPS exact | none |
| arm_dsu_pmu | in-tree BTF | 22/22 | 39/39 | 38/0 | 0 | 270 | common exact + OEM BTF base | none |
| kfifo_buf | in-tree BTF | 14/14 | 12/12 | 22/3 | 0 | 88 | common exact + OEM BTF base | none |
| industrialio-triggered-buffer | in-tree BTF | 4/4 | 12/12 | 8/3 | 0 | 31 | common exact + OEM BTF base | none |

All CRCs (imports and exports), licences, namespaces, KCFI type IDs, raw and semantic relocations,
section headers, symbol and string tables, `.modinfo` (vermagic, srcversion, intree/scmversion, depends) and
`.BTF` are byte-identical. No CRC, srcversion, metadata or BTF was forced, transplanted or patched. No stock
machine code or data was used as a build input.

## Key findings

- **mtk_dpc `depends=…mdp_drv_mt6989`.** This is a natural modpost artefact. `mdp_dpc.o` is linked into four
  mdp_drv variants (wildcard-guarded), and modpost 6.1 records the last exporter it reads. The derivation is
  checked at every build.
- **i2c-mt65xx.** The GQ5012BF1 stock driver reads `mediatek-fifo-use-polling`, and the stock base DTB
  sets exactly that property on `i2c@11280000`, the bus of the MT6375 charger/PMIC and the rt5133 and rt6160
  regulators. Public ALPS uses `mediatek,fifo-use-polling`. This is a new board-specific finding.
- **In-tree modules.** The three in-tree modules are blob-identical between GKI common and the MTK ACK
  tree. Their split BTF matches only against the source-built OEM base (`cafe5987…`).
- **Provider ABI.** All 66 vendor-provider ABI slots are certified-A providers with naturally compiled
  witnesses. No target depends on a C/D/G provider or on proprietary firmware through ELF imports.

## Reproducibility

- **Builds:** B1 and B2 come from fresh no-alternates bundle clones in fresh workspaces, each re-running
  the full offline bootstrap including the OEM BTF base, at 4 CPUs and nice 10.
- **Identity across builds:** raw and stripped `.ko` (32 files), 189 intermediate objects, configs, natural
  symvers and source trees are byte-identical. The batch Module.symvers is identical after mapping the
  workspace path. B1 also equals development D3.
- **Controls:** 222 + 222 real ELF mutation controls behave correctly, including 9 BTF header/type/string
  mutations per build.

## Safety

- **Canonical:** master untouched (`21ec8901`, clean).
- **Stock:** all 471 stock `.ko` are unchanged; live inventory PASS 458/471, 60/60 signed. Stock was only
  read: private copies were used, and every strip wrote to an explicit separate output.
- **Repositories:** no existing maintained repository was modified.
- **Offline:** no ADB, phone, flash or push.

Reports: BOOT-DEPENDENCY-ANALYSIS.md, HARDWARE-CONTRACT.md, SOURCE-LINEAGE.md, ABI-PROVIDERS.tsv,
BATCH-PARITY.tsv, EXPERIMENTS.tsv (including failures), BLOCKERS.tsv (disclosed residuals),
BUILD-REPRODUCTION.md, AUDIT-DELTA.tsv, PROPOSED-AUDIT.patch, MERGE-INSTRUCTIONS.md, NEXT-BATCH.md.
