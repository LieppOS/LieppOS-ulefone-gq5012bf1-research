# Ulefone GQ5012BF1 `tcpc_class.ko` 2.0.31_MTK reconstruction

## Result

**Classification: ABI-exact reconstruction (21/21 stock export CRCs reproduced; 699/707 functions
byte-identical).**

The reconstruction builds on exact GKI 12901745, reports `2.0.31_MTK`, and reproduces the stock
module's complete ABI — every genksyms CRC the stock `tcpc_mt6375.ko` imports — plus every
measurable structural property:

| Property | Stock | Reconstruction | Status |
|---|---|---|---|
| **Export CRCs required by `tcpc_mt6375`** | 21 | 21 | **21/21 identical** |
| Defined functions | 707 | 707 | exact set, no extra/missing |
| Function sizes | — | 699/707 identical | 8 residual |
| Function bytes | — | **699/707 identical** | every size-matching function is byte-identical |
| `struct tcpc_device` allocation | `0x35a8` | `0x35a8` | exact |
| `struct tcpc_ops` layout | 31 slots, `0xf8` | 31 slots, `0xf8` | exact |
| Imports | 101 | 101 | exact set |
| Import MODVERSION CRCs | 102 entries | 102 entries | all identical |
| `.text` | 134 200 B | 134 384 B | +184 B |
| TCPC core version | `2.0.31_MTK` | `2.0.31_MTK` | exact |

Because the CRCs match, the reconstructed module is a drop-in ABI replacement for the stock
`tcpc_class.ko`: the stock `tcpc_mt6375.ko` (and every other stock TCPC consumer using these
symbols) links against it with no `__versions` divergence. No CRC table was ever edited.

> Note: the 21/21 ABI match was achieved after the `tcpc_mt6375` reconstruction supplied four
> `struct tcpc_device` offset immediates as new binary evidence — see
> *Fork-only struct members removed* below.

## Inputs and provenance

| Item | Value |
|---|---|
| Stock `tcpc_class.ko` | `2426edb571f5f8c2c1317b618fe6c10a095a59cf17acdd4d17ef583f63b5b5c5` |
| Stock `tcpc_mt6375.ko` (ABI oracle) | `30abac643ebc7428a5ff350741d22b0f4bdcf65a5a071f55ec7ba78d862ca750` |
| Donor (NothingOSS, 2.0.27_MTK) | `957dac185efe46cbf6336b0fff9516d84c8cd78f` |
| Public 2.0.31_MTK reference located during this task | `MiCode/MTK_kernel_device_modules`, branch `bsp-chagall-w-oss`, commit `2d6f27aa19d521409f443c8d821e2d475bdc72b6` |

A public MediaTek **2.0.31_MTK** TCPC tree was found (previously assumed unavailable). Branch survey:

```text
2.0.22_MTK  bsp-duchamp-u-oss
2.0.27_MTK  malachite-u-oss                (same revision as the NothingOSS donor)
2.0.30_MTK  bsp-dali/goya/rodin-v-oss, dew/flare/spark-w-oss
2.0.31_MTK  bsp-chagall-w-oss, bsp-klee-w-oss, dash-w-oss      <-- stock's revision
2.0.32_MTK  bsp-prague/warhol-w-oss, lapis-v-oss, yili-w-oss
```

The 2.0.31 branches are Xiaomi forks; the reconstruction therefore uses the 2.0.31 baseline **minus
the vendor-only additions that stock disassembly proves absent**.

## Required RED baseline

Reproduced before any change, preserved in `baseline/`:

```text
exact-GKI build succeeded
pd_dbg_info import CRC   = 0x48fb7437
CONFIG_MTK_TYPEC_WATER_DETECT enabled
tcpc_typec_handle_wd exported (0xe5432845)
tcpm_check_suspend_pending / tcpm_suspend / tcpm_resume missing
TCPC core version 2.0.27_MTK
stock .text  = 087b5c7b823fe6311d37c5d1f9782489c9e022ed37cec8f733eb2b8c6217bb96 (134 200 B)
baseline .text = 1d85cea20c3c6273084ac12000194e109dc6f19c4d5f4998b843cf7ff5668616 (139 664 B)
```

