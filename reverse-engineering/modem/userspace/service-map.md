# Modem userspace service map (stock vendor + system_ext)

SELinux domain → device type allow rules (from `vendor/etc/selinux/vendor_sepolicy.cil`):

| device type | nodes (vendor_file_contexts) | allowed domains |
|---|---|---|
| ccci_device | `/dev/ccci.*` (default) | atcid, bip_ap, ccci_mdinit, ccci_rpcd, emdlogger(v), factory, mdlogger, mediaserver, meta_tst, mtk_hal_audio, mtkimsmddomain (= bip_ap only), mtkrild, muxreport, rild, terservice, usp_service, viarild, vtservice |
| gsm0710muxd_device | ttyC0, ttyCMIPC0/1/2/5/9 | atcid, factory, gsm0710muxd, meta_tst, mnld, mtk_hal_nvramagent, rild, thermal_core |
| ccci_aud_device | ccci_aud, ccci_raw_audio | mtk_hal_audio |
| ccci_vts_device / ccci_wifi_proxy_device | ccci_vts / ccci_wifi_proxy | rild |
| nlop_device | ttyC6 | rild |
| nwkopt_device | ttyC5 | mtk_hal_nwk_opt (no stock binary found) |
| agps_device | ttyC2, ccci_c2k_agps | mtk_agpsd |
| mdlog_device | ttyC1 | emdlogger, mdlogger, meta_tst, mnld |
| ccci_mdl_device | ccci_md_log_{tx,rx,ctrl}, ccci_ccb_dhl, ccci_raw_dhl | emdlogger(v), mdlogger |
| ccci_mdmonitor_device | ccci_raw_mdm, ccci_mdl_monitor, ccci_ccb_md_monitor | md_monitor |
| ccci_monitor_device | ccci_monitor | ccci_mdinit |
| ccci_ccb_device | ccci_ccb_ctrl | ccci_mdinit, emdlogger(v), md_monitor, meta_tst |
| md_block_device | md1img, md3img, md1arm7, modem | ccci_rpcd, em_svr, emdlogger(v), md_monitor, meta_tst, update_engine |
| sysfs_ccci | /sys/kernel/ccci | about 25 domains (ccci_mdinit, rild, atcid, mnld, thermal_core, audioserver, ...) |
| proc_ccci_dump / proc_ccci_sib | /proc/ccci_dump, /proc/ccci_sib | aee_aedv, ccci_mdinit, dumpstate / platform_app |

ueventd: `/dev/ccci*`, `/dev/ttyC*` 0660 radio:radio. `ccci_aud`, `ccci_raw_audio` and
`ccci_pcm_*` are 0660 audio:audio.

The per-port consumer table is `../kernel/ccci-port-map.tsv`. The ELF/interface table is
`dependency-map.tsv`.
