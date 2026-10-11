# TCPC class — all eight instruction mismatches resolved, strict ELF still C

## Operands and method

Stock is the SHA-verified `tcpc_class.ko` identity in the frozen 458-module audit. Rebuilt operands are preserved for baseline/E1/E2/E3/E4 and four independent bundle-clone builds. Addresses below are section-relative `.text` addresses, not runtime load addresses. Every original mismatching body has stock/source sizes, SHA256, complete disassembly, relative instruction diff and all function-relative relocation records in `evidence/tcpc-{baseline,E1,E2,E3,E4}/`.

Disassembler correction: LLVM symbol-only selection can stop at embedded `$d/$x` mapping symbols and emit unrelated section relocations. The maintained tool disassembles whole sections and extracts each complete declared function range, including jump tables and later code islands. Early partial views were replaced; raw whole-function byte ledgers always remain authoritative. Branch operands, metadata and relocations are not normalized for acceptance.

## Function-by-function reconstruction

| Function | Stock address / bytes | Baseline bytes | Final address / bytes | Stock-observed source correction | First exact stage |
|---|---|---:|---|---|---|
| `tcpc_store_property` | `0x1050` / 656 | 676 | `0x1050` / 656 | Error path uses existing `dev_err`, not the extra notice logger; parsing/error return retained | E1 |
| `pd_handle_event` | `0x158d0` / 568 | 636 | `0x158d0` / 568 | Remove fork-only `pd_usb_connected` object/writes; retain original exit-action guard and dispatch | E1 |
| `tcpc_typec_handle_cc_change` | `0x1444` / 1280 | 1312 | `0x1444` / 1280 | Remove Rp logger; one attach-wait state selection; omit extra early Rp advertisement; debounce before direct-charge reset | E2 |
| `tcpci_alert` | `0xba78` / 1936 | 1948 | `0xba78` / 1936 | Remove extra cached BIST filtering from alert stage; preserve hard-reset exclusion, rate limiting and event ordering | E2 |
| `pd_put_pd_msg_event` | `0x11cf0` / 812 | 808 | `0x11cf0` / 812 | Earlier ALPS BIST early drop/SOP-only CRC-discard lineage; stock event-stage Ping drop; no extra TX_DISCARD event in this path | E2 |
| `pd_process_protocol_error` | `0x15b88` / 332 | 388 | `0x15b88` / 332 | Remove two fork-only transition Ping suppression blocks; matches preserved earlier 702/709 experiment | E1 |
| `pd_process_event_com` | `0x1e208` / 1836 | 1844 | `0x1e208` / 1836 | No `pd_notify_pe_reset_protocol` notification on `PD_CTRL_NOT_SUPPORTED`; cancellation/result/timer handling retained | E2 |
| `pd_dpm_snk_standby_power` | `0x173ec` / 280 | 272 | `0x173ec` / 280 | Stock unchanged-request and old-current guards, 2.5-W/current clamp, UP/DOWN/STANDBY selection; VCONN/PPS guards retained | E3 |

The E1 exit-action-register speculation was disproven: `w22` is the **new** state, not the old state. No guard change was made. Source corrections are selected-stock reconstructions, not an assertion of equivalence between differing public PD algorithms or proof of OEM original source spelling. No phone, physical PD negotiation, role switching, voltage/current modification or deployment occurred.

## Data/timer closure

E3 matched all 709 function bodies and positions, but still had three real runtime timer initializer differences. They were **not dismissed as metadata**. E4 recovers:

| Timer | Baseline µs | Stock/final µs |
|---|---:|---:|
| BIST continuous mode, index 1 | 36,000 | 60,000 |
| Sender response, index 7 | 27,000 | 24,000 |
| Custom VDM response, index 29 | 550,000 | 450,000 |

Indices were verified against the actual preprocessed timer enum. All 54 compiled timer entries now match stock. The original textual timeout-range spelling is unknown; the reconstructed selected-stock scalar values are explicit. All 113 non-srcversion STT_OBJECT bodies and positions match; the 114th object is generated `__UNIQUE_ID_srcversion336`.

## Remaining exact ELF differences

Final section layout, code, ordinary initialized/BSS objects, imported/exported CRCs, export licenses and KCFI IDs match. Whole ELF acceptance still rejects:

- Natural srcversion: stock `2909B7703B5C133511935DD`, rebuilt `4D57E32A74284A7BDBD3C58`.
- Six compiler-generated FORTIFY field/location strings have different source line numbers. All other referenced string literals match.
- 1,778 raw relocation/addend residues target the changed string pool: 1,766 resolve to identical literals; 12 reference the six changed diagnostic strings. No unclassified relocation residue in the final diagnostic target-resolution pass.
- 37 of 60 BUG entries differ only in source-line fields; instruction/file displacement and flags do not change. These are preserved, not rewritten.
- 18 mapping-symbol entries move with string pooling; raw `.symtab` differences remain.
- Both operands lack `.BTF` and `.BTF.ext`; there is no split-BTF exemption or fabricated BTF acceptance.

See `evidence/metadata/tcpc-class-residue.json` and the complete per-section, raw/semantic relocation, symbol, ABI and raw-difference ledgers. Diagnostic resolution is **not normalization or certification**. All unchanged strict verifier results remain rejection; Category B equivalence has not been asserted to waive provenance/diagnostic residue.
