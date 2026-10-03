# Wired headset stack

## 3.5 mm analog jack

The fitted path is the MT6369 ACCDET block:

```text
jack plug / buttons
  -> MT6369 PMIC EINT0 + ACCDET comparator + AUXADC ch9
  -> mt6369-accdet.ko
  -> ALSA jack reports HEADPHONE / MICROPHONE / BTN_0..2
  -> Android wired-headset device routing
```

DT contract:

- PMIC EINT (`headset-use-ap-eint=0`), EINT0, trigger mode 1;
- `accdet-mic-mode=1`, MIC_BIAS_1 VREF code 7 (the driver documents this range
  as ≤2.7 V);
- 3-key mode; thresholds 0/80/220/400 and CDD thresholds 0/121/192/600;
- button mapping: middle=`KEY_PLAYPAUSE`, up=`KEY_VOLUMEUP`,
  down=`KEY_VOLUMEDOWN`;
- plug-in reports headphone first, then 4-pole headset when microphone contact
  state is established; unplug clears all jack/button state.

Playback uses MT6369 `HPL/HPR`. Headset microphone capture uses AIN1/PGA_L/
ADC_L. The codec also supports impedance measurement/calibration through the
MT6369 AUXADC and HP offset calibration channel.

## FM antenna switch

GQ5012BF1 adds `gpio-accdet-fm-switch` = GPIO 195. Probe requests it low;
ACCDET work drives it high on plug-in and low on unplug. This is direct static
proof that the wired headset cable is switched into the FM antenna path.

## USB-C audio

Digital USB Audio Class devices are supported by Android policy/HAL. Passive
USB-C analog audio is **not fitted/configured**: the Nothing donor's HL5280
analog switch is disabled in stock, no HL5280/FSA4480-type node or module is
present, and no analog USB-C route reaches MT6369. The MT6375 TCPC can detect a
Type-C audio accessory electrically, but detection alone is not an analog audio
signal path.
