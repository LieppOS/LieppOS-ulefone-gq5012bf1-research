# Remaining unknowns and exact evidence needed

| Unknown | Evidence required |
|---|---|
| Installed detector resolution/model/pitch | Passive powered USB descriptors/product/serial plus one stock frame byte count; teardown/module label for silicon proof |
| Actual module VID:PID, speed, interfaces/endpoints/altsettings | `/sys/bus/usb/devices` + raw descriptor/`lsusb -v` after stock app powers module |
| Shipping frame plane offsets and two metadata-line fields | One unmodified frame in each stock negotiated format and correlated stock parser trace |
| Complete AC020 opcode table | USBPcap/usbmon capture of individual safe stock UI actions; map one variable at a time |
| Exact native KT/BT/NUC/environment math and fixed-point scales | Ghidra/rizin decompilation of named exports, vendor headers, or controlled blackbody observations |
| Per-unit file binary layouts/checksums | Read-only `advFileRead` backups from a sacrificial/authorized unit and differential comparison; no writes |
| Exact power/mux delays | Timestamped kernel log + USB hotplug trace through on/off lifecycle |
| Shutter cadence and FFC trigger thresholds on shipping firmware | Observe status/events during stock operation; no forced commands required |
| Firmware/DFU VID:PID and package signature format | Official package/docs or authorized spare-module capture; do not enter ROM on production unit |
| Ulefone UI feature inventory/version | Screenshots/interaction trace from the exact stock build; current snapshot ran LieppOS GSI userspace |
| Accuracy/range/NETD on this physical unit | Manufacturer module label/datasheet and calibrated blackbody/reference tests |
