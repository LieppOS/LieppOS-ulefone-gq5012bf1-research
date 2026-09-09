# GQ5012BF1 `fingerprint.ko` reconstruction

## Final classification

**`STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`**

**FROZEN FOR RE: YES.** The stock-observable hardware behavior is closed, all
10 exports and their CRCs arise naturally, all four stock
`microarray_fp_tee.ko` dependency edges are exact, the exact-GKI build succeeds,
and the fail-closed verifier passes 39/39. `microarray_fp_tee`, `tkcore`, and
`tkcore_drv` remain separate unresolved/stock-held modules.

## Stock oracle

Target: Ulefone Armor 29 Pro Thermal, GQ5012BF1, MT6878/MT6878T.

- canonical extracted path: `workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/fingerprint.ko`
- frozen copy: `workspace/phase4-fingerprint/oracle/fingerprint.stock.ko`
- SHA256: `f5d4dde1f09ac1d67877c66dddf2839de1f496bb2b6b74f50fbe3cd1693b60dc`
- size: 30,552 bytes
- Build ID: `dd2af202eb2ce74d37505ae351e5748eba66ffe9`
- compiler: Android clang 17.0.2, build 10087095, LLVM revision `d9f89f4d16663d5012e5c09495f3b30ece3d2362`
- vermagic: `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`
- name/description/author/license: `fingerprint` / `for yft fingerprint driver` / `Jay_zhou` / `GPL`
- `depends=` empty; `srcversion` absent; parameters none
- aliases: `of:N*T*Cmediatek,yft_finger` and `of:N*T*Cmediatek,yft_fingerC*`
- normal load index 181; recovery index 185

Only one physical module was found. Recovery reuses the shared PLATFORM
ramdisk copy. No differing vendor_dlkm, system_dlkm, proprietary, or backup copy
exists. `modules.dep` proves `microarray_fp_tee.ko` depends on this provider;
there is no fingerprint softdep.

## Source provenance

`NO_PUBLIC_DONOR_FOUND`. Exact YFT identifiers were searched locally and across
public NothingOSS, MediaTek, Motorola, MiCode, OnePlus, OPPO, realme,
Transsion, Sony, Ulefone/YFT, GitHub, Gitee, and Android vendor sources.
Generic MicroArray drivers are sensor-layer code, and generic MediaTek pinctrl
examples are structural donors only. The reconstruction is clean-room and led
by the frozen ELF, merged DT, and stock consumer. See
`phase4-fingerprint-source-candidates.md`.

Tracked source is in `phase4-fingerprint-recon/fingerprint.c` and
`phase4-fingerprint-reconstructed-source.c`. The exact build workspace copy is
`/home/armol/kernel-work/gki-12901745-workspace/lieppos/fingerprint-recon/fingerprint.c`.

## RED

No plausible donor crossed the unchanged-build threshold, so the mandatory RED
result is `NO_PUBLIC_DONOR_FOUND`; no donor was silently adapted. The stock
baseline is 16 functions, 18 kernel MODVERSIONs, 10 exports, 13 required
pinctrl lookups, waitqueue synchronization, no PM, and static-global state.
The full negative-source and baseline comparison is in
`phase4-fingerprint-RED.md`.

## Function inventory

Stock and reconstruction each contain 16 functions:

`yft_finger_get_gpio_info`, `yft_finger_probe_isok`,
`yft_finger_set_power`, `yft_finger_power_deinit`,
`yft_finger_set_reset`, `yft_finger_set_irq`, `yft_finger_get_irqnum`,
`yft_finger_get_irq_gpio`, `yft_finger_get_reset_gpio`,
`yft_finger_set_spi_mode`, `yft_waite_for_finger_dts_paser`,
`yft_get_max_finger_spi_cs_number`, `yft_finger_plat_probe`,
`yft_finger_plat_remove`, `init_module`, and `cleanup_module`.

All 16/16 sizes, KCFI IDs, and relocatable function bytes are identical.
Offsets, sizes, hashes, and KCFI values are in
`phase4-fingerprint-functions.tsv` and
`phase4-fingerprint-function-parity.tsv`.

## Import ABI

The reconstruction naturally reproduces the exact 18-entry stock MODVERSION
map: `__platform_driver_register`, `__stack_chk_fail`, `__wake_up`, `_dev_err`,
`_printk`, `devm_pinctrl_get`, `devm_pinctrl_put`, `finish_wait`,
`init_wait_entry`, `irq_of_parse_and_map`, `of_find_compatible_node`,
`of_get_named_gpio_flags`, `pinctrl_lookup_state`, `pinctrl_select_state`,
`platform_driver_unregister`, `prepare_to_wait_event`, `schedule_timeout`, and
`module_layout`. Import set and CRC parity are 18/18; there are no intermodule
imports. See `phase4-fingerprint-imports.tsv` and
`phase4-fingerprint-modversions.tsv`.

