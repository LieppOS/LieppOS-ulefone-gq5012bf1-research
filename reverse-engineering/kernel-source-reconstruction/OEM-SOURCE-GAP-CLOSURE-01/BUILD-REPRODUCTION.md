# Build reproduction (tmem_ffa)

- **Development:** private clone of the Codex bundle (`55616a25…`, verified), with an experiment commit.
  - Offline bootstrap: GKI/KDM/ALPS/clang/tkcore-public pins all verified.
  - Dev build X1: provider errors `[]`, 9/9 strict PASS.
  - The dev workspace is quarantined at `/home/armol/kernel-work/oem-gap-01/quarantined-dev-ws`.
- **Proof:** fork bundle `bundles/trustkernel-abi.bundle` (sha256
  `d2614b1eb5c3fc0e722ab3ff325f7244b56b20cd6519ed49eb96923d5accd0c7`, commit `15e7e8d8d4f9cbf56982791b2fac0e54087d0f49`), using
  `scripts/prove-tmem_ffa.sh`.
  - B1, then B2, run sequentially, each from a fresh `--no-hardlinks` clone with no alternates and a passing
    `fsck --full`.
  - Each run: offline bootstrap, then `build-reproducible.sh`, which requires provider errors `[]` and bulk
    exit 0.
  - Each run then applies the unchanged `verify.py` to private read-only stock copies (sha256 verified) and runs
    `mutation-test.py`.

| | B1 | B2 |
|---|---|---|
| HEAD / tree | `15e7e8d8…` / `1d133097…` | same |
| build / verify / mutation exit | 0 / 0 / 0 | 0 / 0 / 0 |
| strict GNU20-only | 9/9 PASS (tmem_ffa PASS) | 9/9 PASS |
| ELF mutation controls | 124/124 (14 tmem_ffa) | 124/124 |
| outputs (`.ko` + stripped) | 18 | identical |
| intermediates (`.o`) | 57 | identical |
| vendor `.config`, joint-extra.symvers, provider errors | — | identical |

`tmem_ffa`: 151,456 B, 141/141 functions, 60 data objects, 77 imports, 15 exports, 4 KCFI IDs. The only raw
difference is the 20-byte GNU build ID at offset 68432. B1 and B2 have the same normalized hash, `84857055…`.
