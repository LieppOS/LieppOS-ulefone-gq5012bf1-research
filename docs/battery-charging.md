# Battery and charging

## VERIFIED topology

- Android-facing publisher: MT6375 `battery`/`mtk-gauge` at I2C `5-0034`.
  Stock `mt6375-battery.ko` and charger-policy modules directly acquire
  `3rd-gauge` and republish its pack values; this is not an independent primary
  telemetry source.
- Pack fuel gauge: Sinowealth SH366003 at I2C `9-0055`, exported as
  `3rd-gauge`. Its stock-oracle reconstruction has exact import/MODVERSION/KCFI
  maps, a byte-exact embedded AFI profile, a clean exact-GKI build, and a
  527-check verifier PASS; see
  [`../kernel/phase4-sh366003-reconstruction.md`](../kernel/phase4-sh366003-reconstruction.md).
- Charge pumps: SC8571 master at `11-0066` (`primary_dvchg`) and SC8571
  slave at `6-0067` (`secondary_dvchg`). The stock module is reconstructed and
  exact-GKI-build validated; see
  [`../kernel/phase4-sc8571-reconstruction.md`](../kernel/phase4-sc8571-reconstruction.md).
- SC8510 switched-capacitor converter binding at `6-0069`; reconstructed stock
  driver is a static configuration/debug/IRQ shim with no charger-class policy
  API (`sc851x-charger@6f` is a stale node name; `reg=<0x69>` is authoritative).
- MediaTek charger nodes include master/slave, divider and high-voltage divider
  paths and advertise `PD` and `PD_PPS` USB types. SC8571 itself is only a
  charge-pump actuator/telemetry consumer of `charger_class`: it imports no
  adapter, TCPM/TCPC, USB-PD, PPS, or charger-algorithm symbol and performs no
  negotiation.
- The recovered SC8571 contract has 58 regmap fields, 40 required scalar DT
  settings, fourteen charger callbacks, six exposed ADC channels, raw-dump IRQ
  notification, disabled watchdog, IRQ-only PM handling, and ADC-only shutdown.
  Exact thresholds and callback behavior are in
  [`../kernel/phase4-sc8571-hardware-contract.md`](../kernel/phase4-sc8571-hardware-contract.md).
- Frozen stock correlation: `3rd-gauge` reports 79%, 8397 mV, 13000 µA,
  37.5 °C, 26 cycles and 8594 mAh; the Android `battery` node reports the same
  SOC/current/cycles and normalizes voltage/FCC to 8397000 µV/8594000 µAh.
- Framework thermal HAL is AIDL v3 and exposes CPU, GPU, NPU, TPU, SoC, skin,
  battery, USB-port and power-amplifier temperatures plus charger, backlight,
  Wi-Fi and flashlight cooling devices.

The 8.4 V pack reading and 8.9 V charging target strongly indicate a 2S
multi-cell high-power topology, but the exact cell wiring is not declared here
without direct schematic proof. Software edges SH366003 → `3rd-gauge` →
MT6375 `battery` → Android are proven from stock disassembly and snapshots.

## UNKNOWN

- Exact 120 W negotiation state machine and OEM protocol beyond exposed PD/PPS;
  static analysis proves this policy is outside `sc8571_charger.ko`.
- Board-level SC8510 enable/direction control outside its reconstructed Linux
  shim (if any); exact V1X/V2X/VAC nets require a schematic.
- Exact arbitration between SH366003 pack data and MT6375 coulomb-counter data
  in every charger mode and balancing state (normal published values are proven
  to track SH366003).
- Full-ROM charger-mode UI and high-power thermal throttling behavior.

Do not replace these paths with hard-coded battery values.