## Export ABI

All exports are `EXPORT_SYMBOL`, not GPL-only. Every CRC and KCFI type is
naturally generated; no symvers fabrication, CRC patch, or ELF edit was used.

| export | exact prototype | stock/rebuilt CRC | KCFI |
|---|---|---:|---:|
| `yft_finger_probe_isok` | `int (bool)` | `0x7476a412` | `0xd2a1eef1` |
| `yft_finger_set_power` | `int (int)` | `0x1fc1d7b1` | `0x00050794` |
| `yft_finger_power_deinit` | `void (void)` | `0xad1b117e` | `0xa540670c` |
| `yft_finger_set_reset` | `int (int)` | `0xcae83e02` | `0x00050794` |
| `yft_finger_set_irq` | `int (int)` | `0x6d125ec3` | `0x00050794` |
| `yft_finger_get_irqnum` | `unsigned int (void)` | `0x9cc3cc91` | `0x837de525` |
| `yft_finger_get_irq_gpio` | `unsigned int (void)` | `0x1a8a2d17` | `0x837de525` |
| `yft_finger_get_reset_gpio` | `unsigned int (void)` | `0x6f79cc60` | `0x837de525` |
| `yft_finger_set_spi_mode` | `int (int)` | `0x0cf6e61a` | `0x00050794` |
| `yft_waite_for_finger_dts_paser` | `void (void)` | `0x4202702c` | `0xa540670c` |

The public misspelling `yft_waite_for_finger_dts_paser` is preserved. Detailed
state and side effects are in `phase4-fingerprint-export-contract.md`.

## MicroArray consumer boundary

Stock `microarray_fp_tee.ko` imports exactly four YFT symbols:

| symbol | consumer CRC | calls | proven argument | result |
|---|---:|---:|---:|---|
| `yft_finger_set_reset` | `0xcae83e02` | 1 | `1` | ignored |
| `yft_finger_set_spi_mode` | `0x0cf6e61a` | 2 | `1` | ignored |
| `yft_finger_set_irq` | `0x6d125ec3` | 1 | `1` | ignored |
| `yft_waite_for_finger_dts_paser` | `0x4202702c` | 1 | none | void |

The proven probe sequence is wait, MicroArray regulator setup, reset-high,
SPI pinmux, IRQ pull-up, then consumer-owned IRQ/TEE setup. `mas_sync` invokes
SPI mode 1 again before its mutex/SPI path. All call sites are sleepable process
context; none occurs in the IRQ handler. The provider CRCs match 4/4, therefore
classification at this edge is **`STOCK_CONSUMER_ABI_EXACT`**. This does not
classify the sensor driver itself as reconstructed. See
`phase4-fingerprint-microarray-boundary.md`.

## Device-tree contract

Exact merged path and compatible:

```text
/yft_finger
compatible = "mediatek,yft_finger"
```

The node is enabled and supplies `pinctrl-names`, `pinctrl-0..15`,
`reset-gpio = <&mt6878_pinctrl 30 0>`, `int-gpio = <&mt6878_pinctrl 3 0>`,
`interrupt-parent`, `interrupts = <3 1 3 0>`, and `debounce = <3 0>`.
The module directly gets `reset-gpio`, `int-gpio`, and IRQ index 0. It does not
consume a regulator, clock, supply, wake property, debounce value, or CS number.
See `phase4-fingerprint-dt-contract.md`.

## Pinctrl contract

The provider performs 13 mandatory lookups, in this order:

1. `finger_reset_en1`
2. `finger_reset_en0`
3. `finger_spi0_mi_as_spi0_mi`
4. `finger_spi0_mi_as_gpio`
5. `finger_spi0_mo_as_spi0_mo`
6. `finger_spi0_mo_as_gpio`
7. `finger_spi0_clk_as_spi0_clk`
8. `finger_spi0_clk_as_gpio`
9. `finger_spi0_cs_as_spi0_cs`
10. `finger_spi0_cs_as_gpio`
11. `finger_eint_pull_down`
12. `finger_eint_pull_up`
13. `finger_eint_pull_dis`

Each error pointer aborts parsing with its `PTR_ERR`. DT also names empty
`finger_power_en0/1` states, but stock never looks them up and reports that
finger GPIO power is unnecessary. No initial state is selected during probe.
See `phase4-fingerprint-pinctrl-contract.md`.

