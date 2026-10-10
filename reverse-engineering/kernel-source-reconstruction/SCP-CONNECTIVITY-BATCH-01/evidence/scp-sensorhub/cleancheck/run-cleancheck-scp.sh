#!/bin/bash
set -euo pipefail
test -z "$(ls -A "/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_scp_sensorhub_ulefone_gq5012bf1")" && test -z "$(ls -A /home/armol/kernel-work/codex-conn-batch-01/scp-dev)" && echo "dev checkout and dev workspace hidden (uid $(id -u))"
export TMPDIR=/tmp LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror JOBS=24
bash /tmp/codex-scp-cleancheck-entry.sh /home/armol/kernel-work/codex-conn-batch-01/bundle/scp-sensorhub-26507aa653a09f907329795b6c31c6ec1bd694dd.bundle 26507aa653a09f907329795b6c31c6ec1bd694dd /home/armol/kernel-work/codex-conn-batch-01/cleancheck-scp /home/armol/kernel-work/codex-conn-batch-01/stock-scp
