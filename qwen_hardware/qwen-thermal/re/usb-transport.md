# Internal USB transport

The imaging path is userspace USB host access, not V4L2 exposed to ordinary Android camera APIs. `libusbuvccamera020.so` bundles libusb/libuvc Android USBFS code and opens `/dev/bus/usb/<bus>/<device>` using the file descriptor supplied by `USBMonitor.UsbControlBlock`. Open logs include DFU flag, VID, PID, fd, bus, address, usbfs root and format type.

Driver variants are USB, SPI, MIPI-I2C, USB dual, MIPI-I2C dual, USB dual/native-camera and USB omni; this phone uses internal USB in FactoryMode. Control and streaming interfaces are claimed through libusb; kernel-driver detach/reclaim, altsetting selection, interrupt/status endpoint and transfer cancellation are implemented.

No module enumeration occurred in the boot-only dmesg snapshot because the stock app had not powered it. Actual Armor VID:PID, interface numbers, endpoint address and USB speed remain unknown. Donor P2 Pro uses 0bda:5830 but this value must not be assigned to the Armor module without a live descriptor.
