# Phase 2 — GQ5012BF1 AW883xx hardware contract

Oracle: `vendor_dlkm/lib/modules/aw883xx_driver.ko`
SHA256 `3bc4722c6550abb9cfd75d06602c2a1bff8d0b6af58708324479ef6a0d22c9b4`

Everything below is derived from the stock ELF, the stock ACF blob and the
read-only device-tree snapshot. Nothing was inferred from the filename.

## Exact chip

| item | value | evidence |
|---|---|---|
| fitted part | **AW88394** | `vendor/firmware/aw883xx_acf.bin` DDE `dev_name` field = `aw88394`, and every multi-bin sub-header carries `chip_type[8] = "AW88394"` |
| chip ID register | `0x00` (`AW883XX_CHIP_ID_REG`) | `aw883xx_match_chipid` reads reg 0 and logs `read chip id: 0x%x` |
| chip IDs accepted by the driver | `0x2049`, `0x2066`, `0x2183` | `aw883xx_init_check_chipid` switch; unmatched IDs log `unsupported chip_id 0x%04x` |
| chip ID used at runtime | `0x2049` | the ACF profile bins are `AW88394`, and only the `AW883XX_PID_2049` init path programs `AW_PID_2049_*` registers; the module still carries the 2066/2183 tables |
| register width | 8-bit address / 16-bit big-endian data | `aw883xx_i2c_read/_write` build 1-byte addr + 2-byte data through `i2c_transfer` |
| DSP access | indirect, via `DSPMADD`/`DSPMDAT` register pair | `aw_pa->dsp_mem_desc.dsp_madd_reg / dsp_mdat_reg`; 16- and 32-bit forms (`AW_DSP_16_DATA`, `AW_DSP_32_DATA`) |

`aw88395`, `aw88399`, `aw882xx`, `aw87xxx` do **not** appear anywhere in the
stock binary. The only Awinic families referenced are the three PID tables.

## Bus / addressing

| item | value | evidence |
|---|---|---|
| bus | I2C-6 (`/soc/i2c@11e01000`, alias `i2c6`) | merged DTB + live `/sys/bus/i2c/devices/6-0034` |
| address | `0x34` | DT `reg = <0x34>`; ACF DDE `dev_addr` and every multi-bin `device_addr` field = `0x34` |
| adapter matching | `i2c->adapter->nr` vs ACF `dev_bus`, `i2c->addr` vs ACF `dev_addr` | ACF v1.0.0.0 scene parser (this ACF is v0.0.0.1 so the `DEV_DEFAULT` path is used instead) |
| transfer retries | 5 attempts, 5 ms apart | `AW_I2C_RETRIES` / `AW_I2C_RETRY_DELAY` |

## Instantiation — the module is NOT a bus driver

`aw883xx_driver.ko` registers **no** `i2c_driver` and has no `module_init`.
It exports two symbols:

```
aw883xx_i2c_probe    CRC 0x713728fc   int  (struct i2c_client *, const struct i2c_device_id *)
aw883xx_i2c_remove   CRC 0xb3e48038   int  (struct i2c_client *)
```

The device is bound by MediaTek's `mtk-sp-spk-amp.ko`
(`compatible = "mediatek,speaker_amp"`, i2c alias `i2c:speaker_amp`), whose
`mtk_spk_i2c_probe()` calls `aw883xx_i2c_probe(client, id)` directly and, on
success, sets `mtk_spk_type = 5` (`MTK_SPK_AWINIC_AW883XX`).
`mtk_spk_i2c_remove()` calls `aw883xx_i2c_remove(client)` and discards its
return value — which is why the stock export kept the pre-6.1 `int` prototype.

`modules.dep` records the same relationship:
`mtk-sp-spk-amp.ko: ... aw883xx_driver.ko ...`, and `aw883xx_driver.ko:` has no
dependencies of its own.

## Channel / topology

| item | value | evidence |
|---|---|---|
| amplifier count | **1** | exactly one `speaker_amp@34` node; no second Awinic node in the merged DTB; `g_aw883xx_dev_cnt` reaches 1 |
| channel index | 0 (default) | the DT node has **no** `sound-channel` property, so `aw883xx_parse_channel_dt` takes the `read sound-channel failed,use default 0` path |
| ACF device selection | `AW_DEV_DEFAULT_TYPE_ID` (2) with `dev_index = 0` | all three ACF DDEs are `type = 2`, `dev_index = 0`, `dev_bus/dev_addr = 0xffff` |
| roles | speaker (profile `Music`) and receiver (profile `Receiver`) | the ACF ships exactly two MULTLBIN profiles: `dev_profile = 0` (`AW_PROFILE_MUSIC`) and `dev_profile = 10` (`AW_PROFILE_RECEIVER`) |
| spin / multi-channel rotation | **disabled** | no `spin-mode` property in DT ⇒ `spin-mode get failed, spin switch off`; both `AW_MTK_PLATFORM_SPIN` and `AW_QCOM_PLATFORM_SPIN` are compiled out (the module imports no MTK/AFE IPI symbols), so `aw_send_afe_cal_apr()`/`afe_get_topology()` are the local no-op stubs |
| DAI | one DAI, name built at probe from the codec name; `#sound-dai-cells = <0>` | `aw883xx_dai_drv_append_suffix`, `dai name [%s]`, `pstream_name [%s]`, `cstream_name [%s]` |
| DAPM | `aw883xx_dapm_widgets` (1280 B) + `aw883xx_audio_map` (192 B), names suffixed per i2c/channel | `aw_widgets.name append i2c suffix failed!`, `aw_route.sink append channel suffix failed!` |
| rates / formats | 8 k–48 k + 96 k, S16_LE/S24_LE/S32_LE | `AW883XX_RATES` / `AW883XX_FORMATS` |

