# GQ5012BF1 tkcore Phase 3E — whole static internal callgraph

Every `R_AARCH64_CALL26` relocation was assigned to its containing function, and every target resolving to an internal `STT_FUNC` was normalized to its function name. Local section-symbol-plus-addend calls were resolved rather than discarded.

| Edge set | Count |
|---|---:|
| stock internal direct edges | 103 |
| island internal direct edges | 103 |
| common edges | **103** |
| stock-only edges | **0** |
| island-only edges | **0** |

Thus there are no unexplained static direct-call differences across the full 122-function provider.

Indirect/data edges were audited separately. Phase 3E's three affinity callbacks are address-taken through the exact const operations table, but stock and island both contain no executable indirect callsite of those callback KCFI types. The already-closed `tee_clkmgr_handle` bare indirect callbacks remain covered by the Phase-3D verifier and were not changed.

This establishes provider-internal static callgraph completeness; it is not final consumer acceptance and does not establish runtime behavior.
