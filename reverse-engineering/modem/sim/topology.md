# SIM / UICC topology

## Proven topology

* **Two removable nano-SIM slots, DSDS** (dual SIM dual standby), not DSDA:
  `ro.telephony.sim.count=2`, `persist.radio.multisim.config=dsds`,
  `persist.vendor.radio.msimmode=dsds`, `ro.vendor.radio.max.multisim=dsds`.
* `ro.vendor.mtk_ril_mode=c6m_1rild`: one rild and one MD1 serve both subscriptions.
* Both slots have Android AIDL `IRadioSim`, `IRadioData`, `IRadioVoice`, `IRadioNetwork`,
  `IRadioMessaging`, `IRadioModem` and `ISap` instances (`slot1`, `slot2`).
* Both have MTK `se1`/`se2` radio SIM/modem instances because `ro.vendor.mtk_uicc_clf=1`.
  These are removable UICC secure-element interfaces, **not eUICC**.
* Prior closed scope `DONE/ESIM-EUICC-ABSENCE` proves no eSIM/eUICC feature, LPA, eUICC bus node
  or embedded slot. The YFT `/sys/devices/platform/yft_device/esim_switch` name does not override
  that evidence; it is an OEM board switch/name with no eUICC framework stack.

## Electrical / hot-plug evidence

| slot | pins from live LK `/gpio` map | hot plug |
|---|---|---|
| SIM1 | SCLK GPIO83, SRST GPIO84, SIO GPIO85 | `MD1-SIM1-HOT-PLUG-EINT`: GPIO46/EINT0, level-low, debounce 10 ms, `src-pin=1` |
| SIM2 | SCLK GPIO86, SRST GPIO87, SIO GPIO88 | `MD1-SIM2-HOT-PLUG-EINT` node exists but is empty: no IRQ/property in captured DT |

The MD owns the UICC protocol. The AP forwards GPIO/ADC/DT queries through `ccci_rpc`; no AP
SIM controller driver was found.

## Software path

```
SubscriptionManager/UiccController
  -> AIDL IRadioSim/{slot1,slot2} (+ ISap and MTK mtkradioex.sim)
  -> mtkfusionrild/librilfusion/libmtkmipc-ril
  -> MIPC /dev/ttyCMIPC1 -> CCCI CCIF -> MD1 UICC stack -> physical SIM1/SIM2
```

* STK BIP: `bip_ap` ↔ `/dev/ccci_bip`, started only when CCCI reports READY and stopped on
  reset/flightmode.
* SIM ME lock: `libsimlock.so`, `libsimmelock.so`, `ro.vendor.sim_me_lock_mode=3`.
* Switching policy: `persist.vendor.mtk_sim_switch_policy=2`, dynamic IMS switch enabled,
  smart data switch enabled. The exact policy algorithm is proprietary RIL/MD code.
* `ro.vendor.mtk_sim_card_onoff=3` exposes per-slot SIM on/off support.
* Secondary-slot RAT configuration is `persist.vendor.radio.mtk_ps2_rat=N/L/W/G`; one active
  packet-service subscription at a time is still consistent with DSDS.

No SIM ICCID/IMSI, IMEI or other personal identifier was read or recorded.
