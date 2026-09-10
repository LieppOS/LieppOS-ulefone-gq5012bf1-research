# GQ5012BF1 `yft_gpio_keys.ko` reconstruction

# Final classification

**SOURCE_DELTA_RECONSTRUCTION_EXACT**

The pinned exact-GKI `gpio_keys.c` plus the recovered YFT delta produces all 23 stock function ranges byte-for-byte and closes the complete 65-entry MODVERSION ABI.

# FROZEN status

**FROZEN FOR RE: YES**

All hardware-significant behavior is accounted for. Runtime exercise was intentionally excluded by the static/offline safety rule.

# Stock oracle

Canonical PLATFORM-ramdisk file: `workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/yft_gpio_keys.ko`; frozen copy: `workspace/phase4-yft-gpio-keys/oracle/yft_gpio_keys.ko`.

- SHA-256: `53c2957db5a2866d27f8dda5910ba2ddda0200ab36fa50b7a97bb87436897cec`
- size: 37,136 bytes
- Build ID: `70193380d6a2891f08f9cc0ae8f4e4cf4854a46a`
- compiler: Android clang 17.0.2, toolchain revision `d9f89f4d16663d5012e5c09495f3b30ece3d2362`
- vermagic: `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`
- name/description/author/license: `yft_gpio_keys`; `Keyboard driver for GPIOs`; Phil Blundell; GPL
- depends/srcversion/parameters: empty/absent/none
- aliases: `platform:gpio-keys`, two `yft-gpio-keys` OF aliases
- normal/recovery zero-based load indices: 179/183
- modules.dep: no dependencies; modules.softdep: no entry

Only one physical stock ELF was found in the frozen corpus; normal and recovery lists select it. Full metadata: `phase4-yft-gpio-keys-stock-oracle.txt`.

# Source provenance

Donor: `common/drivers/input/keyboard/gpio_keys.c`, common commit `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`, SHA-256 `22b787ef4dcd0bfb1fa3b5c693baf793da69642f604b0d1f82188e1b2bfd4b79`. Reconstruction: `/home/armol/kernel-work/gki-12901745-workspace/lieppos/yft-gpio-keys-recon/yft_gpio_keys.c`, SHA-256 `b9b81dac6a81b0b9e23cac0a41f3d4d6e04855036d00c84d0cb1e138e38aaa41`.

No public vendor source was accepted as proof. Candidate classification is in `phase4-yft-gpio-keys-source-candidates.md`.

# RED

The untouched exact donor built cleanly but failed stock identity: generic module/driver/compatible, 5-ms default, no custom IRQ masking/re-enable/edge rearm/logging, 63 versus 65 MODVERSION imports, and only 16/23 raw function ranges identical. See `phase4-yft-gpio-keys-RED.md`.

# Upstream gpio_keys comparison

The generic framework—DT parser, structures, input registration, GPIO/IRQ-only paths, sysfs controls, debounce framework, PM and lifecycle—is the pinned donor. No generic rewrite was performed. The final change is minimal and evidence-backed.

# YFT delta

Exact delta: YFT driver/compatible identity; 16-ms missing-property debounce default; disable IRQ at GPIO ISR entry; re-enable after debounce completion; sampled-state printk lines; sampled pressed -> rising and released -> falling IRQ rearm. No kernel long/multi-press or action policy. See `phase4-yft-gpio-keys-yft-delta.md` and delta ledger TSV.

# Function inventory

23 defined functions, all inventoried with section/offset/size/KCFI/hash in `phase4-yft-gpio-keys-functions.tsv`. Relocation-aware disassembly is preserved under `workspace/phase4-yft-gpio-keys/analysis/` for `.text`, `.init.text` and `.exit.text`.

# Import ABI

65 kernel MODVERSION entries: 64 ELF undefined symbols plus version-only `module_layout`; zero intermodule imports; zero exports. Every name and CRC matches the rebuild. See imports/modversions/import-delta TSVs.

# Device-tree contract

Exact node `/yft-gpio-keys`, compatible `yft-gpio-keys`; two active-low GPIO children. No explicit status means enabled. Exact present-versus-consumed analysis is in `phase4-yft-gpio-keys-dt-contract.md`.

# Hardware button topology

- `/yft-gpio-keys/key-custom1`: `customkeyf1`, MT6878 GPIO13 active-low, Linux code `0x3b`/KEY_F1, 16 ms, wake.
- `/yft-gpio-keys/key-custom2`: `customkeyf2`, MT6878 GPIO8 active-low, Linux code `0x3c`/KEY_F2, 16 ms, wake.

IRQs are dynamically obtained with `gpiod_to_irq`; no fixed Linux IRQ number exists in DT. There are no additional module-owned buttons.

# Input ABI

Name `yft-gpio-keys`, phys `gpio-keys/input0`, BUS_HOST, IDs 1/1/0x0100, EV_KEY bits F1/F2, no EV_SW or EV_REP for this DT, exact open/close and reporting order. See `phase4-yft-gpio-keys-input-contract.md`.

# Struct layout

Stock accesses exactly donor layouts: platform data 48 bytes, button 56 bytes, drvdata header 72 bytes and per-button data 344 bytes. Every accessed offset is mapped in `phase4-yft-gpio-keys-struct-layout.md`.

