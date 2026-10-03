# Provenance

## Stock evidence (private extraction, hashes/metadata only published)

* `workspace/gq5012bf1/stock/partitions/{vendor,vendor_dlkm,system_ext,product,system}`
* `workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules`
* `workspace/gq5012bf1/stock/firmware/{modem.img,mcf_ota.img,MT6878_Android_scatter.txt}`
* merged offline DT: `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`
* existing read-only live capture:
  `snapshots/live-stock-adb-20260831-115649/devicetree.tar`

No new adb/device action was used. No modem firmware, NVRAM, calibration or identity payload is
stored under `reverse-engineering/modem/`.

## Source donors

| content | local source repo / commit |
|---|---|
| CCCI, CCIF, DPMAIF, SCP bridge, auxadc | `/home/armol/kernel-work/public-mtk/nt6878.git` / NothingOSS history `fae67a9257dc` (MTK ALPS09525334); exact eccci tree `ca75801a968e…` |
| ccmni, rps, mddp, mdpm, md_cooling, C2K USB | NothingOSS MT6878 KDM `957dac1` component trees |
| MD power throttling | `6df320423600`, already integrated by connectivity commit `05f8044` |
| build baseline | GKI/KDM workspace `/home/armol/kernel-work/gki-12901745-workspace/kernel_device_modules-6.1`; modem reconstruction commit `67c7da4` |

The shared KDM tree was changed only by the isolated modem source-selection commit; unrelated
power/SH366003 work was not touched.

## Reproducibility

* `scripts/modemenv.sh` — local paths and toolchain
* `scripts/build_kdm.sh` / `try_kdm.sh` — candidate builds
* `scripts/parity_modem.sh` — function/data/ABI/whole-file comparisons
* `scripts/rebuild_all.sh` — rebuild all 16 modules
* `scripts/gen_inventory.py`, `gen_port_map.py`, `gen_userspace_deps.py`,
  `gen_firmware_inventory.py` — generated tables

All TSV/report outputs are checked in. The proprietary stock inputs remain referenced by path and
SHA-256 only.
