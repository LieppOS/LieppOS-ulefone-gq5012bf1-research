# AEE low-nibble reboot-mode writer caller trace

Focused firmware analysis established an important distinction between
the early-boot payloads.

`bl2_ext` contains helpers operating on `MTK_WDT_NONRST_REG2[10:4]`.

The directly observed preloader helper at `0x873d4` likewise operates on
bits `[10:4]`.

However `06-aee.bin` contains a helper at `0x2eaa0` that directly modifies
the low reboot-mode field:

    addr = 0x1c00a024
    arg &= 0xff
    old = *addr
    old &= 0xfffffff0
    old |= arg
    *addr = old

This is the same field consumed by main LK to select recovery when its value
is 2.

This investigation finds every direct AArch64 branch/call to the AEE helper,
captures each caller, and checks whether a caller supplies recovery value 2
or bootloader value 3.

The preloader common branch tails near 0x881c0 and 0x88210 are also captured
to finish classification of the previously identified preloader helpers.

No phone state is modified.
