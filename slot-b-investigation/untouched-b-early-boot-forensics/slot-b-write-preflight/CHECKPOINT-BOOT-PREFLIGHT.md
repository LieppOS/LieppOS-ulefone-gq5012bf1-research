# Diagnostic Slot-B boot preflight

The previous pair-completion check returned PAIR_READY_FOR_BOOT=0 only because
ADB became available before sys.boot_completed had reached 1.

The vendor_b, vbmeta_vendor_b and root vbmeta_b hashes were otherwise correct.

This follow-up waits for safe Slot A to finish booting, verifies A remains both
current and active, verifies all three B AVB hashes, and removes any previous
/metadata/lieppos-slotb checkpoint directory before the diagnostic boot.

PAIR_READY_FOR_BOOT=1
OLD_MARKERS_CLEARED=1
B_ACTIVATED=0
