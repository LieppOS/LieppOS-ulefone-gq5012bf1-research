# FT3680 firmware boundary

## Stock object

| item | value |
|---|---|
| symbol | `fw_file` |
| size | 118,972 bytes |
| stock section | `.data` (non-const) |
| stock offset | `.data+0x4a0` |
| SHA-256 | `2269a91f6c07421749f48db31651cf59d63c66da7db92ac767e10cc95ff910bf` |

The module contains no `MODULE_FIRMWARE` declaration. `fts_get_fw_file_via_request_firmware()` can request `focaltech_ts_fw_%s%s.bin`, but the selected built-in module record has an empty filename and `/vendor/firmware` contains no matching file, so the embedded image is the effective fallback.

## Selection and validation

- `module_list` has three records; module ID 0 is selected and only record 0 carries the built-in image.
- Runtime silicon selection uses the recovered 18-record `upgrade_setting_list` and boot IDs.
- Host-side ECC is CRC-16/Kermit (reflected polynomial `0x8408`) and is compared with controller-reported ECC.
- The stock array is writable `.data`, not `.rodata`; the reconstruction preserves that boundary in the private harness.

## Redistribution rule

The blob is a proprietary controller firmware image, not reconstructable source. This repository records only its identity, size, hash, section and selection semantics. It must not be copied into public research or source distributions.

The publishable source tree therefore omits `focaltech_ft3680_fw.i`. A builder must supply an independently authorised image or replace the include with an explicit external-firmware policy.

## Safety rule

No hardware programming or validation was performed. All work was offline ELF/source comparison. The private parity harness compiles programming branches only to reproduce static code. Before any runnable/public build, set `FTS_ALLOW_FW_PROGRAMMING` to `0`; this blocks PRAM/DRAM payload writes and start-PRAM execution. Do not test firmware writes without a recoverable controller and explicit authorisation.

The opaque firmware does not block the kernel-driver/source reconstruction status; it remains a separate `FT3680-FIRMWARE` boundary.
