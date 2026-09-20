# DropBox crash lead closed

The fresh DropBox entries around the Slot-B experiment were both crashes of:

`com.metrolist.music`

Cause:

`SharedPreferences in credential encrypted storage are not available until after user 0 is unlocked`

Both crash records identify the running build as:

`Ulefone/GQ5012BF1_EEA/GQ5012BF1:15/AP3A.240905.015.A2/1761131274:user/release-keys`

Therefore these records belong to the Ulefone/A-side environment and are not
evidence of the failed Lineage Slot-B boot.

The first fixed-vendor B test also had an instrumentation limitation: its ADB
poll accepted only transport state `device`. It did not record `offline`,
`unauthorized`, USB enumeration, or other transport states.
