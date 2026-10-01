# ST21NFC firmware loader — Rev 2 (reproducible recovery + review of Rev 1)

Phase 4b re-work of [`firmware-loader.md`](firmware-loader.md) (Rev 1) and
review of `../../firmware-binary-audit.md` §6.3. Every fact below is derived from
**files committed in this repo**, and one command regenerates every artifact it
cites (host binutils/LLVM, 5 s wall-clock):

```sh
cd hardware/nfc && sh tools/st21-fw-loader-reproduce.sh   # rewrites audit/* from runtime-blobs/*
```

Single queries, if only one claim is disputed (`$B` =
`analysis/st21-gemini-audit/runtime-blobs/nfc_nci.st21nfc.st.so`):
`tools/st21-fw-loader-recovery.py $B` (call graph of the download region),
`tools/st21-data-graph.py $B '^(loader|s_|DW)'` (data-symbol contents),
`tools/st21-annotate.py $B xref 'STNFC_FW_PATH_STORAGE|patch NFC FW'` (string
xrefs), `tools/st21-loader-tables.py $B` (patch descriptors).

Reproduction status of the 10 committed artifacts in `audit/`: the 8 that existed
before this revision (`fw-loader-recovery.tsv`, `fw-loader-xref.txt`,
`fw-path-literals.txt` and all five `disasm/dump-*.txt`) regenerate
**byte-identically**; `loader-tables.txt` differs from its previous copy only by
the deliberate `_size_tab` fix in §4; `fw-loader-data-graph.txt` is new here. The
script is idempotent — a second run is byte-identical to the first (5 s wall
clock). The input blob `runtime-blobs/nfc_nci.st21nfc.st.so`
(MD5 `fda028cf6cc2a0a359d9681eb2330f46`) is byte-identical to
`blobs/nfc_nci.st21nfc.st.so` and to the V15 stock `vendor/lib64/` copy, so there
is exactly one HAL generation behind every claim here.

## 1. Provenance: which generation, and what is actually reproducible

The device has two stock vendor generations in this workspace, and Rev 1 mixed
them up.

| Generation | Where it lives now | Status |
|---|---|---|
| FGV / BSP vendor (`/tmp/gq5012bf1/extract/vendor`, MD5-listed in Rev 1 §2.1) | **gone** — `/tmp` is wiped; no copy anywhere under `~/androido_dalykai` | Rev 1 §2.1 unverifiable, non-reproducible |
| V15 stock dump `m170b-gq-…V15_user_20251022` | `workspace/gq5012bf1/stock/partitions/{vendor,system,system_ext,…}` (2 830 vendor files) + `stock/images` → symlink to the retained `*_a.img` EROFS set | **reproducible**; re-extractable from `vendor_a.img` (1 283 530 752 B) |
| Runtime HAL blobs | committed in `runtime-blobs/` | 3 of 7 byte-identical to the V15 vendor copy |

`runtime-blobs/` is mixed, and that matters when attributing behaviour:

| blob | MD5 | == V15 vendor copy? |
|---|---|---|
| `nfc_nci.st21nfc.st.so` | `fda028cf6cc2a0a359d9681eb2330f46` | **identical** |
| `android.hardware.nfc-service-st` | `0fc8cafeb1c82cbae4ebc3b9abc5fffe` | **identical** |
| `android.hardware.nfc-V1-ndk.so` | `5f916d37b02d7e2ba5c2b416cd9c7321` | **identical** |
| `libstnfc-nci.so` | `55bfd2ddf54c68e77cfa39c7f88c16a5` | absent from the persisted vendor snapshot; shipped copy is `system_ext/lib64/libstnfc-nci.so` |
| `libstnfc_nci_jni.so`, `libnfc_nci_jni.so`, `com.st.android.nfc_extensions.jar` | (see `evidence/runtime-blob-metadata.tsv`) | system/system_ext-side stack, not vendor |

V15 `vendor/firmware/` holds **only** `st21nfc_fw.bin` + `st21nfc_fw7.bin` (both
215 568 B) for NFC. Rev 1's FGV set additionally had 16 `ST22NPFw_*.bin`, an
`unmanaged/ST22NPFw_Clock_patch_SMD5_S32S4.bin`, `libnfc_hal_dnld.so`,
`libunlzodecompress.so` and `liblzo2.so`; **none of those exist in V15** and none
are recoverable in the repo. Any conclusion resting on them is generation-specific.

