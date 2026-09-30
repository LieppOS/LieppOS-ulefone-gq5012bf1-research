# Android 17 VINTF compatibility input collection

Collected from:

- live Slot A vendor/ODM environment
- unbooted Slot B system
- unbooted Slot B system_ext
- unbooted Slot B product

Collected inputs:

- complete VINTF XML trees
- live getprop
- kernel release
- kernel config when exposed through procfs
- Android 17 B build properties
- SHA-256 hashes of VINTF XML files

Safety:

- no flash
- no reboot
- no slot change
- no vbmeta modification
- no userdata modification
- no metadata modification
- Slot B mounted read-only only
