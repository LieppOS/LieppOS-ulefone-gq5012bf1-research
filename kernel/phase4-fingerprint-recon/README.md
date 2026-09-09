# GQ5012BF1 YFT fingerprint glue reconstruction

This is the tracked copy of the source built at:

```text
/home/armol/kernel-work/gki-12901745-workspace/lieppos/fingerprint-recon
```

Target: `//common:kernel_aarch64`, Linux `6.1.115-android14-11`, Android CI
`ab/12901745`, common commit `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`.

Build from the exact workspace:

```sh
tools/bazel build //lieppos/fingerprint-recon:fingerprint_recon
```

Output:

```text
bazel-bin/lieppos/fingerprint-recon/fingerprint_recon/fingerprint.ko
```

The source is stock-oracle-led; no public donor was found. Do not alter the
misspelled public export `yft_waite_for_finger_dts_paser`. Static verification:

```sh
python3 kernel/scripts/phase4_fingerprint_verify_recon.py
```

See `kernel/phase4-fingerprint-reconstruction.md` for the authoritative result.
