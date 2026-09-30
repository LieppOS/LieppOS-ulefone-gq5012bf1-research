# U20 - full camera `availableStreamConfigurations`

**Current claim:** "blob lengths only in HAL dump".

**Previous confidence:** UNKNOWN.

**New evidence - the arrays were fully decoded from the existing capture**

The metadata was present all along in `camera-media.txt` as expanded `[format width height OUTPUT]` rows; the original pass only recorded the array lengths.

| Camera | Driver | Facing | Rows | RAW16 native | Max BLOB/YUV/IMPL | Formats present |
|---|---|---|---|---|---|---|
| 0 | `IMX989_MIPI_RAW` | BACK (main) | 215 | **4096 x 3072** | **8192 x 6144** (incl. **7680 x 4320**, 5760x2880, 5376x3024, 4608x3456) | 0x20 RAW16, 0x21 BLOB, 0x22 IMPLEMENTATION_DEFINED, 0x23 YUV_420_888, 0x36, 0x32315659 (YV12) |
| 1 | `S5KJN1_MIPI_RAW` | FRONT | 215 | **4080 x 3072** | 8192 x 6144 | same six |
| 2 | `S5KJN1MAIN2_MIPI_RAW` | BACK (ultrawide) | 211 | **4080 x 3072** | 8192 x 6144 | same six |
| 3 | `OV64B_MIPI_RAW` | BACK (night vision) | 211 | **4624 x 3472** | **9216 x 6912** | same six |

Each camera additionally publishes 42-43 `android.heic.availableHeicStreamConfigurations` sizes, mirroring the BLOB list.

Companion metadata:

| Camera | physicalSize (mm) | pixelArraySize | Aperture | Focal | OIS | Video stabilization | Max digital zoom |
|---|---|---|---|---|---|---|---|
| 0 | 13.107 x 9.830 | 4096 x 3072 | f/1.9 | 23 mm | `[0]` | `[0,1,2]` | 4.0 |
| 1 | 4.640 x 3.490 | 8160 x 6144 | f/2.45 | 25 mm | `[0]` | `[0,1,2]` | - |
| 2 | 13.107 x 9.830 (copied) | 8160 x 6144 | f/2.2 | 16 mm | `[0]` | `[0]` | - |
| 3 | 6.500 x 4.890 | 4624 x 3472 | f/1.79 | 26 mm | `[0]` | `[0]` | - |

**Contradicting evidence**
Camera 2's `physicalSize` is byte-identical to camera 0's despite a different pixel array - a vendor metadata copy error. `physicalSize` must therefore not be used to infer sensor format on this device; the RAW16 dimensions are the reliable discriminator (and they are what settles U3).

**Internet sources:** VI5, VI7 (focal lengths, apertures and the 117.3-degree autofocus ultrawide claim, which matches camera 2's 16 mm entry).

**Local evidence:** VL12; `../evidence/live-runtime-extracts.md`.

**Read-only live evidence:** the frozen camera HAL dump.

**Final conclusion**
All four cameras publish a complete, ordinary Camera2 configuration set of roughly 210-215 stream entries across six formats, topping out at **50 MP (8192x6144) for the main and both 50 MP modules and 64 MP (9216x6912) for the OV64B night-vision camera**, with **8K (7680x4320) still capture available on the main camera** and 4x maximum digital zoom. **Optical stabilization is reported unavailable on every camera**, while electronic video stabilization is offered on the main and front cameras only.

Note that these arrays describe **still/stream sizes**, not video recording profiles - the "4K30 vs 4K60" question lives in `media_profiles`/the camera application, and the capture's application layer was a GSI, so no stock video-mode conclusion can be drawn from it.

**Final confidence:** **PROVEN** - this is a direct readout of the vendor HAL's static metadata.

**Remaining uncertainty:** `availableMinFrameDurations` and `availableStallDurations` were not decoded in this pass; those determine the achievable frame rate per size and would need the same dump re-parsed. Stock video menus need a stock-system capture.

**Impact on final inventory:** YES - U20 is closed; the camera row and capability matrix gain concrete ceilings instead of "blob lengths only".

**Answers:** (1) full arrays, now tabulated; (2) frame-duration arrays for fps ceilings; (3) yes - it was already in the capture; (4) yes for the rest; (5) no; (6) no; (7) see tables; (8) PROVEN; (9) yes; (10) yes; (11) yes.

## Second-pass update (2026-09-08)

The same HAL dump was re-parsed by camera block (VL27, L22): runtime names are IMX989 (cam 0), S5KJN1
front (cam 1), S5KJN1MAIN2 rear (cam 2), OV64B rear/night (cam 3), and every block reports
`android.lens.info.availableOpticalStabilization = [0]` (OFF only). Static metadata defects matter for ROM
work: cam 2 combines a JN1 instance name with 8160x6144 and the main camera's 13.107 x 9.830 mm physical
size; cam 1 combines JN1-sized 4.640 x 3.490 mm geometry with 8160x6144; aperture/focal-length tags are absent.
Therefore the stream tables are PROVEN as **HAL-advertised modes**, while physical-size/pitch fields for
secondary modules must not be promoted to silicon facts.
