# Slot-A vs Slot-B Tethering APEX generation difference

Known-working Slot A and current Slot B use materially different Tethering APEX
revisions.

Slot A:

- module version: `361099999`
- netbpfload size: `102536`
- netbpfload SHA256:
  `8bd11fc4ad29f082766c30f77cf38c5b3351eb45a2980190ecff34f809ebae80`
- newer Android-15/25Q2-style RC
- includes `SYSLOG` capability
- BPF objects live under `etc/bpf/mainline`

Slot B:

- module version: `352090000`
- netbpfload size: `102504`
- netbpfload SHA256:
  `f78d6e8d09cc9aae705679f4872ea7faa126b8075cc2b3f41438f8038b3de2f3`
- older Android-V RC
- no `SYSLOG` capability in the observed bpfloader service
- older split BPF layout including `net_shared`, `netd_shared`, and
  `@mainline` object variants

The shared `/data/apex/decompressed` Tethering object is Slot-A version
`361099999`, while B ships version `352090000`.

This makes generic kernel BPF incapability unlikely because A proves the kernel
can run a working Android-15 Tethering BPF stack.

The remaining question is whether B's older Tethering APEX itself is
incompatible with this device stack, or whether interaction with the shared
higher-version A decompression cache affects B activation.
