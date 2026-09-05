# Phase 4 — FocalTech FT3680 touchscreen

Target stock module:

    focaltech_touch_spi_ft3680.ko

Device:

    Ulefone Armor 29 Pro Thermal
    GQ5012BF1
    MediaTek MT6878 / MT6878T

## Authoritative report

**This page is superseded.** The authoritative, evidence-backed reconstruction
report is:

    $RESEARCH/kernel/phase4-focaltech-ft3680-reconstruction.md

Read that document for the stock oracle identity, source provenance, ABI and
structural comparisons, device/firmware contracts, residual classification and
the final status. Supporting evidence lives in:

    $RESEARCH/workspace/phase4-focaltech-ft3680/

and the build/reconstruction workspace is:

    $GKI_WS/lieppos/focaltech-ft3680-recon/

## Status

The initial Phase 4 classification on this page was:

    NEEDS_ULEFONE_PORT

That has been replaced by the evidence-backed final classification:

    BLOCKED_WITH_EXACT_MISSING_EVIDENCE

Summary of what is now established (details in the authoritative report):

- the stock module is FocalTech driver revision `FocalTech V4.2 20240407`,
  built with the same clang as exact GKI 12901745;
- the closest source is the public NothingOSS MT6878 FocalTech **V4.1** driver
  at commit `957dac185efe46cbf6336b0fff9516d84c8cd78f`; no public V4.2/FT3680
  source exists;
- the untouched donor and the reconstruction both build against exact GKI
  12901745 with `BUILD_RC 0`;
- all 104 stock imports resolve with zero CRC mismatches; the module exports
  nothing and no stock module consumes it;
- the GQ5012BF1 device-tree, power/GPIO and firmware/config contracts are fully
  recovered, and the 118,972-byte stock firmware image is preserved
  byte-for-byte in the reconstruction;
- work remains blocked on six precisely identified evidence gaps
  (`yft_devinfo`/`yft_tpd_gesture` source, the FT3680 chip-ID tuple, the
  upgrade-setting record semantics, the FHP ioctl ABI and the firmware-debug
  protocol).

No device tree, partition, boot image or live phone state was modified during
this work.
