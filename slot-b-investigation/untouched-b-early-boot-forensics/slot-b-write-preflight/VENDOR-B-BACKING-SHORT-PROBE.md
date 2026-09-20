# vendor_b backing short probe

Verified from Android Slot A:

- super resolves to /dev/block/sdc75
- super major:minor is 259:59
- super block device is writable
- vendor_b dm table is exactly:
  `0-1594432: linear, 259:59 17098384`

The original longer mount-check command was manually interrupted because the
remote `su -c` grep invocation hung. No write occurred.

See:
- vendor-b-exact-mount-short.txt
- vendor-b-lp-state-short.txt
