# Checkpoint-instrumented Slot-B AVB pair

Final diagnostic pair:

- vendor_b candidate size: 816349184
- vendor_b candidate SHA-256: 814335c726d0d29b54009c4df4f869498c6c5e7ea0457fbd3442657b142a59de
- vbmeta_vendor_b candidate size: 4096
- vbmeta_vendor_b candidate SHA-256: 2b16ad27b333fb4ef35fb7d49eca36e5c20c86ac3558352a39a263cf0a5fd0ed
- vendor hashtree root digest:
  38f622a7da873a1a60ce266bf14472f043295cde
- expected trusted vendor public key SHA-1:
  664998c1c258771293715a829bd8caeae5d5626b

The resized vendor filesystem prefix was previously proven byte-identical to
the raw build through byte 800980992.

For the final verification, the resized image was copied to an isolated
directory as vendor.img so avbtool's vendor descriptor could not accidentally
resolve to the raw build image.

PAIR_READY=1
PHONE_MODIFIED=0
