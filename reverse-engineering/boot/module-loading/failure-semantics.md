# Failure semantics

Classes: **FATAL** (boot blocker / reboot), **HANG** (service-gated stall, no reboot),
**LOGGED** (error logged, boot continues), **IGNORED** (no visible effect), **BENIGN-EEXIST**.

| condition | first stage (`/lib/modules`, strict) | insmod_sh passes | init.touch.rc modprobe | rc `insmod` |
|---|---|---|---|---|
| listed module file missing | `ModuleExists` false → `LoadWithAliases(strict)` false → loop **stops**, `LOG(FATAL) "Failed to load kernel modules"` → **FATAL** | LOGGED ("LoadWithAliases was unable to load"), next name; property still set | LOGGED (16 of 19 names are missing on stock — normal) | LOGGED (`msync2_dms` ENOENT on stock) |
| name not in `modules.dep` | same as missing → FATAL | LOGGED | LOGGED | n/a (raw path) |
| CRC mismatch (`disagrees about version of symbol`) / unknown symbol (`-ENOENT`/`-EINVAL` from finit_module) | FATAL | LOGGED; users of the module also fail (their hard dep returns false) | LOGGED | LOGGED |
| vermagic mismatch | kernel compares only the flags after the release token when `modversions` is set (`same_magic`), so release-string differences (`g945dff7bc1bf` vendor vs `g6b18f0b574ab-ab12901745` GKI) are accepted; a flag mismatch → `-ENOEXEC` → as above | — | — | — |
| unsigned module | accepted (not `MODULE_SIG_FORCE`); kernel taints (`E`), all 411 vendor_boot/vendor_dlkm `.ko` are unsigned, all 60 system_dlkm `.ko` signed | — | — | — |
| unsigned module exports a GKI-protected symbol | rejected (`Protected symbol: %s`) → as "init error" | — | — | — |
| dependency failed | dependent not inserted; in first stage → FATAL | LOGGED, dependent skipped | LOGGED | n/a |
| duplicate insertion / already loaded | in-process `module_loaded_` skip; cross-process: `finit_module` EEXIST → treated as success | BENIGN-EEXIST (4 vendor names pre-loaded by first stage; `bluetooth` from system_dlkm) | BENIGN-EEXIST (`hynitron` race) | **LOGGED** — init reports `failed: File exists` (captured for `bt_drv_6878`), harmless |
| module `init` returns error | `finit_module` error → FATAL | LOGGED, continue | LOGGED | LOGGED |
| module `init` never returns | first stage hangs → watchdog | modprobe never returns → property stays 0 → **HANG** at post-fs-data | background process stuck, boot continues | init's action queue blocked (builtin runs synchronously) |
| optional (softdep) module fails | non-strict, IGNORED | IGNORED | IGNORED | — |
| malformed `modules.softdep` line | line ignored (stock: `softdep mt6878_dcm pre:mtk_dcm.ko`) — `mtk_dcm` still loads as a hard dep | — | — | — |
| `init.insmod.mt6878.cfg` missing | — | script `exit 2`, no setprop → **HANG** | — | — |
| setprop denied | — | retried ≤129×, then gives up → **HANG** | — | — |
| `/proc/cmdline` read denied (stock AVC) | — | libmodprobe sees no kernel-cmdline module options; IGNORED (stock has none) | — | — |

Retry: none for module loading anywhere; only the final `setprop` is retried.
