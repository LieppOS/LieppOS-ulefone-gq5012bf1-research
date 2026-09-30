# OrangeFox fastbootd direct-start runtime test

The previous same-boot test established that BootControl was healthy before
requesting sys.usb.config=fastboot, but the host never received a fastboot
transport and ADB remained connected.

This test separates two questions:

1. does OrangeFox init successfully start fastbootd after BootControl is ready?
2. if so, does fastboot FunctionFS become ready even while the USB gadget
   remains exposed as ADB?

No partition writes or reboots are performed. If this test manually starts
fastbootd, it restores the original stopped state afterward.
