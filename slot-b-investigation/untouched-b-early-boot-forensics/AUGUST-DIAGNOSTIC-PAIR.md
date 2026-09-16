# August post-firmware diagnostic pair

The final August TIER3 post-firmware B diagnostic temporarily changed exactly
two Android physical images:

- diagnostic `vendor_boot_b`
  SHA256 `5e6cfa811d738f1735c45b8923a5fef736ce005d90b597cff84192eb381627ef`

- diagnostic root `vbmeta_b`
  SHA256 `a7a8ea78f0a21127ee9bfdf4074fc4a796089c72a299281f080f18f726e45d88`

TIER3 records state that the diagnostic vendor_boot differs from baseline only
by the bootconfig instrumentation:

`printk.always_kmsg_dump=Y`

The diagnostic root vbmeta was regenerated only to cover the modified
vendor_boot digest.

All other Android images, LK, subordinate B firmware, and logical partitions
were unchanged.

Therefore the August observation of `0e8d:201c` should not currently be treated
as evidence that the diagnostic pair repaired an otherwise non-booting baseline.
It is more consistent with diagnostic instrumentation revealing progress that
ordinary ADB polling could miss.

The September untouched-B test only proved that stable ADB was not observed; it
did not include the August USB-event instrumentation required to rule out brief
`0e8d:201c` kernel/init gadget enumerations.
