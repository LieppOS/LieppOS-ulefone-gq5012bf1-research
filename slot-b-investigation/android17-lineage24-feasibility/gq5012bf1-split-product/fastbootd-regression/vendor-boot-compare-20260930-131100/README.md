# vendor_boot fastbootd-regression comparison

The known-working August 12 fastbootd environment used exact factory V15
vendor_boot_a:

c8953d16b7a47976362aa23b53d0a08dde451f25cab4c552fa70c43e56ee0756

The current Slot-A vendor_boot hash is:

43e838073c3153e263173ad5fa8523b847cc5595fe7c1d2b1c3811b582b3e08b

Recovery/fastbootd is carried by the vendor_boot recovery fragment on this
device. This comparison parses the vendor boot v4 table and compares the
header, DTB, platform ramdisk, recovery ramdisk, and archive member sets.

Binary dumps/fragments are intentionally not added to git.
