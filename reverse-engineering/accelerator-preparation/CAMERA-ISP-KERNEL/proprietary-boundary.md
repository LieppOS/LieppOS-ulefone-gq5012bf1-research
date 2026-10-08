# Proprietary boundary — CAMERA-ISP-KERNEL

CAMERA-HAL-ISP stays PARTIAL for proprietary CameraProvider/HAL, 3A, tuning, calibration interpretation and CCU/ISP firmware algorithms. The child owns the explicit 19-module ledger only. Keep all parent historical evidence and source material where it is; its references become historical/cross-links, not a second primary owner. CAMERA-EEPROMS/VCMS/OIS/flash/LDO and closed sensor TUs are dependencies, never restarted.

[firmware metadata](firmware-boundaries.tsv) records paths, sizes and hashes only. Its historical coverage-loader labels are not loader implementation proofs; trace each real source/stock host loader separately. A signed scatter image is not necessarily loaded by Linux `request_firmware`. Code/data in remote images, secure-world functions, model/3A/tuning/PQ algorithms, per-unit calibration and signing keys are outside kernel-source parity.

No proprietary `.ko`, `.bin`, `.img`, calibration, Android HAL/library payload or raw dump enters this preparation tree or Git. Reuse private local artifacts by exact path/hash.

Existing camera reports prove measured function/data axes, not a complete full-module acceptance packet for every owned target. No new camera parity is claimed here. On-device streaming, tuning/quality and firmware algorithms remain outside static DONE.
