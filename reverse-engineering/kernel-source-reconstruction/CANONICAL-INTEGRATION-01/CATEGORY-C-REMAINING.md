# Ten retained Category C identities

Exact identities/partitions come from the integrated audit; full rows and evidence paths are in
`CATEGORY-C-REMAINING.tsv`. None was promoted or demoted by integration. Five (charger_class,
mtk_chg_type_det, rt_pd_manager, tcpc_mt6375, tcpc_class) received only the USB-TYPEC-CLOSURE
22-field evidence update (source_commit/parity/blocker/difference text, TCPC 709/709); class stays C.
aw883xx_driver came from AUDIO-BATCH-01 (G→C in staging). The four legacy islands are unchanged
since f61ebf03. No residual was normalized.

| Module | Partition | Class at f61 | Source | Recorded blocker (truncated) | Next experiment |
|---|---|---|---|---|---|
| `aw883xx_driver.ko` | vendor_dlkm | G | audio @ec57573ca9 | inlined v1.7.1 scene-parser codegen (insertion-sort loop shape) not reproduced; stock semantics restored | Authentic Awinic v1.7.1 OEM source; helper/type permutation grids are exhausted (ALL-C helper-probe). |
| `charger_class.ko` | vendor_boot_platform | C | charging_battery @b2a343a9d8 | Srcversion-only raw OEM source-token/dependency lineage remains unavailable; instructions/data except fingerprint, ABI and relocations exact; no metad | Recover the authentic OEM source-token stream behind the stock srcversion, or a new input set proven by actual modpost reads. |
| `focaltech_touch_spi_ft3680.ko` | vendor_dlkm | C | . @a56d3d5416 | Real opcode/call-boundary differences remain; 40 functions size-different and complete semantic proof absent. Recipe preservation also requires comple | Authentic FT3680 SPI V4.2 OEM driver revision; 40 size-different functions. |
| `mtk_chg_type_det.ko` | vendor_boot_platform | C | charging_battery @b2a343a9d8 | Srcversion-only raw OEM source-token/dependency lineage remains unavailable; instructions/data except fingerprint, ABI and relocations exact; no metad | Same OEM source-token recovery for its stock srcversion. |
| `rt_pd_manager.ko` | vendor_boot_platform | C | usb_typec @758f9edc78 | Srcversion-only raw OEM source-token/dependency lineage remains unavailable; instructions/data except fingerprint, ABI and relocations exact; no metad | Same OEM source-token recovery for its stock srcversion. |
| `st21nfc.ko` | vendor_boot_platform | C | . @a56d3d5416 | 22/24 raw function matches; complete independent clean-input/relocation/semantic acceptance at current audit standard is not demonstrated. Recipe pres | Original OEM/ST revision beyond scanned public blobs; close ioctl/ping and natural srcversion (22/24 raw function matches). |
| `tcpc_class.ko` | vendor_boot_platform | C | usb_typec @758f9edc78 | 709/709 instruction bodies/positions and 113/114 data objects exact, including all54 timers; natural srcversion, six source-line diagnostic strings/37 | Original multi-object token set from its traced modpost read list; preserve 709/709 functions and 54 timers. |
| `tcpc_mt6375.ko` | vendor_boot_platform | C | usb_typec @758f9edc78 | 66/66 code exact; genuine license/version order restored; unknown +1 counter prefix and natural srcversion remain; no fabricated declarations or metad | Original OEM include/declaration stream explaining the one-higher __COUNTER__ numbering and srcversion (USB-TYPEC-CLOSURE/TCPC-METADATA-INVESTIGATION.md); preserve 66/66 functions. |
| `tkcore.ko` | vendor_boot_platform | C | . @a56d3d5416 | Source island is statically complete, but only 5/19 consumer edges retain historical stock CRCs. 14 private-type CRC edges do not permit a stock-compa | 6.x TrustKernel release or anvil-kernel history before 8e1a0f39478f; test only struct-tee-closure declarations it contains (7:2.2 layout 9/9, H1 14/25 natural provider CRCs). |
| `yft_devinfo.ko` | vendor_boot_platform;vendor_dlkm | C | . @a56d3d5416 | 10 exported device_add CRCs and 11 KCFI IDs differ; remaining provider enum/type graph and probe/sysfs codegen are unclosed. Recipe preservation also  | Authentic ODM enum/type declarations from a consumer/source release; 10 export CRCs and 11 KCFI IDs differ. |

These are integration facts, not new reconstruction: no USB, AW883XX or TrustKernel experiment
was rerun here (assignment §14).
