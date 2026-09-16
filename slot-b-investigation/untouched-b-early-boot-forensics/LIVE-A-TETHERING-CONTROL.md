# Working Slot-A Tethering/BPF control

A read-only control capture was taken from fully booted Slot A on the exact
Ulefone stock kernel.

Observed:

- `ro.boot.slot_suffix=_a`
- `sys.boot_completed=1`
- `apexd.status=ready`
- `init.svc.bpfloader=stopped`
- `com.android.tethering` is active under `/apex`

The active A Tethering APEX defines:

`service bpfloader /apex/com.android.tethering/bin/netbpfload`

with:

`reboot_on_failure reboot,bpfloader-failed`
`override`

Since Slot A remains successfully booted, its oneshot bpfloader invocation did
not terminate through the reboot-on-failure path.

Therefore the exact Ulefone kernel is demonstrably capable of supporting a
working Android-15 Tethering BPF configuration.

The active A netbpfload binary is:

- size: 102536 bytes
- SHA256:
  `8bd11fc4ad29f082766c30f77cf38c5b3351eb45a2980190ecff34f809ebae80`

Its BPF payload includes mainline objects for at least:

- offload
- test
- netd
- dscpPolicy
- clatd

The current-B Tethering payload is a different revision/layout. Thus generic
lack of stock-kernel BPF support is strongly weakened, while a B-specific
netbpfload/BPF-object compatibility failure remains possible.

The current A boot-time logcat/dmesg buffers contained no retained matching
netbpfload/BPF-loader lines. This is negative log-retention evidence only and
does not contradict the successful service state.
