# UVC capabilities (firmware 00.00.04.07, stock use)

| item | value | evidence |
|---|---|---|
| UVC version | 1.10 (`bcdUVC 0x0110`; kernel log `Found UVC 1.10 device Camera (3474:4321)`) | F, S |
| clock | dwClockFrequency 15 MHz | F |
| camera terminal | IT 1, ITT_CAMERA, **no controls** (bmControls 0, focal/ocular 0) | F |
| processing unit | PU 2, **no controls** (bmControls 0), no video standards | F |
| extension units | **none** | F; `uvc-extension-units.tsv` |
| output terminal | OT 3, USB streaming, source PU 2 | F |
| status endpoint | 0x83 interrupt, 64 B, 4 ms | F |
| streaming interface | if1; alt 0 zero bandwidth, alt 1 iso 0x81 1024 B/µframe | F, S |
| still image / trigger | none (bStillCaptureMethod 0, trigger 0) | F |
| formats | 1: uncompressed, GUID YUY2, 16 bpp | F |
| frames | 1: 256×194 @25 Hz (99 328 B); 2: 256×386 @25 Hz (197 632 B); discrete single interval each | F |
| colour matching | BT.709 / BT.709 / SMPTE 170M | F |

## What stock negotiates

`libusbuvccamera020.so` (`UVCPreview::setPreviewSize` → `uvc_get_stream_ctrl_format_size_fps`)
maps the SDK `mode` 1 → libuvc frame format 3 (`YUY2` GUID in the library's format table),
2 → 12 (`NV12`), other → 9, and requires an **exact** width/height match (frame loop
compares `wWidth`/`wHeight`; no match → `UVC_ERROR_INVALID_MODE` −51). `libAC020sdk`
sets `mode = 1` for `FrameOutputFormat` YUYV_IMAGE_OUTPUT(0)/YUYV_AND_TEMP_OUTPUT(3) and
`mode = 2` for the NV12 variants (`native_init_handle_engine`, both USB and
USB_DUAL_NATIVE_CAM branches).

| caller | request | negotiated |
|---|---|---|
| M170infisens `Tiny2cDualPreviewFragment` → `UvcNativeCamDualFusionPreviewManager.init(256, 386, 1.0f, 25, …)`; `FrameOutputFormat` default 0; `DriverType.USB_DUAL_NATIVE_CAM` | YUYV 256×386, min=max fps 25, bandwidth factor 1.0 | **frame 2 (256×386 @25 Hz)** — exact match |
| M170infDlp (`UvcNativeCamDualCalManager`, IR_SENSOR 256×386 @25, bandwidth 1.0) | same | frame 2 |
| M170infDlp `FirmwareUpgradeManager` (`DriverType.USB`) | control only (no stream) | – |
| FactoryMode `InfirayEcoTest` (`DriverType.USB`, 256×**384**, YUYV_AND_TEMP) | YUYV 256×384 | **no matching frame descriptor** in firmware 04.07 → libuvc returns −51 and `iruvc_camera_start_stream` fails (static result; FactoryMode residue, see `stale-claims.md`) |

Frame 1 (256×194 = image + 2 info lines, no temperature plane) is advertised but not
requested by any stock caller.

Standard UVC requests issued by stock: VS_PROBE/VS_COMMIT (`uvc_query_stream_ctrl`
SET_CUR/GET_CUR/GET_MIN/GET_MAX), VC_REQUEST_ERROR_CODE (`uvc_vc_get_error_code`,
wValue 0x0200, only on error paths), SET_INTERFACE alt 1/0, standard GET_DESCRIPTOR
(device/config/string/BOS). **No camera-terminal or processing-unit control** is used
(device advertises none; no caller of `uvc_get_*/uvc_set_*` control helpers in any stock
library).
