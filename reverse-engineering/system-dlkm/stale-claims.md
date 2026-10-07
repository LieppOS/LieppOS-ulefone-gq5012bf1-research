# SYSTEM-DLKM — stale claims (2026-10-07)

| # | claim | verdict | correction |
|---|---|---|---|
| 1 | "Still required: complete source/artifact parity" | **RESOLVED** | 60/60 modules are byte-identical to stock bodies (build-id included) from the stamped GKI 12901745 build; only the signature differs. |
| 2 | (implicit) the workspace GKI build reproduces stock modules | **WRONG until fixed** | The unstamped build gave `-maybe-dirty` vermagic, no `intree`/`scmversion`, and no `.llvm_addrsig` (host clang default). Stamping plus `-faddrsig` was needed. |
| 3 | "integration test" as a blocker | **RECLASSIFIED** | The stock-signed modules are code-identical. Shipping and signature policy are integration. |
