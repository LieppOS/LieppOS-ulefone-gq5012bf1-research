# Hynitron userspace/factory consumer contract

A recursive static search of extracted `system`, `system_ext`, `product`,
`vendor`, and `odm` for Hynitron/CST816/second-touch/rear-touch/firmware terms
found no dedicated Hynitron application, service, factory binary, overlay,
SELinux rule, IDC, or key-layout consumer.

The two exact hits are:

1. `vendor/etc/init/init.touch.rc`, whose `on init` modprobe candidate list
   contains `hynitron.ko`.
2. Generic framework `system/lib64/libinputreader.so`, which contains the input
   device name `hyn_ts`; this is generic Android InputReader classification,
   not a private control protocol.

No userspace binary references either kernel export; those are direct kernel
ABI consumed only by stock `spi_tiny_co5300_lcd.ko`. Rear-display userspace
coordinates through that LCD driver's own interface, not directly through a
Hynitron ioctl/misc device. Driver-created sysfs ABI is inventoried separately
in `phase4-hynitron-userspace-abi.md`.

Marketing behavior is intentionally not inferred beyond this evidence.
