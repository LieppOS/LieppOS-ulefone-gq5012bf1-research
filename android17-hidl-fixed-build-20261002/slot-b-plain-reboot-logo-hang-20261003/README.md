# Controlled plain A -> B reboot: logo hang

The test began from healthy Slot A with normal LK boot mode, an empty
recovery/fastboot BCB, the expected corrected system_b image, and the expected
metadata-encryption key.

Slot B was activated using Android boot control.

The only reboot command used was:

    adb reboot

No recovery, fastboot, or bootloader reboot target was supplied.

Result:

- the device remained at the boot logo;
- no ADB transport appeared during the 120-second observation window;
- no fastboot/fastbootd transport appeared during that window;
- automatic host-side rescue could therefore not execute.

This experiment does not establish the B-side LK boot mode because no B-side
transport or log was captured before rescue.

The phone was subsequently returned manually to Slot A.
