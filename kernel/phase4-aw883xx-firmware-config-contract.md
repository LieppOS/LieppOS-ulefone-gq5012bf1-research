# Phase 6 — firmware / config / blob contract

## What the kernel module loads

`aw883xx_driver.ko` calls `request_firmware()` for exactly **two** names:

| name | source in stock image | requester | when |
|---|---|---|---|
| `aw883xx_acf.bin` | `/vendor/firmware/aw883xx_acf.bin` | `aw883xx_request_firmware_file()` (`AW883XX_ACF_FILE`) | asynchronously after probe; retried up to 5 times, `msleep()` between attempts |
| `aw883xx_monitor.bin` | **not shipped** | `aw_monitor_real_time_update_monitor()` (`AW883XX_MONITOR_NAME`) | only when userspace writes `1` to the `monitor_update` sysfs attribute |

There is no third firmware name, no `nvmem`, no `filp_open`, and no
`kernel_read`/`kernel_write` in the stock module (see the ABI table — those
symbols are simply not imported).

Because `aw883xx_monitor.bin` is absent from the stock image, `monitor_update`
always fails with `failed to read aw883xx_monitor.bin`; the monitor table used at
runtime is the one embedded in the ACF (`ACF_SEC_TYPE_MONITOR` section).

## The ACF blob

```
path    /vendor/firmware/aw883xx_acf.bin
size    36141
sha256  cc246bae1ca600908d88fd77309054e1e73bf92f73bbecf758dca581b34071a0
magic   a_id = 0x0a15f908  ("ACF_FILE_ID")
```

Header (`struct aw_cfg_hdr`, little-endian):

| field | value |
|---|---|
| `a_project` | `M190` |
| `a_custom` | `DZ` |
| `a_version` | `0.0.0.2` |
| `a_author_id` | 320 |
| `a_ddt_size` | 192 (= 3 × 64, total table size, **not** the entry size) |
| `a_ddt_num` | 3 |
| `a_hdr_offset` | 0x50 |
| `a_hdr_version` | **0x00000001** = `AW_CFG_HDR_VER_0_0_0_1` |

Because the header version is `0_0_0_1`, the DDE entries are the 64-byte
`struct aw_cfg_dde` (not the 96-byte `aw_cfg_dde_v_1_0_0_0`) and the runtime
path is `aw_dev_load_cfg_by_hdr()` → `aw_dev_parse_dev_type()` /
`aw_dev_parse_dev_default_type()`. The v1.7.1-only
`aw_dev_parse_scene_v_1_0_0_0()` code path is **not exercised on this device**.

Directory (all three DDEs are `AW_DEV_DEFAULT_TYPE_ID`, `dev_index = 0`,
`dev_bus = dev_addr = 0xffff`, i.e. "match by channel", so channel 0 selects
all of them):

| # | dev_name | profile | sec type | size | file offset | data_crc |
|---|---|---|---|---|---|---|
| 0 | `aw88394` | 0 (`MUSIC`) | `ACF_SEC_TYPE_MONITOR` (10) | 192 | 0x00110 | 0x000000dc |
| 1 | `aw88394` | 0 (`AW_PROFILE_MUSIC`) | `ACF_SEC_TYPE_MUTLBIN` (7) | 17594 | 0x001d0 | 0x00000029 |
| 2 | `aw88394` | 10 (`AW_PROFILE_RECEIVER`) | `ACF_SEC_TYPE_MUTLBIN` (7) | 18083 | 0x0468a | 0x00000022 |

So the device exposes exactly **two ALSA profiles**: `Music` and `Receiver`.

### Multi-bin decomposition (both profiles)

Each MULTLBIN is a 60-byte-header container (`header_ver = 0x01000000`,
`bin_data_type = 0x2000` = `DATA_TYPE_MULTI_BINS`, `chip_type = "AW88394"`) with
four sub-bins:

profile `Music` (`ui_ver = 0x000f0000`, `check_sum = 0x001458e0`):

| # | type | len | reg_byte_len | data_byte_len | dev_addr | download addr |
|---|---|---|---|---|---|---|
| 0 | `DATA_TYPE_REGISTER` (0x00) | 188 | 2 | 2 | 0x34 | — (46 register words) |
| 1 | `DATA_TYPE_DSP_REG` (0x10) | 1436 | 2 | 4 | 0x34 | 0x9c80 (356 DSP words) |
| 2 | `DATA_TYPE_SOC_APP` (0x21, DSP firmware) | 3968 | 0 | 0 | 0x34 | 0x8c00, app_ver 0xffff0001 |
| 3 | type `0x12` | 11666 | 0 | 0 | 0x34 | — |

profile `Receiver` (`ui_ver = 0x00110000`, `check_sum = 0x001521a8`):

| # | type | len | download addr |
|---|---|---|---|
| 0 | `DATA_TYPE_REGISTER` | 188 | — (46 register words) |
| 1 | `DATA_TYPE_DSP_REG` | 1440 | 0x9c80 (357 DSP words) |
| 2 | `DATA_TYPE_SOC_APP` | 4320 | 0x8c00, app_ver 0xfffe0001 |
| 3 | type `0x12` | 11799 | — |

Sub-bin type `0x12` is **not** in the driver's `data_type_enum` and is not
handled by `aw_parse_bin_header_1_0_0()`; both the stock module and the
reconstruction silently skip it (it is never registered in
`aw_bin->header_info[]`, so `aw_dev_prof_parse_multi_bin()` never maps it into
`sec_desc[]`). This is stock behaviour, reproduced exactly — the section is
consumed by userspace, not by the kernel (see below).

