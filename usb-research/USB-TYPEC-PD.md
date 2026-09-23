# Type-C, TCPC, orientation and Power Delivery

## Hardware identity

Classification: **PROVEN**.

The Type-C Port Controller is the MT6375 TCPC function below the MT6375 MFD:

```text
/soc/i2c@11280000/mt6375@34/tcpc
  compatible = "mediatek,mt6375-tcpc"
  tcpc,name = "type_c_port0"
  interrupt = pd_evt
```

The live driver stack is:

```text
MT6375 TCPC hardware
  -> tcpc_mt6375.ko
  -> tcpc_class.ko / MediaTek-Richtek TCPM
  -> rt_pd_manager.ko
  -> mtk_pd_adapter.ko
  -> charger framework
```

The DT declares dual power role, dual data role, local USB communication and PD identity `29cf:6375` / `RichtekTCPC`.

## CC and role detection

`tcpc_mt6375.ko` implements:

- CC1/CC2 measurement (`get_cc`);
- Rp/Rd/open programming (`set_cc`);
- plug polarity (`set_polarity`);
- VCONN (`set_vconn`);
- PD transmit/retransmit;
- VBUS-present/safe-0-V detection;
- low-power mode and fault handling.

`extcon-mtk-usb.ko` subscribes to the TCPC notifier stream and converts attach/role/VBUS events into MTU3 role-switch and MT6375 OTG-regulator operations.

The captured port state while connected to a PC was dual-role with active device/sink and sink preference. See `evidence/stock-typec-state.txt`.

## Orientation handling

The MT6375 driver programs the TCPC `PLUG_ORIENT` bit according to detected CC polarity. The DT overlay links the TCPC connector endpoint to `/soc/typec-mux-switch`, which registers Linux Type-C orientation/mode callbacks through `mux_switch.ko`.

Important limitation: stock `mux_switch.ko` has no I2C, GPIO or regmap imports. It is a callback fan-out layer, not proof of a physical SuperSpeed mux. USB2 D+/D− do not require orientation-switched lane pairs because the receptacle's duplicated USB2 contacts can be tied together correctly.

Therefore:

- **CC orientation detection:** PROVEN;
- **software orientation notification:** PROVEN;
- **physical SuperSpeed lane mux:** UNKNOWN, no positive evidence;
- **integrated MT6878 U3 lane switching:** UNKNOWN, strongly disfavored by absent U3 PHY.

## VCONN

VCONN is controlled inside the MT6375 TCPC, not by the MTU3 data controller. The reconstructed stock-equivalent driver:

1. enables MT6375 VCONN over-voltage and reverse-voltage protection;
2. checks VCONN fault state;
3. sets the TCPC `POWER_CTRL.VCONN` bit;
4. enables the MT6375 VCONN UVP/OCP charge-pump control;
5. reverses the sequence on disable.

This is **PROVEN from the stock-equivalent `tcpc_mt6375` control flow**. The live PC attachment reported `vconn_source=no`, as expected for the tested device/sink state.

## PD and PPS

PD messaging is implemented by MT6375 TCPC hardware plus `tcpc_mt6375.ko`/`tcpc_class.ko`. `mtk_pd_adapter.ko` exposes negotiated adapter functions to MediaTek charging policy, and `mtk_pd_charging.ko` supplies PD charging policy.

PPS appears as a supported charger-framework USB type (`PD_PPS`) and the charging framework explicitly selects a “pd pps adapter” path. Classification:

- PD support: **PROVEN**;
- PPS support: **PROVEN software path**, not exercised with a PPS analyzer in this session;
- current PC attachment using PD: **NOT CLAIMED**.

PD/PPS manage power negotiation. They do not imply USB3 data lanes.

## UFCS

The MediaTek charger framework contains an independent `ufcs_adapter` policy path and logs `pd_type` and `ufcs_type` separately. Existing stock evidence records `pd_type:2, ufcs_type:1`. `mtk_pep40.ko` also searches independently for PD and UFCS adapters.

Classification: **PROVEN stock UFCS policy integration; exact low-level UFCS adapter provider remains UNKNOWN**. No evidence connects UFCS signaling to MTU3 SuperSpeed data.

## DisplayPort Alt Mode

The MT6375 connector capability node contains generic DisplayPort pin-assignment data and the overlay links the TCPC to the software Type-C mux node. No enabled DP PHY, USB/DP selector, DRM bridge, physical mux/redriver or userspace DP service was found for GQ5012BF1.

Verdict: `DISPLAYPORT_ALT_MODE = UNKNOWN / NO OPERATIONAL EVIDENCE`.

Generic TCPC capability data is not proof that the receptacle or PCB carries DP lanes.
