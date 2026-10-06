# Camera module EEPROMs — topology and association proof

Table: [`eeprom-topology.tsv`](eeprom-topology.tsv).

| camera | sensor | EEPROM (wire) | DT client | char dev | data the stock kernel parses |
|---|---|---|---|---|---|
| 0 | imx989 | **i2c-7 / 0x50** | `7-0051` | `/dev/camera_eeprom0` | header, AWB, LSC, AF, PDAF |
| 1 | s5kjn1 (front) | **i2c-4 / 0x50** | `4-0050` | `/dev/camera_eeprom1` | header, AWB, LSC |
| 2 | s5kjn1main2 | **i2c-2 / 0x50** | `2-0050` | `/dev/camera_eeprom2` | header, AWB, LSC, AF, PDAF |
| 3 | ov64b | **i2c-4 / 0x53** | `4-0051` | `/dev/camera_eeprom4` | header, AF |

All four are **external module EEPROMs** (16-bit offset addressing,
separate I2C slaves from the sensors, `data_ver = SINGLE_EEPROM`), not sensor OTP.

## The DT address is not the wire address

`read_data_region()` (and `read_region()` for raw `read()`) save
`client->addr`, set it to `config->i2c_write_id >> 1` (or
`g_camCalList[].slaveID >> 1`), perform the transfer, and restore it, all
under the per-device mutex. Every stock config uses `0xA0` (0x50), except
`ov64b_cust_eeprom` with `0xA6` (**0x53**). The DT `reg` values (0x51 / 0x50 /
0x50 / 0x51) only give the I2C core distinct clients to bind. The node
name `camera-eeprom<N>` gives the char-device index N, through `retrieve_index()`.

Consequence on the shared i2c-4: `camera-eeprom1` (`4-0050`) and
`camera-eeprom4` (`4-0051`) both live on the same adapter. Which physical chip
answers depends only on the address the selected config uses: 0x50 for s5kjn1
and 0x53 for ov64b.

## Association proof (no proximity-only inference)

For each camera, independent channels:

1. **Kernel config keyed by sensor ID.** The HAL passes the sensor ID in the
   ioctl. `check_layout_function` matches `config->sensor_id` and then reads the
   4-byte header at offset 0 from the config's address. A layout only binds
   when that sensor's module EEPROM answers with magic `0x77006901` at the
   config address on the bus of the opened node.
2. **imgsensor reads the same EEPROM through the sensor's own I2C client**
   (closed imgsensor scope, stock data). Each read goes to the adapter the
   sensor itself is bound to:
   * imx989 (sensor0, client `7-0020`): `eeprom_info = {header_id 0x77006901, i2c_write_id 0xA0, QSC @0xd4f+0xc00 → sensor reg 0x1000}`
   * s5kjn1 (sensor1, `4-0010`): `read_4cell_from_eeprom()`, `EEPROM_READ_ID 0xA0`, blocks @0x0d4f/0x1afd/0x1dfd/0x2d9d
   * s5kjn1main2 (sensor2, `2-0010`): same 4-cell reads at 0xA0, plus `eeprom_info {header 0x77006901, 0xA0, QSC 0x300f+0x15a, qsc_support 0}`
   * ov64b (sensor4, `4-0020`): **no** EEPROM access in imgsensor
   So 0x50 on i2c-7 belongs to imx989, 0x50 on i2c-2 to s5kjn1main2, and 0x50 on i2c-4
   to s5kjn1. The only other EEPROM address on i2c-4 is 0x53, used only by the
   ov64b config and `g_camCalList[4]` (0x566442 → 0xA6).
3. **HAL device index.** `CamCalHelper::getEepromDevIdx(sensorDev)`
   (`libfeatureiodrv_mem.so`) takes the index from
   `IHalSensorList::querySensorStaticInfo(dev)` (field at +0x64), falling back
   to `ctz(sensorDev)`. It opens `/dev/camera_eeprom<idx>`. The DT EEPROM node
   indices 0/1/2/4 equal the imgsensor node indices `sensor0/1/2/4`.
4. **Data content consistency.** Only the AF-capable cameras (0, 2, 3; proven
   independently in CAMERA-VCMS) have AF items. The fixed-focus front parser
   sets `S2aBitEn = 1` (AWB only).
5. **Live binding** (stock read-only capture): `7-0051`, `4-0050`, `2-0050`,
   `4-0051` are bound to `mediatek,camera_eeprom`, and
   `/dev/camera_eeprom{0,1,2,4}` exist (0660 `system:camera`,
   `u:object_r:camera_eeprom_device:s0`).

No DT phandle links a sensor to an EEPROM. The EEPROM nodes' phandles are
unreferenced.

## Power

EEPROM nodes have no supplies or pinctrl. The EEPROMs are powered by their
camera module's rails, which imgsensor switches. The HAL handles this with
`CAM_CALIOC_G_GKI_NEED_POWER_ON` and `CamCalHelper::sensorPowerOn/Off`; see
[`../kernel/read-write-path.md`](../kernel/read-write-path.md).

## Size

The chips have no size or ID register, so capacity is bounded only by use:

* 16-bit addressing (2-byte address phase), so at least 24C32-class.
* s5kjn1 and s5kjn1main2: stock software reads up to 0x300e, so at least a 16 KiB-class part.
* imx989: up to 0x194e. ov64b: up to 0x14ff.
* Stock kernel window: `max_size = 0x4000` for all four.

The exact EEPROM die is **not electronically identifiable** from stock software.
