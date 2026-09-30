# Fastbootd regression comparison

Purpose: compare the August 12 known-working Slot-B fastbootd environment with the current Android 17 staging environment.

Known historical facts:
- Host fastboot: /usr/bin/fastboot 36.0.1.
- Direct suffixed logical names such as system_b were proven.
- Historical system_b resize succeeded.
- Historical system_b flash wrote all three sparse chunks successfully.
- Historical executor rebooted A and re-entered fastbootd after each explicit logical resize.

Current observed regression before this comparison:
- fastbootd reports is-userspace=yes.
- fastbootd current-slot was blank.
- direct fastboot flash system_b failed on first write with remote: No such file or directory.
- post-failure system_b remained byte-identical to its pre-write image.
- Android-side inactive B dm mappings are read-only.
