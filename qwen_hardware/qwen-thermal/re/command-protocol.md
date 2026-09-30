# Command protocol

See `protocol/vdcmd-uvc-transport.md` for the wire reconstruction.

The exact OEM command architecture is `IrcmdEngine` -> JNI -> `libircmd020.so` (`vdcmd.c`) -> selected transport driver. Three packet families exist: standard, short and long; all support read/write, polling and CRC helpers. OEM UVC binary immediates corroborate vendor requests 0x44/0x45, wValue 0x78 and status selector 0x0200. Donor trace provides selectors 0x1d00/0x1d08/0x1d10 and long/chunk selectors 0x9d00/0x9d08; these are high-confidence family behavior but still require an Armor capture before destructive or firmware commands.

The typed surface covers device info/state, preview, gain, FFC/shutter, palette, environmental correction, DPC/RMVC, TNR/DDE/gamma/edge, stream taps, files/flash, firmware and diagnostics. Recovered command names are exact symbols; unverified numeric opcodes are not invented.
