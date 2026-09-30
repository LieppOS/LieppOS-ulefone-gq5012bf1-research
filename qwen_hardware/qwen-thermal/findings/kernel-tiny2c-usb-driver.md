# Kernel driver RE — `yft_tiny2c_usb.ko` (module for the thermal module front-end)

Evidence: `evidence/local/fm78100/yft_tiny2c_usb.ko.txt`, `yft_tiny2c_usb.objdump.txt`
(full `llvm-objdump -d --reloc` of `vendor_dlkm/lib/modules/yft_tiny2c_usb.ko`,
sha256 `77baeee8fa7c01d9b6ad9b3a9743caa69aa61b840c3d565d5263d3e965d63eed`).
All statements below are from the disassembly + `.rodata` strings unless marked INFERENCE.

## Identity / bindings (VERIFIED via modinfo)
- `description = "Module For tiny2c_usb"`, `author = yft-drv`, `license = GPL`, kernel `6.1.115-android14`.
- Aliases: `i2c:tiny2c_usb-sensor`, `of:N*T*Cmediatek,yft_tiny2c_usb` (+`C*`).
- `depends: mt6375-charger` and undefined symbol `yft_usb_flag` (exported by the mt6375
  charger/Type-C driver). This is the cross-driver handshake (see mode_store below).
- DT node on live device: `soc/i2c@11e03000/fm78100@0x3c` with
  `compatible = "mediatek,tiny2c_usb"`; bus `i2c@11e03000` = SCL GPIO 141 / SDA GPIO 142.
  ⇒ The "fm78100" node name is legacy OEM naming for the thermal-module front-end,
  bound to THIS driver (`tiny2c_usb-sensor` id). There is a separate `fm78100-sensor`
  naming family that is NOT what binds this module.

## Function inventory (VERIFIED via nm)
`init_module/cleanup_module`, `tiny2c_usb_probe/remove` (platform),
`tiny2c_usb_i2c_probe/remove/i2c_read/read_chipid/power_init/parse_dts`,
sysfs: `tiny2c_usb_mode_show/store` and `sensor_id_show` created on the
`/sys/devices/platform/yft_tiny2c_usb/` device. A separate `extcon-mtk-usb.ko`
`show/store_tiny2c_mode` owns `/sys/class/yft_extcon/tiny2c_mode` and queues delayed USB-route
work; FactoryMode writes both nodes.

Kernel API used (VERIFIED via `nm -u`): `i2c_transfer`, `i2c_register_driver`,
`gpio_request`, `gpio_to_desc`, `gpiod_get_raw_value`, `gpiod_set_raw_value`,
`of_get_named_gpio_flags`, `sscanf`, `scnprintf`, `msleep`, `__const_udelay`, `yft_usb_flag`.

## GPIO rails (VERIFIED)
`tiny2c_usb_parse_dts` logs `gpio_1v8=%d,gpio_3v3=%d,gpio_5v=%d,gpio_io3v3:%d`; DT names:
`tiny2c_gpio_1v8`, `tiny2c_gpio_3v3`, `tiny2c_gpio_5v`, `tiny2c_gpio_io3v3`
(and legacy aliases `tiny2c_usb_vdd_1v8=192`, `tiny2c_usb_vdd_3v3=191`,
`tiny2c_usb_vdd_5v`, `tiny2c_usb_vddio_3v3=149` — phandles from live DT snapshot).
Four regulator/enable GPIOs: 1.8 V, 3.3 V core rail, 5 V (VBUS-style boost for the module),
and 3.3 V I/O. Error strings `"[GPIO]reset gpio request failed gpio_*"`.

## `tiny2c_usb_power_init(en)` (RECOVERED control flow)
`printk("...enter. en=%d")` then, for each of the four descriptors (struct offsets +0xc,
+0x8, +0x4, +0x0 in `tiny2c_usb_chip_data`): `gpiod_set_raw_value(gpio_to_desc(n), en)`.
i.e. it is a flat all-rails-to-level helper; no sequencing delays inside this function.

## `tiny2c_usb_mode_store` — the ON/OFF switch (RECOVERED)
- Parses one int with `sscanf` (format in `.rodata`).
- `en == 1` → branch at 0x1a4: `printk("power on: %d")`; four
  `gpiod_set_raw_value(..., 1)`; **stores 1 into `yft_usb_flag`**; done.
- else (`en == 0`) → after 0x214 block prints `"%s: power off: %d"`, four
  `gpiod_set_raw_value(..., 0)` (all rails low), then `w1 = wzr` and **stores 0 into
  `yft_usb_flag`**.
- `tiny2c_usb_mode_show` re-reads raw GPIO levels via `gpiod_get_raw_value` and `scnprintf`s
  `"%s %d."` per rail on `/sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode`.

⇒ Semantics: writing `1` to the **platform** node powers the thermal module rails and raises
`yft_usb_flag`; writing `0` powers down and clears it. Separately, writing the same value to
`/sys/class/yft_extcon/tiny2c_mode` makes `extcon-mtk-usb.ko` queue delayed USB-role/mux work.
FactoryMode deliberately writes both nodes before registering USBMonitor and clears both after
release. This two-node ownership is confirmed by the two independent module disassemblies.

## `tiny2c_usb_read_chipid` (RECOVERED)
- Retry loop: counter init `#5` with 6 total attempts (string `"6%s. retry = %d, chip_id = 0x%x."`).
- Each attempt: build two I2C msgs — 1-byte write (register/address pointer; debug string
  `"[%s] zzt_1 addr=0x%x"` / `"[%s]addr=0x%x start..."`) then 2-byte read via `i2c_transfer`;
  on success `printk("yft-drv Read_Data_ok=%x,,buf:[%x,%x]")`, `chip_id = (buf[0]<<8)|buf[1]`
  (`mov w9,#0x100` shift-or at 0x518); non-zero chip_id exits the loop; exhaustion prints
  `"read sensor-id fail"` and returns `-ENODEV` (`#-0x13` = -19).
- `dev_attr_sensor_id` exposes it read-only. FactoryMode's exact `InfiraySmtTest` acceptance
  constant is **`0x4c59`** and it only enables Pass when
  `/sys/devices/platform/yft_tiny2c_usb/sensor_id` trims to that string. Thus `0x4c59` is the
  expected production front-end/module chip ID (EXACT_STOCK_CODE), although the offline
  snapshot did not contain a contemporaneous live read.

## `tiny2c_usb_i2c_read` (RECOVERED)
Generic helper identical in shape: write 1 byte reg addr, read `len` (called with 2),
`-ENODEV` on transfer count mismatch, log `"i2c transfer failed (%d)"`.

## Role summary
`yft_tiny2c_usb` is NOT a sensor driver in the imaging sense: it is a **power/LTE-switch
glue driver + chip presence probe** for the InfiRay thermal module attached over the
USB2 "tiny2c" front-end (I2C 0x3c probe, GPIO rail enables 1v8/3v3/5v/io3v3, Type-C lane
flag `yft_usb_flag` to mt6375). All imaging traffic itself is USB/UVC from user space
(`libusbuvccamera020.so` → `/dev/bus/usb/*`). This closes the earlier open question U6:
FM78100 is a node label; the bound driver is `tiny2c_usb-sensor`; its role is module
power sequencing + lane switch + presence check.
