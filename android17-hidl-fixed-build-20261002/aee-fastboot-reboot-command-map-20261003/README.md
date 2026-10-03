# AEE fastboot reboot command map

Previous analysis proved that AEE contains an exact writer for
`MTK_WDT_NONRST_REG2[3:0]` at `0x2eaa0`.

Three direct writer invocations exist:

- value 3 at `0xee20`;
- value 2 at `0xef14`;
- value 0 at `0x43804`.

The value-2 invocation is therefore an explicit executable AEE recovery-mode
path, not merely a generic writer whose recovery use was inferred.

This investigation maps AEE command strings:

- `reboot`;
- `reboot-bootloader`;
- `reboot-recovery`;
- `reboot-fastboot`;
- `boot-recovery`;
- `boot-fastboot`;

to their raw AArch64 code references and the known value-2/value-3 handler
regions.

The objective is to establish which fastboot/reboot command dispatch path
plants recovery magic 2 into `0x1c00a024`.

No phone state is modified.
