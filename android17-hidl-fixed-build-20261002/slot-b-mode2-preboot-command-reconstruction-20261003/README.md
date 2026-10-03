# Slot-B mode-2 preboot command reconstruction

The prior shell-history audit found no explicit Oct 2 host
`reboot recovery` or `reboot fastboot` command, but zsh history had a large
gap covering the actual Slot-B experiments. Shell history is therefore not
sufficient negative evidence.

The experiment artifacts themselves provide a stronger timeline.

The first Slot-B boot was mode 0 and explicitly restarted with target
`bootloader` (reboot-mode value 3).

LK consumes and clears the reboot-mode field.

The later metadata-fixed boot began with mode 2.

Therefore a fresh value-2 write must exist between those events.

This audit reconstructs all device-control commands from the metadata-root
fix and metadata-install experiment transcripts and from every artifact
created in the 19:30-20:00 UTC critical window.

It also searches retained evidence for an explicit
`bootstrap-apexd-failed` marker.

No phone state is modified.
