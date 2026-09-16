# Current-B BPF handoff follow-up

Current B contains a valid Android-35 arm64 platform bpfloader:

- path: `/system/bin/bpfloader`
- size: `52808`
- SHA256:
  `32b3fd8c6ea4fbbeb0334fa1b237fc27f77114c422acb8d1a105cba00d889c74`
- Build ID:
  `00e89b7144483dccb2be27f5227e4933`

Therefore absence of `com.android.uprobestats` does not by itself break the
netbpfload post-mainline handoff. NetBpfLoad can fall back to the platform
`/system/bin/bpfloader`.

Working A differs:

- platform bpfloader size: `103568`
- SHA256:
  `48ddd61b3c9ef9044f88db945948b50e63d4c60993a330a8e7042d4d9934a394`
- working A has `com.android.uprobestats`
- working A reports `bpf.progs_loaded=1`

Current-B BPF object metadata also contains two generations.

Mainline/current objects include:

- `netd_shared/netd.o`
- `net_shared/clatd.o`
- `net_shared/dscpPolicy.o`
- `offload@mainline.o`
- `test@mainline.o`

These advertise:

- minimum bpfloader version: `43`
- maximum bpfloader version: `65536`

Android-V root netbpfload computes loader version `46`, which is within this
range.

Legacy `offload.o` and `test.o` advertise:

- minimum: `2`
- maximum: `19`

This does not yet establish a failure. Exact source behavior for
`bpfloader_min_ver` / `bpfloader_max_ver` must be checked to determine whether
these legacy objects are intentionally skipped for loader version 46.

No runtime claim is made that B reached or failed either bpfloader stage.
