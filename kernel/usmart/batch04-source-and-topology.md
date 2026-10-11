# Batch04 uSmart integration preservation

Selected extcon-mtk-usb now has independent complete stock A source acceptance in
android_kernel_modules_usb_platform_ulefone_gq5012bf1 at
b80b5b115548ee5d728690f7b937eccec161318c. Other selected USB consumers and PHY also
match wholly. This preserves the board-specific uSmart implementation, not a new driver
or authorization to operate it.

Existing GPIO28 active-low detect, GPIO152 accessory power and GPIO55 D+/D− route evidence
remains authoritative. GPIO55/152 do not power or select the internal thermal module;
thermal usesGPIO149/191/192 via separately owned yft_tiny2c_usb plus tiny2c_mode. Old USB
topology's contrary labels were corrected during historical recovery. Physical thermal/
default route sharing remains UNKNOWN; all paths share USB0/controller role.

Type-C notifications are not serialized with a uSmart-active lock; route/power GPIOs can
remain selected while role changes. Removal queuesNONE without replay of already attached
Type-C state. Existing typec-interaction.md/usb-routing.md record these stock limitations.
No new measured behavior or unsupported simultaneous-port capability is claimed.

Complete source hashes, dependency/load/DT/API evidence and grades:
reverse-engineering/kernel-source-reconstruction/PLATFORM-BATCH-04/HARDWARE-CONTRACT.md.
No accessory/PD/USB role/GPIO/firmware/phone operation or push.