Preserved artifacts: `tcpc_class.ko`, `Module.symvers`, `Makefile`, `BUILD.bazel`,
`source-sha256.txt`, `imports.txt`, `import-modversions.txt`, `exports.txt`, `function-sizes.txt`.

## Recovered 2.0.31 changes

### 1. PM API (`tcpm_check_suspend_pending`, `tcpm_suspend`, `tcpm_resume`)

Recovered source (matches stock byte-for-byte):

```c
int tcpm_check_suspend_pending(struct tcpc_device *tcpc)
{
	if (atomic_read(&tcpc->suspend_pending) > 0)
		return -EBUSY;

	if (atomic_read(&tcpc->pending_event) > 0 ||
	    tcpc_get_timer_tick(tcpc))
		return -EBUSY;

	return 0;
}
EXPORT_SYMBOL(tcpm_check_suspend_pending);

int tcpm_suspend(struct tcpc_device *tcpc)
{
	int ret = 0;

	ret = tcpm_check_suspend_pending(tcpc);
	if (ret)
		return ret;

#if CONFIG_TYPEC_SNK_ONLY_WHEN_SUSPEND
	tcpci_lock_typec(tcpc);
	ret = tcpc_typec_suspend(tcpc);
	tcpci_unlock_typec(tcpc);
	if (ret)
		return ret;
#endif	/* CONFIG_TYPEC_SNK_ONLY_WHEN_SUSPEND */

	atomic_set(&tcpc->is_suspended, true);

	ret = tcpm_check_suspend_pending(tcpc);
	if (ret)
		tcpm_resume(tcpc);
	return ret;
}
EXPORT_SYMBOL(tcpm_suspend);

void tcpm_resume(struct tcpc_device *tcpc)
{
	atomic_set(&tcpc->is_suspended, false);
	wake_up_all(&tcpc->resume_wait_que);

#if CONFIG_TYPEC_SNK_ONLY_WHEN_SUSPEND
	tcpci_lock_typec(tcpc);
	tcpc_typec_resume(tcpc);
	tcpci_unlock_typec(tcpc);
#endif	/* CONFIG_TYPEC_SNK_ONLY_WHEN_SUSPEND */
}
EXPORT_SYMBOL(tcpm_resume);
```

Verification against the stock oracle:

| Function | Stock size | Reconstructed | Bytes | External calls |
|---|---:|---:|---|---|
| `tcpm_check_suspend_pending` | 84 | 84 | identical | `tcpc_get_timer_tick` |
| `tcpm_suspend` | 148 | 148 | identical | `tcpc_get_timer_tick` ×2, `__wake_up` |
| `tcpm_resume` | 56 | 56 | identical | `__wake_up` |

The offsets named in the task map to real members:

```text
+0x22dc  atomic_t pending_event
+0x22e0  atomic_t suspend_pending
+0x22e4  atomic_t is_suspended        (new in 2.0.31)
+0x2320  wait_queue_head_t resume_wait_que  (new in 2.0.31)
```

`tcpm_resume()` is `void` — confirmed by the reference prototype and by the absence of a return
value in stock code; the disabled-PD stub is `static inline void tcpm_resume(...) {}`.

### 2. New/changed struct members

```c
	atomic_t pending_event;
	atomic_t suspend_pending;
	atomic_t is_suspended;          /* added */
	uint64_t timer_tick;
	wait_queue_head_t event_wait_que;
	wait_queue_head_t timer_wait_que;
	wait_queue_head_t resume_wait_que;  /* added */
```

Initialisation added to `tcpc_device_register()` right after `spin_lock_init(&tcpc->timer_tick_lock)`:

```c
	init_waitqueue_head(&tcpc->resume_wait_que);
```

`tcpc_get_timer_tick()` changed from `static inline` (file-local) to an exported-to-module global
declared in `inc/tcpci_timer.h`, because `tcpm.c` now calls it.

### 3. `struct tcpc_ops` revision (recovered from the stock MT6375 initializer)

