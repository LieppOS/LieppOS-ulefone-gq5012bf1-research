# GQ5012BF1 tkcore island Phase 3C — baseline

Frozen before every Phase-3C source edit.

## Identity and repository state

- Mission: ioctl + compat + command-marshalling reconstruction, static/offline only.
- `START_RESEARCH_HEAD=89fd623eec43605022987a759f51f42c0ca27c0c`
- Required Phase-3B commits are ancestors and present:
  - `aa4caa60ed555ad7f30e3620a645ffbfcbe67bf6` — shared-memory reconstruction
  - `89fd623eec43605022987a759f51f42c0ca27c0c` — cross-phase verifier correction
- Exact-GKI `common`: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`; tracked and untracked status clean at gate time.
- Ten pre-existing untracked research paths were observed and left untouched (TODO, NFC/hardware, qwen and dumpsys work); they are unrelated to tkcore Phase 3C.

## Mandatory build gate

Built from the live island, before edits:

```text
//lieppos/tkcore-island:tkcore
//lieppos/trustkernel-layout:tk_layout_probe
```

| Check | Result |
|---|---:|
| build RC | 0 |
| compiler warnings | 0 |
| compiler errors | 0 |
| modpost warnings | 0 |
| unresolved symbols | 0 |
| static-assert failures | 0 |
| `depends` | empty |
| module size | 166120 |
| module SHA-256 | `860ad5ee0c4da579627c202b19892b20e44ef34287054f11ab802b09e9933640` (**exact Phase 3B reproduction**) |

The frozen module retains Build ID `f2ac7127bf1efe6590cbf97bd33fb7ddae8c7e19`, srcversion `0930BDEBAEE73D3CE34B030`, and vermagic `6.1.115-android14-11-maybe-dirty SMP preempt mod_unload modversions aarch64`.

## Mandatory verifier gate

| Verifier | Result |
|---|---:|
| Phase 3B shared memory | **203/203 PASS** |
| Phase 3A-R core/context/session | **162/162 PASS** |

No repair was needed or performed during the gate.

## Frozen baseline evidence

`workspace/phase4-tkcore-island/phase3c/before/` contains:

- exact `tkcore.phase3b.ko` and SHA;
- `nm`, complete `readelf`, relocation-aware `.text/.init.text/.exit.text` disassembly, `modinfo`, and section sizes;
- clean baseline build log and machine result environment;
- complete output and return code from both prerequisite verifiers;
- all 18 live island-source hashes;
- all 8 live TrustKernel-header hashes;
- frozen layout-probe ELF, SHA and `readelf` evidence;
- the exact starting research HEAD.

Per-function stock and Phase-3B disassemblies used for immutable RED are under `workspace/phase4-tkcore-island/phase3c/oracle-functions/`.

## Starting measured state

| Metric | Phase 3B |
|---|---:|
| stock-function coverage | 104 / 122 |
| missing stock functions | 18 |
| byte-identical functions | 44 |
| exports | 21 / 25 |
| undefined imports | 97 |
| defined objects | 50 |
| relocations | 2309 |
| island-only functions | 0 |
| compiler-enforced shared layout anchors | 83 PASS |

## Boundary frozen at baseline

Phase 3C may reconstruct only the seven named ioctl/compat functions and audit directly reached command/RPC code. It does not include clkmgr, SPI, platform/affinity/uaccess, runtime testing, or final consumer natural-link acceptance. Todo **#18 remains pending**, and `workspace/phase4-tkcore-island/acceptance/` remains empty.
