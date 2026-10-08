# Proprietary boundary — MTK-VCODEC-KERNEL

VCP host/status modules belong to the auxiliary component; VCP firmware algorithms and Codec2/vendor codec implementations are proprietary. Shared CMDQ/IOMMU/SMI/power providers are not duplicated. Existing generic source triage was not module-level source/parity closure.

[firmware metadata](firmware-boundaries.tsv) records paths, sizes and hashes only. Its historical coverage-loader labels are not loader implementation proofs; trace each real source/stock host loader separately. A signed scatter image is not necessarily loaded by Linux `request_firmware`. Code/data in remote images, secure-world functions, model/3A/tuning/PQ algorithms, per-unit calibration and signing keys are outside kernel-source parity.

No proprietary `.ko`, `.bin`, `.img`, calibration, Android HAL/library payload or raw dump enters this preparation tree or Git. Reuse private local artifacts by exact path/hash.

Unchanged-donor binary equivalence and actually functioning exposed codecs are UNKNOWN. XML/config/source capabilities are static declarations only; runtime encode/decode and signed firmware internals are excluded.