## 2. Corrected Rev 1 §2 — where the loader actually lives

Rev 1 §2 attributed the loader to `libnfc_hal_dnld.so` + `libstnfc-nci.so` and
listed `hal_fd_load_files`, `ft_DownloadFirmwareUpdate`, `NfcMfwUpdate`,
`HAL_FD_FILE_ERROR`. On the persistent V15-generation stack:

- **`nfc_nci.st21nfc.st.so` (237 exports, not stripped) owns the whole
  firmware-download + patch path.** Its internal log tag literals name the
  routine `hal_fd_load_files` *inside this blob* — so Rev 1's function naming was
  right, but there is no separate `libnfc_hal_dnld.so` in this generation:
  `readelf -d libstnfc-nci.so` `NEEDED` lists no `libnfc_hal_dnld.so` and no
  `libunlzodecompress.so`; it needs `libz.so` only.
- The Java/JNI-facing layer is `NfcAdaptation::DownloadFirmware()`
  (`libstnfc-nci.so` @0x182d10, MTK source
  `vendor/mediatek/proprietary/hardware/stnfc/src/adaptation/NfcAdaptation.cc`),
  whose only literals are `"%s; enter"`, `"%s; try open HAL"`, `"%s; try close HAL"`,
  `"%s; nfcc_power_mode=%d"`. It gates the download on NFCC power mode and hands
  off to the HAL — it never names a file.
- Call graph of the HAL region `[0x218a8, 0x237f0)` (`ft_cmd_HwReset` … the start
  of `BackToFactoryLoaderIfPossible`; ~8 KB of inlined `HAL_FwDownload`): 117
  `bl` sites, and after `.rela.plt` resolution they are
  `__android_log_print` ×66, `GetStrValue` ×5, `fread` ×4, `fclose` ×3,
  `fopen` ×2, `fgetpos` ×2, `__strlcpy_chk` ×6, `__strlcat_chk` ×4,
  `__strlen_chk`, `stat`, `fsetpos`, `fgets`, `memset`, plus the ST helpers
  `HalSendDownstreamTimer` ×10, `I2cResetPulse`, `AuthCheckUnload`,
  `AuthCheckCoreResetNtf`, `hal_wrapper_set_state`.
  → Real file I/O (`fopen`/`fread`/`fgetpos`/`fsetpos`/`stat`) plus
  `CNfcConfig::GetStrValue`-style conf lookups. This is what Rev 1 §5 summarised
  as "no fopen anywhere", which held only for the lost FGV blob set.

## 3. Corrected Rev 1 §3 — the config chain *is* present

Rev 1 §3 concluded "the firmware loader is driven by `DTB_*` keys … those keys do
not exist on this device" and listed the shipped keys as an afterthought. On V15
the shipped `vendor/etc/libnfc-hal-st.conf` keys are exactly the ones the loader
reads, in this order (line numbers from the persisted copy):

```
107:STNFC_FW_PATH_STORAGE="/vendor/firmware/"
109:STNFC_FW_CONF_STORAGE="/vendor/etc/"
111:STNFC_FW_BIN_NAME="st21nfc_fw7.bin"
112:STNFC_FW_CONF_NAME="st21nfc_conf.txt"
 19:STNFC_FW_DEBUG_ENABLED=1
```

and `hal_fd_load_files` consumes them with per-key fallbacks (from
`audit/fw-loader-recovery.tsv`):

