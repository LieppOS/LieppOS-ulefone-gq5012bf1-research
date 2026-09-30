# Power sequencing

FactoryMode powers thermal on by writing `1` to both:
1. `/sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode`
2. `/sys/class/yft_extcon/tiny2c_mode`
then registers `USBMonitor`. On disconnect/destroy/check completion it unregisters and writes `0` to both.

`yft_tiny2c_usb.ko` disassembly proves its mode store sets all four module GPIO rails high for 1, low otherwise, and sets external `yft_usb_flag` accordingly. Its helper has no per-rail delay: all rails receive the same level in struct order. Probe obtains GPIOs and performs an I2C chip-ID read at 0x3c. The extcon node is owned by `extcon-mtk-usb.ko`; its store parses 0/1 and queues delayed work, routing USB/OTG asynchronously.

Safe order matching stock: extcon/role and rail nodes must both be coordinated; wait for USB hotplug; open via Android USB permission; stop stream/release libusb before switching off. Never leave libusb transfers active while dropping rails. Exact delay within extcon work and module settle time need live timing/log evidence.
