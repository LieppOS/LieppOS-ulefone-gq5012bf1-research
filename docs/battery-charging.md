# Battery and charging

## VERIFIED topology

- Primary Android battery path: MT6375 `mtk-gauge` at I2C `5-0034`.
- Secondary fuel gauge: SH366003 at I2C `9-0055`, exported as `3rd-gauge`.
- Charge pumps: SC8571 master at `11-0066`, SC8571 slave at `6-0067`.
- SC8510 switched-capacitor converter binding at `6-0069`; reconstructed stock
  driver is a static configuration/debug/IRQ shim with no charger-class policy
  API (`sc851x-charger@6f` is a stale node name; `reg=<0x69>` is authoritative).
- MediaTek charger nodes include master/slave, divider and high-voltage divider
  paths and advertise `PD` and `PD_PPS` USB types.
- Stock battery sample: 78%, charging, 8.400 V, 35.0 °C, Li-ion, design capacity
  approximately 8,588,000 µAh.
- Framework thermal HAL is AIDL v3 and exposes CPU, GPU, NPU, TPU, SoC, skin,
  battery, USB-port and power-amplifier temperatures plus charger, backlight,
  Wi-Fi and flashlight cooling devices.

The 8.4 V pack reading and dual gauge/charge-pump layout strongly indicate a
multi-cell high-power topology, but the exact cell wiring is not declared here
without direct schematic/driver proof.

## UNKNOWN

- Exact 120 W negotiation state machine and OEM protocol beyond exposed PD/PPS.
- Board-level SC8510 enable/direction control outside its reconstructed Linux
  shim (if any); exact V1X/V2X/VAC nets require a schematic.
- Which gauge is authoritative during every charger mode and balancing state.
- Full-ROM charger-mode UI and high-power thermal throttling behavior.

Do not replace these paths with hard-coded battery values.
