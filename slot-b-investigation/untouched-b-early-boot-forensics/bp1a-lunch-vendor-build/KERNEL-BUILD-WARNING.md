# Lineage kernel.mk prebuilt-kernel warning

During the successful BP1A `vendorimage` build, Lineage emitted:

- the device is using a prebuilt kernel binary;
- building from a prebuilt kernel is deprecated;
- kernel source should eventually be provided under the device's kernel source path.

Classification:

`PREBUILT_KERNEL_WARNING=EXPECTED_FOR_CURRENT_BRINGUP`

This warning does not invalidate the current vendor-image work. The
`vendorimage` target completed successfully and the MT6878 insmod configuration
was independently verified inside the final EROFS vendor image.

It remains technical debt for the eventual full custom-kernel integration.
The long-term LieppOS target is to replace the prebuilt-kernel path with the
reconstructed/source-built Ulefone MT6878 kernel.

Other build warnings about optional `wear-sdk` / XR uses-libraries and duplicate
identical BoardPlatform/ProductModel keys were non-fatal for this build target.