## Reset / IRQ / power

| item | value | evidence |
|---|---|---|
| reset GPIO | `<&pio 193 0>` (`reset-gpio` in DT) | live `/sys/firmware/devicetree/base/soc/i2c@11e01000/speaker_amp@34/reset-gpio = 00000089 000000c1 00000000` |
| reset sequence | request as output-low, then 1→0→1 with `usleep_range` around each edge | `aw883xx_gpio_request` → `devm_gpio_request_one`, `aw883xx_hw_reset` → `gpiod_set_raw_value_cansleep`; absent GPIO logs `no reset gpio provided, will not hw reset` |
| IRQ GPIO | `<&pio 41 0>` (`irq-gpio` in DT) | live DT `irq-gpio = 00000089 00000029 00000000` |
| IRQ registration | `gpiod_to_irq()` + `devm_request_threaded_irq` (threaded, one-shot) | `aw883xx_interrupt_init`; the module logs `irq gpio provided ok.` / `no irq gpio provided.` and `skipping IRQ registration` when `AW883XX_FLAG_SKIP_INTERRUPTS` is set |
| IRQ handler | `aw883xx_irq` — reads the SYSINT register, latches it into `int_desc.sysint_st`, then re-masks | `read interrupt reg fail, ret=%d`, `check sysint fail, reg=0x%04x` |
| regulators | none | the module imports no regulator API; the DT node declares no supplies |
| pinctrl | none | the DT node declares no `pinctrl-*` |
| power sequencing | `pwd` (SYSCTRL power-down) → `amppd` (amp power-down) → `hmute` → `dsp_enable`; start = reverse order with PLL/SYSST/DSP checks | `aw883xx_device_start` / `aw883xx_device_stop` |
| battery/thermal input | `power_supply_get_by_name()` + `power_supply_get_property()` | `no struct power supply name : %s`; used by the software monitor when configured |

## Monitor / protection

* Three protection domains are compiled in:
  * **hardware monitor** (`hardware monitor is enable`) — chip-internal.
  * **software monitor** (`sortware monitor is enable`) — `delayed_work`
    sampling temperature + voltage and stepping `ipeak`/`gain`/`vmax` through
    the `aw_table` set parsed from the ACF `ACF_SEC_TYPE_MONITOR` section.
  * **DSP monitor** (`dsp monitor is enable`) — `dsp_monitor_work`, default
    delay `AW_DSP_MONITOR_DELAY = 1000 ms`; the DT may override it with
    `hw-monitor-delay` (`parse hw-monitor-delay:[%d]`), not present here.
* CRC integrity of the downloaded DSP firmware and config is enforced:
  `aw_pid_2049_dsp_crc32_check`, `aw883xx_crc_realtime_check`,
  `crc_check failed,check val %x != %x`, `check crc32 fail`.
* PLL / SYSST / DSP-status checks gate `aw883xx_device_start`:
  `pll check failed cannot start`, `check pll lock fail,reg_val:0x%04x`,
  `check dsp st fail,reg_val:0x%04x`, `IV data abnormal, please check`.
* `AW_DEV_SYSST_CHECK_MAX = 10` retries at 2 ms.

### v1.7.1-specific protection change

The stock (v1.7.1) `aw_dev_sysst_check()` differs from the public v1.6.0 code:

* `struct aw_sysst_desc` no longer has `st_sws_check`; `st_check` now carries the
  `*_BIT_SYSST_SWS_CHECK` value directly.
* `struct aw_noise_gate_en` became a 2-entry gate table
  `{reg, noise_gate_mask, st_and_mask}[2]`. For every entry whose `reg` is not
  `AW_REG_NONE`, the register is read and, if `(val & ~mask) != 0`, the entry's
  `st_and_mask` is ANDed into the expected SYSST value.
* AW88395/PID 2066 populates one entry
  `{PWMCTRL3 0x16, NOISE_GATE_EN_MASK, ~SWS_SWITCHING (0xfffffeff)}`
  — behaviourally identical to the old `st_check`/`st_sws_check` pair.
* AW88399/PID 2183 adds a second entry
  `{BSTCTRL10 0x69, ~bit2 (0xfffffffb), ~BSTS_FINISHED (0xfffffdff)}`,
  i.e. when bit 2 of register 0x69 is set the boost-finished bit is no longer
  required for SYSST to be considered good. Bit 2 of 0x69 has no published name;
  it is carried by address (`AW_PID_2183_REG_0X69_BIT2_MASK`).
* PID 2049 (the part actually fitted) leaves both gate entries at
  `AW_REG_NONE`, so this path is inert on GQ5012BF1.

## Userspace-visible interfaces

| kind | name | notes |
|---|---|---|
| sysfs (i2c device) | `reg rw drv_ver dsp_rw awrw fade_step dbg_prof spk_temp phase_sync fade_en dsp_re i2c_log_en dsp` | on `/sys/bus/i2c/devices/6-0034/` |
| sysfs (monitor) | `monitor monitor_update` | same kobject |
| sysfs (calibration) | `cali_time cali_re cali_f0 cali_f0_q re_range` | same kobject |
| class | `/sys/class/smartpa/` with `cali_time re25_calib f0_calib f0_q_calib re_range` | `class_register`, created once for all devices |
| miscdevice | `/dev/aw_smartpa` | `misc_register`, `aw_cali_misc_fops` (open/read/write/unlocked_ioctl/compat_ioctl/release) |
| ALSA kcontrols | profile enum, PA switch, volume, monitor switch, (spin when enabled) | `snd_soc_add_component_controls` with dynamically built names |

No procfs and no debugfs interface exists in the stock module.
