# Build reproduction — MTK-VCODEC-KERNEL

Everything below was executed offline, from a **fresh clone** of
`android_kernel_modules_vcodec_ulefone_gq5012bf1`, with no file copied from any earlier
working tree.

## Procedure

```sh
git clone <maintained repo> /path/to/clean/repo
LIEPPOS_VCODEC_MIRROR=<pin mirror> /path/to/clean/repo/scripts/bootstrap.sh <ws>
/path/to/clean/repo/scripts/b1b2.sh <ws> <dir with the five stock .ko>
```

`bootstrap.sh` verifies every input before use:

```
ok common   6b18f0b574ab…  tree 710eb859513863cda0204995a411d5795ad3fe92
ok clang    (clang-r487747c) tree 8eb8e3afb00a52d48b29381d73daf352362231ad
ok kdm      957dac185efe…  tree 05f9c65d40ef9e4bdbe17397a90edd303a5da6dd
ok alps5e41 5e415e059253…  tree 9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c
ok GKI 12901745 vmlinux.symvers   (sha256 pinned)
```

Each of B1 and B2 then deletes and regenerates, in order:

1. `src/kdm` and `src/prov` from the ALPS archive + the two build-scope patches
   (tree ids asserted: `a6f90e65…`, `9303b1bb…`);
2. the vendor kernel output `kout` (gki_defconfig + mgk_64_k61_defconfig, release stamped,
   `Module.symvers` = GKI `vmlinux.symvers`), `.config` sha256 asserted
   `8f9d1d2901dfbc77062764b4f9e21bc1000097392a36f8ba1eebd9c47d35f50e`;
3. the external provider ABI, by compiling provider source and extracting genksyms
   `#SYMVER` records — `PASS: 60/60 source-derived provider CRCs equal stock consumer references`;
4. the five owned modules, rejecting any compiler diagnostic or modpost warning/error.

## Determinism

`b1b2.sh` compares B1 against B2 and requires equality of:

* `SHA256SUMS` — raw `.ko` and `--strip-debug` stripped images of all five modules, plus the
  provider and per-directory `Module.symvers`;
* `INTERMEDIATE-SHA256SUMS` — every `.o` under the three target directories, including the
  composite module objects and the generated `.mod.o`;
* `SOURCE-TREE` — both git tree ids;
* `provider-crc-witnesses.tsv` — the exact `.cmd` record each provider CRC came from;
* `config.sha256` — the regenerated kernel output configuration.

Result: **identical**, including the GNU build IDs (the build is reproducible with itself;
the build ID differs only from MediaTek's original build, whose inputs include their own
absolute paths and link-time state).

## Stock comparison

`verify.py` then asserted, per module, against the stock binary: whole-file equality after
zeroing only the `.note.gnu.build-id` descriptor, plus per-function bytes, per-data-object
bytes, section header fields and contents, raw and semantic relocations, `__versions` import
CRCs, `__crc_*` export CRCs with licence bucket, absolute KCFI type ids and `.modinfo`.

```
mtk-vcodec-common  PASS  raw_differing_bytes 20  functions 59   data 48   imports 92   exports 61  relocations 2373
mtk-vcodec-dec-v1  PASS  raw_differing_bytes 20  functions 199  data 165  imports 254  exports 0   relocations 9866
mtk-vcodec-enc-v1  PASS  raw_differing_bytes 20  functions 178  data 136  imports 230  exports 0   relocations 9165
mtk-vcu            PASS  raw_differing_bytes 20  functions 52   data 68   imports 100  exports 14  relocations 2443
clk-mt6878-vcodec  PASS  raw_differing_bytes 20  functions 3    data 19   imports 7    exports 0   relocations 64
```

Full transcript: `evidence/reconstruction/build/b1b2-clean-checkout.log`.
Hashes: `evidence/reconstruction/build/B1-SHA256SUMS.txt`, `B2-SHA256SUMS.txt`,
`B1-INTERMEDIATE-SHA256SUMS.txt`. Acceptance JSON and per-axis ledgers:
`evidence/reconstruction/acceptance/`.

## Notes and known constraints

* The workspace path must contain no spaces (kbuild limitation); the research repository
  path does, so builds run under `/home/armol/kernel-work/`.
* `make-kout.sh` demotes one host-tool diagnostic (`tools/lib/bpf` vs glibc ≥ 2.42). Host
  tools only; module output is unaffected and was verified byte-for-byte.
* The provider witness build is intentionally `-k` with `KBUILD_MODPOST_WARN=1`: it compiles
  provider source that legitimately references modules outside this scope. It is rejected if
  any *compile* error or modpost **ERROR** appears; acceptance is the 60/60 CRC equality,
  never a produced provider binary.
