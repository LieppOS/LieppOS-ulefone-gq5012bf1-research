# AW883XX integration summary

The full driver reconstruction remains in
`Reverse Engineer - DONE/AW883XX-SPEAKER-AMP/`.

- fitted chip: **AW88394**, PID 0x2049;
- one I2C instance: i2c-6 / 0x34, channel 0;
- reset GPIO 193, IRQ GPIO 41;
- library module: `mtk-sp-spk-amp.ko` calls exported probe/remove;
- MTK speaker type 5 = AW883XX;
- AFE playback/ref interfaces: I2S_OUT4 / I2S_IN4;
- one configured speaker channel;
- kernel result: 235/236 byte-exact, all 236 code/reloc/call/string equivalent,
  full ABI.

New route correction: the ACF's `Receiver` profile does not prove the amp drives
the earpiece. `RCV_PATH_INT=yes` selects the MT6369 internal receiver path in
stock; normal external-speaker playback selects AW88394.

See [`firmware-boundary.md`](firmware-boundary.md).
