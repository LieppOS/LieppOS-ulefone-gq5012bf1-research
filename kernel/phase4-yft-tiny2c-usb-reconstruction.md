# GQ5012BF1 `yft_tiny2c_usb.ko` reconstruction

# Final classification

**`STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`**

The target is reconstructed from the frozen stock binary oracle. No public donor was used as
completion evidence. All stock-observable hardware, DT, userspace, provider and lifecycle
behavior is accounted for, exact GKI ABI is reproduced, and the fail-closed verifier passes.

# FROZEN status

**FROZEN FOR RE: YES**

The only non-identical code is compiler layout/instruction selection in three functions; it
introduces no hardware-significant, ABI, DT, userspace, state-machine or failure-semantic
residual. Whole-ELF identity is not required by the project standard.

# Stock oracle

- Canonical path: `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/yft_tiny2c_usb.ko`
- Frozen copy: `workspace/phase4-yft-tiny2c-usb/oracle/yft_tiny2c_usb-stock.ko`
- SHA256: `77baeee8fa7c01d9b6ad9b3a9743caa69aa61b840c3d565d5263d3e965d63eed`
- Size: 30,464 bytes
- Build ID: `c626fad2c0d464704f27a9a5ad5dd514be63c3da`
- Compiler: Android clang 17.0.2, build 10087095
- Vermagic: `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`
- Metadata: name `yft_tiny2c_usb`; description `Module For tiny2c_usb`; author
  `yft-drv`; license `GPL`; depends `mt6375-charger`; no parameters or srcversion.
- Normal load: vendor_dlkm `modules.load` one-based line 195 / zero-based index 194.
- Recovery: no copy and not loaded.
- Two local stock/proprietary copies exist and are byte-identical.

Full freeze: `kernel/phase4-yft-tiny2c-usb-stock-oracle.txt`.

# Source provenance

Bounded exact-identifier local and public searches produced **`NO_USEFUL_SOURCE`** and
**`NO_PUBLIC_DONOR_FOUND`**. The local Nothing/MediaTek `mt6375-charger.c` is provider
framework evidence only and lacks Ulefone's `yft_usb_flag` delta. Generic TinyUSB and
USB-to-I2C results are unrelated. See `kernel/phase4-yft-tiny2c-usb-source-candidates.md`.

Reconstruction source:
`workspace/phase4-yft-tiny2c-usb/reconstruction/yft_tiny2c_usb.c` and exact-GKI working
copy `/home/armol/kernel-work/gki-12901745-workspace/lieppos/yft-tiny2c-usb-recon/`.

# RED

An explicit empty-source RED was frozen before reconstruction: 0/12 functions, no module,
no provider edge, no DT/sysfs behavior and fail-closed verifier status. See
`kernel/phase4-yft-tiny2c-usb-RED.md`.

# Function inventory

Stock defines 12 functions: module init/exit; platform probe/remove; power helper; mode
show/store; sensor-ID show; I2C read/chip-ID/probe/remove. Sections, offsets, sizes, KCFI and
call edges are in `kernel/phase4-yft-tiny2c-usb-functions.tsv`. All 12 appear in the rebuild.

# Import ABI

- Undefined ELF symbols: 22 = 21 GKI imports plus intermodule object `yft_usb_flag`.
- `__versions`: 23 = those 22 plus `module_layout`.
- Rebuild: exact 22/22 undefined-symbol set and exact 23/23 CRC set.
- Exports: 0 stock, 0 rebuild.

See `kernel/phase4-yft-tiny2c-usb-imports.tsv` and
`kernel/phase4-yft-tiny2c-usb-modversions.tsv`.

# MT6375 provider ABI

The sole intermodule edge is not a call. It is:

```c
extern int yft_usb_flag; /* CRC 0x398e9c8b; provider GPL export */
```

The module writes 1 after power-on GPIOs and 0 after power-off GPIOs. Stock
`mt6375-charger.ko` has a zero-initialized four-byte `.bss` object and two reader sites:
`mt6375_chg_bc12_work_func` and `mt6375_tcp_notifier_call`. A value of 1 prevents the normal
charger USB-PHY/DPDM BC1.2 mode transition on the internal thermal USB route and affects
BC1.2 work scheduling. It is not an OTG/VBUS-enable or reverse-charge function.

A build-only C ABI witness exports the genuine object declaration through
`EXPORT_SYMBOL_GPL`; genksyms naturally produces `0x398e9c8b`. No CRC, symvers or ELF patch
was injected. Runtime provider remains the stock MT6375 charger. Details:
`kernel/phase4-yft-tiny2c-usb-provider-abi.md`.

# Device-tree contract

Platform node: `/yft_tiny2c_usb`, compatible `mediatek,yft_tiny2c_usb`.

