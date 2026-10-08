# Source-to-userspace contract — MTK-VCODEC-KERNEL

What Android can reach in these drivers, and what remains unproven.

## 1. Kernel-exposed interfaces (source-exact)

### V4L2 memory-to-memory devices

* `mtk-vcodec-dec-v1` registers one video device (`MTK_VCODEC_DEC_NAME = "mtk-vcodec-dec"`),
  `mtk-vcodec-enc-v1` one (`MTK_VCODEC_ENC_NAME = "mtk-vcodec-enc"`), both
  `VFL_TYPE_VIDEO` with dynamic minor, `v4l2_m2m` + `videobuf2` multiplanar queues
  (`V4L2_MEMORY_MMAP` and `V4L2_MEMORY_DMABUF`).
* Standard ioctl surface: `VIDIOC_QUERYCAP`, `ENUM_FMT`, `G/S/TRY_FMT`, `REQBUFS`,
  `QUERYBUF`, `QBUF`/`DQBUF`, `EXPBUF`, `STREAMON`/`STREAMOFF`, `G/S_SELECTION`,
  `SUBSCRIBE_EVENT`/`DQEVENT`, `DECODER_CMD`/`ENCODER_CMD`, plus `poll`/`mmap` through the
  vb2 helpers. Decoder capability (`ENUM_FRAMESIZES`/`ENUM_FRAMEINTERVALS`) is answered from
  values queried from VCP (`vdec_if_get_param(..., GET_PARAM_CAPABILITY_*)`), i.e. the
  advertised set depends on the firmware actually answering.
* Compressed formats present in the decoder source: `H264`, `H264_SLICE`, `H265`, `HEIF`,
  `VP8`, `VP9`, `AV1`, `MPEG1`, `MPEG2`, `MPEG4`, `H263`, `WMV1/2/3/A`, `WVC1`, `RV30`,
  `RV40`. Encoder source: `H264`, `H265`, `HEIF`, `MPEG4`, `H263`. Raw formats include
  `NV12`/`NV21`(`M`), `YUV420`/`YVU420`(`M`), `P010M`/`P010S`, `MT10`/`MT10S`, assorted
  RGB/ARGB/1010102 variants and the AFBC-compressed variants.
  **Presence in a source table is not proof that the shipped firmware accepts the format.**

### VCU character device

`mtk-vcu` creates the `vcu` char device (`VCU_DEVNAME "vcu"`, `alloc_chrdev_region` +
`device_create`) with `open`/`release`/`mmap`/`unlocked_ioctl`/`compat_ioctl`. Its ioctl
numbers (`'v'` family) are:

| cmd | code | payload |
|---|---|---|
| `VCU_SET_OBJECT` | `_IOW('v', 0, …)` | `struct share_obj` |
| `VCU_MVA_ALLOCATION` | `_IOWR('v', 1, …)` | `struct mem_obj` |
| `VCU_MVA_FREE` | `_IOWR('v', 2, …)` | `struct mem_obj` |
| `VCU_CACHE_FLUSH_ALL` | `_IOWR('v', 3, …)` | `struct mem_obj` |
| `VCU_CACHE_FLUSH_BUFF` | `_IOWR('v', 4, …)` | `struct mem_obj` |
| `VCU_CACHE_INVALIDATE_BUFF` | `_IOWR('v', 5, …)` | `struct mem_obj` |
| `VCU_PA_ALLOCATION` | `_IOWR('v', 6, …)` | `struct mem_obj` |
| `VCU_PA_FREE` | `_IOWR('v', 7, …)` | `struct mem_obj` |
| `VCU_GCE_SET_CMD_FLUSH` | `_IOW('v', 8, …)` | `struct gce_cmdq_obj` |
| `VCU_GCE_WAIT_CALLBACK` | `_IOW('v', 9, …)` | `struct gce_obj` |
| `VCU_GET_OBJECT` | `_IOWR('v', 10, …)` | `struct share_obj` |

A 32-bit compat path translates the same structures. **But** no node in the stock merged DTB
matches any `mtk-vcu` OF alias, so whether this device is instantiated on GQ5012BF1 is
**UNKNOWN**; its exported symbols (`vcu_*`, `vcodec_trace*`) are nonetheless consumed by the
codec modules.

### Module parameters (writable at runtime by privileged userspace)

`mtk-vcodec-common`: `fence_debug`. Decoder: `mtk_v4l2_dbg_level`, `mtk_vdec_lpw_level`,
`mtk_vcodec_dbg`, `mtk_vcodec_perf`, `mtk_vdec_trace_enable`, `mtk_vcodec_vcp`,
`mtk_vdec_lpw_limit`, `mtk_vdec_lpw_timeout`, `mtk_vdec_slc_enable`, plus the string
callbacks `mtk_vdec_vcp_log` and `mtk_vdec_property`. Encoder: the corresponding
`mtk_venc_*`, `venc_max_mon_frm` and `venc_smi_monitor_mode`.

## 2. Android media stack above these drivers (static evidence only)

* Declared service: `vendor.mediatek.hardware.mtkcodecservice` (owner:
  `GENERIC-PLATFORM-INFRASTRUCTURE`; 1 VINTF declaration, 0 in a manifest).
* Configuration shipped in `vendor/etc`: `media_codecs.xml`, `media_codecs_c2.xml`,
  `media_codecs_performance.xml`, `mtk_platform_codecs_config.xml`.
* Hardware-named Codec2 components declared by those XMLs: `c2.mtk.avc.decoder`,
  `c2.mtk.hevc.decoder`, `c2.mtk.vp9.decoder`, `c2.mtk.avc.encoder`, `c2.mtk.hevc.encoder`.
  Everything else declared is a software (`c2.android.*`) component, including AV1, VP8 and
  all audio.
* The vendor Codec2 implementation libraries that bind these component names to the V4L2
  devices are **proprietary** and were not reconstructed. The precise call chain
  MediaCodec → Codec2 HAL → vendor library → `/dev/video*` is therefore a **candidate**
  mapping, not a traced one.
* Protected/secure decode: the drivers carry an SVP/WFD region concept
  (`support_svp_region`, `support_wfd_region` exported from `mtk-vcodec-common`, secure
  DMA-heap handling). The secure-world half is out of scope and unverified.

Advertised XML capability is a declaration. It is **not** evidence that the hardware decodes
or encodes any of it.

## 3. Runtime testing still required (none performed; separate authorisation needed)

1. Module load of all five in stock order and successful `probe()` of
   `mediatek,mt6878-vcodec-dec`, `-enc` and both clock syscons.
2. Creation of the two V4L2 nodes and a successful `VIDIOC_QUERYCAP` / format enumeration.
3. VCP readiness, feature registration and a completed IPI round trip on both channels.
4. A real hardware decode and a real hardware encode (H.264 and H.265 at minimum), proven to
   use the hardware path rather than a software Codec2 fallback.
5. Interrupt servicing, fence/completion signalling and buffer ownership under load.
6. Timeout, abort, stream-off and VCP-restart recovery behaviour.
7. Clock/power-domain, MMQoS bandwidth, SLBC/SLC and DVFS behaviour, plus thermal limits.
8. Whether `mtk-vcu` ever probes on this board, and if not, confirmation that nothing depends
   on its platform side.
9. Protected/secure decode path behaviour.
