# External driver donors

## AW883XX audio amplifier

Awinic publishes an official GPL-2.0 AW883XX SmartPA driver:

https://github.com/awinic-driver/aw883xx

Awinic also publishes a kernel integration patch:

https://github.com/awinic-driver/aw883xx_patch

The published source contains explicit MediaTek platform handling through
AW_MTK_PLATFORM.

This is a high-value candidate source donor for the stock Ulefone
aw883xx_driver.ko.

Exact source equivalence is not yet proven. The next step is comparison of:

- DT compatible / I2C identification
- module aliases
- imported kernel symbols
- exported symbols
- firmware/profile naming
- driver strings/version information

against the stock GQ5012BF1 aw883xx_driver.ko.

## AW36515 flashlight

A separate Android 15 MT6878 device, TECNO Pova 7 5G / LJ7, is publicly
documented using AW36515 flash hardware.

Observed userspace interfaces include V4L2 flash subdevices named:

- aw36515-led0
- aw36515-led1

and standard V4L2 flash controls.

Reference:

https://github.com/AndyRathaur/volkey-torch

This does not provide AW36515 kernel source by itself, but it confirms that
AW36515 is used in another contemporary MT6878 Android implementation and
suggests that MediaTek V4L2 camera-flash integration is the appropriate donor
architecture to investigate.

A public LJ7 development organization also exists:

https://github.com/Tecno-Pova-7-5G-LJ7-Development

It exposes device, kernel and firmware-dump repositories and should be
inspected as a possible MT6878/AW36515 donor.


## AW883XX stock-to-upstream comparison

The stock GQ5012BF1 aw883xx_driver.ko was compared with Awinic's public
aw883xx source at:

4f52a107e82b88512124a14cc69601cdefd40b9e

The comparison shows unusually strong source-lineage agreement.

Stock module metadata includes:

- description: ASoC AW883XX Smart PA Driver
- license: GPL v2
- module name: aw883xx_driver
- import namespace:
  VFS_internal_I_am_really_a_filesystem_and_am_NOT_a_driver

The public source contains:

- the same module description
- the same GPL v2 license
- MODULE_IMPORT_NS for the same unusual VFS namespace
- AW_MTK_PLATFORM enabled
- ACF configuration parsing
- DSP firmware/configuration management
- calibration paths
- CRC checking
- firmware/profile handling
- I2C device name aw883xx_smartpa
- OF compatible awinic,aw883xx_smartpa
- default ACF filename aw883xx_acf.bin

The stock binary also contains many diagnostic strings corresponding directly
to these public source subsystems, including ACF parsing, DSP firmware,
calibration, CRC checks and AW883XX device registration.

Conclusion:

The public Awinic repository is now classified as a PROBABLE_DIRECT_SOURCE_FAMILY
for Ulefone aw883xx_driver.ko, not merely a related hardware donor.

Exact source revision equivalence remains unproven. Driver version, OF/I2C
aliases and additional distinctive strings should be compared next.


### AW883XX version comparison

The stock GQ5012BF1 binary contains:

- driver version: v1.7.1
- ACF filename: aw883xx_acf.bin
- I2C/device identifier: aw883xx_smartpa
- diagnostic format: driver_ver: %s

The checked public Awinic revision
4f52a107e82b88512124a14cc69601cdefd40b9e contains:

- driver version: v1.6.0
- ACF filename: aw883xx_acf.bin
- I2C/device identifier: aw883xx_smartpa
- identical module description
- identical unusual VFS namespace import
- matching ACF/DSP/calibration architecture

Conclusion:

The public source is very-high-confidence direct source lineage, but the
checked public revision is older than the Ulefone stock source.

The stock binary appears to derive from AW883XX driver v1.7.1, while the
current checked Awinic repository revision identifies itself as v1.6.0.

Reverse engineering from scratch is therefore unnecessary; the remaining task
is locating the v1.7.1 source revision or forward-porting v1.6.0 while
reconstructing the v1.7.1 delta.


### AW883XX v1.7.1 source availability

The stock binary identifies itself as AW883XX driver v1.7.1.

The checked official Awinic GitHub source identifies itself as v1.6.0.
The official repository exposes only a very small public history, and no
v1.7.1 source revision was found in the inspected repository history or in the
targeted public search.

An older official Awinic integration patch contains v1.3.0.

Therefore the current evidence indicates:

- Ulefone stock is from the same direct Awinic driver lineage.
- The public v1.6.0 tree is not the exact stock revision.
- Ulefone likely received a later vendor revision/branch.
- Reconstruction should start from Awinic public source rather than from
  disassembly.
- The useful reverse-engineering problem is the v1.6.0 -> v1.7.1 delta, not
  the entire AW883XX driver.