The stock `tcpc_mt6375.ko` object `mt6375_tcpc_ops` is 0xf8 bytes (31 slots) and its relocations
resolve to:

```text
+0x000 init                 +0x058 set_polarity        +0x0b0 set_force_discharge
+0x008 init_alert_mask      +0x060 set_vconn           +0x0b8 (NULL: set_command)
+0x010 alert_status_clear   +0x068 deinit              +0x0c0 set_msg_header
+0x018 fault_status_clear   +0x070 alert_vendor_...    +0x0c8 set_rx_enable
+0x020 set_alert_mask       +0x078 set_auto_dischg_... +0x0d0 get_message
+0x028 get_alert_mask       +0x080 get_vbus_voltage    +0x0d8 protocol_reset
+0x030 get_alert_status_and_mask  +0x088 set_water_protection  +0x0e0 transmit
+0x038 get_power_status     +0x090 set_cc_hidet        +0x0e8 set_bist_test_mode
+0x040 get_fault_status     +0x098 get_cc_hi           +0x0f0 retransmit
+0x048 get_cc               +0x0a0 set_vbus_short_cc
+0x050 set_cc               +0x0a8 set_low_power_mode
```

Compared with 2.0.27 this confirms the 2.0.31 renames/removals
(`get_alert_status` → `get_alert_status_and_mask`, `get_power_status()` loses its out-parameter,
`set_vbus_short_cc_en` → `set_vbus_short_cc`, `is_vsafe0v` and `set_bist_carrier_mode` removed),
and it proves that the Xiaomi-only callbacks `enable_io_boost` and `set_watchdog` are **not** part of
the Ulefone/MediaTek revision. Removing exactly those two reproduces the stock 31-slot layout;
`tcpci_set_msg_header` then loads `[ops + 0xc0]` exactly as stock does.

### 4. Ulefone-only vendor sysfs attribute

Stock defines `yft_tcpc_polarity_show` (140 B) and imports `class_create_file_ns`. Recovered from
the stock disassembly, string table and `.data` object `class_attr_yft_tcpc_polarity`:

```c
static ssize_t yft_tcpc_polarity_show(struct class *class,
				      struct class_attribute *attr, char *buf)
{
	struct tcpc_device *tcpc = tcpc_dev_get_by_name("type_c_port0");
	int polarity = -1;

	if (tcpc->typec_attach_old != TYPEC_UNATTACHED &&
	    tcpc->typec_attach_new != TYPEC_UNATTACHED)
		polarity = tcpm_inquire_cc_polarity(tcpc);

	return snprintf(buf, 256, "%d\n", polarity);
}
static CLASS_ATTR_RO(yft_tcpc_polarity);
```

registered in `tcpc_class_init()` immediately after `regmap_plat_init()`:

```c
	if (class_create_file(tcpc_class, &class_attr_yft_tcpc_polarity))
		pr_info("Failed to create device file(sw_ctrl)\n");
```

Evidence: `class_find_device(tcpc_class, NULL, "type_c_port0", <match fn>)`, `dev_get_drvdata`
(`[dev + 0x98]`), two adjacent byte tests at `tcpc + 0x2c73/0x2c74`, `tcpm_inquire_cc_polarity`,
`snprintf(buf, 0x100, "%d\n", …)`, the `.data` attribute whose name string is `"yft_tcpc_polarity"`
and whose `show` pointer is `.text + 0x12e4`, and the init-time `class_create_file_ns(tcpc_class,
&attr, NULL)` with the error string `"Failed to create device file(sw_ctrl)"`.

Adding this made the defined-function set and the import set **exactly** match stock.

### 5. Stock-target configuration differences

| Symbol | Stock | Notes |
|---|---|---|
| `CONFIG_MTK_TYPEC_WATER_DETECT` | 1 | already proven; kept |
| `CONFIG_RT_REGMAP` | 1 | kept |
| `CONFIG_TCPC_CLASS_MODULE`, `CONFIG_USB_POWER_DELIVERY_MODULE`, `CONFIG_PD_DBG_INFO_MODULE` | 1 | kept |
| `CONFIG_TYPEC_SNK_ONLY_WHEN_SUSPEND` | 0 | new in 2.0.31, default 0 |
| `CONFIG_USB_PD_UFP_FLOW_DELAY` | 0 | stock has no `dpm_reaction_ufp_flow_delay` |
| `CONFIG_SUPPORT_SOUTHCHIP_PDPHY` | undefined | stock has no southchip ops/fields |

