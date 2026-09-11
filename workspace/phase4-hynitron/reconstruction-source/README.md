# Hynitron GQ5012BF1 clean-room reconstruction

Final module basename: `hynitron.ko`. Build from the exact CI-12901745 GKI
workspace with:

```sh
./tools/bazel build //lieppos/hynitron-recon:hynitron_recon
```

The public AYN/LineageOS Hynitron tree was used only as a structural donor;
hardware behavior, ABI, DT, images and Ulefone exports were reconstructed from
the frozen stock ELF. `stock-yft-devinfo.symvers` is an exact witness derived
from the real stock provider and is required because the historical
`yft_touchpanel_device_add` CRC is not naturally reproducible from the separate
provider reconstruction.

Firmware programming is disabled by default with
`HYNITRON_ALLOW_FW_PROGRAMMING=0`. The stock ELF contains no reachable flash
programmer, so an opt-in build returns `-ENOSYS` rather than importing a donor
algorithm. Exact images are retained and verified.

Authoritative evidence: `kernel/phase4-hynitron-reconstruction.md`.
