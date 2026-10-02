# GQ5012BF1 recovery reboot-mode end-to-end investigation

Previous LK reverse engineering proved that:

- TOPRGU/WDT base is `0x1c00a000`.
- `MTK_WDT_NONRST_REG2` is at offset `0x24`.
- LK function `0x3dc80` consumes bits `[3:0]`.
- value `2` causes `RECOVERY_BOOT`.
- the consumer clears bits `[3:0]` after reading them.

Subsequent device-tree search found an actual GQ5012BF1
`syscon-reboot-mode` node with:

    mode-recovery = <0x02>;

The vendor package also contains the generic Linux `reboot-mode` and
`syscon-reboot-mode` modules.

This investigation resolves the remaining device-tree offset, mask and
parent syscon mapping, identifies the true LK low-nibble setter at or near
`0x3dc5c`, and records live driver/device-tree state.

No partition, boot-control, reboot-mode or Slot-B state is written by this
investigation.
