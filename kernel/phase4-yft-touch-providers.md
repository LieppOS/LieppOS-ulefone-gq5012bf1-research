# Phase 4 — YFT touchscreen support providers

These modules provide Ulefone/YFT touchscreen integration APIs required by the
GQ5012BF1 FocalTech FT3680 driver.

## Authoritative status

| Provider | Status | Report |
|---|---|---|
| `yft_tpd_gesture` | **Reconstructed — byte-exact code/data; 2 of 3 export CRCs reproduced from source** | [`kernel/phase4-yft-tpd-gesture-reconstruction.md`](phase4-yft-tpd-gesture-reconstruction.md) |
| `yft_devinfo` | **Reconstructed — complete provider builds against exact GKI; 17 of 27 export CRCs + all 40 import CRCs from source** | [`kernel/phase4-yft-devinfo-reconstruction.md`](phase4-yft-devinfo-reconstruction.md) |
| `mtk_disp_notify` | direct source match | `kernel/phase4-mtk-disp-notify.md` |

### `yft_tpd_gesture` result (authoritative)

Classification: **`BYTE_EXACT_CODE_RECONSTRUCTION`**, with a single
`BLOCKED_WITH_EXACT_MISSING_EVIDENCE` item scoped to the `tpgesture_value`
export CRC.

* No source exists publicly or locally; the reconstruction was driven purely by
  RED of the stock oracle.
* Built with `BUILD_RC=0` against `//common:kernel_aarch64` as
  `//lieppos/yft-tpd-gesture-recon:yft_tpd_gesture_gki`.
* Byte-identical to stock: `.text` (2076), `.init.text` (116), `.exit.text`
  (112), `.rodata` (672), `.rodata.str1.1` (911), `.data` (416),
  `.data..read_mostly` (10), `.bss` layout (13), `.altinstructions` (288),
  `__jump_table` (64), `.init.eh_frame` (576), `__versions` (1664).
* Identical function set / sizes / KCFI type IDs (12 functions), identical
  imports (26), identical relocation content (283).
* Export CRCs generated from source, never patched:
  `tpgesture_hander 0x8386526d` ✔, `tpgesture_status 0x30ac810a` ✔,
  `tpgesture_value 0xec3d4c19` vs stock `0x02f3ea4c` ✗.
* Remaining non-ABI deltas: `vermagic`/build-id/`__UNIQUE_ID` counters (build
  provenance) and one `.rela` section-header ordering nit.

Supporting artifacts live in `workspace/phase4-yft-providers/`
(`yft-tpd-gesture-stock-inventory.md`, `yft-tpd-gesture-RED.md`,
`yft-tpd-gesture-source-candidates.md`,
`yft-tpd-gesture-export-crc-analysis.md`,
`yft-tpd-gesture-verification.txt`, plus the TSV/strings/disassembly dumps).

## yft_tpd_gesture

Stock location:

    vendor_boot platform ramdisk / lib/modules/yft_tpd_gesture.ko

Role:

    gesture-wakeup integration

Exports required by FocalTech:

    tpgesture_status
    tpgesture_value
    tpgesture_hander

The module is explicitly loaded by both the normal and recovery vendor_boot
module lists.

Initial reconstruction priority:

    HIGH

Expected difficulty:

    LOW_TO_MODERATE

Outcome: **done** — see
`kernel/phase4-yft-tpd-gesture-reconstruction.md`. Recovered API:

```c
void tpgesture_hander(void);      /* EXPORT_SYMBOL     */
char tpgesture_status;            /* EXPORT_SYMBOL_GPL */
char tpgesture_value[10] __read_mostly;  /* EXPORT_SYMBOL_GPL */
int  gesture_create_attr(struct device_driver *dev);
int  gesture_delete_attr(struct device_driver *dev);
```

Userspace ABI: misc device `/dev/touch`, ioctls `_IOW('A',3,int)` (gesture
enable) and `_IOR('A',4,char *)` (blocking gesture-value read, 10-byte payload);
platform driver `mtk_yft_tpd` with sysfs attributes `tpgesture` (0444) and
`tpgesture_status` (0644); OF compatible `mediatek,yft_tpd`.

## yft_devinfo

Stock primary location:

    vendor_dlkm/lib/modules/yft_devinfo.ko
    (byte-identical copy in the vendor_boot platform ramdisk)

Outcome: **done** — see
[`kernel/phase4-yft-devinfo-reconstruction.md`](phase4-yft-devinfo-reconstruction.md).

Classification: **`STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION`** with a single
`BLOCKED_WITH_EXACT_MISSING_EVIDENCE` item scoped to one 73-character vendor
enum type text.

* No source exists publicly or locally; driven purely by RED of the stock
  oracle. One partial donor was used and confirmed byte-exactly: MediaTek's
  `hf_sensor_io.h` (`struct sensor_info`).
* Built with `BUILD_RC=0` against `//common:kernel_aarch64` as
  `//lieppos/yft-devinfo-recon:yft_devinfo_gki`.
* 72/72 functions present, 37 size-identical, 34 byte-identical,
  **69/72 with identical external call sequences**; 42/42 objects match in
  size and section; **40/40 imports with zero CRC mismatches**.
* 17 of 27 export CRCs generated from source, never patched — including all
  four `*_fw_version` arrays and all nine `yft_set_*_device_used`.
* The 10 `*_device_add` CRC gaps are proven to be one missing token: the
  second parameter is a 73-character vendor enum, not `int`.

### Recovered API

