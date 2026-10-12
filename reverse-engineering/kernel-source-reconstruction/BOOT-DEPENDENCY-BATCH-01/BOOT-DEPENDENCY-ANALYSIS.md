# Boot dependency analysis (16 frozen targets)

Sources of evidence, kept separate:

- **ELF**: `BOOT-DEPENDENCY-GRAPH.tsv`, produced by `scripts/dep-graph.py` from read-only stock modules. It
  has 574 import edges, each resolved to its exporting vendor_boot module or GKI 12901745 vmlinux.symvers,
  with the import CRC compared to the provider CRC (574/574 consistent) and the stock
  `modinfo depends` checked.
- **Load contract**: `reverse-engineering/boot/module-loading/module-classification.tsv`
  (vendor_boot `modules.load` / recovery list / sequence / `pulled_in_by`, plus `loaded_in_capture`).
- **DT**: stock merged device tree `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`
  (vendor_boot base DTB plus the dtbo).
- **Not available**: no saved runtime device-binding/probe evidence (`observed_bindings` and
  `bound_probe_status` are UNKNOWN in the audit for all 16). No module was loaded or omitted
  experimentally (offline-only assignment).

## What `P0_BOOT` means here

`generate.py` assigns `P0_BOOT` to every non-A/B, non-optional row whose resolved load phase is
`first-stage`. All 16 are in the vendor_boot first-stage `modules.load`, except kfifo_buf, which is pulled in
as `dep-of:industrialio_triggered_buffer`. All 16 were recorded as loaded in the saved capture.
arm_dsu_pmu and mtk-swpm-perf-arm-pmu are **not** in the recovery list. This is a statement about the
stock load contract. It does not prove that the platform fails to boot without the module.

## Per-target classification

| Module | seq | Stock-ELF providers | Reverse importers (all 471 occurrences) | DT role | Classification |
|---|---:|---|---|---|---|
| nvmem_mtk-devinfo | 13 | GKI only | none | `efuse@11f10000` `mediatek,devinfo`, 12 cells; 7 `nvmem-cells` consumer properties | REQUIRED_BY_OTHER_PROVIDERS (DT nvmem consumers); runtime effect unmeasured |
| timer-mediatek | 15 | GKI only | none | `systimer@1cc10000` `mediatek,mt6878-timer`/`mt6765-timer`, IRQ 0xf9, clocks `<0xe0>` | FULL_STOCK_RUNTIME (MTK system timer; the arm arch timer is GKI built-in, so not proven necessary for early boot) |
| sec | 17 | GKI only | none (25 exports unused by any stock module) | `security-ao@1040d000`, `masp@1040e000` | FULL_STOCK_RUNTIME (MASP security services) |
| mtk-vmm-spm | 40 | GKI only | none | `vmmspm` `mediatek,vmm_spm_mt6878`, SPM_BASE 0x1c001000, `vmm-pmic-supply` | FULL_STOCK_RUNTIME (VMM power domain for multimedia) |
| mtk-mminfra-imax | 77 | mtk-cmdq-drv-ext (A), mtk_slbc (A) | none | `mminfra-imax@1e80b000` | FULL_STOCK_RUNTIME (multimedia infrastructure) |
| mtk_dpc | 95 | mmprofile, mtk-mmdvfs-v3, mediatek-drm, mtk-cmdq-drv-ext, mtk-mml, mdp_drv_mt6878 (all A) | none | `disp-dpc@14020000` `mediatek,mt6878-disp-dpc` | FULL_STOCK_RUNTIME (display power control) |
| 8250_mtk | 98 | mtk-uart-apdma (A), uarthub_drv (A) | none (32 exports unused) | `serial@11001000/2000/3000` | FULL_STOCK_RUNTIME (UART; console/UARTHUB path) |
| teeperf | 109 | GKI only | none | `teeperf` `mediatek,teeperf` | FULL_STOCK_RUNTIME (TEE performance hinting) |
| regulator-vibrator | 127 | GKI only | none | `regulator-vibrator` (vib-supply, 2.2–3.5 V) | FULL_STOCK_RUNTIME (haptics LED-class device) |
| i2c-mt65xx | 128 | pinctrl-mtk-common-v2_debug (A) | none (4 exports unused) | 15 controllers; `i2c@11280000` hosts mt6375@34 (charger/PMIC), rt5133@18, rt6160@75 | REQUIRED_BY_OTHER_PROVIDERS (bus for first-stage charger/regulator drivers, DT topology) |
| rtc-mt6685 | 134 | aee_aed (A) | none | `spmi@1cc04000/mt6685_mfd/mt6685_rtc` | FULL_STOCK_RUNTIME (RTC/alarms) |
| kfifo_buf | 135 | GKI only | industrialio-triggered-buffer (2 symbols) | — | REQUIRED_BY_OTHER_PROVIDERS (ELF import + `depends=kfifo_buf`) |
| industrialio-triggered-buffer | 136 | kfifo_buf (this batch) | mt6375-adc (seq 137, 1 symbol) | — | REQUIRED_BY_OTHER_PROVIDERS (ELF import by first-stage mt6375-adc) |
| arm_dsu_pmu | 165 | GKI only | none | `dsu-pmu-0` `arm,dsu-pmu`, PPI 0x23 | FIRST_STAGE_LIST_ONLY (perf counters; absent from recovery list) |
| mtk-swpm-perf-arm-pmu | 166 | GKI only | vendor_dlkm mtk-swpm-dbg-common-v1 (9), mtk_mbraink (1) | none (no device match) | FIRST_STAGE_LIST_ONLY (power telemetry provider for second-stage modules; absent from recovery list) |
| reset-ti-syscon | 168 | GKI only | none | reset controllers under `syscon@112b8000` and `syscon@112bb000`; one `resets` consumer property | FULL_STOCK_RUNTIME |