- `tiny2c_usb_vdd_1v8 = <&pio 192 0>`
- `tiny2c_usb_vdd_3v3 = <&pio 191 0>`
- `tiny2c_usb_vddio_3v3 = <&pio 149 0>`
- `tiny2c_usb_vdd_5v`: absent on GQ5012BF1

I2C node: `/soc/i2c@11e03000/fm78100@0x3c`, compatible
`mediatek,tiny2c_usb`, address `0x3c`, status `okay`. Parent bus GPIO IDs are SCL 141 and
SDA 142, owned by the controller rather than this module. No pinctrl, regulator, clock,
interrupt, extcon, USB-controller, PHY, role-switch or charger phandle is consumed.

# Hardware topology

The module directly drives raw active-high enables on GPIO 149 (I/O 3.3 V), 191 (3.3 V) and
192 (1.8 V), and reads the module ID endpoint over I2C8/0x3c. Its generic optional 5-V GPIO
slot has no GQ5012BF1 DT property and therefore proves no direct 5-V/VBUS output. USB data
and VBUS routing are the separate extcon/MT6375/USB1 path.

`tiny2c` is the stock YFT/InfiRay internal thermal-module family/path name. The legacy node
name `fm78100` is not evidence that the bound endpoint is an independent thermopile.

# Thermal-camera relationship

This is the built-in ThermoVue/InfiRay thermal-camera power and identification glue. The
thermal image/temperature stream is an internal USB UVC path handled by `USBMonitor`,
libusb/AC020 and radiometry libraries, not by this I2C driver. Stock `M170infisens`,
`M170infDlp` and FactoryMode coordinate platform power mode with extcon `tiny2c_mode`.
FactoryMode accepts exact cached ID text `0x4c59`. USB enumeration alone is insufficient:
userspace first controls the rail and route nodes.

# uSmart relationship

**`SHARED_USB_PATH` at board-fabric level; not `DIRECT_CONTROLLER` and not direct
`SHARED_POWER_PATH`.** The module has no uSmart switch/detect/VBUS GPIO or ABI. uSmart uses
MT6375 OTG -> extcon -> USB1/UVC GPIOs. Thermal uses its own low-voltage rails plus the
paired extcon tiny2c route. SC851x remains unrelated.

# USB contract

The module has no USB-core, role-switch, extcon, Type-C, TCPC, PHY, regulator, gadget, host
or UVC import. It never directly enables OTG/VBUS, switches USB role or drives a port mux.
Its `usb` behavior is limited to powering the internal USB endpoint and setting the MT6375
BC1.2-exclusion flag. The separate extcon node performs role/route/VBUS behavior.

# GPIO/pinctrl contract

GPIO results are parsed/requested in 1v8, 3v3, optional 5v, io3v3 order. Runtime writes are
io3v3, optional 5v, 3v3, 1v8, with no delay. The module uses raw descriptor operations,
ignores DT polarity flags, and never sets GPIO direction. Probe temporarily writes all
available rails high for I2C identification and then low. There are no pinctrl states.

# Userspace ABI

- `/sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode`, declared 0644 and chmod 0666.
  Show: `gpio_1v8=%d,gpio_3v3=%d,gpio_5v=%d,gpio_io3v3:%d\n`.
  Store uses `%d`; 1 powers on, 0 powers off, unparsable input defaults to the off path,
  other integers change nothing, and every store returns full input count.
- `/sys/devices/platform/yft_tiny2c_usb/sensor_id`, declared 0444 and chmod 0666.
  Show: `0x%x\n` from cached global; no I2C read on show.

No misc/proc/debugfs/ioctl/module parameter or uevent ABI exists. Stock clients and SELinux
labels are enumerated in `kernel/phase4-yft-tiny2c-usb-userspace-abi.md`.

# Mode/state machine

| input | rail raw values | provider flag | direct VBUS/role |
|---|---|---:|---|
| `1` | 149/191/192 high (optional generic 5v slot high) | 1 after rails | none |
| `0` | all available low | 0 after rails | none |
| unparsable | same as 0 | 0 | none |
| other integer | unchanged | unchanged | none |

There is no cached mode, lock, rollback, delay or error acknowledgement.

# Private state layout

The exact 20-byte heap structure is five consecutive 32-bit fields: GPIO 1v8 at +0, 3v3 at
+4, 5v at +8, io3v3 at +12, reused OF flags at +16. Static state is a four-byte `chip_id`
and an eight-byte data pointer. No unknown gaps remain. No device/client pointer, lock,
work, notifier, PM, wake, regulator, pinctrl or cached mode field exists.

# Probe contract

Platform probe allocates/publishes the 20-byte object, parses/requests GPIOs, powers on,
registers the I2C driver, powers off, then creates mode and ID sysfs files. I2C probe sleeps
400 ms, performs up to three chip-ID calls separated/followed by 10 ms delays, returns early
for `0x4c59`, accepts any final nonzero ID and fails `-1` only for zero. Low-level ID logic
uses five retry attempts on the second transfer failure and combines register 0 low byte with
register 1 high byte.

