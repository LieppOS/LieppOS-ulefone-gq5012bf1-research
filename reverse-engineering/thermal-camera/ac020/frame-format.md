# What crosses USB: frame byte format

Transport: UVC 1.10 isochronous IN 0x81, alt 1, 1024 B per µframe, each USB transfer
starts with a standard UVC payload header (stripped by the bundled libuvc
`_uvc_process_payload`); frames are delimited by the FID/EOF bits and validated by byte
count (`broken frame!:format=%d,actual_bytes=%d/%d(...)`).

The descriptor labels the format **YUY2, 16 bpp**, but only the first plane is a picture;
the payload is a container of three planes of 2-byte samples.

## Stock frame: 256×386 "YUY2" = 197 632 bytes (frame index 2)

| bytes | rows (of 256 × 2 B) | content | layout | evidence |
|---|---|---|---|---|
| 0 … 98 303 | 0–191 | **IR image**, 256×192 | 2 B/pixel, row stride 512 B; YUYV 4:2:2 as treated by the SDK (`FrameOutputFormat.YUYV_*`, `yuyv2bgr24`) — STRONGLY SUPPORTED; pixel semantics = module-rendered image | app copies `[0, mIrLength)` with `mIrLength = 256·192·2`, feeds it to `MNN_SR_TINY2C` / YUV→RGB (`yuyv2bgr24`) |
| 98 304 … 99 327 | 192–193 | **info lines** (2 × 512 B = 1024 B) | packed little-endian fields, map in `info-line-layout.tsv` | `IrcamEngine.getInfoLineBean()` reads `[mIrLength, mIrLength+1024)` |
| 99 328 … 197 631 | 194–385 | **temperature plane**, 256×192 | u16 little-endian per pixel, row stride 512 B | app copies `[mIrLength+mInfoLength, +256·192·2)` into `mTempData` and passes it to `TempCompensation`/`libadvirtemp*` |

`mIrHeight = (386 − 2) / 2 = 192`, `mInfoDataHeight = 2` (M170infisens `init()`);
`IR_SENSOR_HEIGHT 386`, `IR_SENSOR_LINE_HEIGHT 2` (M170infDlp `Const`). Total
256·386·2 = 197 632 = `dwMaxVideoFrameBufferSize` of frame 2. Image and radiometric data
share the **same** stream and the same frame; there is no second endpoint.

Byte order: little-endian for the temperature plane and every multi-byte info field
(`byteArrToBinStr` assembles bytes high-index first, i.e. LE, then keeps the low *n* bits).
No per-frame header/trailer beyond the UVC payload header; the in-band metadata are the two
info lines.

### Info lines (fields consumed by stock; offsets relative to the start of row 192)

See `info-line-layout.tsv` (32 fields). Highlights: frame counter u16 @128 and @360,
FFC countdown u8 @42, sun-protect flags @82/@138, max/min/point/region temperature
records (x/y 12-bit, temperature u16). The stock app converts info-line temperatures as
`value / 64 − 273.15 °C` (Kelvin in 1/64 K); that is an app-level formula on module-reported
values, recorded as observed, not as a radiometry model. Bytes not listed are not read by
stock and remain **UNKNOWN**.

### Temperature plane semantics

Byte layout PROVEN (u16 LE, 256×192). The conversion from these samples to scene
temperature in stock goes through proprietary code (`TempCompensation`, `libadvirtemp*`,
`libcommonsdk`, gain-dependent tables) and is **out of scope** (THERMOVUE-T2 radiometry).

## Frame 1: 256×194 (99 328 B)

Image plane (rows 0–191) + 2 info lines, no temperature plane — advertised, unused by
stock.

## Host-side derived formats (not on the wire)

`FrameOutputFormat` NV12 / NV12_AND_TEMP select libuvc mode 2 (NV12 GUID) — not offered by
this firmware, so only the YUYV modes can open. 640×512 output exists only after the app's
`MNN_SR_TINY2C` ×2 super-resolution (and optional fusion with the 1440×1080 visible
camera); it never crosses USB.