```c
/* char[30], EXPORT_SYMBOL_GPL */
extern char touch_fw_version[30];        /* FocalTech and anything != "hyn_ts" */
extern char second_touch_fw_version[30]; /* Hynitron ("hyn_ts")                */
extern char fuelgauge_fw_version[30];
extern char tinylcd_fw_version[30];

int yft_camera_device_add(char *name, int used);
int yft_touchpanel_device_add(struct i2c_driver *driver, int used);
int yft_spitouchpanel_device_add(struct spi_driver *driver, int used);
int yft_accsensor_device_add(struct sensor_info *sensor, int used);
int yft_msensor_device_add(struct sensor_info *sensor, int used);
int yft_alspssensor_device_add(struct sensor_info *sensor, int used);
int yft_sarsensor_device_add(struct sensor_info *sensor, int used);
int yft_barosensor_device_add(struct sensor_info *sensor, int used);
int yft_fuelgauge_device_add(struct i2c_driver *driver, int used);
int yft_tinylcd_device_add(struct spi_driver *driver, int used);

int yft_set_touch_device_used(char *name, int used);   /* + 8 sibling classes */
int yft_device_dump(struct seq_file *m);
int yft_memory_dump(struct seq_file *m);
int yft_cts_dump(struct seq_file *m);
int is_yft_cts_board(void);
```

(The `used` parameter of the ten `*_device_add()` entries is a vendor enum in
the stock header — see the report.)

Userspace ABI: `/proc/yftinfo`, `/proc/yftmeminfo`, `/proc/yftctsinfo` (0666);
platform-device sysfs `yft_cts_flag`, `yft_sar_name`, `secure_boot`,
`ufs_lifetime` (0444); class `yft_device` with `yft_fm_switch` (0444);
OF compatible `mediatek,yft_devices`, driver name `mtk_yft_tpd`-style
`yft_device`, DT GPIO `urxdo_gpio_select`.

### Consumers — the assumption below was wrong

A scan of all 471 stock modules shows **seven** consumers, not two:

    focaltech_touch_spi_ft3680.ko   hynitron.ko        hf_manager.ko
    imgsensor.ko                    sh366003_fg.ko     spi_tiny_co5300_lcd.ko
    aw36518.ko

`yft_devinfo` is a nine-class device registry (camera, touchpanel, acc, m,
alsps, sar, baro sensors, fuel gauge, tiny LCD) — not an FT3680/Hynitron-only
helper.

Supporting artifacts live in `workspace/phase4-yft-devinfo/`
(`stock-oracle.txt`, `RED.md`, `yft-devinfo-stock-inventory.md`,
`yft-devinfo-source-candidates.md`, `yft-devinfo-consumers.tsv`,
`yft-devinfo-providers.tsv`, `yft-devinfo-abi-comparison.tsv`,
`yft-devinfo-verification.txt`, `yft-devinfo-callseq-compare.txt`, plus the
TSV/strings/disassembly dumps).

## Dependency chain

    yft_tpd_gesture ─────┐
                         │
    mtk_disp_notify ─────┼──> focaltech_touch_spi_ft3680
                         │
    yft_devinfo ─────────┘

`mtk_disp_notify` has already been solved as a direct-source match.

The next reverse-engineering targets are therefore:

1. ~~yft_tpd_gesture.ko~~ — **done**, see
   `kernel/phase4-yft-tpd-gesture-reconstruction.md`
2. ~~yft_devinfo.ko~~ — **done**, see
   `kernel/phase4-yft-devinfo-reconstruction.md`
3. ~~rebuild FT3680 against the reconstructed providers~~ — **done**;
   FT3680 now builds with `depends=mtk_disp_notify,yft_devinfo` and has zero
   undefined symbols lacking a MODVERSION (was 4). A latent
   `KBUILD_EXTRA_SYMBOLS` bug in the FT3680 `Makefile` — which had silently
   disabled *all* provider resolution — was fixed as part of this.
4. continue the remaining FT3680-specific reconstruction
   (`fts_fwupg_work()` so `touch_fw_version` is referenced, and the
   `yft_tpd_gesture` dependency).

Confirmed in step 2: the four `yft_devinfo` byte-array exports
(`touch_fw_version`, `second_touch_fw_version`, `tinylcd_fw_version`,
`fuelgauge_fw_version`) are `char NAME[30]` and all four stock CRCs
(`0xd0815107`, `0x7198d58d`, `0x36887f32`, `0x8c280260`) now reproduce from
the built module, not just from the CRC model.

## Exact stock oracle identities

### yft_tpd_gesture

Stock oracle:

    $RESEARCH/workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/yft_tpd_gesture.ko

SHA256:

    e7d4e7cfe4defdd69ff0e1be50c7a3de173b5c717e47e969cf0f9dec13baf9bc

Metadata:

    name:        yft_tpd_gesture
    description: YFT touch gesturewake driver
    author:      <@yft.hk>
    license:     GPL
    depends:     none

Exports:

    tpgesture_status     1-byte object
    tpgesture_value      10-byte object
    tpgesture_hander     108-byte function

The module imports only kernel/GKI interfaces and has no vendor-module
dependencies.

This makes it the first YFT provider reconstruction target.

### yft_devinfo

The vendor_dlkm and vendor_boot copies are byte-identical.

SHA256:

    0d5e547e3e6c313c88695b2c8f9aae04398e3c8822f16d57dff6aea011f821fe

Exported ABI: 27 symbols (23 `EXPORT_SYMBOL`, 4 `EXPORT_SYMBOL_GPL`) — the
four `*_fw_version` arrays, ten `*_device_add`, nine `*_set_*_device_used`,
`yft_device_dump`, `yft_memory_dump`, `yft_cts_dump`, `is_yft_cts_board`.

Consumers (all 471 stock modules scanned):

    focaltech_touch_spi_ft3680.ko   hynitron.ko        hf_manager.ko
    imgsensor.ko                    sh366003_fg.ko     spi_tiny_co5300_lcd.ko
    aw36518.ko