Stock leaks/quirks are preserved: no allocation/GPIO unwind; I2C remains registered after
later sysfs failure; I2C-register failure leaves rails high; sysfs failure removes the current
and prior attempted attributes; no invented devm cleanup.

# Async behavior

None. Delays are synchronous in I2C probe. The paired extcon driver's delayed work is not
this module's behavior.

# Lifecycle / PM

Init/exit register/unregister only the platform driver. I2C remove logs and unusually calls
`i2c_unregister_device(client)`. Platform remove only logs and returns 0. There are no
shutdown/suspend/resume callbacks and no explicit power-down, flag clear, sysfs removal,
I2C-driver unregister, GPIO free or memory free at platform remove/module exit.

# Exact-GKI build

Workspace `/home/armol/kernel-work/gki-12901745-workspace`, common commit
`6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`, target `//common:kernel_aarch64`.

- clean RC: 0
- build RC: 0
- compiler warnings: 0
- modpost warnings: 0
- unresolved symbols: 0
- rebuilt SHA256: `f96f75dfbcbf435e35445987edca7842b2cb207b30683ecee0f4ae3e5e426af4`

# Function parity

Stock 12; rebuild 12; shared 12; stock-only 0; rebuild-only 0; size-identical 11;
byte-identical 9; KCFI 12/12. The three non-byte-identical functions are
`tiny2c_usb_i2c_read`, `tiny2c_usb_read_chipid` and `tiny2c_usb_probe`.
The first two have equal size/call surfaces and equivalent CFG/semantics. Probe is 1068 vs
1064 bytes because the compiler emits a second static `device_remove_file` call site for the
same backwards cleanup semantics; all normal and failure transitions remain closed.

# Object parity

All hardware-significant objects are `BYTE_IDENTICAL`, `RELOCATION_EQUIVALENT`, or
`SEMANTIC_EQUIVALENT`; none is unresolved. OF/I2C tables, platform/I2C drivers, attributes,
state globals, string contracts, versions and metadata are accounted for. See
`kernel/phase4-yft-tiny2c-usb-object-parity.tsv`.

# Behavioral verifier

`kernel/scripts/phase4_yft_tiny2c_usb_verify_recon.py` is fail-closed and checks oracle hash,
source hash, identity, aliases, functions, KCFI, imports/CRCs, provider export/CRC, DT/GPIO,
mode transitions, I2C behavior, userspace clients, lifecycle and clean build gates.

**Result: `68/68 CHECKS PASSED`.** Log:
`workspace/phase4-yft-tiny2c-usb/build/verifier.log`.

# Residuals

- Whole-ELF bytes/build ID/vermagic suffix are not identical and are not required.
- Three functions have documented code-generation/layout differences; none changes a
  hardware-significant operation, provider edge, userspace result, failure result or lifecycle.
- The exact Ulefone-added MT6375 provider source line is unavailable; its object definition,
  export CRC, initial value and every stock reader are closed directly from the provider ELF.
- No live USB VID/PID or runtime descriptor is claimed. It is not needed to close this leaf's
  observable behavior.

**Unexplained hardware-significant residuals: NONE.**

# Runtime-validation status

Static/offline only by instruction. No runtime write or power test was performed. Runtime
validation remains intentionally not performed and is not used to support frozen status.

# Safety

No VBUS/OTG/charger/USB role/GPIO/I2C/sysfs action, module load/unload, bind/unbind, flash,
reboot or slot change was performed. Evidence came from frozen ELFs, DT/userspace files,
read-only snapshots, provider source/binary and exact-GKI builds.

# Evidence index

- Oracle/inventories: `workspace/phase4-yft-tiny2c-usb/oracle/`,
  `kernel/phase4-yft-tiny2c-usb-{functions,objects,imports,modversions,relocations,strings}.tsv`
- Contracts: all `kernel/phase4-yft-tiny2c-usb-*-contract.md` files and provider ABI report
- Source/RED: `kernel/phase4-yft-tiny2c-usb-source-candidates.md`,
  `kernel/phase4-yft-tiny2c-usb-RED.md`
- Reconstruction/build: `workspace/phase4-yft-tiny2c-usb/reconstruction/`,
  `workspace/phase4-yft-tiny2c-usb/build/`
- Parity/verifier: `kernel/phase4-yft-tiny2c-usb-{function,object}-parity.tsv`,
  `kernel/scripts/phase4_yft_tiny2c_usb_verify_recon.py`

# Final verdict

`yft_tiny2c_usb.ko` is `SOURCE_RECONSTRUCTED`, `SOURCE_NOW`, and `FROZEN FOR RE` as a
**`STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`** leaf. It can be removed from the active
ZERO-BLOB reverse-engineering queue. This verdict does not alter any other module's status.
