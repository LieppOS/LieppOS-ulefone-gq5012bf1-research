# ABI parity — CAMERA-ISP-KERNEL

**Result: PASS for all nineteen reconstructed modules.**

The accepted builds retain exactly the stock module ABI:

| axis | identical rows |
|---|---:|
| imported symbol + modversion CRC | 1 792 |
| exported symbol + export namespace/bucket + CRC | 204 |
| absolute KCFI type id | 218 |
| `.modinfo` key/value record | 316 |
| **total** | **2 530** |

The complete machine ledger is
[`evidence/reconstruction/acceptance/abi-parity.tsv`](evidence/reconstruction/acceptance/abi-parity.tsv);
every row is `IDENTICAL`. Symbol names, values/sizes, ordering, `__versions`,
`__ksymtab*`, `__kcrctab*`, `__ksymtab_strings`, `.kcfi_traps`, aliases, licence,
parameters, `depends=`, `srcversion` and stock
`6.1.115-android14-11-g945dff7bc1bf` vermagic are also covered by the section and
symbol comparisons.

## External provider CRCs

The modules have 1 792 import occurrences: 1 547 GKI/core, 78 owned-module and 167
external-vendor occurrences (552, 76 and 105 distinct symbols respectively). The provider
build ledger has 107 distinct symbols: those 105 external symbols plus
`mtk_ccu_ipc_register` and `mtk_ccu_rproc_ipc_send`, owned CCU exports included with
historical provider identities for package-scoped modpost.

* **97/107 vendor CRCs are naturally regenerated** from public NothingOSS provider
  source under the same GKI/toolchain/config. Each is recorded in
  `evidence/reconstruction/build/provider-crc-witnesses.tsv` with the provider `.cmd`
  witness that generated it.
* **10/107 are `STOCK_PROVIDER_EXPORT`**: three CMDQ-sec exports have a public-source ABI
  divergence, and seven are OEM-provider ABI boundaries. Their CRC comes from the stock
  *provider's* `__kcrctab`, not from
  the camera consumer and not from a guessed prototype. This is an explicit retained
  external binary-ABI boundary.
* The merged input used by modpost is
  `evidence/reconstruction/build/external-provider.symvers`.

No CRC was rewritten in an ELF, no forced `__crc_*` constant is accepted as source/type
proof, and no unresolved modpost warning was ignored.

## Internal dependency nuance

Stock `.modinfo` can name historical providers (`mtk_ccu`, `mtk_ccu_mssv`) even though
the 457-module device inventory contains neither filename. The actual exported symbols
and matching CRCs are provided by `mtk_ccuv.ko`; the build preserves the stock dependency
string where required rather than inventing modules. Dependency names and symbol-provider
identity are distinct evidence axes.

## KCFI

All 218 absolute `__kcfi_typeid_*` values are equal. Function entry bytes, relocation
targets/addends and `.kcfi_traps` are covered separately by the function, relocation and
section ledgers. Therefore the result is stronger than matching symbol names or modversion
CRCs alone.
