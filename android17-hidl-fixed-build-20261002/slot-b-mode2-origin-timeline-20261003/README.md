# Slot-B mode-2 origin timeline

The first attempt at this audit stopped because of a Python parser bug before
host-history correlation could run.

The retained first Slot-B boot evidence itself is unaffected:

- the boot entered Linux in MediaTek mode 0;
- after mounting the early filesystems it shut down normally;
- the kernel explicitly reported:
  `Restarting system with command 'bootloader'`.

The reboot-mode DT assigns value 3 to bootloader.

LK's `0x3dc80` consumer reads the low reboot-mode nibble from
`MTK_WDT_NONRST_REG2` and explicitly clears that nibble during consumption.

The later metadata-fixed Slot-B attempt nevertheless entered Linux with
MediaTek boot mode 2.

Therefore a new value-2 write must occur after an intervening LK clear.

This continuation parses generated init services and multiline shell history
to determine whether the new writer was an explicit host recovery/fastboot
transition or another component.

No phone state was modified.
