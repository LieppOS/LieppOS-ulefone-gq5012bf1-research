# Proprietary boundary — APUSYS-NPU-KERNEL

All APU/MDLA/MVPU RPMsg accelerator nodes previously attributed to CAMERA-HAL-ISP move to this kernel owner. Camera AIE/FD hardware stays CAMERA-ISP-KERNEL. GenieZone trusty-sapu remains the existing secure transport. Shared generic IOMMU/QoS/SSPM providers remain dependencies. APUware/NeuroPilot/neuron/NNAPI libraries and signed apusys firmware algorithms are retained binaries, not a claim of proven model execution.

[firmware metadata](firmware-boundaries.tsv) records paths, sizes and hashes only. Its historical coverage-loader labels are not loader implementation proofs; trace each real source/stock host loader separately. A signed scatter image is not necessarily loaded by Linux `request_firmware`. Code/data in remote images, secure-world functions, model/3A/tuning/PQ algorithms, per-unit calibration and signing keys are outside kernel-source parity.

No proprietary `.ko`, `.bin`, `.img`, calibration, Android HAL/library payload or raw dump enters this preparation tree or Git. Reuse private local artifacts by exact path/hash.

Dedicated NPU model execution, actual exposed inference throughput, signed payload algorithms and secure internals are UNKNOWN. DT enablement, loaded apusys and runtime library presence are not inference-execution proof.
