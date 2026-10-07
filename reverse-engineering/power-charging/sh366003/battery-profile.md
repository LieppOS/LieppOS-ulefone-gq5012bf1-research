# SH366003 battery profile / calibration ownership

## What the driver contains

| item | where | value |
|---|---|---|
| battery model/profile program ("AFI") | **compiled into the module**: `.rodata` object `sinofs_afi_data`, 2142 B, sha256 `4888c5bc…59e1` (stock), included as `sinofs_afi_data.inc` (sha256 `c4c297b3…a4d1`, private tree `kernel/phase4-sh366003-recon/`) | 209 records: 104 writes, 104 waits, 1 compare; data-flash 0x4000–0x47B8 (51 × ≤32 B through 0x3E) + 51 embedded checksum/length commits through 0x60, then `0x00 ← 45 00`, `0x3E ← 46 00`, compare `46 00 d3 8c` |
| expected profile identity | code constants | MAC 0x004D == **0x5A93** (date 2025-04-19); final AFI checksum **0x8CD3** (MAC 0x0046) |
| auto-update threshold | code constant | update when 0x004D ≠ 0x5A93 **or FCC < 3500 mAh** (`cmp #0xdab; b.gt` — corrects "≤ 3500"/"> 3500" in older notes) |
| unseal / full-access keys | code constants | `0x12345678`, `0x90ABCDEF` (sent as 5678,1234,CDEF,90AB) |

Everything else that a fuel gauge needs — OCV table, resistance (Ra) model, Qmax/design capacity,
design voltage, temperature compensation, sense-resistor/CC calibration, 2S configuration, aging
(lifetime) data, learned FCC and cycle count — lives **in the gauge's own data flash**. The driver
neither reads nor writes these fields individually: it only (re)programs the opaque 0x4000–0x47B8
image and reads the SBS results. The semantic layout of SH366003 data flash is not public and
not needed by the kernel driver.

## Storage classification

| class | storage |
|---|---|
| static battery-model profile | module `.rodata` → gauge data flash (programmed by the driver) |
| DT | nothing battery-related (see `dt-properties.tsv`) |
| external file / firmware loader / NVRAM / userspace | **none** (no `request_firmware`, no file APIs; MTK `fuelgauged` NVRAM belongs to the MT6375 gauge path) |
| per-device calibration, learned capacity, cycle/lifetime history | gauge internal flash only; never read, written or backed up by the driver; not published |
| manufacture date | MAC 0x004D; writable once via sysfs (raw reg 0x4D) when it reads 0 |

The AFI is a per-battery-model static program, identical on every unit running this build;
it is documented by hash and record structure. No unique per-device calibration was found or
published.

## Pack figures available to the driver

| quantity | source | note |
|---|---|---|
| pack voltage | SBS 0x08 mV | 2S |
| cell voltages | MAC 0x0071 (log), MAC 0x0060 max (`maxvoltage = v1 + v2`, stored only) | 2 cells |
| FCC | SBS 0x12 mAh | exported as CHARGE_FULL_DESIGN; earlier capture 8594 mAh |
| remaining | SBS 0x10 mAh | log only |
| design capacity | **not read** (no SBS 0x18 access) | — |
| charge V/I request | SBS 0x30 / 0x32 | log only (capture 8900 mV / 9500 mA) |
| SOH | SBS 0x2E (log) and synthetic sysfs `soh` from cycle count | — |
| termination voltage | `term_volt` field is **never set** (always 0) | dead template field |
