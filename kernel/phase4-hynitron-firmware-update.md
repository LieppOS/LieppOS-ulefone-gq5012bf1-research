# CST816D/CST816T/CST820 firmware/update contract

## Embedded images

Extracted verbatim from stock `.data`:

| object | stock offset | size | SHA256 | table use |
|---|---:|---:|---|---|
| `cst8xx_fw` | `.data+0x240` | 15419 | `0566ea7799d6f8bbce026639d9dbb89f0e629ab533d1d90e4901c81d5611e1d8` | CST816D `0xb6`/module 4 and CST820 `0xb7`/module wildcard |
| `cst816t_fw` | `.data+0x3e7b` | 15410 | `0d02fde67223c1e7aa6c4ce1d1e522bcbe79d4d58decf1aa79b865cb2e504de3` | CST816T `0xb5` |

Files are under `workspace/phase4-hynitron/firmware/`. Both contain a 0x3c00
(15360-byte) controller payload plus six metadata bytes and a non-NUL source
filename. Names are
`CSW_2205166_CST816D_SGD_FC_F013362_SHDZ_YJZN_S105.hex` and
`CSW_2302271_CST816T_DWS_XPD_T9_QCG_C3315.hex`; metadata/checksums at 0x3c00
are `00000000068b` and `000000002c3b`.

## Stock decision logic

Probe first reads running project/module/version/checksum with `0xa6`. Only if
that normal read fails does it attempt the stock CST8xx ROM-presence handshake
(`0xa001=0xaa`, poll `0xa003==0x55` up to ten times) and reset back to normal
mode. The later probe-time `hyn_update_firmware_init` re-reads identity and
resolves the configured chip table row, but does not call image selection.

Image selection occurs only when `hyn_boot_update_fw` is invoked through the
stock sysfs/debug path. It attempts project/chip matching across ten 24-byte
slots (three populated), falls back to configured-chip matching, stores the
selected name/data/length, disables IRQ, marks update work mode, and calls
`cst8xx_firmware_info`; it then restores normal work mode/IRQ. CST820 selects
the CST816D-family payload through the `0xb7` wildcard entry. The source names
encode package revisions; running version remains authoritative for YFT display.
No evidence supports forced downgrade.

## Critical negative finding: programmer absent

The frozen module defines `hyn_update_firmware_init`, `hyn_boot_update_fw`,
`hyn_find_fw_idx` and `hyn_detect_bootloader`, but has **no erase/program-block/
status-poll/checksum-verify function**. A complete relocation-aware enumeration
of every call to all I2C helpers finds no payload programming loop, no flash
address progression, and no checksum command. `hyn_boot_update_fw` is selection
and decision scaffolding only. Thus erase command, block size, program delay,
program status and retry count are **NOT PRESENT IN THIS ELF**. Importing a donor
programmer would add hardware behavior and is forbidden.

## Reconstruction safety

`HYNITRON_ALLOW_FW_PROGRAMMING` is defined to 0 by default and asserted by the
verifier. Stock-compatible sysfs selection paths may return success, but the
default build has no erase/program call and cannot write an image. Raw-register
and bootloader-presence interfaces remain structurally stock-compatible; none
was exercised. Even an explicit programming opt-in cannot invent a missing
programmer: the gated branch returns `-ENOSYS`. The exact embedded images and
selection algorithm remain present for evidence/future authorized work. No
live update/reset/write was executed during research.