### 6. Xiaomi-only code removed (proved absent in stock)

* ops callbacks `enable_io_boost`, `set_watchdog` and wrapper `tcpci_enable_io_boost`
* exported wrapper `tcpci_set_vbus_short_cc_en`
* `get_pd_usb_connected`, `tcpm_inquire_pd_state_curr`
* direct-cap-change (DCC) feature: `tcpm_set_adapter_dcc_support`,
  `tcpm_set_direct_cap_change_over`, `tcpm_get_direct_cap_change_status`,
  `dpm_check_adapter_power_decrease`, the DCC branches in `pd_dpm_pdo_select.c` and
  `tcpm_dpm_pd_request`, the `pd,support-direct-cap-change` DT property, and the `struct pd_port`
  members `last_changed_cap` / `direct_cap_change_support` / `adapter_support_dcc` /
  `direct_cap_change_active` / `dcc_skip_request_cnt`
  (152 bytes — removing them restored `sizeof(struct tcpc_device)` to the stock `0x35a8`)
* the `tcpc->ps_changed = true;` assignment inside `tcpci_check_vbus_valid_from_ic()`

### 7. Exact-GKI compatibility

`class_create("tcpc")` (6.4+ signature used by the 2.0.31 reference) restored to the
android14-6.1 form `class_create(THIS_MODULE, "tcpc")`; stock uses `__class_create` with a module
argument, confirming the same call shape.

## 21-symbol MT6375 ABI table

All 21 symbols are exported and **all 21 CRCs match the stock oracle exactly**.

| Required by `tcpc_mt6375.ko` | Stock CRC | Reconstruction CRC | |
|---|---|---|---|
| `tcpci_alert_wakeup` | `0x0ab94724` | `0x0ab94724` | OK |
| `tcpc_typec_handle_wd` | `0x117b6a26` | `0x117b6a26` | OK |
| `tcpc_device_unregister` | `0x126f9b9b` | `0x126f9b9b` | OK |
| `tcpci_lock_typec` | `0x16e9a06b` | `0x16e9a06b` | OK |
| `tcpm_suspend` | `0x1ccba3ae` | `0x1ccba3ae` | OK |
| `tcpc_get_dev_data` | `0x30745b36` | `0x30745b36` | OK |
| `tcpm_shutdown` | `0x3b13f1ba` | `0x3b13f1ba` | OK |
| `tcpm_check_suspend_pending` | `0x446dd691` | `0x446dd691` | OK |
| `tcpc_typec_handle_otp` | `0x5bcd512c` | `0x5bcd512c` | OK |
| `tcpci_notify_wd0_state` | `0x5f619089` | `0x5f619089` | OK |
| `tcpci_notify_vbus_short_cc_status` | `0x6536e1a8` | `0x6536e1a8` | OK |
| `tcpci_notify_cc_hi` | `0x6f2d399b` | `0x6f2d399b` | OK |
| `tcpci_unlock_typec` | `0x7a0d7b35` | `0x7a0d7b35` | OK |
| `tcpci_alert` | `0x95642690` | `0x95642690` | OK |
| `tcpc_dev_get_by_name` | `0xa4a78f74` | `0xa4a78f74` | OK |
| `tcpc_typec_handle_ctd` | `0xcbe57860` | `0xcbe57860` | OK |
| `tcpc_typec_handle_fod` | `0xcec4c0ab` | `0xcec4c0ab` | OK |
| `tcpc_typec_is_act_as_sink_role` | `0xdad58a05` | `0xdad58a05` | OK |
| `tcpc_device_register` | `0xf0a933ca` | `0xf0a933ca` | OK |
| `tcpm_resume` | `0xf7af27dd` | `0xf7af27dd` | OK |
| `tcpci_is_plugged_in` | `0xff65f0c0` | `0xff65f0c0` | OK |

