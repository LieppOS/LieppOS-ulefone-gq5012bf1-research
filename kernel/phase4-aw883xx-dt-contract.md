# Phase 3 — GQ5012BF1 device-tree contract for aw883xx_driver.ko

Sources (all read-only):

* `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb`
  (base DTB + DTBO overlay, already merged during the ConnFem phase)
* `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/devicetree.tar`
  (`/sys/firmware/devicetree/base` captured from the running stock system)
* `workspace/gq5012bf1/stock/vendor_boot-unpacked/dtb`

No DT/DTBO artifact was modified during this task.

## The node

`/soc/i2c@11e01000/speaker_amp@34`

Raw property bytes from the live `/proc/device-tree` capture:

```
compatible        6d6564696174656b2c737065616b65725f616d7000   "mediatek,speaker_amp"
reg               00000034                                     0x34
status            6f6b617900                                   "okay"
#sound-dai-cells  00000000                                     0
reset-gpio        00000089 000000c1 00000000                   <&pio 193 0>
irq-gpio          00000089 00000029 00000000                   <&pio 41  0>
re-min            000003e8                                     1000    (mOhm)
re-max            00009c40                                     40000   (mOhm)
phandle           000002ca
```

Parent bus:

```
i2c@11e01000 {
    compatible = "mediatek,mt6989-i2c";
    reg  = <0 0x11e01000 0 0x1000  0 0x11300600 0 0x80>;
    interrupts = <0 0x196 4 0>;
    scl-gpio-id = <0x89>;  sda-gpio-id = <0x8a>;
    status = "okay";
};
aliases { i2c6 = "/soc/i2c@11e01000"; };
```

Sound-card link:

```
sound { mediatek,speaker-codec { sound-dai = <0x2ca>; }; }   /* -> speaker_amp@34 */
__symbols__ { spk = "/soc/i2c@11e01000/speaker_amp@34"; }
snd-audio-dsp { swdsp-smartpa-process-enable = <0x05>; }
```

Live confirmation (`buses.txt` from the same snapshot):

```
===/sys/bus/i2c/devices/6-0034===
/sys/bus/i2c/drivers/speaker_amp
/sys/module/mtk_sp_spk_amp
speaker_amp
of:Nspeaker_ampT(null)Cmediatek,speaker_amp
```

## Instantiation path

The node's `compatible` is **`mediatek,speaker_amp`**, not an Awinic string.
It is matched by `mtk-sp-spk-amp.ko`:

```
alias: of:N*T*Cmediatek,speaker_amp
alias: i2c:speaker_amp
depends: snd-soc-audiodsp-common,audio_ipi,aw883xx_driver
```

`mtk_spk_i2c_probe()` calls the exported `aw883xx_i2c_probe(client, id)`.
`aw883xx_driver.ko` itself contains **no** `of_device_id` table and never calls
`i2c_register_driver`, so the Awinic `awinic,aw883xx_smartpa` compatible present
in the public upstream driver is absent from the stock binary.

## Properties the driver actually reads (and what this DT supplies)

| property | parser | present here | effect |
|---|---|---|---|
| `reset-gpio` | `aw883xx_parse_gpio_dt` | **yes** `<&pio 193 0>` | `reset gpio provided ok`; hardware reset performed in probe |
| `irq-gpio` | `aw883xx_parse_gpio_dt` | **yes** `<&pio 41 0>` | `irq gpio provided ok.`; threaded IRQ registered |
| `re-min` | `aw_dev_parse_re_range_dt` (`aw883xx_device.c`) | **yes** `1000` | `parse re-min:[1000]` — lower calibration-Re bound |
| `re-max` | `aw_dev_parse_re_range_dt` | **yes** `40000` | `parse re-max:[40000]` — upper calibration-Re bound |
| `sound-channel` | `aw883xx_parse_channel_dt` | no | `read sound-channel failed,use default 0` |
| `fade-enable` | `aw883xx_parse_fade_enable_dt` | no | `read fade-enable failed, close fade_in_out` |
| `sync-flag` | `aw883xx_parse_sync_flag_dt` | no | `read sync flag failed,default phase sync off` |
| `sync-load` | `aw883xx_parse_sync_load_dt` | no | `read sync load failed,default async loading fw` |
| `rename-flag` | `aw883xx_parse_rename_flag_dt` | no | `read rename flag failed,default rename off` |
| `dsp_monitor_delay` | `aw_monitor_parse_dt` | no | `read hw-monitor-delay failed, set deafult value:[1000]ms` |
| `aw-cali-check` | `aw_cali_parse_dt` | no | ` cali-check get failed ,default turn off` |
| `aw-cali-mode` | `aw_cali_parse_dt` | no | calibration interface mode falls back to the built-in default |
| `spin-mode` | `aw883xx_spin_init` | no | `spin-mode get failed, spin switch off` |
| `spin-data` | `aw883xx_spin_init` | no | not reached (spin off) |
| `aw-rx-topo-id` | `aw883xx_spin_init` | no | `read aw-rx-topo-id failed,use default` (0x1000FF01) |
| `aw-rx-port-id` | `aw883xx_spin_init` | no | `read aw-rx-port-id failed,use default` (0x1006) |

There is **no** regulator supply, **no** pinctrl state, **no** `interrupts`
property (the IRQ comes from `gpiod_to_irq(irq-gpio)`), and **no** second
Awinic amplifier node anywhere in the merged tree.

## Consequences for the reconstruction

* Single mono amplifier, channel 0.
* Both calibration-Re guard rails come from DT: 1000 … 40000 mOhm. Values
  outside this window are rejected with `out range re value: [%d]mohm` /
  `cali_re:%d out of range, no set`.
* Every optional feature (spin, phase sync, fade, renaming, synchronous
  firmware load, cali-check) is at its compiled-in default on this device.
* Firmware is loaded **asynchronously** (`sync-load` absent), i.e. probe returns
  before the ACF is parsed; the load is retried from a work item.
