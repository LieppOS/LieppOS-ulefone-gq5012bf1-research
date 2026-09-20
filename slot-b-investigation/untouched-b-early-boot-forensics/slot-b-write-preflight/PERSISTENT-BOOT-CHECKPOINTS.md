# Persistent Slot-B boot checkpoints

The first-stage fstab and live Slot-A state establish that `/metadata` is a
suitable persistent diagnostic channel:

- `/metadata` is F2FS and mounted read-write.
- `/metadata` is explicitly `first_stage_mount`.
- approximately 33 MiB was free during the audit.
- evidence written there survives manual recovery to Slot A.

The first-stage fstab also mounts `system_ext` as a slot-selected logical
partition during first stage. Together with the existing hwservicemanager
binary and explicit `start hwservicemanager`, the previous missing-executable
hypothesis is demoted.

A diagnostic vendor init RC now records these milestones:

00 early-init
10 fs
20 hwservicemanager running
21 hwservicemanager ready
25 late-fs trigger entered
30 post-fs reached
40 vendor modules ready
50 post-fs-data reached
51 SoC model ready
60 APEX activated
69 odsign running
70 odsign key complete
80 odsign verification complete
90 zygote running
99 boot completed

No partition was written by this source-change step.
