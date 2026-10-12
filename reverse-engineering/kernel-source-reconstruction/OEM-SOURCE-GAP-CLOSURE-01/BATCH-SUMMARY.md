# OEM-SOURCE-GAP-CLOSURE-01 — summary

| | |
|---|---|
| Baseline | canonical `4e47a5b9` (after DISPLAY-INTEGRATION-01): A420 B1 C11 D3 G23 = 421/458 |
| New certification (proposed) | **tmem_ffa C→A**, giving **A421 B1 C10 D3 G23 = 422/458 (92.1%)**, CAS scratch-validated |
| Key finding | TrustKernel 6:1.1 `struct tee_shm` has no `shm_name`; this closes the private-declaration CRC blocker (25/25 tkcore exports) |
| New authentic source | TrustKernel `4.0p0.4.19p0` (anvil-kernel 4.19 `492dbcf3`), used as a declaration bracket |
| Maintained source | `android_kernel_modules_trustkernel_abi_ulefone_gq5012bf1` @ `15e7e8d8` (fork of Codex secure_transport 00929490); bundle `d2614b1e…` |
| Independent proof | fresh B1/B2: 9/9 strict GNU20-only PASS, 124/124 mutations each, 18 outputs + 57 intermediates identical |
| Remaining uncertified | 36 after integration: 12 G owned by Codex batch-02, 11 G with no authentic source, 10 C, 3 D |

## Reports

| Document | Contents |
|---|---|
| `MISSING-SOURCE-MATRIX.tsv` | all 37 rows by gap type |
| `CATEGORY-C-CLOSURE-STATUS.md` | per-row status of the 11 C rows |
| `TRUSTKERNEL-ABI-INVESTIGATION.md` | the TrustKernel declaration finding and evidence |
| `FLASHLIGHT-SOURCE-GAP.md` | the OEM `flashlight-core.c` gap |
| `SHIPPED-OBJECT-SOURCE-GAP.md` | `fpsgo` and `msync2_frd` (`license=Proprietary`) |
| `SOURCE-RECOVERY-EXPERIMENTS.tsv` | experiments SR01–SR14 |
| `ORIGINAL-SOURCE-REQUESTS.md` | index of the request drafts (`ULEFONE-`, `TRUSTKERNEL-`, `COMPONENT-SOURCE-REQUESTS.md`), **all unsent** |
| `SOURCE-RELEASE-EVIDENCE.md` | licence and source evidence for the requests |
| `HANDOFF-TO-CODEX.md` | information for Codex batch-02 |
| `NEXT-ACTIONS.md` | next steps |
| tmem_ffa certification | `BATCH-MANIFEST.tsv`, `BATCH-PARITY.tsv`, `ABI-PROVIDERS.tsv`, `SOURCE-LINEAGE.md`, `BUILD-REPRODUCTION.md`, `AUDIT-DELTA.tsv`, `PROPOSED-AUDIT.patch`, `MERGE-INSTRUCTIONS.md` |

## Safety

- Canonical was not modified in this stage.
- No phone operation and no push.
- Stock operands were private read-only copies with verified hashes; `llvm-objcopy` was used only on our own
  probe object.
- No Codex repository or worktree was written; the anvil-kernel queries were read-only HTTP.
