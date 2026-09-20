# Slot-B-sized fixed vendor image

The raw Lineage-built fixed vendor image was 4096 bytes larger than the current
vendor_b allocation.

The corrected AVB maximum-image-size calculation showed this was not a
filesystem-capacity problem.

Current vendor_b allocation:

`816349184`

Maximum AVB original-image size:

`803381248`

Fixed EROFS/original-image size:

`800980992`

Available original-image headroom:

`2400256`

The fixed filesystem therefore fits the existing vendor_b allocation without
shrinking the filesystem or resizing super.

A copy of the already-verified fixed vendor image was resized with
`avbtool resize_image` to the exact existing vendor_b allocation.

Resulting image:

`/mnt/SamsungSSD/android/lineage-22.2/out/target/product/armol/vendor.slotb-fit.img`

Size:

`816349184`

SHA256:

`7abbeb81e68ab4e9afd5847ea788b0c6bcdc48f9d6fc049d4b1b81d0e84c71ba`

The embedded AVB metadata and hashtree descriptor remained semantically
identical to the previously verified fixed vendor image.

`EMBEDDED_AVB_SEMANTICS_IDENTICAL=1`

The existing regenerated vbmeta_vendor was then verified against the resized
vendor image using both its embedded public key and the expected vendor.pem
key.

`PAIR_VERIFY=1`

`EXPECTED_KEY_VERIFY=1`

Final conclusions:

`SUPER_RESIZE_REQUIRED=0`

`EROFS_REBUILD_REQUIRED=0`

`VBMETA_VENDOR_REGEN_REQUIRED=0`

`ROOT_VBMETA_REWRITE_REQUIRED=0`

`SLOTB_VENDOR_READY=1`

The large vendor image itself is not committed to the research repository;
its path, size and SHA256 are recorded here.

No phone operation occurred.
