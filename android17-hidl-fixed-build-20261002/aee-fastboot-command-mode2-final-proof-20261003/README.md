# AEE fastboot reboot-recovery to NONRST mode-2 proof

The GQ5012BF1 AEE payload contains the fastboot reboot command handlers used
before Linux.

All four runtime callback pointers share load base:

    0xffff00007e000000

After normalizing that base, the callback map is:

    reboot             -> 0xedd0
    reboot-bootloader  -> 0xedfc
    reboot-fastboot    -> 0xee30
    reboot-recovery    -> 0xef24

The registration block independently associates these pointers with their
fastboot command strings.

`reboot-fastboot` loads:

    boot-fastboot

and branches into the shared BCB handler at 0xee3c.

`reboot-recovery` loads:

    boot-recovery

and branches into the same shared BCB handler.

After a successful BCB write, the shared path reaches:

    0xef10  mov w0, 2
    0xef14  bl 0x2eaa0

AEE function 0x2eaa0 directly modifies:

    MTK_WDT_NONRST_REG2
    physical address 0x1c00a024
    field bits [3:0]

by clearing the low nibble and ORing in its argument.

Therefore successful AEE `reboot-recovery` handling explicitly writes:

    MTK_WDT_NONRST_REG2[3:0] = 2

before reset.

The corresponding `reboot-fastboot` command uses the same recovery-mode-2
transport while setting `boot-fastboot` in the BCB, causing recovery mode to
enter fastbootd rather than ordinary recovery userspace.

This proves the static firmware command semantics.

It does not by itself prove what issued the relevant AEE command during the
historical Slot-B experiment.

No phone state was modified.

## Proof-classifier correction

The initial final-proof classifier incorrectly formatted five-digit radare2
addresses by constructing textual strings such as `0x00002eaa0`, while
radare2 displays the same file offset as `0x0002eaa0`.

This caused false FAIL results for the already-disassembled
`0x2eaa0` NONRST writer instructions.

The corrected classifier parses instruction addresses numerically.

The underlying static evidence was unchanged.
