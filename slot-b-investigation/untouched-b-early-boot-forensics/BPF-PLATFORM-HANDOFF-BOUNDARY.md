# Slot-B platform BPF loader handoff boundary

Current-B `/system/bin/bpfloader` is an Android-35 arm64 Rust executable.

All ELF `DT_NEEDED` libraries observed for it are present in the current-B
filesystem image, including:

- `libandroid_logger.dylib.so`
- `liblog_rust.dylib.so`
- `libstd.dylib.so`
- `libc.so`
- `libbpf_android.so`

Current-B `libbpf_android.so` exports all three symbols required by the
platform bpfloader wrapper:

- `createBpfFsSubDirectories`
- `legacyBpfLoader`
- `execNetBpfLoadDone`

Exact Android 15 source confirms the platform loader sequence:

1. initialize logging;
2. create required bpffs subdirectories;
3. execute the legacy platform BPF object loader;
4. exec `/apex/com.android.tethering/bin/netbpfload done`.

The final netbpfload `done` path sets `bpf.progs_loaded=1`.

Failure exits are explicit:

- bpffs-directory setup failure -> exit 120;
- legacy BPF object loading failure -> sleep 20 seconds, exit 121;
- failure to exec netbpfload `done` -> exit 122.

These failures can propagate through the existing init
`reboot_on_failure reboot,bpfloader-failed` service policy.

No such failure has been observed on B.

The initial host check reported `/system/bin/linker64` as missing. That result
is NOT yet classified as a defect because `test -e` follows symlinks. An
absolute Android symlink into `/apex/com.android.runtime/...` can appear
dangling from a host-mounted filesystem even though it resolves normally in
Android after APEX activation.

The exact linker symlink and Runtime APEX target must therefore be inspected
without following the host-side absolute target before drawing any conclusion.

If linker resolution and platform BPF-object metadata are coherent, static BPF
investigation should stop absent direct runtime evidence of `bpfloader-failed`.
