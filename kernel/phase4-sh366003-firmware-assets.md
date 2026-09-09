# SH366003 firmware/profile assets

## Exact asset

| Path | Size | SHA256 | Referenced by | Format/version | Classification |
|---|---:|---|---|---|---|
| `workspace/phase4-sh366003/oracle/sinofs_afi_data.stock.bin` | 2,142 | `4888c5bc4b847ec6c118cd7bd334cbcffbf52c5fa2bf8f8660c3ac65e03359e1` | stock object `sinofs_afi_data`; `file_decode_process("sinofs_afi_data")` | 209-record SinoFS AFI data-flash program; target AFI 0x8cd3, profile/date 0x5a93 | exact embedded stock profile |
| `workspace/phase4-sh366003/oracle/sh366003_fg.stock.ko` | 85,968 | `527bddb4ddb11e94ed85e6969a10f807178cbb3f0fd326c8509824800a3d61a7` | vendor_boot/recovery module lists | ELF containing interpreter and embedded profile | frozen oracle |

`kernel/phase4-sh366003-afi-records.tsv` is a byte-exact decoded inventory; it is not a regenerated firmware blob. `workspace/phase4-sh366003/oracle/parse_afi.py` asserts both size and hash before decoding.

## External partition search

Stock vendor/system/product/system_ext/odm and extracted ramdisks were searched for `*.bin`, `*.hex`, `*.afi`, `*.fw`, `*.cfg`, and `*.dat`, plus strings `sh366003`, `sh366`, `fuel`, `gauge`, `battery`, `afi`, `profile`, `cell`, and `pack`.

No external file is referenced by this module. There is no `request_firmware` import, filesystem-open import, firmware filename, path, or userspace upload interface. The only accepted parser name is the literal `sinofs_afi_data`, which selects the embedded object.

MediaTek `fuelgauged` configuration/NVRAM assets belong to the primary MT6375 gauge path and are not classified as SH366003 assets.

No asset was modified, regenerated, or written to hardware.
