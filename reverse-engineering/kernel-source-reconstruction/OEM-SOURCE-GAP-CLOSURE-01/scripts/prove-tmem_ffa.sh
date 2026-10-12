#!/bin/bash
set -euo pipefail
E=/home/armol/kernel-work/oem-gap-01; X=$1; C=$(cat $E/proof/COMMIT); D=$E/proof/$X
rm -rf $D; mkdir -p $D
export JOBS=4 GIT_NO_LAZY_FETCH=1 GIT_ALLOW_PROTOCOL=file PYTHONDONTWRITEBYTECODE=1 LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/g-source-recovery-batch-01/pin-mirror
git clone -q --no-hardlinks $E/proof/trustkernel-abi.bundle $D/repo; cd $D/repo; git checkout -q --detach $C
test ! -e .git/objects/info/alternates; git fsck --full > $D/fsck.log 2>&1; echo "$(git rev-parse HEAD) $(git rev-parse HEAD^{tree})" > $D/HEAD
nice -n 10 taskset -c 0-3 bash scripts/bootstrap.sh $D/ws > $D/bootstrap.log 2>&1
set +e; nice -n 10 taskset -c 0-3 bash scripts/build-reproducible.sh $D/ws $X > $D/build.log 2>&1; echo $? > $D/build-exit; set -e
O=$D/ws/out/$X
python3 scripts/verify.py $O $E/stock-flat $D/acceptance > $D/verify.log 2>&1; echo $? > $D/verify-exit
python3 scripts/mutation-test.py $O $E/stock-flat > $D/mutation.log 2>&1; echo $? > $D/mutation-exit
(cd $O && sha256sum *.ko *.stripped 2>/dev/null) > $D/OUTPUT-SHA256SUMS
(cd $D/ws/src && find . -name '*.o' -print0 | sort -z | xargs -0 sha256sum) > $D/INTERMEDIATE-SHA256SUMS
cp $O/provider-boundary-errors.json $O/joint-extra.symvers $D/ 2>/dev/null || true
sha256sum $D/ws/kout/.config | cut -d' ' -f1 > $D/CONFIG-SHA256
echo done > $D/DONE
