# Batch04 USB source and board routing preservation

All ten selected USB host/gadget/PHY/platform modules have complete stock A acceptance
from maintained usb_platform commit `b80b5b115548ee5d728690f7b937eccec161318c`.
Three source-family engines independently compiled all30 B1/B2 with originals unavailable;
all30 raw/stripped and156 intermediate objects reproduce identically.25 whole accepted,
five source/token/TCPC C failures explicitly retained. Full evidence:
../kernel-source-reconstruction/PLATFORM-BATCH-04/USB-HOST-GADGET-PHY/.

Actual extcon YFT source, controller/gadget/PHY composition, USB boost/logging/offload
and natural exported types are preserved; no copied target objects or stock CRC overrides.
ADSP/SCP/audio producer APIs are source-checked, not firmware startup/offload proof.
Type-C source uses genuine public2.0.31 plus full historical patches; its incomplete
metadata/behavior is not excused by the USB consumer's complete acceptance.

Important established routing correction:GPIO55/152 are uSmart USB2 pair/power controls,
not internal thermal camera controls. Thermal's separately owned yft_tiny2c_usb uses
GPIO149/191/192 and tiny2c_mode. USB0 PHY/MTU3/xHCI and role state are shared; physical
thermal/default route wiring remains UNKNOWN. hardware/topology.md is corrected from
kernel/usmart and thermal-camera evidence, not new hardware testing. Type-C support
and generic XS-PHY code do not establish a fitted USB3 path or concurrent independent ports.

See Batch04 HARDWARE-CONTRACT.md and actual per-target source/DT/resource/load/API ledgers.
No USB role/PD/GPIO/charging/DMA/firmware commands or phone interaction occurred.
