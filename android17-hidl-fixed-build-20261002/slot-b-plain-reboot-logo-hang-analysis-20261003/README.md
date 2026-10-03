# Controlled plain Slot-B reboot logo-hang analysis

This analysis uses only the pstore captured after manually returning the
device to Slot A.

The controlled test itself had:

- healthy Slot A;
- normal boot mode before the experiment;
- empty recovery/fastboot BCB;
- expected corrected system_b;
- expected metadata-encryption key;
- Slot B selected using boot control;
- plain `adb reboot` with no reboot target.

The resulting Slot-B attempt hung at the graphical boot logo and exposed no
ADB or fastboot transport during the observation window.

Machine classification of the recovered pstore:

SLOT_B_MARKER=NO
SLOT_A_MARKER=NO
MODE0_MARKER=NO
MODE2_MARKER=NO
FORCE_NORMAL_BOOT=NO
RECOVERY_OR_FASTBOOTD=NO
LINUX_STARTED=NO
FIRST_STAGE_INIT=NO
SECOND_STAGE_INIT=NO
SERVICEMANAGER_SEEN=NO
APEXD_SEEN=NO
ZYGOTE_SEEN=NO
SYSTEM_SERVER_SEEN=NO
BOOT_COMPLETED_SEEN=NO
KERNEL_PANIC=NO
EXPLICIT_REBOOT_SEEN=NO
B_BOOTMODE_VERDICT=B_BOOTMODE_NOT_PROVEN_FROM_PSTORE
DEEPEST_BOOT_STAGE=NO_LINUX_PROGRESS_PROVEN

Supporting marker extracts are stored in this directory.

No additional Slot-B boot was performed.
