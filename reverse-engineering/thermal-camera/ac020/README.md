# AC020-UVC — Tiny2-C thermal module USB/UVC transport (GQ5012BF1)

**DONE (static, scope = USB/UVC transport + control boundary).** Status: `STATUS.md`.

**3474:4321, UVC 1.10, VS interface 1 alt 1 exposes one YUY2-labelled uncompressed format
with 256×194 and 256×386 frames at 25 Hz over isochronous IN 0x81 (1024 B/µframe); stock
negotiates 256×386 (256×192 image + 2 info lines + 256×192 u16-LE temperature). The GKI
built-in uvcvideo binds first, then the stock apps detach it and drive the device through
usbfs with a bundled libusb/libuvc. There is no Extension Unit and no standard UVC
control: thermal commands use vendor EP0 requests to interface 0 — 0x41/bRequest 0x20
(command), 0xC1/0x22 (status: 1 busy, 2 data ready, 3 done), 0xC1/0x21 (response) — with
18/12/24-byte CRC16-protected vdcmd frames from `libircmd020.so`.**

"AC020" is the InfiRay/Raytron SDK family name, not a chip: the module is a
Raytron/InfiRay Tiny2-C (TC2-C) whose own ASIC is the USB device; there is no bridge.

## Files

| file | content |
|---|---|
| `usb-device-identity.md` | AC020 verdict, VID/PID/strings/serial behaviour, DFU mode |
| `usb-descriptors.md`, `firmware-descriptor-dump.txt` | complete descriptor tree, decoded from the stock-shipped module firmware 00.00.04.07 |
| `usb-interfaces.tsv` | interfaces / alternate settings / endpoints with purpose and class |
| `uvc-capabilities.md` | UVC units, formats, frames, what stock negotiates, standard controls (none) |
| `frame-format.md`, `info-line-layout.tsv` | byte layout of a stock frame and the consumed info-line fields |
| `kernel-path.md` | GKI uvcvideo → usbfs takeover; no custom driver (parity N/A); V4L2 unused |
| `userspace-path.md`, `uvc-path.md` | app → JNI → libAC020sdk/libircmd020/libusbuvccamera020 → usbfs |
| `vendor-control-protocol.tsv`, `vendor-control.md` | EP0 vendor protocol, frame header, DFU, dead donor path |
| `vendor-opcodes.tsv` (M170 build, with stock callers), `vendor-opcodes-factorymode.tsv` | command header catalogue |
| `uvc-extension-units.tsv` | none |
| `stream-sequence.md` | power → role → enumerate → open → commands → probe/commit → alt 1 → frames; reverse |
| `fm78100-boundary.md` | relation to 8-003c / `yft_tiny2c_usb` |
| `firmware-boundary.md`, `calibration-boundary.md` | module flash, update path, calibration ownership/transport |
| `stale-claims.md` | 14 corrections |
| `scripts/` | `parse_fw_usb_desc.py`, `extract_vdcmd_headers_v2.py`, `ctl_sites.py`, `reproduce.sh` (+ the 2026-10-06 `extract_vdcmd_headers.py`) |

## Stock artifacts (sha256)

| artifact | sha256 |
|---|---|
| `system/app/M170infisens/M170infisens.apk` | `255ec1ab242daff5f9381395a98b87ef843d67530033f321dda888e9280b8b30` |
| `system/app/M170infDlp/M170infDlp.apk` | `dc9765c3a900fe11bededdac2d5b9d566b1260ccf9ee1636f14c3053b342c875` |
| `system/app/FactoryMode/FactoryMode.apk` | `01d431749b62000d666f2ec6c6191a7241997a7c5157245f8dc6b78af0050ca9` |
| arm64 `libAC020sdk.so` (M170*) / FactoryMode | `4af60e8e941729e87c5c8f572e1f89e2a8f2bf09b1ea9655fd9a1a4298bbc9d3` / `332764f014cb4f26566fddcea4e3cd055c48ac024247f9f929a7377b33f29869` |
| arm64 `libircmd020.so` (M170*) / FactoryMode | `682fe2a84121b46e53b5237e80fe1d9743624baf3f27e50827e67e8f95d36157` / `0aa7d5c751379281e6f6e8bfb88bb4b0eed2031b30072c1ccad7034dd3d281ad` |
| arm64 `libusbuvccamera020.so` (M170*) / FactoryMode | `d3e36b336ef65535a52e71dea926bd1e5b6db9207e8fe8a4c29e1a6c59dbefe8` / `fb94d993b4dbb0cbf2c315b870aac9674ca8d4413d5c93d6bc38627faddcfa2f` |
| module firmware `firmware_EXT.bin` 00.00.04.07 | `111e20d822f991eae42b08084f403bf6c75188dc5002869d19e404d20792a8a4` |

Not copied: APKs, libraries, firmware.