# Probe contract

DT/platform-data choice, allocations, parser order, GPIO input acquisition, debounce setup/fallback, dynamic IRQ mapping, devm IRQ/quiesce, capability/input registration and every error class are documented in `phase4-yft-gpio-keys-probe-contract.md`. Probe bytes are exact.

# IRQ contract

Both buttons initially request rising+falling+shared through `devm_request_any_context_irq`, with no ONESHOT. Stock masks in the ISR, debounces, samples/reports/syncs, rearms the next physical edge and enables. See `phase4-yft-gpio-keys-irq-contract.md`.

# Debounce contract

DT 16 ms; request 16,000-us controller debounce. On failure, exactly 16-ms software fallback via hrtimer or delayed work according to GPIO sleepability. IRQ remains masked until completion. See `phase4-yft-gpio-keys-debounce-contract.md`.

# Wakeup / PM contract

Both keys initialize device wake. Suspend enables both IRQ wakes and marks suspended; action ANY causes no PM-time trigger rewrite. Wake ISR stays awake and emits a synthetic press; completion relaxes. Resume disables IRQ wake and resamples both states. See `phase4-yft-gpio-keys-pm-contract.md`.

# Userspace mapping

Generic.kl maps scan codes 59/60 to Android KEYCODE_F1/F2 (131/132). Stock `YftPhoneWindowManager` explicitly handles both in queue/dispatch policy; action selection is settings/product dependent (smart key, mini display, optional PTT/SOS/camera branches). See `phase4-yft-gpio-keys-userspace-contract.md`.

# Lifecycle

Module init/exit register/unregister the platform driver; no explicit remove; devres and a quiesce action release/cancel per-device resources. Shutdown uses suspend. See lifecycle contract.

# Exact-GKI build

Target: `//lieppos/yft-gpio-keys-recon:yft_gpio_keys_recon` against `//common:kernel_aarch64`.

- BUILD_RC 0
- compiler warnings 0
- modpost warnings 0
- unresolved symbols 0
- artifact SHA-256 `2bf6f6ea5ccc5376edd05746b384a2d0bad867f2ea40aff80c5371f772bb6a6d`
- artifact path `workspace/phase4-yft-gpio-keys/yft_gpio_keys.rebuilt.ko`

# Function parity

Stock 23, rebuilt 23, shared 23, stock-only 0, rebuilt-only 0, size-identical 23, byte-identical 23, KCFI-exact 23. Entire `.text`, `.init.text` and `.exit.text` sections are byte-identical. See function parity TSV.

# Object parity

Hardware-relevant `.data`, `.rodata`, `.rodata.str1.1` and `__versions` are byte-identical. OF table, PM ops, platform driver and sysfs objects are accounted for. Link/module metadata differences are classified in object parity TSV.

# Import parity

Stock/rebuild 65/65, shared 65, CRC mismatch 0, stock-only 0, rebuild-only 0, unresolved 0.

# Behavioral verifier

`kernel/scripts/phase4_yft_gpio_keys_verify_recon.py` fails closed over stock hash, source hashes, functions/KCFI/bytes, imports/CRCs, identity, DT/button/GPIO/code/polarity, IRQ/debounce/wake/input/event/lifecycle data, important sections and clean build. Result: **40/40 CHECKS PASSED**.

# Residuals

No hardware-significant or ABI-symbol residual remains. Whole-ELF identity is intentionally not claimed. Non-behavioral differences are:

- stock KMD-tree vermagic suffix `g945dff7bc1bf` versus local unstamped Kleaf `maybe-dirty` (the running exact GKI snapshot is independently `g6b18f0b574ab-ab12901745`);
- source path string, Build ID, `.llvm_addrsig`, symbol/relocation numbering and resulting relocation records;
- two-byte `.modinfo` length difference from vermagic.

These do not alter code, important data, imported ABI names/CRCs or hardware behavior. Production packaging should use the project's stamped exact-GKI release policy rather than the local unstamped suffix.

# Runtime-validation status

Not performed and not required for static RE closure. A future integration build may validate input enumeration and physical keys without changing the reconstruction verdict.

# Safety

Static/offline only. No key injection, GPIO/pinctrl/IRQ mutation, sysfs write, bind/unbind, module load/unload, flash, reboot or slot switch was performed.

# Evidence index

- stock oracle, functions, objects, imports, modversions, relocations, strings TSV/TXT files
- source candidate, RED, delta ledger and all contract documents
- function/object/import parity TSV files
- frozen stock/rebuild ELFs and raw disassemblies under `workspace/phase4-yft-gpio-keys/`
- final build log `workspace/phase4-yft-gpio-keys/recon-build-final.log`
- verifier transcript `kernel/phase4-yft-gpio-keys-verify-recon-vs-stock.txt`

# Final verdict

The exact stock implementation is the pinned Android common GPIO-keys driver plus a small YFT IRQ/debounce/identity delta. The reconstruction is exact at every function byte range, closes all 65 MODVERSION imports, and has no unexplained hardware-significant residual. `yft_gpio_keys` is **SOURCE_NOW** and may leave the active reverse-engineering queue.
