# hwservicemanager lifecycle V2 Slot-B AVB pair

vendor_b candidate:

- SHA-256: fd98debd4863cbb7626ef40c633789c1f9bbe9021b9aea9489be5160f045a613
- size: 816349184
- hashtree root: 37c8d0d37656e92c22d5cc221a7ddd0da3e7432a

vbmeta_vendor_b candidate:

- SHA-256: 4ffdac2894b54c47f2582afb2b180f12452e0f8f493e0acd1bf391bb3947e039
- size: 4096
- trusted vendor public-key SHA-1: 664998c1c258771293715a829bd8caeae5d5626b

The original EROFS filesystem prefix was compared byte-for-byte before and
after AVB resize.

The exact resized vendor image and signed vbmeta_vendor image were then copied
to an isolated directory as vendor.img and vbmeta_vendor.img and verified
together with avbtool.

PAIR_READY=1
PHONE_MODIFIED=0