| call site | callee | literal primed at the call site |
|---|---|---|
| 0x21cf0 | `GetStrValue` | `STNFC_FW_PATH_STORAGE` |
| 0x21d3c | `__strlcpy_chk` | `/vendor/firmware/` (fallback when the key is absent) |
| 0x21d50 | `GetStrValue` | `STNFC_FW_CONF_STORAGE` → fallback `/vendor/etc/` |
| 0x21db0 | `GetStrValue` | `STNFC_FW_BIN_NAME`, defaults `{st54j_fw.bin, st21nfc_fw7.bin, st21nfc_fw.bin, st54l_fw.bin}` |
| 0x21e84 | `GetStrValue` | `STNFC_FW_CONF_NAME`, default `st21nfc_conf.txt`; alternate pattern `st21nfc_conf_%s.txt` |
| 0x220a4 / 0x22440 | `fopen(…, "r")` | `"%s - FW update file = %s"`, `"%s - FW config file = %s"` |
| 0x220e8 … 0x22638 | log | `"%s - %s file detected."`, `"text configuration detected."`, `"custom configuration not detected."`, `"-> bin configuration CRC 0x%04X ."`, `"-> txt configuration CRC 0x%04X ."`, `"configuration file name not recognized."` |
| 0x223ac → 0x223f0 | `fgetpos` → log | `"generic"`, `"RA7"`, `"%s --> %s integrates patch NFC FW version 0x%08X (r:%d,t:%s)."`, `"%s --> %s integrates unknown patch NFC FW -- rejected."` |
| 0x227d8 … 0x229a0 | log | `"Loader update available, do this first.."`, `"No loader currently active, enter loader mode to reactivate factory loader.."`, `"Loader mode and no applicable FW patch available.."`, `"No update for this hardware version.."`, `"FW patch needs to be applied.."` |

So: the loader is conf-driven (`STNFC_FW_*`, not `DTB_*`), it can take a **binary
or a text** firmware-config descriptor (both CRC-checked), and the device is
explicitly configured for `st21nfc_fw7.bin`. Rev 1's "the loader is driven by
DTB_* keys that do not exist here" framing was an artefact of the FGV/eSE
variant; the live chain here is fully specified.

## 4. New (decisive) — the patch payload is embedded in the HAL blob

`nfc_nci.st21nfc.st.so` exports its patch tables as *data* symbols:

| symbol | section | value / extent |
|---|---|---|
| `loader_RA7_patch_version` | `.rodata` 0x8c0c | `0x20201` |
| `loader_RA7_patch_cmd_nb` | `.rodata` 0x8c10 | `0x6c` (108) |
| `loader_RA7_patch_AuthKeyId` | `.rodata` 0x8c14 | `0x2` |
| `loader_RA7_patch` | `.rodata` 0x8c18 | `nm -D -S` size **24 610 B** (window to the next symbol ≤ 24 612 B) |
| `loader_RA7_patch_size_tab` | `.rodata` 0xec3c | 108 B, **96 of them `0xf8`** — see below |
| `loader_RA9_patch_{version,cmd_nb,AuthKeyId}` | `.rodata` 0xeca8… | `0x20301`, `0x6c`, `0x1` |
| `loader_RA9_patch` / `_size_tab` | `.rodata` 0xecb4 / 0x14cd8 | 24 610 B / 108 B (same `0xf8` filler) |
| `loader_patch{,_cmd_nb,_AuthKeyId,_size_tab}` | `.bss` 0x290dc, 0x290e0, 0x290e8, 0x290f0 | zero-filled → runtime slots |
| `loader_patch_version` | `.data` 0x27ed0 | `0xffffffff` — sentinel "nothing selected yet" |

Two things make "embedded payload" more than a name-based guess, and both are in
`audit/fw-loader-data-graph.txt`:

- **The windows are payloads, not indirection tables.** `loader_RA*_patch` and
  `_size_tab` have **0** entries in `.rela.dyn`, so nothing external is written
  into them at load time — a pointer array in a PIE `.so` would have to be
  relocated. Both payloads open with a firmware record header
  (`2f 04 15 80 32 00 00 10` = LE `0x8015042f, 0x10000032`) and their bodies are
  high-entropy, unlike the 0-relocation *string* tables in the same section.
- **`_size_tab` is a label, not a spec.** The two 108 B windows (= `cmd_nb`) that
  follow the payloads are byte-identical to each other, `0xf8`-padded (96/108)
  and hold only 6 distinct u32 values: tail padding, not per-chunk sizes.
  Reading them as u32 sizes is meaningless, which is exactly the mistake the
  earlier `loader-tables.txt` made ("sum = 101 495 841 160 bytes"); the tool now
  prints the window's raw words instead of summing them.

The same record tag `2f 04 15 80` (= LE `0x8015042f`) heads both patch payloads
at offset 0 *and* occurs exactly three times in each shipped container: at `0x4`
(word1), at `0x1c` (12 B into the body, i.e. a second record) and at `0x349f8` =
`size − 24`, i.e. a trailer. Container headers are
`magic 0x80922001, 0x8015042f, 0x10000088, <per-image word>`
(`st21nfc_fw.bin` → `0x90fe2552`, `st21nfc_fw7.bin` → `0x0022e84f`).

