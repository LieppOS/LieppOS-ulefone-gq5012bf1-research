#!/bin/bash
set -euo pipefail
test -z "$(ls -A "/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_audio_ulefone_gq5012bf1")" && test -z "$(ls -A /home/armol/kernel-work/codex-audio-batch-01/dev)" && echo "dev checkout and dev workspace hidden (uid $(id -u))"
export TMPDIR=/tmp LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror LIEPPOS_AUDIO_MIRROR=/home/armol/kernel-work/codex-audio-batch-01/mirror JOBS=24
bash /tmp/codex-cleancheck-entry.sh /home/armol/kernel-work/codex-audio-batch-01/bundle/audio-ec57573ca9f48c92b8485137064840025525f23f.bundle ec57573ca9f48c92b8485137064840025525f23f /home/armol/kernel-work/codex-audio-batch-01/cleancheck /home/armol/kernel-work/codex-audio-batch-01/stock
