# MTK-VCODEC-KERNEL — reconstruction report

**Result: all five owned modules reconstructed from unmodified public MediaTek ALPS source and
proven identical to the shipped stock binaries except each module's 20-byte GNU build-ID.**

Device: Ulefone Armor 29 Pro Thermal (`GQ5012BF1`, MT6878T), stock kernel
`6.1.115-android14-11-g945dff7bc1bf`.

## 1. Per-module parity

| Module | Functions exact | Data exact | Imports / exports | CRC / KCFI | Relocations | Residual |
|---|---|---|---|---|---|---|
| `mtk-vcodec-common.ko` | 59/59 byte-identical | 48/48 byte-identical | 92 / 61 identical | all import+export CRCs identical; 1 absolute KCFI id identical | 2 373 raw **and** semantic identical | 20-byte GNU build ID |
| `mtk-vcodec-dec-v1.ko` | 199/199 byte-identical | 165/165 byte-identical | 254 / 0 identical | all import CRCs identical; 20 absolute KCFI ids identical | 9 866 raw **and** semantic identical | 20-byte GNU build ID |
| `mtk-vcodec-enc-v1.ko` | 178/178 byte-identical | 136/136 byte-identical | 230 / 0 identical | all import CRCs identical; 22 absolute KCFI ids identical | 9 165 raw **and** semantic identical | 20-byte GNU build ID |
| `mtk-vcu.ko` | 52/52 byte-identical | 68/68 byte-identical | 100 / 14 identical | all import+export CRCs identical; 1 absolute KCFI id identical | 2 443 raw **and** semantic identical | 20-byte GNU build ID |
| `clk-mt6878-vcodec.ko` | 3/3 byte-identical | 19/19 byte-identical | 7 / 0 identical | all import CRCs identical; no absolute KCFI id | 64 raw **and** semantic identical | 20-byte GNU build ID |

Function and data counts come from the ELF symbol tables of the stock binaries, keyed by
(section, offset, name, size) so same-named static symbols are never conflated. `.text` KCFI
type words sit inside the compared function bytes; the counts above are the *additional*
absolute `__kcfi_typeid_*` symbols, which also match.

Whole-file result per module (`verify.py`): `raw_differing_bytes = 20`, all inside the
`.note.gnu.build-id` descriptor; every other byte of every section, including `.modinfo`,
`__versions`, `__ksymtab*`, `__kcrctab*`, `.rela*`, `.symtab` and `.strtab`, is identical.

Difference classification: **BYTE_EXACT** for every function, data object, section, relocation,
CRC, KCFI id and `.modinfo` key. **BUILD_METADATA_ONLY** for the five GNU build-ID
descriptors. **UNRESOLVED: none.** No instruction or datum was spliced, patched or stamped.

Ledgers: [function-parity.tsv](function-parity.tsv), [data-parity.tsv](data-parity.tsv),
[abi-parity.md](abi-parity.md), `evidence/reconstruction/acceptance/`.

## 2. Source

Single donor: public ALPS release `5e415e059253ce0d2e61c97108e5f5785d71f06f`
(`NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878`), base tree
`9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c`.

**No C file and no header is modified.** Two build-only patches add seven `Kbuild` scope
wrappers (three for the owned modules, four for the provider ABI witness scope); each wrapper
includes the unchanged vendor `Makefile` and only restricts `obj-m`. Patch count: **2**
(0 functional patches). Details in [SOURCE.md](SOURCE.md).

The earlier Nothing-ROM donor (`957dac18`) is *not* the stock source: its
`mtk_vcodec_dec_drv.c`, `mtk_vcodec_drv.h`, `mtk_vcodec_enc.c`, `mtk_vcodec_enc_drv.c`,
`mtk_vcodec_util.c`, `vdec/vdec_vcp_if.c` and `venc/venc_vcp_if.c` differ from the shipped
binaries (measured: 37 differing functions, extra/missing log strings and mutexes in
`mtk-vcodec-common`, size-differing functions in the encoder). It is retained only as vendor
Kconfig/defconfig input. This is recorded in [stale-claims.md](stale-claims.md).

## 3. External ABI

60 external exports consumed by the five modules are **not** in GKI and **not** owned here.
Their modversion CRCs were regenerated naturally by genksyms from the same public source
(`scripts/derive-provider-crcs.sh`) and all 60 equal the CRCs the stock modules record in
`__versions`. No symvers file was copied from a stock binary into the build.
Providers: `vcp`, `vcp_status`, `mtk_tinysys_ipi`, `mtk-cmdq-drv-ext`, `mtk-smi`,
`mtk-smi-dbg`, `mtk_slbc`, `iommu_debug`, `mtk-icc-core`, `mtk-mmdvfs-v3`, `emi`,
`system_heap`, `scheduler`, `clk-common`. 242 further imports resolve against the verified
GKI `vmlinux.symvers` of build 12901745. See
[evidence/reconstruction/build/provider-crc-witnesses.tsv](evidence/reconstruction/build/provider-crc-witnesses.tsv).

## 4. Reproducibility

Independent clean checkout of the maintained repository, bootstrapped only from pinned
immutable inputs, then two from-scratch builds:

* B1 == B2 for the raw modules, the stripped modules, **every** target `.o` (including
  composite and generated `.mod.o`), the target and provider symvers, the kernel output
  `.config` and both source tree ids.
* Each rebuilt module then matched its stock counterpart on all axes above.

Transcript: [evidence/reconstruction/build/b1b2-clean-checkout.log](evidence/reconstruction/build/b1b2-clean-checkout.log).
Procedure: [build-reproduction.md](build-reproduction.md).

## 5. Hardware, firmware and userspace

See [hardware-contract.md](hardware-contract.md), [firmware-boundary.md](firmware-boundary.md)
and [source-to-userspace-contract.md](source-to-userspace-contract.md). Those documents keep
PROVEN HARDWARE / STOCK BINARY IMPLEMENTATION / CONFIGURED BUT UNVERIFIED / UPSTREAM
REFERENCE ONLY / UNKNOWN strictly separated.

## 6. What this does not establish

Nothing here was executed on the phone. No probe, decode, encode, firmware handshake,
interrupt, DVFS transition or recovery path was observed. Advertised Codec2/XML capability is
a static declaration, not proof of hardware execution. VCP firmware remains proprietary and
unmodified. Runtime work still required is enumerated in
[source-to-userspace-contract.md](source-to-userspace-contract.md).
