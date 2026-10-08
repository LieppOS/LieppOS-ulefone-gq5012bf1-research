# Kernel/userspace ABI — CAMERA-ISP-KERNEL

The previous preparation note is superseded by the completed contracts:

* [abi-parity.md](abi-parity.md) — exact kernel module/KMI, CRC, KCFI and modinfo parity;
* [source-to-userspace-contract.md](source-to-userspace-contract.md) — media/V4L2,
  character-device, remoteproc/RPMsg, buffer and private-ioctl boundary;
* [hardware-contract.md](hardware-contract.md) — board DT resources and compatible match;
* [firmware-boundary.md](firmware-boundary.md) — retained CCU/ISP firmware and HAL scope.

Machine proof is in `evidence/reconstruction/acceptance/abi-parity.tsv`: all 2 530 rows are
identical. Source API witnesses remain in [abi-source-witnesses.tsv](abi-source-witnesses.tsv).

Numerical ABI equivalence does not prove live device-node numbering, successful probe or
userspace use; those require the on-device acceptance plan.