No CRC table was edited at any point; every CRC shown is the natural genksyms output of the
reconstructed headers. Because genksyms hashes the full expanded type graph, this equality proves
that `struct tcpc_device`, `struct tcpc_desc`, `struct pd_port`, `struct pe_data`, `struct pd_msg`
and every nested type now match the stock definitions member-for-member and name-for-name.

### Fork-only struct members removed (the ABI fix)

Four immediates in the stock `tcpc_mt6375.ko` disassembly (`pd_retry_count` `0x2ffb`,
`disable_pe` `0x2ffc`, `vbus_safe0v` `0x3541`, `typec_cable_type` `0x355c`) proved the
reconstruction's `struct tcpc_device` carried two excess bytes, and four more
(`0x328/0x344/0x35c/0x380`) proved `struct pd_port` carried three excess bytes. All were
MiCode-fork additions absent from both the 2.0.27 donor and the Ulefone stock module:

```c
/* struct tcpc_device */
-	bool pd_ping_event_pending;   /* declared, never referenced in the fork */
-	bool ps_changed;              /* MiCode VBUS ps_changed flow */

/* struct pd_port */
-	bool support_quick_revchg;
-	bool rev_quick_chg;
-	bool support_revcable;
```

with their code removed as well: the two `ps_changed` branches in `tcpci_alert()`, the
`support_quick_revchg` battery-capacity branch and the `pd,support-quick-revchg` /
`pd,support-revcable` DT parsing in `pd_core.c`, and the `rev_quick_chg` 350 ms override in
`tcpc_enable_timer()`. Removing them made 21/21 CRCs match, raised byte-identical functions from
632 to 699, and made `tcpc_mt6375.ko` byte-exact.

## Import table comparison

```text
imports:                 stock 101, reconstruction 101, sets identical
import MODVERSION CRCs:  102 common entries, 0 mismatches
```

The stock-only import `class_create_file_ns` was resolved by reconstructing the Ulefone vendor class
attribute; the reconstruction-only imports of the 2.0.27 baseline (`__pm_relax`,
`pm_wakeup_ws_event`, `wakeup_source_register/unregister`, `devm_power_supply_get_by_phandle`,
`__const_udelay`) disappeared with the 2.0.31 source revision, and the stock-only ones
(`___ratelimit`, `mutex_trylock`, `mutex_is_locked`) appeared with it.

## Additional recovered deltas

| Change | Evidence |
|---|---|
| `typec_lpm_tout = 5000` (fork: `15000`) | stock immediate `0x1388` vs built `0x3a98` in `typec_cc_open_entry`, `typec_unattached_entry`, `typec_unattached_snk_and_drp_entry` |
| `tcpci_alert()` has no `-ENODATA` early return | stock lacks the `tst alert_status, alert_mask; b.eq` pre-check; independently confirmed by stock `mt6375_pd_evt_handler` having no retry loop |
| `pd_put_pd_msg_event()` has no "Drop PING" block | `Drop PING` / `Ignore Ping` strings absent from stock `.rodata.str1.1`; `pd_ping_event_pending` absent from the struct |
| `pd_put_pd_msg_event()` discard path does not `pd_free_event()`+`return false` | stock function is 812 B; fork tail adds 68 B |
| `pd_put_pd_msg_event()` discard condition does not test `pd_msg->frame_type` | stock does not load `[pd_msg + 0]` at that point |
| `tcpci_check_vbus_valid_from_ic()` does not set `ps_changed` | stock keeps the warning log but not the store |

## Function-size comparison

707 of 707 functions present in both; **699 identical sizes and 699 byte-identical** (every
size-matching function is also byte-identical). Residual:

| Function | Stock | Reconstruction | Δ | Identified cause |
|---|---:|---:|---:|---|
| `pd_handle_event` | 568 | 636 | +68 | PD event/ping handling revision |
| `pd_process_protocol_error` | 332 | 388 | +56 | fork's two `PE_INFO("Ignore Ping")` cases absent from stock |
| `tcpc_typec_handle_cc_change` | 1280 | 1312 | +32 | fork's `TYPEC_INFO("RpLvl Alert")` absent from stock |
| `tcpc_store_property` | 656 | 676 | +20 | sysfs store revision |
| `tcpci_alert` | 1936 | 1948 | +12 | residual alert-path revision |
| `pd_process_event_com` | 1836 | 1844 | +8 | ping-event case set |
| `pd_dpm_snk_standby_power` | 280 | 272 | −8 | standby-current expression form |
| `pd_put_pd_msg_event` | 812 | 808 | −4 | discard-path condition form |

The two remaining stock-absent strings (`TCPC-PE:Ignore Ping`, `TCPC-TYPEC:RpLvl Alert`) are the
only real content differences in `.rodata.str1.1`; all other string deltas are the `__FILE__`-
bearing FORTIFY messages that embed the build path.

## `.text` comparison

```text
stock .text : 134 200 B  sha256 087b5c7b823fe6311d37c5d1f9782489c9e022ed37cec8f733eb2b8c6217bb96
final .text : 134 384 B  sha256 43dec274e8944562f8bf91fa607890faa17cf8248fb6af44adf83d4ae17996f2
```

Progression: baseline 2.0.27 +5 464 B → public 2.0.31 +2 112 B → ops/DCC trim +600 B →
struct + ping/alert deltas **+184 B**.

## Remaining differences

1. **Eight function-size deltas** (table above), all localised to the PD event/ping path, the
   Type-C CC-change logger and one sysfs store handler. They are genuine source-revision
   differences between the MiCode 2.0.31 fork and MediaTek's 2.0.31 as shipped by Ulefone; two of
   them are already pinpointed to specific log statements that stock does not contain
   (`Ignore Ping`, `RpLvl Alert`).
2. **`.text` +184 B**, entirely attributable to (1).
3. `.modinfo` `vermagic`/`srcversion`, `.note.gnu.build-id` and symbol-table ordering — build
   environment artifacts, not code.

Critically, none of the residuals touch the ABI: all 21 export CRCs, all 102 import CRCs, the full
function name set, both key struct layouts and the ops table match stock exactly.

## Artifacts

Reconstruction workspace:

```text
/home/armol/kernel-work/gki-12901745-workspace/lieppos/tcpc-class-recon
  baseline/      RED baseline (2.0.27 water-enabled) module, symvers, imports, exports, sizes
  iterations/    iter1-pm, iter2-headers, iter3-full-2.0.31-source, iter4-klee-variant,
                 iter5-dash-variant, iter6-stock-abi-trim, iter7-abi-exact (21/21 CRCs),
                 iter8-ping-alert
  final/         tcpc_class.ko, Module.symvers, Makefile, BUILD.bazel, src/, imports.txt,
                 function-sizes.txt, text.bin, text.sha256, validation.txt,
                 reference-2.0.31-to-final.patch
  check.py       stock-vs-reconstruction validation harness
  fdiff.py       normalized per-function disassembly diff (relocation-resolved)
```

Analysis:

```text
/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/workspace/phase4-tcpc-class-reconstruction
  baseline/  analysis/  iterations/  final/
  final/validation.txt                  full comparison record
  final/reference-2.0.31-to-final.patch  public 2.0.31 → Ulefone reconstruction delta
  final/SHA256SUMS
  analysis/stock.yft_tcpc_polarity_show.txt, stock.init.text.txt, stock.exit.text.txt
```

Public 2.0.31 reference trees (read-only, for provenance):

```text
/home/armol/kernel-work/vendor-reference/MiCode-MTK-kernel-device-modules-chagall-2.0.31
/home/armol/kernel-work/vendor-reference/MiCode-bsp-klee-w-oss
/home/armol/kernel-work/vendor-reference/MiCode-dash-w-oss
```

## Scope compliance

No phone was flashed, no slot switched, no partition, boot, vendor_boot, DTBO or vbmeta touched, the
clean Android device tree was not modified, `pd_dbg_info` was not changed (its reconstructed
`Module.symvers` is consumed unmodified, import CRC `0x48fb7437`), and `tcpc_mt6375` was used only as
a read-only ABI oracle.