Consequences for Phase 4:

1. **Rev 1 §6.4 / Q3's blocker is not supported.** "No `ST22NPFw_*.bin` patch
   file is present, therefore patching is blocked" applied to a *different*
   (ST21-eSE/DTB) variant. For this device the RA7/RA9 patch content ships
   **inside** `nfc_nci.st21nfc.st.so`, keyed by a per-variant `AuthKeyId`
   (RA7→2, RA9→1), selected into the runtime `loader_patch*` slot.
2. The gate is *selection*, not file absence: `"Loader update available, do this
   first."`, `"FW patch needs to be applied."`, `"No update for this hardware
   version."`, `"…integrates unknown patch NFC FW -- rejected."`.
3. `PREINIT_COLD_SHUTDOWN_PATCHDOWN=TRUE` (Rev 1 §1) is still the enable bit, and
   `loader_patch*` being `.data`/`.bss` (written at init, not `.rodata`) matches a
   loader that *populates* that slot at boot rather than shipping it const.

## 5. Container format — correction of `firmware-binary-audit.md` §6.3/§7

Observed on the two **V15** images (identical sizes, both 215 568 B = 0x34a10):

| field | `st21nfc_fw.bin` | `st21nfc_fw7.bin` |
|---|---|---|
| word0 | `0x80922001` | `0x80922001` |
| word1 | `0x8015042f` | `0x8015042f` |
| word2 | `0x10000088` | `0x10000088` |
| word3 | `0x90fe2552` | `0x0022e84f` |
| payload @16 (16 B) | `0e13fe2dff3104e7fada39432f041580` | `97dede0fbfa0e485fe098cc72f041580` |
| payload entropy | 7.9852 bits/byte, 256 distinct bytes, 27 adjacent-zero pairs in 215 552 | 7.9850, 256, 26 |
| diff vs each other | **207 709 of 215 568 bytes differ** | (Rev 1 §7: "differ by one 4-byte word at 0x000100A0" — true only for the lost FGV pair) |

Corrections:

- **word1 is not a firmware version and is not `decompressed_length`.**
  Rev 1 §2.2 recorded "`decompressed_length`: both `0x34a10` (= file size —
  header already counted…)" *and* "`firmware version`: `0x80150000` vs
  `0x800e0000`" for the FGV pair — arithmetically the first is just the file
  size restated. On V15 word1 is `0x8015042f`, which is exactly the address that
  heads both embedded patch payloads (§4): it is a **target load address**, and
  `0x8015_0000` / `0x800e_0000` on the FGV pair are two different banks — i.e.
  that field distinguished *which controller/RAM bank* the image targets.
