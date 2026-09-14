# GQ5012BF1 — uSmart state-machine contract (Phase 7)

Evidence grades used strictly:

- **PROVEN_EXACT** — name/size/call-sequence/string evidence from the stock ELF
- **PROVEN_STRUCTURE** — semantics pinned by stock strings, call order and data
  object sizes, but instruction-level layout not asserted
- **PROVEN_HIGH_LEVEL** — behaviour certain, exact enum/source spelling not proven
- **UNKNOWN** — not proven statically; requires a device

No device was touched. Nothing below is a runtime observation.

## 1. Accessory inserted (GPIO 28 LOW)

| step | effect | grade |
|---|---|---|
| ID IRQ fires | queue delayed work on `system_power_efficient_wq` | PROVEN_EXACT |
| GPIO 152 | HIGH | PROVEN_STRUCTURE |
| GPIO 55 | HIGH | PROVEN_STRUCTURE |
| `uvc_insert_status` | 1 | PROVEN_STRUCTURE |
| role | `USB_ROLE_HOST` queued | PROVEN_STRUCTURE |

## 2. Accessory removed (GPIO 28 HIGH)

GPIO 152 LOW, GPIO 55 LOW, `uvc_insert_status` = 0, `USB_ROLE_NONE` queued.
Grades as above.

## 3. Probe with accessory already inserted

Probe samples the ID GPIO (`gpiod_get_value_cansleep`) and applies the same
state immediately. **PROVEN_STRUCTURE** — the stock probe carries the
`id value : %d` literal and the initial `gpio_to_desc`/`gpiod_set_raw_value`
pair before the IRQ is requested.

## 4. `yft_usb_flag == 1` gate — STOCK QUIRK, PRESERVED

At the head of the detect work:

```
if (yft_usb_flag == 1) {
        pr_info("[%s] yft_drv ignore usb func for yft_usb_flag\n", __func__);
        return;               /* no GPIO change, no role change */
}
```

The literal `[%s] yft_drv ignore usb func for yft_usb_flag` is **PROVEN_EXACT**
and is referenced from `mtk_usb_extcon_detect_cable`,
`mtk_usb_extcon_psy_detector` and `mtk_extcon_tcpc_notifier`.

**Consequence (documented, deliberately not "fixed"):** a removal that happens
while the thermal camera owns the path leaves stale GPIO/role state. This is
stock behaviour and is reproduced as-is in the stock-compatible reconstruction.

## 5. USB role contract

`mtk_usb_extcon_set_role()` allocates and queues role work; the worker updates
the `usb_role_switch` and the cached data role (stock literal
`cur_dr(%d) new_dr(%d)`, PROVEN_EXACT).

`/sys/class/yft_extcon/tiny2c_mode`:

| op | behaviour | grade |
|---|---|---|
| write `1` | `USB_ROLE_HOST` | PROVEN_STRUCTURE |
| write any other parsed int | `USB_ROLE_NONE` | PROVEN_STRUCTURE |
| read | always `0\n` | PROVEN_STRUCTURE |

`tiny2c_mode` does **not** touch GPIO 55, GPIO 152, GPIO 37 or `usb-otg-vbus`.
It is only a role-command endpoint, and no unrelated behaviour was merged into
it.

## 6. Type-C / VBUS

Numerically handled notifier events: **8, 13, 17**. Correlating MTK headers map
these to source-VBUS, Type-C state and DR swap — that correlation is
**PROVEN_HIGH_LEVEL**, the instruction behaviour is authoritative, the enum
naming is not asserted as exact source proof.

Stock literals recovered from the notifier (all PROVEN_EXACT):

```
%s dr_swap, new role=%d      switch role to device     switch role to host
old_state=%d, new_state=%d   Type-C plug out           Type-C SINK plug in
Type-C SRC plug in           source vbus = %dmv        vbus turn %s
[%s] YFT_OTG_yft_otg_gpio set_high / set_low
vbus regulator set voltage failed / set current failed / enable failed
```

Source-VBUS enable path: GPIO 37 HIGH → log → request 5.25 V → request 1.8 A →
`regulator_enable()`. Disable path: `regulator_disable()` → GPIO 37 LOW → log.
`yft_usb_flag == 1` suppresses the selected ordinary role/VBUS behaviour; the
gates are preserved exactly.

Stock inlines `mtk_usb_extcon_set_vbus` into the notifier, which is why stock
has no out-of-line symbol for it.

## 7. Power supply

`usb_is_online()` reads `POWER_SUPPLY_PROP_ONLINE` and `POWER_SUPPLY_PROP_TYPE`
— **not** `POWER_SUPPLY_PROP_USB_TYPE`. Stock literals `failed to get online
prop`, `failed to get usb type`, `online=%d, type=%d` (PROVEN_EXACT). Accepted
types correspond to USB and USB_DCP, i.e. values 4 and 6 (PROVEN_HIGH_LEVEL).

The detector is gated by `yft_usb_flag`. With the VBUS regulator present, online
from `ROLE_NONE` can request DEVICE; without it, DEVICE/NONE follows online
state.

## 8. `vbus_limit_cur`

Accepts only `0` / `1` (`kstrtoint`, stock literals `Invalid input`,
`Do not change current`, `No vbus instance`, `vbus regulator set current
failed` — PROVEN_EXACT). While VBUS is active, 1 → 500000 uA, 0 → 1800000 uA.
Read returns the cached state. Regulator errors are propagated.

## 9. procfs

`/proc/mtk_typec/smt_u2_cc_mode` is created only when `tcpc == "type_c_port0"`
and `mediatek,u2` is present. The handler resolves the TCPC
(`tcpc_dev_get_by_name`), calls `tcpm_inquire_remote_cc`, and prints `1` only
when **both** CC values are neither 0 nor 15, else `0` (stock literals
`cc1=%d, cc2=%d`, `0\n`, `1\n`, and `seq_puts` in the import set —
PROVEN_STRUCTURE).

## 10. Shutdown

Turn VBUS off if active → GPIO 37 LOW → `regulator_disable()` → clear cached
source/current-limit state. Stock literal `shutdown` plus the inlined
`set_vbus` tail (PROVEN_STRUCTURE). **No YFT suspend/resume hooks were proven
and none were invented.**

## 11. UNKNOWN (explicitly not claimed)

Physical uSmart connector pinout, connector pin numbers, charging the phone from
uSmart, reverse-power acceptance, external mux/load-switch IC identity,
accessory current/inrush limits, USB descriptor matrix, a second USB controller,
SC851x ownership, `reverse_charging_level`. Runtime notify-type coverage of the
notifier also remains UNKNOWN — it needs a device.
