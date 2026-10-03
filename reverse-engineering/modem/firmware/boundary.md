# Modem firmware boundary (PARTIAL / proprietary)

No firmware payload is copied into this public-facing research directory. `inventory.tsv` records
hashes, offsets, sizes and consumers against the private stock extraction only.

## md1img (`modem_a` / `modem_b`)

Stock extraction: `workspace/gq5012bf1/stock/firmware/modem.img`

* MKIMG multi-image container, **81,565,392 B**; SHA-256 in `inventory.tsv`.
* LK loads it before Linux and writes 28 `ccci_tag_mem` records. Linux reads the resulting
  addresses/status; it does not authenticate or load MD code itself.
* Main CHECK_HEADER v6:
  * platform `MT6878_S00`, `bind_sys_id=1`, image type 14/NLWCG
  * build `MOLY.NR17.R1.MP5.RC.MP.V23.9.P1`, 2025-10-22 22:04, `TK_MD`
  * MD memory 0x1e000000 (480 MiB), DSP offset 0x1d780000, DSP size 0x880000
* Sub-images: md1rom, md1drdi, md1dsp, certificate pairs, 7 logging filters, EM filter,
  compressed DSP/ARM debug info, MDDB/ODB databases, monitor layout and file map.
* `cert1md` / `cert1` / `cert2` records accompany the executable/data images. LK reports
  `lk_info_ld_flag=1`, `lk_info_err_no=0`, `lk_info_ld_md_errno=0`; therefore the captured boot
  successfully passed the platform's secure load path. The raw partition has no AVB footer;
  authentication is the MediaTek image/LK mechanism, not Linux dm-verity.

`md1drdi` (5.94 MiB) is the RF Dynamic Radio/Device Data Interface profile. It is opaque. The
exact band list, antenna tuning and RF-set selection cannot be proven by platform marketing data.

## MCF carrier/modem configuration (`mcf_ota_a` / `mcf_ota_b`)

Stock extraction: `workspace/gq5012bf1/stock/firmware/mcf_ota.img`

* ext4, 29,999,104 B; 49 `MTK_OPOTA_SBPID_*.mcfopota`, 28
  `MTK_NWOTA_SBPID_*.mcfnwota`, MTK OTA packages and
  `HW_CONFIG_SAR_Type0_Set1_MMRF.mcfrawota`.
* OEM `custom/` directory is empty: no separate Ulefone/YFT MCF payload was found.
* No AVB footer is present in the extracted image. Whether the bootloader verifies this partition
  through a platform-specific chain is not proven; do not call it unsigned/replaceable.
* Selected by the SBP values persisted in nvdata and consumed by MD via the CCCI FS path.

## Vendor files delivered to MD

`vendor/etc/md/` contains 760 small, non-device-specific files:

* 504 APN configs (`apncfg/<MCC>_<MNC>.conf`), typically IMS APN records;
* 19 IKEv2 and 20 TLS CAs;
* 217 TS25 PLMN records.

`vendor/etc/mdota/` is empty. These vendor files are protected as part of the verified vendor
partition; they are not RF calibration.

## Reconstruction boundary

Linux CCCI, CCIF, DPMAIF, CCMNI, power/thermal support and C2K USB debug drivers are complete and
exact. The MD ARM/DSP code, Layer 1/2/3, NAS/RRC, IMS/SIP, RF control, DRDI and carrier policy are
signed/opaque proprietary firmware and are not reconstructed or modified.
