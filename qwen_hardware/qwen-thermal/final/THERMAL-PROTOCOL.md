# Thermal protocol

Imaging uses Android USBFS/libusb/libuvc; output modes are YUYV, NV12 and combined image+temperature. Commands use InfiRay vdcmd standard/short/long frames over UVC vendor controls with polling and CRC. OEM binary corroborates requests 0x44/0x45, wValue 0x78 and status selector 0x0200; donor captures supply the remaining high-confidence selector/header mapping and limited opcodes.

Do not send donor opcodes to this module until verified by passive stock capture. See `../re/usb-transport.md`, `../re/uvc-stream.md`, `../re/protocol/vdcmd-uvc-transport.md` and `../re/reconstructed-ac020-api.h`.