### What ends up in each profile

`aw_dev_prof_parse_multi_bin()` maps the recognised sub-bins onto
`prof_desc->sec_desc[]`:

* `DATA_TYPE_REGISTER` → `AW_DATA_TYPE_REG` (written register-by-register at
  `aw883xx_device_start`)
* `DATA_TYPE_DSP_REG` → `AW_DATA_TYPE_DSP_CFG` (byte-swapped by
  `aw883xx_dev_dsp_data_order()` then block-written to DSP RAM at `0x9c80`)
* `DATA_TYPE_SOC_APP` → `AW_DATA_TYPE_DSP_FW` (byte-swapped, written to
  `0x8c00`, `prof_desc->fw_ver` = `app_version`)

Selection rules, in order:

1. **Device match** — v0.0.0.1 header: `aw_dev_parse_dev_type()` first tries
   `dev_bus == i2c adapter nr && dev_addr == i2c addr`; with no match it logs
   `get dev type num is 0, parse default dev` and falls back to
   `aw_dev_parse_dev_default_type()`, which matches `dev_index == aw_dev->channel`
   (0 here). Both this device's MULTLBINs have `dev_index = 0`, so both are taken.
2. **Validity filter** — `aw_dev_cfg_get_vaild_prof()` keeps only profiles whose
   `prof_st == AW_PROFILE_OK` **and** whose REG, DSP_CFG and DSP_FW sections are
   all non-empty, then compacts them into `prof_info->prof_desc[]`
   (`get vaild profile:%d`).
3. **Naming** — `aw_dev_create_prof_name_list()` builds the kcontrol enum from
   the static `profile_name[]` table indexed by `prof_desc->id`
   (`prof name is %s`).

## Other Awinic blobs in the stock image (userspace, not kernel)

| path | size | sha256 | consumer |
|---|---|---|---|
| `/vendor/etc/smartpa_param/AW_DSP.bin` | 14596 | `f7e4a085ed6a89913267551c15492cc4a4e0404d77b280813ee33f9ba6cc1d83` | `libawinicsmartpaparse.so` (`aw_skt_arsi_load_param`, falls back to `AW_DSP_DEFAULT.bin`). Same `0x0a15f908` container magic, project `SKTune`, custom `awinic`. |
| `/vendor/firmware/awinic_params.bin` | 13640 | `9801c0d2a91b77c7e6c51b51590c4b79d32a27838d59807cf3cd3a9de7650b8e` | `awinic.audio.effect.so` (SKTune effect), never opened by the kernel |
| `/vendor/firmware/awinic_sinwave_params.bin` | 13640 | `8dcfb1782dbc946bde6a8a731ce4f5b1e88216a94131c46f58dbf592fcd82954` | same |
| `/vendor/lib64/libawinicsmartpaparse.so` | 13904 | `1f1597cc3f08f861e8e4c5334df8e386cf966dbe91077b0427423366a6929aac` | HAL scene switching (`aw_mtk_set_scene`) |
| `/vendor/lib64/hw/awinic.audio.effect.so` | 289536 | `27e5db93e35c40ffa803617b392ef487a6e80f78c4cb540575496eae1ec857b3` | SKTune effect; owns `Algo cali re = set cali re + ra` and the `set cail re out of range(%d, %d)!` guard |

A whole-image content scan shows that the strings `aw883xx_acf`, `aw_smartpa`
and `re25_calib` occur in **exactly one file**: `aw883xx_driver.ko` itself.
Nothing in `/vendor/bin` or `/vendor/lib*` opens `/dev/aw_smartpa` or the
`/sys/class/smartpa` attributes on this build.

## Classification of every configuration source

| # | question | answer |
|---|---|---|
| 1 | compiled into the `.ko`? | Only the per-PID register/descriptor tables (`aw883xx_pid_2049/2066/2183_init.c`) and the `profile_name[]` string table. No tuning data. |
| 2 | loaded from the filesystem? | **Yes** — `/vendor/firmware/aw883xx_acf.bin` via `request_firmware`. Optionally `aw883xx_monitor.bin` (absent). |
| 3 | delivered through userspace/HAL? | Yes — SKTune parameters (`AW_DSP.bin`, `awinic_params.bin`) go through the audio HAL/effect, never through this driver. |
| 4 | stored in NVRAM/persist/vendor data? | Calibration only: MTK NVRAM item `/mnt/vendor/nvdata/APCFG/APRDCL/smartpa_calib` (`iAP_CFG_CUSTOM_FILE_SMARTPA_CALIB_LID`), written by `vendor/bin/smartpa_nvtest` + `libcustom_nvram.so`. The kernel module never touches it. |
| 5 | obtained from DSP/AFE? | No. `AW_MTK_PLATFORM_SPIN`/`AW_QCOM_PLATFORM_SPIN` are compiled out, so the AFE/APR transport is the local no-op stub. The on-chip Awinic DSP is programmed over I2C only. |

## Stock blobs still required by the reconstruction

`aw883xx_acf.bin` (unmodified, sha256 above) must remain in
`/vendor/firmware/`. It is **device calibration/tuning data**, not executable
kernel code, and the reconstruction consumes it byte-for-byte as the stock
driver does. It was not modified, re-generated or re-signed at any point.
