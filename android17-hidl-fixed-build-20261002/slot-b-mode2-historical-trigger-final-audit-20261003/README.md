# Slot-B mode-2 historical trigger final static audit

The recovery-mode firmware mechanism is now statically proven end to end.

AEE fastboot commands `reboot-fastboot` and `reboot-recovery` both use the
shared mode-2 transport:

    BCB command
        -> WDT NONRST_REG2[3:0] = 2
        -> reset
        -> main LK RECOVERY_BOOT

The remaining question is historical rather than architectural: whether one
of those commands was issued during the October 2 Slot-B metadata-fix
workflow.

Disk `.zsh_history` has a gap over the relevant experiment period, so this
audit additionally uses live interactive zsh history, git history, unique
install-transcript markers and retained scripts.

No phone state is modified.
