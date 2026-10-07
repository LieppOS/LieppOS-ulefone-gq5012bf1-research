# Boundary to FM78100-COMPANION (8-003c)

| question | answer | evidence |
|---|---|---|
| same silicon? | yes: 8-003c is the I2C slave of the same module ASIC that enumerates as 3474:4321 (no separate FM78100 fitted) | FM78100-COMPANION (DONE) `hardware/topology.md` |
| must it initialise before USB enumeration? | no. Its only traffic is a boot-time chip-ID read (`0x4c59`) in `yft_tiny2c_usb` probe, after which the rails are switched **off**; the thermal session powers the module afresh and sends no I2C | `fm78100/power-sequence.md` |
| does it control the same module at run time? | no I2C command channel exists in any stock component; all run-time control is USB vdcmd | `kernel-path.md`, `vendor-control.md` |
| shutter / FFC? | over USB only (`basic_ffc_update` 0x10/0x02/0x43, `adv_shutter_tab_open` 0x01/0x0f/0x45, auto-FFC module 0x02) | `vendor-opcodes.tsv` |
| power / reset of the USB function? | the module power rails (GPIO 149/191/192) belong to `yft_tiny2c_usb.ko`, the same driver that owns 8-003c; there is no reset GPIO; module reset is by USB vdcmd (`basic_reset_to_rom/bootloader/normal`) or power cycle | FM78100 closure |
| shared sysfs | `sensor_id` (FactoryMode pass = `0x4c59`) from the I2C side; `tiny2c_usb_mode` power node used by the USB thermal session | FM78100 closure |

Cross-references: AC020-UVC = USB function + vdcmd + stream; FM78100-COMPANION = I2C ID
endpoint + power driver. Neither depends on the other at run time.
