# gz_main_mod → gz_trusty_mod / gz_ipc_mod transport acceptance

## 1. Method

All transport edges were re-derived independently from the stock
`gz_main_mod` ELF and matched against the export tables of the two
source-closed transport providers. The provider used is the REAL source-built
`//kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/gz-trusty:gz_transport`,
which produces both modules in one invocation.

No stock transport symvers witness participates in this build.

## 2. gz_trusty_mod — 5/5 edges, all NATURAL

| symbol | stock CRC | source-built CRC | call sites | status |
|---|---|---|---:|---|
| `get_smcnr_dev` | `0x5fdc32d1` | `0x5fdc32d1` | 3 | NATURAL_OK |
| `trusty_adjust_task_attr` | `0x756ff09a` | `0x756ff09a` | 2 | NATURAL_OK |
| `trusty_fast_call32` | `0x0c06e871` | `0x0c06e871` | 2 | NATURAL_OK |
| `trusty_nop_set_switch_pri` | `0x124e8423` | `0x124e8423` | 1 | NATURAL_OK |
| `trusty_std_call32` | `0x1816bb67` | `0x1816bb67` | 1 | NATURAL_OK |

The independently derived count is **5**, matching the previously recorded
gz_trusty_mod consumer-edge figure for this module.

Usage:

* `get_smcnr_dev` — maps a device to its SMC number space; used by the version
  query and the SDSP path.
* `trusty_fast_call32` — the fast SMC used by `mtee_sdsp_enable`.
* `trusty_std_call32` — the standard (sleeping) SMC used by `get_gz_version`.
* `trusty_adjust_task_attr` — applied by `gz_adjust_task_attr`, which first
  guards on `IS_ERR_OR_NULL(tz_system_dev)` and then passes
  `tz_system_dev->dev.parent`.
* `trusty_nop_set_switch_pri` — the `TRUSTY_NOP_SET_PRI` ioctl.

## 3. gz_ipc_mod — 1/1 edge, NATURAL

| symbol | stock CRC | source-built CRC | call sites | status |
|---|---|---|---:|---|
| `tipc_set_default_cpumask` | `0xdabdc7b5` | `0xdabdc7b5` | 1 | NATURAL_OK |

The independently derived count is **1**, and the symbol matches the
previously recorded edge exactly.

Sole call site: `gz_manual_adjust_trusty_wq_attr`, reached from the
`MTEE_CMD_ADJUST_WQ_ATTR` ioctl. It pushes
`manual_task_attr.mask[TRUSTY_TASK_KICK_ID]` down to the TIPC layer as the
default kick cpumask. This is a global tuning knob, not a per-session
operation — `gz_main_mod` never opens or manipulates a TIPC channel directly.

## 4. Combined result

**6/6 transport edges NATURAL. 0 witnesses. 0 mismatches.**

## 5. Effect on the transport stack

None. Building `gz_main_mod` does not modify, rebuild or re-link
`gz_trusty_mod` or `gz_ipc_mod`. Both remain `DIRECT_SOURCE_MATCH /
FROZEN FOR RE`, and the 738/738 transport stack verifier continues to pass
unchanged.
