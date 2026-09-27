# New finding - two built-in analog microphones and MT6369 capture route

**Previous claim:** two microphones were suggested by generic product
configuration, but the active AMIC/DMIC project and ADC/lane map were unresolved.

**Current claim:** the fitted configuration has **two built-in AMICs**. The main
role is labelled `bottom` and maps to MT6369 AIN0/PGA_L/ADC_L/UL1_CH1; the sub
role is labelled `back` and maps to AIN2/PGA_R/ADC_R/UL1_CH2. A wired-headset
mic is a separate accessory input. No third built-in mic or separate microphone
IC is proven.

## Evidence

1. Live DT at `second_pmic@5/mt6369codec` contains:

   ```text
   mediatek,mic-type = <1 1 1>
   mediatek,dmic-mode = <0>
   mediatek,bypass-vant18 = <1>
   ```

2. Static analysis of `audio.primary.mediatek.so` shows the MicInfo selection
   branch reading `/proc/device-tree/.../mic-type`; type `1` selects
   `SPH1642HT5H_REV_B` and type `0` selects digital project
   `SPK0641HT4H_1_Rev_A`.
3. `MicInfo_AudioParam.xml` describes the selected analog project as two records:
   main `bottom`, sub `back`, both `AMIC`.
4. `mixer_paths.xml` route `builtin_Mic_DualMic` sets ADC1/AIN0/PGA_L and
   ADC3/AIN2/PGA_R, then `MISO0_MUX=UL1_CH1` and
   `MISO1_MUX=UL1_CH2`. `builtin_Mic_BackMic` selects only UL1_CH2. Codec
   disassembly and register definitions identify `MIC_BIAS_0` at 1.9 V for the
   built-in analog route.
5. `UplinkConfiguration_AudioParam.xml` requests two microphones for Default,
   VoIP, Recognition, Camcorder, MIC, Fast Record, Unprocessed and Voice
   Performance. VoIP additionally requests echo reference.
6. The MT6369 codec, MT6878 AFE and machine modules expose the matching internal
   mic-bias/PGA/ADC, ADDA uplink and UL1/UL2 PCM controls. No enabled external
   microphone codec or microphone-specific I2C/SPI device was found.

## Processing and Android boundary

Stock enables dual-mic and normal-handset in-call AP-side DMNR. Hands-free and
VoIP DMNR options are disabled, although Record/Speech/VoIP DMNR calibration
families ship. Android AEC/NS/AGC effects are present;
policy pre-attaches AEC only for voice communication. The service boundary is
the MediaTek Audio HAL (`android.hardware.audio@7.1` plus AIDL
`vendor.mediatek.hardware.audio.IMtkAudio/default`). AudioPolicy exposes a
built-in input and wired-headset input, not separate public bottom/back devices.

Voice wake-up statically selects one main built-in mic and disables reference,
third-mic and SCP-DMIC sources. AP/SCP DMIC pin groups and generic `DMic`/
`ThreeMic` paths remain SoC/BSP capability only.

## Remaining limits

Static evidence does not establish microphone manufacturer, exact PCB position,
acoustic port direction, live channel polarity, or proprietary DMNR coefficient
semantics. Runtime ALSA/PCM traces and controlled acoustic tests are required.

**Final confidence:** two built-in AMICs, selected project, codec/ADC/lane route
and absence of a separate enabled mic IC = **PROVEN by converging static
artifacts**. Exact physical placement and acoustic behavior = **TEARDOWN/RUNTIME
REQUIRED**.

Primary detailed workspace:
`../../../../Reverse Engineer - PARTIAL/MICROPHONES/` after reclassification.