None of the 16 is labelled "strictly required for early boot": that would need runtime omission
evidence, which this offline assignment cannot produce.

## Provider classes

68 of the 574 import edges resolve to vendor_boot modules. 66 of them (66 distinct symbols) resolve to
**Category A** providers in the canonical audit. The other 2 resolve to `kfifo_buf`, which is itself a
target in this batch and is linked by the same native modpost run. The remaining 506 edges resolve to
GKI vmlinux. No target
depends on a remaining C, D or G provider, and none on proprietary firmware through an ELF import.
Firmware or secure-world boundaries exist only at runtime (sec/MASP, teeperf/TEE, mtk_dpc/SPM/VLP,
mtk-vmm-spm/SPM) and are not reconstructed or claimed here.

A provider witness compiled here (`ABI-PROVIDERS.tsv`) proves only CRC, licence, namespace, symbol
type and KCFI prefix agreement for the imported slot. It does not certify or transfer provider ownership.

## Load order consistency

In every case the first-stage sequence loads providers before importers. Examples: mtk-uart-apdma 96
and uarthub_drv 97 before 8250_mtk 98; mdp_drv_mt6878 80, mtk_mml 81 and mediatek-drm 89 before mtk_dpc
95; pinctrl-mtk-common-v2_debug 114 before i2c-mt65xx 128; kfifo_buf 135 before
industrialio-triggered-buffer 136 before mt6375-adc 137.

## modinfo `depends` anomaly resolved

mtk_dpc's stock `depends=` lists `mdp_drv_mt6989`, a module that is not shipped. Its only import
there, `mdp_dpc_register`, is provided at runtime by the shipped `mdp_drv_mt6878` (same CRC 0x768f691e).
Source analysis shows that `mdp_dpc.o` is linked into mdp_drv_mt6878/6897/6985/6989. The Makefile
wildcard guards keep only the variants whose `mdp_mtXXXX.c` exists. modpost 6.1 in external-module mode
records the last exporter it reads (head insertion in `hash_add_symbol`; duplicates allowed by
`sym_add_exported` when `external_module`). That gives `mdp_drv_mt6989`. The stock string is therefore a
natural build artefact, reproduced by derivation rather than by editing metadata.
