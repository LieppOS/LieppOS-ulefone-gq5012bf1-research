# RT5133 audit correction — final evidence decision

Final review: 2026-10-08. Supersedes the RT5133 assertions in audit commit `9958328`; it does not alter the component's static DONE status.

## Decision

**RETRACT** the claim that RT5133 was successfully bound and operating as this phone's camera LDO. **REJECT** `RT5133-POWER-IC → RT5133-CAMERA-LDO-INTEGRATION`. Keep the existing name and its proven static scope. A DT declaration and a loaded module do not establish successful probe, physical population or rail usage.

## Exact evidence and chronology

1. [Stock ADB capture, 2026-08-31 11:56:49](../../../workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/buses.txt), lines 79–82:

   ```text
   ===/sys/bus/i2c/devices/5-0018===
   /sys/devices/platform/soc/11280000.i2c/i2c-5/5-0018/driver
   rt5133
   of:Nrt5133T(null)Crichtek,rt5133
   ```

   The first value is an unresolved device-local `driver` path, **not** `/sys/bus/i2c/drivers/rt5133`. The following `rt5133` is the client `name`. Compare lines 14–18 of the *same capture*: `11-0029` has `/sys/bus/i2c/drivers/wl2864c` and `/sys/module/custom_ldo_wl2868`, proving the WL2864C camera-LDO binding. Capture SHA-256: `1b39dd774b0c710a78a429d03f86659ce40b5dbea0a4467011b46743ff451a26`.

2. [Independent stock-kernel/vendor_boot, GSI-system pstore capture, 2026-08-29 investigation](../../../evidence/boot-hang-2026-08-29/pstore/ulefone-pstore-v9-validated-baseline/console-ramoops-0), lines 298–300, boot times 14.820258–14.820268 seconds: `rt5133-gpio3`, `rt5133-gpio1`, and `rt5133-gpio2` each report `deferred probe pending`. SHA-256: `c6ea67505401840a2a81bca40a06cb95457be8030ca28087d2a0142a4a51366d`. This is a different boot state, corroborating failure rather than proving a later successful bind.

3. [Build14/OrangeFox capture](../../../evidence/hw-tests/build14-touch-usb/of-live-input-buses.txt), line 93: `5-0018 driver=driver ... Crichtek,rt5133`. The literal basename `driver`, unlike `driver=mt6375` on `5-0034`, also does not show a bound RT5133. This artifact was already imported by commit `d7c1905` (2026-09-01); no success timestamp can be inferred from it.

4. [Authoritative RT5133 topology](../../power/rt5133/hardware/topology.md), especially §§1–5, and [static status](../../power/rt5133/STATUS.md), committed in `8ed7c06` on **2026-10-06 14:10 +0300**, explicitly withdrew the earlier client-name misreading. It establishes the base-DTB I²C5/0x18 reference node (68/68 properties equal to ALPS), no successful probe, no registered RT5133 regulators/GPOs, and no external rail consumers. The first CHIP_INFO/0x00 transaction failure is the exact-source control-flow inference documented there; the captures do **not** independently report a measured register value or the precise NACK/CRC/power cause.

5. Audit commit `9958328` subsequently repeated the older “bound camera-sensor LDO” prose in `hardware.tsv`, `device-tree.tsv`, `PROPOSED-CHANGES.md` and the index. Its builders and checker even enforced that assumption. It cited **no new runtime capture**. A later-written report is not later runtime evidence: this was an audit error, not a demonstrated state transition.

## Board-specific limits and safety

The reference driver is a camera-LDO capability, but on the observed GQ5012BF1 boot the camera rails use WL2864C/WL2868C at `11-0029`. RT5133's reference HWEN and WL2864C reset both specify GPIO1. The detailed source/DT analysis warns that forcing RT5133 probe success could retain GPIO1 and block the working WL2864C path. No register accesses, phone tests or DT changes were made in this audit.

Physical absence versus an unpowered/nonresponding footprint is not proved by sysfs alone. Use **PRESENT-NOT-BOUND** (declared client, not proven populated), not “operating camera LDO” or unconditional silicon absence. `rt5133-regulator.ko` and its `extdev_io_class.ko` dependency remain statically source/parity closed; loaded/reference capability is distinct from active board usage. Preserve all original captures and parity evidence.
