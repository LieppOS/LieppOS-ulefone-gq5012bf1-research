# V13 vendor image size handling

The size-neutral V13 source modification changed exactly six bytes in
init.insmod.sh and preserved its 1244-byte file size.

A normal vendorimage rebuild nevertheless produced:

    816357376 bytes

while the existing Slot-B vendor logical extent is:

    816349184 bytes

Difference:

    8192 bytes

No oversized image was written to the phone.

A copy of the V13 vendor image was tested with AVB's resize_image operation
against the exact existing vendor_b extent.

RESIZE_RC=0
FIXED_VENDOR_SIZE=816349184
SOURCE_ROOT_DIGEST=65ffa3b7dc5bc2018a936f4b321a530561e6d2fd
FIXED_ROOT_DIGEST=65ffa3b7dc5bc2018a936f4b321a530561e6d2fd
FIXED_VENDOR_VERIFY_RC=0
V13_FIXED_PAIR_READY=1

PHONE_MODIFIED=0