- **The §6.3 LZO decision procedure cannot have been applied as described.**
  Rev 1 §6.3 "Decoded LZO1X at offset 16: succeeds, `decompressed_length =
  0x34a10`" contradicts "`decompressed_length` … (= file size)": a body whose
  stored length already equals the declared output length is not compressed.
  Independently, no header field is a plausible LZO output size for the 215 552 B
  payload (word2 `0x10000088` is not), and the recorded destination bound
  `LZO_max_dest_size = 0x40000` caps expansion at 1.21×, which is impossible for
  a 7.985 bits/byte body.
- **Verdict on the disputed README claim**
  ("ST21 firmware is either LZO-compressed or uncompressed with 0x80922001
  magic", `REVERSE-ENGINEERING-STATUS.md:595`): **keep the claim, downgrade the
  evidence to PARTIAL.** The magic and the record/TLV framing of word1/word2 hold
  on durable bytes; whether the payload is LZO-compressed remains **unresolved**
  and must not be asserted. `lzop` and `python3-lzo` are both absent here, so a
  real decode needs a bundled LZO1X-1 decoder first — until then §6.3's
  "both are LZO-compressed inside a 16-byte header" is a hypothesis, and
  "plaintext LZO inside LZO → `-5`" proves only that the payload is not *raw*
  LZO (consistent with either an encrypted or a per-record compressed layout).

## 6. Answers to Rev 1 §5

1. **Does the flag open a patch path?** Yes, and far more strongly than Rev 1
   claimed: `PREINIT_COLD_SHUTDOWN_PATCHDOWN=TRUE` gates `hal_fd_load_files`,
   which does real `fopen`/`fread` of `STNFC_FW_PATH_STORAGE + STNFC_FW_BIN_NAME`
   = `/vendor/firmware/st21nfc_fw7.bin` plus a CRC-checked binary-or-text config
   (`STNFC_FW_CONF_STORAGE + STNFC_FW_CONF_NAME` = `/vendor/etc/st21nfc_conf.txt`),
   and falls back to embedded RA7/RA9 patch payloads.
2. **Which decompression is required?** Unknown — unresolved per §5. The V15 HAL
   core links `libz.so` (zlib/gzip) and no LZO helper, which is *counter*-evidence
   to Rev 1's LZO framing but does not by itself prove the payload format.
3. **Can a patched/rebuilt firmware image be produced?** Re-derivable inputs now:
   the two 215 568 B images (MD5 `352ed0cdce339c172bfd1dd5a83e14ae` /
   `119f62d525a0b8ee4c8ca0319895d394`), the 24 612 B embedded RA7/RA9 patch
   payloads with `(version, cmd_nb, AuthKeyId)` = `(0x20201, 108, 2)` /
   `(0x20301, 108, 1)`, and `st21nfc_conf.txt`. Remaining blocker: no CRC-verified
   write path in the HAL (see `../../REPORT.md` §5), and the payload format of §5.
4. **Patch-file availability vs the loader** — resolved: not required for this
   variant (§4). Rev 1's `unmanaged/` suggestion is moot here; it stays relevant
   only if a FGV-generation vendor image is re-extracted from `stock/images`.

## 7. Review of `../../firmware-binary-audit.md` §6.3 (requested)

| aspect | verdict |
|---|---|
| "LZO1X-1 + 16-byte header" model | **Unsupported.** Header word1 is a load address; no field is a plausible LZO output size. Mark hypothesis, not finding. |
| "uncompressed fallback exists" (code path present) | **Supported** and independent of the above: `stat`/`fopen`/`fread`/`fgetpos`/`fsetpos` plus a CRC-checked bin-or-text config path exist in the shipped loader. |
| `LZO_max_dest_size = 0x40000`, `LZ4_max_1X_output_size = 0x34a25` | Constants likely transcribed correctly, but their *inference* ("so LZO is real") fails: 0x40000/215 552 = 1.21× cannot hold for a 7.985 bits/byte payload. Keep as buffer bounds only. |
| "`st21nfc_fw.bin` and `fw7.bin` same size" | **Supported** (both 215 568 B on V15) — but the *reason* is a fixed-size load-bank image, not compression to an exact size; on V15 the two differ in 207 709 bytes. |
| binwalk "no lzo/echo plugin" → must decode manually | **Correct**, and still the gating step: no LZO tool is installed here (`lzop` absent, `import lzo` fails). |

## 8. Evidence added by this revision

- `audit/fw-loader-recovery.tsv` — 117 call sites of the firmware-download
  region with PLT-resolved callees and the string literal primed at each site;
  regenerate with `tools/st21-fw-loader-recovery.py`.
- `audit/fw-loader-xref.txt` — string→function xrefs for the FW path/patch/
  factory-loader literals; regenerate with `tools/st21-annotate.py … xref`.
- `audit/fw-loader-data-graph.txt` — per-data-symbol contents with a `.rela.dyn`
  cross-check (`tools/st21-data-graph.py`). This is the artifact that decides §4:
  0 relocations inside the patch windows ⇒ payload, not pointer array; and the
  `_size_tab` windows are `0xf8` padding, not sizes.
- `audit/disasm/dump-0x{176d0,17b00,218a8,237f0,23900}.txt` — per-function
  listings (`tools/st21-annotate.py … dump <addr>`), tracked.
- `audit/disasm/*.text.asm` — the raw `llvm-objdump -d` corpus they are cut from
  (~15 MB, git-ignored by `hardware/nfc/.gitignore`, regenerated as an
  intermediate by the reproduce script).
- `tools/st21-annotate.py` — fixed: `xref` no longer resolves its regex as a
  symbol name, `index`/`calls` added, and PLT stubs are now resolved through
  `.rela.plt` (previously every libc call degraded to `<local>`).
- `tools/st21-loader-tables.py` — fixed: reports the patch/`_size_tab` windows as
  raw words; the previous `u32` sum over `_size_tab` was a category error (§4).
- `tools/st21-fw-loader-reproduce.sh` — one command regenerates all of the above.
