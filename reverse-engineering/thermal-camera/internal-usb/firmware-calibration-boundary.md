# Firmware / calibration boundary (integration)

- The internal USB integration (yft_tiny2c_usb, extcon-mtk-usb, MTU3/xHCI, usbcore) loads
  **no firmware** and has no `request_firmware` path for the module.
- The module boots from its own flash (enumerates ~0.73 s after rails on, no host download).
  Updates only through the explicit SDK upgrade over USB (vdcmd, then USB DFU) — AC020-UVC
  `firmware-boundary.md`.
- Calibration lives in module flash and is read/written over USB vdcmd (`adv_cfg_file_*`) —
  AC020-UVC `calibration-boundary.md`. No I2C calibration path (FM78100-COMPANION).
- Radiometry, image processing and fusion are THERMOVUE-T2 / THERMAL-RADIOMETRY scope.
