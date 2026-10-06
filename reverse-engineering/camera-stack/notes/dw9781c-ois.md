# DW9781C OIS — exact source, interface, ownership

## Source (PROVEN, byte-level)

Stock `vendor_dlkm/lib/modules/dw9781c.ko` (sha256 5421b83c…) is built from
NothingOSS MT6878 `device_modules/drivers/misc/mediatek/lens/ois/dw9781c/
dw9781c.c` (sha256 2391c3b1…) **without modification**:

* exact GKI 12901745 toolchain (clang r487747c), `KBUILD_EXTRA_SYMBOLS`
  carrying the two stock `hf_manager` CRCs;
* 19/19 functions byte-identical, 19/19 KCFI ids, 37/37 imports,
  38/38 MODVERSION CRCs, 52/52 strings;
* every code/data section identical (`.text`, `.rodata`, `.data`,
  `.rodata.str1.1`, `.init/.exit.text`, `__versions`, `.bss`…); only
  `.modinfo` vermagic tag (`-g945dff7bc1bf` vs local `-maybe-dirty`),
  build-id, relocation-section ordering and our debug sections differ.
* reports: `donor-comparisons/dw9781c-stock-vs-nothing-parity.txt`,
  `dw9781c-section-parity.tsv`; rebuild: `scripts/build_donor_camera_modules.sh`.

## Interface (from the exact source)

* I2C: DT node `i2c@11c23000/camera-ois-main@e` (i2c-4), but probe and
  init force `client->addr = 0x14 >> 1` = **0x0A**. The live bus entry is
  `4-000e`; traffic goes to 0x0A on i2c-4. (`main_vcm`'s DT client is also 0x0A, on
  i2c-7, but its traffic goes to 0x0C — see `../../camera/vcm/`. Note that
  `main2_vcm` shares i2c-4 with the OIS: its traffic goes to 0x0C, so no conflict either.)
* Supplies: `devm_regulator_get("vdd")` (no `vdd-supply` in DT → dummy) and
  `"rst"` → `rst-supply = camera-common-dovdd` (regulator-fixed 1.8 V,
  **no GPIO** — always-on/dummy-gated). No pinctrl states, no clocks used.
* Registers: CHIP_CTRL 0xD000, DSP_CTRL 0xD001, LOGIC_RESET 0xD002,
  write-protect 0xEBF1=0x56FA, FW_VER 0x7001, FW_DATE 0x7002, OIS_MODE
  0x7014 (STILL 0x8000), OIS_CTRL 0x7015, IMU_SELECT 0x7012
  (`ICM42631_AUX2`=8), GYRO_INIT 0x7018, CMD_STATUS 0x73E5, gyro
  0x70F0/F1, target 0x7274/75, lens pos 0x7049/4A, pan-tilt limit
  0x725C/5D = 1100.
* Firmware: `FW_UPDATE` undefined → **no firmware download path compiled**
  (the VIVO FW header is not even included). Only version/date read.
* **NVM write hazard:** `dw9781c_init()` writes a "store" sequence
  (`0x7015=2, 0xFD00=0x5252, 0x7011=0x00AA, 0x7010=0x8000`) whenever
  `GYRO_INIT != 1` after reset. Any reconstruction/test must treat this as
  a calibration-memory write.
* Init path: probe → `hf_manager` device `dw9781c` sensor type `OIS1`
  (polling, sync) + v4l2 subdev; `ois_init_fx` workqueue on stream-on;
  `VIDIOC_MTK_S_OIS_MODE` ioctl; `hf_manager` sample returns gyro/target/
  hall data.

## Userspace ownership (PROVEN)

`libcam.hal3a.oisdrv.so` (`aaa/peripheraldriver/ois/ois_drv.cpp`) obtains
the subdev name via `GetOisDriverName()` from `libcameracustom.lens.so`.
In that library `vcm_list_0` maps sensors 0x989/0x988/0x8E1→`main_vcm`,
0x38E2→`main4_vcm`, 0x566442→`main2_vcm`, but **all six `ois_list_N`
tables contain only the `Dummy` entry (sensor id 0xFFFF)**. The stock HAL
therefore never opens DW9781C → `availableOpticalStabilization = [0]` on
every camera. The kernel driver is alive (hf_manager OIS1) but no camera
pipeline consumer exists.

## Physical association

UNKNOWN. For OV64B: same i2c-4, `sensor4` has `oisen_0/1` pinctrl, DT
alias `main_ois_cam1` (cam1 = the alias index used for OV64B's
`main_af_cam1`). For IMX989: node name `camera-ois-main`, `sensor0`
`oisvdd_0/1` pinctrl (GPIO22), Nothing donor IMX989 pw_seq had OISVDD.
Stock IMX989 and OV64B pw_seqs both **removed** OIS steps. No calibration
relationship exists in stock (no EEPROM OIS fields consumed by any stock
kernel code).

## Correction to earlier notes

`qwen_hardware/verification/findings/ois-vcm-lens-mapping.md` (second
pass) and `qwen_hardware/verification/evidence/live-devicetree-secondpass.txt`
state that `camera-ois-main@e` carries `camreg = <&mt6363_vcm3 …>`,
`dw9781c,VDD/ACCURACY/HALL1VDD…`, `reset-gpios 146`, `pwdn-gpios 148`, and
that the WL2864C node has `ois-en-gpios = <133>`. **The live DT tarball does
not contain these properties**: `camera-ois-main@e` has only `compatible`,
`name`, `reg`, `rst-supply`, `port/endpoint`; `pmu@wl2864c` has only
`compatible, reg, reset-gpios, id_reg, id_val, id_reg_2868c, id_val_2868c,
name`; no `camreg` string exists in the merged DTS or in `dw9781c.ko`.
Those statements should be treated as unsupported.
