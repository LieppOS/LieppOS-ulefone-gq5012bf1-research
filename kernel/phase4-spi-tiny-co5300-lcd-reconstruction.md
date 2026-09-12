# Phase 4 `spi_tiny_co5300_lcd` reconstruction closure

## Classification

**NO_PUBLIC_SOURCE_FOUND / STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE / SOURCE_RECONSTRUCTED / SOURCE_NOW / FROZEN FOR RE**

No exact public source donor was found. Generic SSD1317 and CO5300 sources were
used only as bounded controller/structural references; all device-specific
behavior comes from the frozen stock ELF, stock DT, and stock TinyLCD HAL.

## Reconstructed scope

The source reconstruction preserves:

- the exact `hxytech, spi_tiny_lcd` compatible and stock SPI-driver identity;
- all 25 stock function names, with exact KCFI IDs on every address-taken
  callback;
- the complete 58-entry MODVERSION map and zero exports;
- all four vendor provider edges and their exact CRCs;
- mode-3 SPI, 52 MHz writes, 1 MHz reads, command/data DC polarity;
- accepted IDs `DA=33`, `DB=10/11` and `tiny_lcm_number` mapping;
- the exact 1232-byte, 44-record CO5300 initialization table;
- exact 340x340 and centered 320x320 RGB565 frame paths;
- the exact 231200-byte embedded image object;
- falling-edge TE IRQ, delayed work, and frame-status state machine;
- rail/reset/pinctrl/IRQ power sequencing and AOD behavior;
- `/dev/tiny_lcd_miscdev`, native ioctl values, compat-forwarding quirk, and
  five SPI-driver sysfs attributes;
- stock YFT registry and rebuilt-Hynitron power/gesture integration;
- stock boot-mode exclusion and lifecycle behavior.

Detailed contracts:

- `phase4-spi-tiny-co5300-lcd-behavior-contract.md`
- `phase4-spi-tiny-co5300-lcd-userspace-abi.md`
- `phase4-spi-tiny-co5300-lcd-dt-provider-contract.md`
- `phase4-spi-tiny-co5300-lcd-register-map.tsv`

## Exact object evidence

These rebuilt objects are byte-identical to stock, including sizes and
initializers:

- `gImage_logo` (231200 bytes);
- `init_setting` (1232 bytes);
- `spi_tiny_lcd_driver` (216 bytes);
- `tiny_lcd_fops` (272 bytes);
- `tiny_lcd_miscdev` (80 bytes);
- `framesize` and `write_frame_status`;
- all five `driver_attr_*` objects;
- OF match tables and the principal scalar/state objects.

The stock compiler split an anonymous global aggregate into `g_data.0` through
`g_data.13`; reconstructed source expresses the same fields as one typed
`struct tiny_lcd_data`. This accounts for the object-count difference (64 stock
versus 55 rebuilt) and is not an ABI difference: none of the state objects is
exported.

## Provider provenance

- Hynitron calls are linked against the real source-built Hynitron
  `Module.symvers`; Hynitron remains frozen and was not reopened.
- The historical YFT `*_device_add()` CRC gap is handled with the permitted
  two-symbol stock `yft_devinfo` ABI witness. The CRCs were extracted directly
  from stock `yft_devinfo.ko::__kcrctab`.
- No CRC patching, manual `__versions`, fake provider object, ELF edit, or
  `KBUILD_MODPOST_WARN` is present.

## Verification result

`kernel/scripts/phase4_spi_tiny_co5300_lcd_verify_recon.py` passes **30/30**.
It fail-closes on source/artifact hashes, function/KCFI parity, exact import/CRC
maps, provider CRCs, critical object bytes, controller/geometry/SPI/ioctl/TE/
power/boot contracts, provider provenance, prohibited ABI fabrication, and the
warning-free exact-GKI build log.

The final module is:

```text
/home/armol/kernel-work/gki-12901745-workspace/lieppos/spi-tiny-co5300-lcd-recon/spi_tiny_co5300_lcd.ko
SHA256 9149da0533d4d8327518d22762964c2e656f4aeb95fdd8a88280c109555dbfe2
```

Static/offline scope remains intentional: no module loading, live SPI/GPIO,
power/reset, sysfs/ioctl operation, DT modification, flash, or reboot was
performed.
