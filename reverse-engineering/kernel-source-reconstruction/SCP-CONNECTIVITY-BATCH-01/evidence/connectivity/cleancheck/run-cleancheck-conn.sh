#!/bin/bash
set -euo pipefail
test -z "$(ls -A "/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_connectivity_ulefone_gq5012bf1")" && test -z "$(ls -A /home/armol/kernel-work/codex-conn-batch-01/conn-dev)" && echo "dev checkout and dev workspace hidden (uid $(id -u))"
export TMPDIR=/tmp LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror LIEPPOS_CONN_MIRROR=/home/armol/kernel-work/codex-conn-batch-01/mirror LIEPPOS_NATIVE_MIRROR=/home/armol/kernel-work/platform-batch-03-native-inputs JOBS=32
bash /tmp/codex-conn-cleancheck-entry.sh /home/armol/kernel-work/codex-conn-batch-01/bundle/connectivity-d0b9e10fbb3bb4810de79fda190a4216cec65b00.bundle d0b9e10fbb3bb4810de79fda190a4216cec65b00 /home/armol/kernel-work/codex-conn-batch-01/cleancheck-conn /home/armol/kernel-work/codex-conn-batch-01/stock-conn
