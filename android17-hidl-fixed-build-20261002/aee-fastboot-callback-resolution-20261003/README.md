# AEE fastboot callback resolution

AEE's fastboot registration code loads callback pointers from four data
slots:

    reboot             -> 0xddda8
    reboot-bootloader  -> 0xdddf0
    reboot-fastboot    -> 0xdddf8
    reboot-recovery    -> 0xdde00

Previous static analysis already proves that AEE contains an exact
`MTK_WDT_NONRST_REG2[3:0]` writer and explicit value-2/value-3 callers.

This continuation resolves the actual callback pointer values without
assuming function boundaries.

The important question is whether the callback registered for
`reboot-recovery` directly reaches the value-2 writer path.

No phone state is modified.
