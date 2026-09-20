# vendor_b write-path investigation

The first fastbootd write attempt failed with:

```
Resizing 'vendor_b' OKAY
Sending sparse 'vendor_b' 1/4 ... OKAY
Writing 'vendor_b' FAILED (remote: 'No such file or directory')
```

The subsequent post-failure audit proved that failure had no persistent
effect:

- vendor_b remained rollback-exact
- vendor_b geometry remained unchanged
- super/lpdump metadata remained identical
- vbmeta_vendor_b remained unchanged
- vbmeta_b remained unchanged
- snapshot state remained none

This follow-up is read-only and investigates whether:

1. host fastboot `--slot=b flash vendor` is materially different from
   explicitly targeting `vendor_b`;
2. fastbootd exposes unsuffixed/suffixed vendor aliases differently;
3. Android A already maps `vendor_b` through device-mapper.

Android-A vendor_b mapping observed:

`ANDROID_VENDOR_B_MAPPED=1`

Post-probe vendor_b remains rollback-exact:

`VENDOR_B_STILL_ROLLBACK_EXACT=1`

Post-probe vbmeta_vendor_b remains rollback-exact:

`VBMETA_VENDOR_B_STILL_ROLLBACK_EXACT=1`

No flash operation occurred.
