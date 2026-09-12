# GQ5012BF1 CO5300 TinyLCD source reconstruction

This is a source reconstruction of stock `spi_tiny_co5300_lcd.ko` for the
exact Android 6.1.115 GKI workspace. It preserves the stock DT binding,
340x340/320x320 RGB565 paths, SPI rates, CO5300 command table, TE state
machine, misc ioctl ABI, YFT registry calls, and Hynitron gesture/power calls.

Provider ABI inputs:

- `hynitron-rebuilt.Module.symvers`: copied from the real source-built
  Hynitron provider;
- `stock-yft-devinfo.symvers`: the two stock YFT TinyLCD export CRCs read from
  the stock provider's `__kcrctab`.

No CRC patching, manual `__versions`, fake provider object, ELF edit, or
modpost-warning bypass is used.
