# Contradictions and reconciliation

## 640x512 product claim vs 256x192 factory path
Prior hardware/marketing research identifies Mini640-class 640x512/12 um/25 Hz. FactoryMode and M170infDlp contain exact 256x192-class paths (256x384 combined, 256x386 with two metadata lines), while APK seed calibration includes 160x120 and WN640 tables. Reconciliation: the vendor SDK/FactoryMode is multi-product; the 256 and 160 paths can be generic/reused manufacturing support. Installed resolution remains STRONGLY_SUPPORTED 640x512, not locally proven until a powered descriptor/frame is captured.

## AC020 chip vs SDK family name
`AC020` is exact in library/class names and the command/radiometry stack. No passive silicon identifier string proves that the physical ASIC itself is branded AC020. Report it as AC020-class processing/SDK role with high confidence, not microscopy-level identity.

## No boot dmesg enumeration vs internal USB
The module is normally rail-gated and routed only when the app writes both sysfs nodes. Boot-only dmesg therefore need not contain enumeration. Libraries and FactoryMode prove the USB path.

## `/mnt/vendor/nvcfg/infiray`
Prior reports identify it as preservation-critical, but extracted readonly partitions do not contain runtime `/mnt/vendor` contents. Treat it as a runtime mount/path to verify and back up when present, not as captured evidence in this corpus.

## `fm78100`
Node name resembles a sensor name, but compatible/driver/functionality prove it is tiny2c module power/presence glue. Expected read ID is 0x4c59; neither string should be treated as detector model identity.
