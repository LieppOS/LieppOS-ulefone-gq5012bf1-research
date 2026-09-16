# First-stage AVB key-path conclusion

The stock Ulefone MT6878 first-stage fstab contains:

`avb_keys=/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey`

for `system` and `system_ext`.

However, no such AVB public-key files are present in:

- factory V15 init_boot ramdisk
- current A init_boot ramdisk
- current B init_boot ramdisk
- exact factory vendor_boot platform ramdisk
- searched TIER3 evidence tree

Therefore absence of these GSI key files is not unique to Slot B.

Android 35 first-stage source explicitly supports fstab entries containing both
`avb_keys` and ordinary `avb` handling. Missing or unusable standalone-key
verification can fall back to the built-in AVB hashtree path when the standalone
handle cannot be established.

The missing q/r/s GSI key files are therefore not currently classified as the
Slot-B boot defect.

Additionally, the August post-firmware attempt reached USB PID `0e8d:201c`,
which requires Android init USB configuration. That places the observed runtime
boundary downstream of basic first-stage mounting during that attempt.

Next investigation: distinguish ordinary ADB PID 201c from charger/KPOC USB
configuration and localize the subsequent reset.