## Reset contract

`yft_finger_set_reset(0)` selects reset-low and `(1)` selects reset-high;
other values are accepted no-ops. Both pointers are checked first. Any
`ERR_PTR` returns literal `-1`; pinctrl selection errors are ignored and the
normal return is 0. There is no delay, pulse, GPIO API, lock, or cached state.
The stock consumer only calls value 1. See
`phase4-fingerprint-reset-contract.md`.

## IRQ contract

This setter controls pin bias only: 0 selects pull-down, 1 pull-up, and 2 bias
disable; other values are accepted no-ops. Any of the three state pointers
being an `ERR_PTR` produces literal `-1`; select errors are ignored. It never
calls Linux IRQ enable/disable/wake APIs and has no handler. IRQ index 0 maps
GPIO/EINT3 with rising-edge type; the consumer owns registration and wake.
See `phase4-fingerprint-irq-contract.md`.

## SPI-mode contract

“Mode” is pinmux, not CPOL/CPHA. Mode 0 selects CLK, CS, MI, MO as GPIO in that
order. Mode 1 selects CLK, CS, MI, MO as SPI0 alternate functions in that order.
Other values are no-ops. All eight pointers are validated first; selection
returns are ignored. There is no controller-mode write, clock gate, standalone
CS operation, delay, rollback, or lock. See
`phase4-fingerprint-spi-mode-contract.md`.

## DT-ready synchronization

`yft_waite_for_finger_dts_paser()` uses the statically initialized
`finger_init_waiter` waitqueue. It waits interruptibly for
`yft_finger_plat != NULL` with timeout `3 * HZ` (750 jiffies in this build),
then discards the wait result and returns void. Repeated callers are allowed.
Probe publishes the platform pointer before parsing, and parsing wakes the queue
before `devm_pinctrl_get`; therefore “ready” means pointer published, not parse
success. Remove clears the pointer without wake. These quirks are preserved.
See `phase4-fingerprint-dt-wait-contract.md`.

## Struct layout

There is no private allocation or aggregate state structure. `.bss` is exactly
0x88 bytes: one pinctrl pointer, 15 state pointers (including two unused power
pointers), and the platform-device pointer, all at eight-byte intervals.
`.data` contains the 24-byte waitqueue at +0, 400-byte two-entry OF table at
+0x18, and 248-byte platform driver at +0x1a8. There are no cached GPIO/IRQ
numbers, parse-status flag, power/reset/SPI state, mutex, or completion. See
`phase4-fingerprint-struct-layout.md`.

## Probe

`yft_finger_plat_probe` performs exactly:

1. publish `yft_finger_plat = pdev`;
2. print the entry log;
3. call `yft_finger_get_gpio_info(pdev)`;
4. ignore that return and return 0.

The parser finds the compatible node with no NULL guard, logs node names, wakes
waiters, obtains pinctrl, then looks up all 13 states in the order above. It
returns the first pinctrl error or 0. Probe performs no initial pin selection,
power action, reset transition, IRQ registration, resource allocation, or
cleanup. The ignored parse error is a stock quirk, not repaired. See
`phase4-fingerprint-probe-contract.md`.

## Lifecycle / PM

Init registers the platform driver; any nonzero register result is converted to
`-ENODEV`. Remove only clears `yft_finger_plat` and returns 0. Exit unregisters
the driver. There are no shutdown, suspend, resume, PM, wake-IRQ, or automatic
power/reset/pinmux transitions. `yft_finger_power_deinit`, if externally called,
clears the unused power pointers and puts pinctrl. See
`phase4-fingerprint-lifecycle-contract.md`.

## Userspace relation

`fingerprint.ko` is board glue and exposes no device node, sysfs ABI, ioctl, SPI
transfer, or secure-world command. Stock `microarray_fp_tee.ko` is the actual
MicroArray SPI/TEE sensor driver and owns `/dev/madev0`. The vendor MicroArray
HAL and Android biometric service sit above it; TrustKernel owns the secure
transport. No sensor or secure-world behavior is attributed to this provider.
See `phase4-fingerprint-userspace-contract.md`.

## Exact-GKI build

Workspace and target:

```text
/home/armol/kernel-work/gki-12901745-workspace
//common:kernel_aarch64
Linux 6.1.115-android14-11, ab/12901745
common 6b18f0b574ab3267615ae6ce642d5a7c3c21ac09
```

Build command:

```sh
tools/bazel build //lieppos/fingerprint-recon:fingerprint_recon
```

