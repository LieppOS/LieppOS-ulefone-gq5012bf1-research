# Current A Runtime Baseline

Observed before untouched-B boot control.

- `ro.boot.slot_suffix = _a`
- `ro.build.fingerprint = Ulefone/GQ5012BF1_EEA/GQ5012BF1:15/AP3A.240905.015.A2/1761131274:user/release-keys`
- `ro.boot.verifiedbootstate = green`
- `ro.boot.slot` was empty
- non-root `bootctl get-current-slot` failed to obtain the bootctl module

Conclusion:

Current running Android is confirmed to be stock-derived Slot A.
Slot B has passed static AVB/payload integrity verification but has not yet been proven to boot.
