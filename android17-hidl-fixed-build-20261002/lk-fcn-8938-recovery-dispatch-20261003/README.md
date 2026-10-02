# LK function 0x8938 reboot-mode dispatch investigation

The recovery reboot-mode register contract is already proven:

- syscon base: 0x1c00a000
- register offset: 0x24
- physical register: 0x1c00a024
- mask: 0x0f
- recovery magic: 2
- bootloader magic: 3
- LK low-field writer: 0x3dc5c

LK function 0x8938 contains at least two calls to the writer:

- call site 0x8d18, with w0 = 3
- call site 0x8e0c, with w0 = 2

This investigation captures the entire function, its control-flow graph,
referenced strings, direct calls, incoming xrefs, the reset function used
after the reboot-mode write, and the third caller of 0x3dc5c.

The purpose is to determine exactly what conditions cause LK itself to write
the bootloader or recovery reboot-mode values.

This investigation is host-only. It performs no ADB operations, partition
writes, boot-control writes, reboot-mode writes, or reboots.