Result: `BUILD_RC=0`, compiler warnings 0, modpost warnings 0, unresolved
symbols 0. The Kleaf `check_no_remaining` artifact is empty. All 18 kernel
MODVERSIONs and all 10 generated provider CRCs match stock. No fake symvers,
CRC patching, ELF editing, or `KBUILD_MODPOST_WARN` was used.

Rebuilt artifact: 30,544 bytes, SHA256
`72538ba836ee6a075d42609b845cf3fde84858c6c91e3900149aef2481df05f1`.

## Function parity

- function count: stock 16 / rebuilt 16
- function names: 16/16
- function sizes: 16/16 identical
- function KCFI: 16/16 identical
- relocatable function bytes: **16/16 byte-identical**
- section sizes: `.text` 0x838, `.init.text` 0x48, `.exit.text` 0x28 in both

See `phase4-fingerprint-function-parity.tsv`.

## Object parity

Both modules contain 38 inventoried objects. After normalizing compiler line
suffixes on five `__UNIQUE_ID_*` symbols, 37/38 objects are size-identical and
byte-identical. The only differing semantic object is generated vermagic:
stock has the CI git suffix and reconstruction has `maybe-dirty`. `.data`
(0x2a0), `.bss` (0x88), export tables, CRC table, and `__versions` (0x480) have
identical sizes. Relocation count is 317/317 and every relocation has the same
target section, offset, type, and symbol; 232 addends are identical, while
string-pool layout changes the remaining addends. The complete printable
hardware/diagnostic string set is preserved.

The whole ELF is intentionally not claimed byte-identical: generated vermagic,
Build ID/signature/provenance, unique-ID line suffixes, and string-pool layout
differ. See `phase4-fingerprint-object-parity.tsv`.

## Consumer compatibility

The reconstructed provider generates all 10 stock export CRCs. The four CRCs
recorded in the stock MicroArray consumer are exact, yielding
**`STOCK_CONSUMER_ABI_EXACT`** with 0 mismatches. The remaining six public
exports are also exact, so the provider itself is
**`SOURCE_STACK_INTERNAL_ABI_COMPLETE`**. This says nothing about reconstructing
`microarray_fp_tee.ko`, which remains untouched.

## Behavioral verifier

`kernel/scripts/phase4_fingerprint_verify_recon.py` independently inventories
stock, rebuilt provider, and stock consumer and fails closed on stock SHA,
functions, imports/MODVERSIONs, exports/CRCs/KCFI, DT/pinctrl strings, reset,
IRQ, SPI, wait, probe/lifecycle semantics, build status, and consumer CRCs.

Result: **39/39 CHECKS PASSED**. Frozen output:
`phase4-fingerprint-verify-recon-vs-stock.txt`.

## Residuals

No material stock-observable hardware or ABI residual remains. Whole-ELF
identity is not reached only for generated build provenance and compiler
string-pool layout described above. The provider's early wake and ignored
probe-parse error are preserved behavior, not unknowns. The exact MicroArray
sensor die remains unknown but is outside this module.

## Runtime-validation status

No runtime test was performed. This closure is static/offline by design.
Runtime insertion/binding remains a future integration-validation activity, not
an RE evidence gap.

## Safety

No GPIO, IRQ, reset, pinctrl, SPI, secure-world, `/dev/madev0`, bind/unbind,
module load/unload, flash, reboot, or slot operation was performed. Evidence was
limited to stock ELF/DT, read-only snapshots, the stock consumer, source search,
and exact-GKI offline builds.

## Evidence index

- oracle: `workspace/phase4-fingerprint/oracle/`
- stock inventory: `phase4-fingerprint-{functions,objects,imports,exports,modversions,relocations,strings}.tsv`
- source search / RED: `phase4-fingerprint-source-candidates.md`, `phase4-fingerprint-RED.md`
- behavior contracts: `phase4-fingerprint-{dt,pinctrl,reset,irq,spi-mode,dt-wait,probe,struct-layout,lifecycle,userspace}-contract.md`
- consumer: `phase4-fingerprint-microarray-boundary.md`
- reconstruction: `phase4-fingerprint-recon/`
- parity: `phase4-fingerprint-function-parity.tsv`, `phase4-fingerprint-object-parity.tsv`
- verifier: `scripts/phase4_fingerprint_verify_recon.py`, `phase4-fingerprint-verify-recon-vs-stock.txt`

## Final verdict

`fingerprint.ko` is source-reconstructed, stock-consumer ABI exact, behaviorally
closed, and **FROZEN FOR RE**. It may replace the stock YFT glue provider after
the project's separate staged integration process. Stop at this provider:
`microarray_fp_tee`, `tkcore`, and `tkcore_drv` are not reconstructed or marked
complete by this work.
