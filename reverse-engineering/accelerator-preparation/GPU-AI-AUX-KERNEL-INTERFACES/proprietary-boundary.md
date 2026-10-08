# Proprietary boundary — GPU-AI-AUX-KERNEL-INTERFACES

MTK-MBOX, MTK-RPMSG-MBOX and MTK-TINYSYS-IPI remain DONE for their exact transport modules. SENSOR-HUB-KERNEL keeps scp/hf_manager/sensorhub; AUDIO-DSP-KERNEL keeps adsp/audio host modules. CCU belongs to CAMERA-ISP-KERNEL and APUSYS to APUSYS-NPU-KERNEL. Firmware algorithms, signing, secure-boot loader internals and per-channel remote implementations are excluded.

[firmware metadata](firmware-boundaries.tsv) records paths, sizes and hashes only. Its historical coverage-loader labels are not loader implementation proofs; trace each real source/stock host loader separately. A signed scatter image is not necessarily loaded by Linux `request_firmware`. Code/data in remote images, secure-world functions, model/3A/tuning/PQ algorithms, per-unit calibration and signing keys are outside kernel-source parity.

No proprietary `.ko`, `.bin`, `.img`, calibration, Android HAL/library payload or raw dump enters this preparation tree or Git. Reuse private local artifacts by exact path/hash.

GPUEB/VCP target rebuild parity is not yet measured. Secure firmware internals, runtime message timing and remote algorithm behavior cannot be settled by this static preparation. MCUPM/SSPM client parity is UNKNOWN outside the owned GPU/video targets, not falsely counted as DONE.
