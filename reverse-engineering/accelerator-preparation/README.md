# GQ5012BF1 hardware accelerator RE preparation

Authoritative metadata, ownership and executable Claude plans for the captured MT6878 stock build. Entry point: [master roadmap](../accelerator-re-roadmap.md).

## Six scopes

- [MALI-GPU-KERNEL](MALI-GPU-KERNEL/CLAUDE-HANDOFF.md) — eight KMD/platform modules.
- [APUSYS-NPU-KERNEL](APUSYS-NPU-KERNEL/CLAUDE-HANDOFF.md) — two monolithic APU/power modules, not invented MDLA/MVPU binaries.
- [CAMERA-ISP-KERNEL](CAMERA-ISP-KERNEL/CLAUDE-HANDOFF.md) — nineteen exact kernel modules; preserve sixteen existing function/data proof pairs and closed sensor TUs.
- [MTK-VCODEC-KERNEL](MTK-VCODEC-KERNEL/CLAUDE-HANDOFF.md) — common/decoder/encoder/VCU and dedicated clocks.
- [MTK-MDP-KERNEL](MTK-MDP-KERNEL/CLAUDE-HANDOFF.md) — actual mdp_drv/MML/platform-MML and dedicated clocks.
- [GPU-AI-AUX-KERNEL-INTERFACES](GPU-AI-AUX-KERNEL-INTERFACES/CLAUDE-HANDOFF.md) — three GPUEB/VCP/status host targets; existing SCP/ADSP and messaging providers remain DONE.

All six registrations are justified by exact unclosed normal-world kernel work, not by library existence or a generic-source classification. None existed in any status tree at discovery HEAD `3bb6db32de2c5f312be31265482a7f8539145b62`. New components remain PARTIAL. Camera HAL stays PARTIAL; its existing source/evidence and history are preserved in place and cross-linked. No unrelated merge/removal/rename or reconstruction is authorized here.

## Reproducible evidence

`scopes.json` is the explicit scoped target/decision list. `inventory.py` derives hashes/sizes, actual ELF function/data/import/export metadata, load order, direct vs transitive dependency labels, existing proof citations, DT properties/provider references and codec XML declarations. `contracts.py` extracts file/line/hash donor interface witnesses (not stock equivalence). `write-plans.py` renders scoped docs and the roadmap. These scripts never build or exercise hardware.

```sh
python3 reverse-engineering/accelerator-preparation/inventory.py
python3 reverse-engineering/accelerator-preparation/contracts.py
python3 reverse-engineering/accelerator-preparation/write-plans.py
python3 reverse-engineering/accelerator-preparation/validate.py
```

[Module transfer ledger](ownership-changes.tsv), [DT transfer ledger](dt-ownership.tsv), [source candidates](source-candidates.tsv), [import/provider graph](dependency-edges.tsv), [complete parity standard](PARITY-STANDARD.md). Every dependency mention is a cross-reference, not a second primary owner. Generic `syscon` compatibles shared by different blocks remain generic; node-specific accelerator compatibles have one scope.

## Limits

No new function/data parity, hardware inference/graphics/video execution, runtime probe, firmware algorithm or reconstruction is claimed. Missing behavior is UNKNOWN. Firmware tables contain metadata only; exact private stock operands stay at their existing paths. Loader labels from the historical firmware inventory are evidence to reconcile, not proof that Linux loads every signed scatter image. Signed firmware, userspace algorithms, secure-world internals, keys and calibration are outside kernel-source parity.

Offline static preparation only: no adb, hardware commands, driver loads, reboot, flash, partition or firmware/calibration writes. Preserve the stock Slot-B anchor and all concurrent/shared source work.
