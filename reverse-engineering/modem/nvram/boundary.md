# Modem NVRAM / calibration boundary (private device state)

No per-device contents were opened, copied, hashed or recorded. This is a path/consumer/category
map derived from fstab, init, ELF strings and SELinux only.

## Ownership map

| location | category / role | consumers | handling |
|---|---|---|---|
| raw `nvram` partition | MediaTek NVRAM backup/bin-region and factory NV | nvram_daemon/libfile_op | never wipe/copy/generate |
| `/mnt/vendor/nvdata/md/NVRAM/CALIBRAT` | MD RF/network calibration records | nvram daemon, ccci_mdinit, MD through ccci_fs | device-specific; private |
| `.../NVD_IMEI` | device radio identity | same | **never inspect or record** |
| `.../NVD_CORE`, `.../NVD_DATA` | modem core/config/state | same | private persistent state |
| `.../IMPORTNT`, `.../BACKUP`, `INFO_FILE` | important-file set, backup and schema metadata | libfile_op/libnvram | preserve as a unit |
| `/mnt/vendor/nvdata/md_cmn` | common modem state | ccci_mdinit / MD | private |
| `/mnt/vendor/nvdata/APCFG/APRDCL/MD_SBP` | selected modem carrier/SBP profile | ccci_mdinit, RIL | config; preserve |
| `.../CXP_SBP` | CXP/operator profile | ccci_mdinit, librilfusion/RIL | config; preserve |
| `/mnt/vendor/nvcfg` | NVRAM config, OSLK backup marker, AGPS/almanac state | NVRAM AIDL (`/dev/ttyCMIPC0`), ccci_mdinit, mnld | non-slotted persistent state |
| `/mnt/vendor/protect_f/md`, `/mnt/vendor/protect_s/md` | protected factory modem reserves | ccci_mdinit | never modify |
| `md1drdi` inside modem.img | generic/SKU DRDI database, not per-device writable NV | LK/MD | proprietary signed image |
| `mcf_ota` + `vendor/etc/md` | carrier/network defaults | ccci_mdinit/MD/RIL | product config, not calibration |

The directory names for inactive md2/md3/md5 variants also occur in generic `libfile_op.so`; their
presence as strings is not evidence that those modems exist. GQ5012BF1 has only MD1.

## Boot/backup contract

1. nvram_daemon restores/checks the raw NVRAM bin region and publishes
   `vendor.service.nvram_restore`.
2. ccci_mdinit waits for NVRAM readiness, resolves USP/CIP/project/NVRAM SBP values, creates/checks
   MD directory roots, then starts the CCCI FS service.
3. MD accesses NV/config through `/dev/ccci_fs` and cache smem (`SMEM_USER_MD_NVRAM_CACHE`).
4. NVRAM AIDL also uses MIPC `/dev/ttyCMIPC0` and `/mnt/vendor/nvcfg/OSLK_BACKUP_DONE`.

## Category conclusions

* **RF calibration / antenna calibration:** CALIBRAT + DRDI relationship exists; record schema and
  values unknown and intentionally unread.
* **IMEI/device identity:** NVD_IMEI exists; not inspected.
* **band/SKU configuration:** DRDI + MCF/SBP + GPIO99/100 band straps; exact selected band profile unknown.
* **carrier configuration:** MD_SBP/CXP_SBP, MCF and vendor/etc/md.
* **SIM/network state:** MD NVD_CORE/NVD_DATA categories; exact records unknown.

These partitions are non-slotted. A slot-B ROM experiment must treat them as shared live device
state. See the main workspace `PARTIAL/NVRAM-CALIBRATION`; this modem map narrows its remaining
unknowns but does not make the overall cross-subsystem component DONE.
