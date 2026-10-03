# Future authorized runtime qualification plan

Not executed in this pass.

## Read-only baseline

1. Capture `cat /proc/asound/cards`, `/proc/asound/pcm`, `/proc/asound/devices`.
2. Capture read-only `tinymix` and `dumpsys media.audio_policy`,
   `dumpsys media.audio_flinger` before and during each normal use case.
3. Capture loaded-module list, ASoC debugfs routes (if already exposed) and
   kernel logs without changing debug levels.
4. Confirm HAL service/interface with `lshal`/service dumps.

## Headset

1. Insert/remove a known passive 4-pole headset while recording read-only input
   events and jack state.
2. Verify headphone/headset distinction and three buttons.
3. Observe GPIO/pinctrl state only if already exposed read-only; do not export or
   drive GPIO 195 manually.
4. Test a digital USB Audio Class adapter separately; do not infer passive
   USB-C analog support from digital USB success.

## Microphones

Record low-level ambient speech independently for normal recorder, rear/front
camera, voice recognition, VoIP, handset and speakerphone. Compare channel
correlation/ordering and cover one acoustic port at a time. Do not inject bias
or probe codec registers.

## Output routing

Use normal low-volume media under explicit authorization (not generated test
tones) and observe mixer/PCM state for speaker, earpiece and headset. Confirm
that speaker selects I2S_OUT4/AW88394 and receiver selects MT6369 RCV.

## Prohibited

- no `smartpa_nvtest` write/calibration mode;
- no NVRAM/persist modifications;
- no raw I2C/SPMI writes;
- no forced impedance/excursion/sine-wave calibration;
- no high-level tones or thermal/protection stress;
- no flashing/rebooting/slot changes.
