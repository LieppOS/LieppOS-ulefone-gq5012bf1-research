# Security and integrity

`libcommon_utils.so` performs native `getPackageName`, `getSha1Sig`, `checkPckNameValidity`, `checkSigValidity` and `isSigValid`. Static relocated data reveals a package whitelist including `com.energy.usbir`, `com.energy.usbdual`, `com.energy.usbirmini640`, `com.energy.usbirmini640v2`, `com.infisense.eco`, `com.energy.tc2c`-family donors and other OEM apps. Strings include multiple 40-hex SHA-1 certificate fingerprints. This is an application/signature gate, not cryptographic protection of USB traffic.

`libencrypt_comm.so` bundles AES, hashes/signature support and JSON/config encryption. Firmware packages have JSON manifests and integrity/status checks. Do not bypass these checks for production updates.

LieppOS integration options, safest first:
1. retain the stock signed app and native libraries under original package/SELinux policy;
2. use a narrow privileged broker signed/installed consistently and expose only safe read/stream APIs;
3. independently reimplement only verified non-destructive UVC controls.

Never make `/dev/bus/usb` globally writable. Grant only the thermal VID:PID/interface after it is measured. Preserve module calibration, `/mnt/vendor/nvcfg/infiray`, app-private readbacks, SELinux labels and hashes. Firmware, flash, ROM-entry, calibration writes and clear/reset commands require explicit expert authorization and backups.
