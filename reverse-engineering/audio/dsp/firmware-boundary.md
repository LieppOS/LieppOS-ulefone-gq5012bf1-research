# Proprietary DSP/algorithm boundary

The Linux transport is source-closed; these payloads are not:

1. **ADSP/SCP executable firmware.** The extracted vendor filesystem contains
   only a 32-byte zero `remoteproc_scp` placeholder; the executable payload is
   delivered outside the normal vendor filesystem (dedicated boot/firmware
   storage). No DSP algorithm source is present.
2. **Modem speech firmware.** Cellular speech, normal-call DMNR and modem-side
   processing execute across the MD1 PCM link. Linux exposes transport/routing,
   not modem algorithms.
3. **MediaTek Aurisys/speech libraries.** `libMtkSpeechEnh.so`,
   `libMtkSpeechEnh_swb.so`, primary-HAL Aurisys code and calibration parameter
   sets are proprietary ELF/data.
4. **Awinic protection/acoustic algorithms and tuning.** Kernel control is
   reconstructed, but SKTune, ACF, parameter bins and per-unit impedance data
   remain proprietary/product-specific.

Known configured processing:

- normal handset two-mic DMNR: enabled;
- hands-free call DMNR: disabled;
- VoIP normal/hands-free DMNR options: disabled;
- Android `voice_communication`: MediaTek AEC + NS + AGC effects;
- BesLoudness: enabled and run in HAL;
- VOW: enabled, single microphone, maximum two PDK models;
- speaker protection: AW88394 profile/monitor path plus Awinic parameters.

A faithful ROM can reuse these stock binary/data interfaces. Reimplementing the
algorithm internals is not an offline kernel reverse-engineering task.
