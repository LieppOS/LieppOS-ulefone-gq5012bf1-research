# Current Slot-B Tethering BPF loader conclusion

The exact current-B `com.android.tethering` CAPEX has been unpacked host-side.

Its original APEX contains:

- `/bin/netbpfload`
- `/etc/netbpfload.33rc`
- `/etc/netbpfload.35rc`

For Android V, `netbpfload.35rc` defines the real APEX service:

`service bpfloader /apex/com.android.tethering/bin/netbpfload`

with:

- `override`
- `reboot_on_failure reboot,bpfloader-failed`

It also defines `mdnsd_netbpfload`, which can trigger:

`reboot,netbpfload-failed`

Therefore `/system/bin/netbpfload` being absent is expected.

The system-side `/system/bin/false` definition is deliberately a fallback and
can cause `reboot,netbpfload-missing` only if the Tethering APEX service
override is not loaded.

There are now two distinct Tethering failure mechanisms to investigate:

1. APEX activation/config import failure:
   fallback `/system/bin/false` survives
   -> `reboot,netbpfload-missing`

2. APEX activates but its real `netbpfload` fails:
   -> `reboot,bpfloader-failed` or `reboot,netbpfload-failed`

The B embedded original Tethering APEX SHA256 is:

`8023cff4dfc5ffafd86ce081610906974c8d1b242ea779444fcad44211daf34f`

The currently shared stock-A decompressed Tethering APEX SHA256 is:

`ec3e2e246d6ce411fc2cca74581c1e70d43635bf259a952407b05543c8e3629a`

They differ.

This mismatch is not itself classified as a defect because Android 15 apexd
validates decompressed CAPEX payloads by version, root digest, and public key
before reuse and has redecompression/replacement paths for mismatches.

The next investigation target is the real BPF loader path: exact APEX RC import
timing, historical reboot-target evidence, Tethering BPF object requirements,
and compatibility with the stock Ulefone kernel BPF configuration.
