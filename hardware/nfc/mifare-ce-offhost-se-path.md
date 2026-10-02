# MIFARE Classic card emulation — the off-host (SWP-CLT) path

Date: 2026-10-02
Status: **addendum + partial correction** to
`analysis/st21-mifare-ce-qwen-bad-report/REPORT.md` and to §8 / §11 of
`st21nfc-current-findings.md`.

Scope: read-only re-derivation from already-captured artifacts (stock vendor
images + on-device logcat/dumpsys already in this repo) plus ST primary
sources. **No new device-side write was performed.** No firmware or config was
modified.

---

## 1. Why this addendum exists

The earlier MIFARE-CE report concluded:

> **Conclusion**: **MIFARE Classic PICC/card emulation is NOT supported** on
> this platform. The Android NFC stack (NFA_CE module) has no T2T listen mode
> infrastructure, and no vendor-specific path exists to enable it via static
> configuration.

That conclusion is correct **for the question it actually asked** — can the
Android *host* (HCE / `NFA_CE`) emulate a MIFARE Classic PICC? It cannot, and the
report's stack trace (§2–§5 there) is the evidence.

But the report's own grep surface never contained the words `SWP`, `CLT`,
`secure element`, `UICC`, or `off-host`:

```text
$ grep -n 'SWP\|CLT\|secure element\|SE\b\|UICC\|license\|off-host\|offhost' REPORT.md
(no output)
```

ST's MIFARE card-emulation feature is **not** a host-CE feature. It is an
*off-host* feature: the CLF relays the 14443A/MIFARE listen-direction traffic
to a **secure element** over SWP/CLT (ETSI-SWP), and the emulation state machine
plus the MIFARE keys live **inside the SE**. So "no `NFA_CeT2t*` functions" does
not falsify the capability — it is evidence about a different transport. The
earlier verdict is therefore **narrowed, not kept**: *host-side* MIFARE CE is
impossible; *SE-side* MIFARE CE was never evaluated and is still open.

---

## 2. What ST actually documents (primary sources)

| Source | Verbatim | Reading |
|---|---|---|
| ST21NFCJ product page <https://www.st.com/en/secure-mcus/st21nfcj.html> | "Active mode – Card Emulation – ISO/IEC 14443 Type A & B – JIS X 6319 – 4 – **MIFARE Classic(a)(b) through SWP-CLT**" (same wording reproduced in third-party manuals of ST-based designs) | MIFARE CE on this family is defined **through SWP-CLT**, i.e. SE-transported. |
| ST21NFCJ product page | "The product can come with MIFARE Classic. The availability of the **MIFARE Classic R/W mode** feature depends on the license conditions." | The licence caveat is scoped to **R/W (reader) mode**, not to CE. |
| ST21NFCL data brief <https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/7130/st21nfcl.pdf> | "card emulation mode – ISO/IEC 14443 Type A & B – FeliCa™ – Intelligent card switching – **MIFARE® (1)**" / footnote "1. MIFARE **R/W mode** feature availability is pending on license conditions." | Confirms the footnote attaches to R/W only; CE lists MIFARE unconditionally. Also: "**SWP master interfaces** up to 1.695 Mbit/s: – **2 SWP UICC support** – **1 SWP for external SE support**". |
| ST54L data brief <https://newsroom.st.com/wp-content/uploads/2023/11/Databrief-for-ST54L-NFC-controller.pdf>, ST54L product page | "ST54L is a single-die solution integrating a contactless front-end (ST54L_CLF) and a **secure element (ST54L_SE)**"; CE bullets list "MIFARE®", and the part is described with "**MIFARE Classic®1 cryptography hardware** a…". | In the ST54J/L/K generation the SE die is on the same die as the CLF and carries MIFARE crypto hardware — i.e. MIFARE CE is an SE feature of the silicon, not a missing CLF feature. Note our HAL probes `st54j_fw.bin` / `st54l_fw.bin` alongside `st21nfc_fw*.bin` (see `analysis/st21-gemini-audit/audit/fw-path-literals.txt`), so this HAL generation serves exactly those CLF+SE parts. |

Consequence: the user's premise is right at the silicon level. ST21/ST54 do have
MIFARE emulation capability. What the earlier report proved is only that this
board exposes none of it **through Android**.

---

## 3. What this board actually has (our own evidence)

From `analysis/mifare-090-nfc-startup.txt` (stock runtime, NFC open sequence) and
`blobs/st21nfc_conf.txt` (shipped controller config, byte-identical to V15 stock
vendor):

| Captured fact | Value | Meaning for the SE path |
|---|---|---|
| `NFA_EeGetInfo` | `nfcee_id=0x81 ee_status=0x1`, `nfcee_id=0x82 ee_status=0x1`, `nfcee_id=0x10 ee_status=0x0` | Two real SEs enumerate and **enable**: 0x81 = UICC, 0x82 = eSE. 0x10 is the virtual/host-side NDEF-CE endpoint used by the proven T4T path. |
| `OFFHOST_ROUTE_UICC=8183`, `OFFHOST_ROUTE_ESE=82`, `DEFAULT_OFFHOST_ROUTE=0x81`, `OFF_HOST_ESE_PIPE_ID=0x5E` | 2 UICC ids + 1 eSE id + an eSE **pipe id** | Matches the CLF's documented "2 SWP UICC + 1 SWP external SE" topology exactly. The SE transports are provisioned, not vestigial. |
| `UICC_LISTEN_TECH_MASK = 0x07` | A \| B \| F listen for the UICC | The **listen-direction** tech mask towards the SE already includes NFC-A/14443-3A — the carrier under which MIFARE CE is activated. Transport-ready. |
| `HOST_LISTEN_TECH_MASK = 0x3` | A \| B for the host | Host CE has no proprietary/MIFARE dimension — and there is **no bit in this vocabulary for a protocol**, only for technologies. So "flip the config bit" is not expressible; nothing to flip here. |
| `RoutingManager::updateEeTechRouteSetting: Default route A/B: 0x0`, `EE[0] Handle=0x0410 … seTechMask[0]=0x00`, `Default SC route=0x81`, `dumpsys nfc` → `Default route: host`, `Routed to 0x10:` | SEs get **AID/APDU-level** routing only; **no technology-level listen route** is programmed for 0x81/0x82. | This is the real software gap on this build — and unlike "the code path is absent", a tech-route is a *configuration* surface. |
| `NCI_SEND_PROP,0F,02,0400100100…` / `…1001 01…` (`REM Writing CustomA RF Parameters`, `CustomB`) in `st21nfc_conf.txt` | RX/listen RF parameters per technology are programmed | The CLF's listen-mode RF layer for 14443-A is configured, as expected. |
| `NCI_DIRECT_CTRL,2F,02,04000A01001A48…` (`REM UICC CONFIG`) and `04000B01001A48…` (`REM SE CONFIG`), identical 26-byte payloads | Vendor CLT/SE config written at init | The vendor-specific SE/CLT parameter block **is** present and **is** CRC-checked only (Phase 4b Q8) — i.e. editable in principle. It contains no MIFARE-CE enable bit; it is timing/interface config, not an applet. |
| T4T NDEF emulation on an NFCEE — **runtime proven end-to-end** (`st21nfc-current-findings.md`) | external reader reads the phone's emulated Type-4 tag; survives NFC toggle and reboot | The **off-host CE plumbing itself works on this board**. MIFARE CE is the same class of feature with a proprietary protocol instead of ISO-DEP — so this is a *provisioning* problem, not a plumbing problem. |

---

## 4. Revised verdict

| Path to "emulate a MIFARE card" | Verdict | Why |
|---|---|---|
| **A. Android host / HCE (any app, or a patched `libnfc_nci_jni.so`)** | **NO — architectural** | `NFA_CE` has no MIFARE/T2T listen path, and even with the bits force-patched there is no Crypto-1 engine and no key store on the host side; the SE applet is where the state machine lives. Earlier report §5/§8.2/§10.3 stands for this path. |
| **B. Off-host SE through SWP-CLT (0x81/0x83 UICC, or 0x82 eSE)** | **NOT TESTED — the only live route** | Silicon + CLF transport + listen tech mask + pipes all present (§3). Missing piece is entirely on the SE: an applet implementing MIFARE emulation **with NXP-provisioned MIFARE keys**, plus a technology-level listen route (`seTechMask` currently `0x00`). |
| **C. Patch the controller firmware (`st21nfc_fw.bin`/`_fw7.bin`) to unlock it** | **NO — not a lever** | The loader path is auth-gated in controller ROM (Phase 4b: erase → activate loader → **auth** → exit-loader on a 100 ms timer, `0x80922001` / `0x8015042f` framing); we cannot produce an accepted payload, and MIFARE CE keys/state do not live in CLF firmware anyway. The RA7/RA9 24 610 B blobs inside the HAL are ST's own patches for their RA FW. |
| **D. Patch `st21nfc_conf.txt` (vendor config)** | **NOT SUFFICIENT, but harmless to try** | HAL gates configs on CRC16 only, not a signature (Phase 4b Q8), so edits are *accepted*; but the config vocabulary has no MIFARE-CE enable. At most it could carry CLT/RF parameters. Do not expect an unlock. |
| **E. Don't emulate MIFARE — present a tag a reader can read** | **ALREADY PROVEN** | Type-4 NDEF emulation on the NFCEE works on this device today, externally readable, reboot-stable. Use this for any "phone as badge/tag" goal unless the target reader specifically requires MIFARE crypto. |

---

## 5. The actual blocker on path B

1. **Keys, not code.** MIFARE Classic emulation needs NXP-licensed key material
   provisioned into the SE. That is a provisioning/licensing fact, independent of
   this ROM. Nothing we build changes it.
2. **Which SE is reachable by us.**
   * `0x82` eSE: present and enabled at NCI level, but writing a MIFARE-emulation
     applet needs GlobalPlatform SCP08x keys we do not have. Effectively blocked.
   * `0x81` / `0x83` UICC (SIM1/SIM2): the realistic target — a **programmable
     Java Card test UICC** with an ETSI-SWP/CLT MIFARE-emulation applet is exactly
     how commercial "NFC-SIM" MIFARE services work. Requires lab hardware
     (test card + typically a shell/APDU toolchain) and is *not* a ROM change.
3. **Route programming.** Even with such an SE, this build programs the SEs with
   AID routing only (`seTechMask[0]=0x00`, `Default route A/B: 0x0`), so the
   listen-direction, protocol-level route to the SE must be programmed (host
   `RF_SET_LISTEN_MODE_ROUTING_CMD` path, HAL string at `0x5c0b`, or a vendor NCI
   command) for the CLF to hand MIFARE frames to the SE in listen mode.

---

## 6. Cheap read-only experiments that would close the remaining UNKNOWNs

All observation-only; nothing destructive; ordered by cost.

1. **Dump the controller's own config back out** — `CORE_GET_CONFIG` / the HAL's
   `getConfig` path over the already-parsed tags (`0x0A` UICC CONFIG, `0x0B` SE
   CONFIG) and diff against `blobs/st21nfc_conf.txt` payloads. Answers "does the
   CLF hold a MIFARE-listen route entry that Android never programs?"
2. **`dumpsys nfc` full route table + `NFA_EE_DISCOVER_REQ_EVT` for *every*
   NFCEE** (our capture only printed `0x410`). If `0x81`/`0x82` discovery maps
   carry a proprietary protocol (`0x90` per
   `NFA_PROPRIETARY_CFG=05FFFF068A9077FFFF`) in listen direction, path B is
   closer than it looks.
3. **Passive observation with an ST25-based reader** (Flipper/ACR122/ST25R
   discover): bring the phone near a *reader that only speaks MIFARE* in listen
   direction and capture whether the CLF answers a 14443-3A ATTR/SELECT while the
   SE is powered. Distinguishes "CLF silently ignores MIFARE CE" from "CLF hands
   it to an empty CLT channel".
4. Only after 1–3: consider a programmable test UICC. Until then, no config or
   firmware edit is justified.

---

## 7. Claims to keep out of the record

* Do **not** write "ST21 supports MIFARE CE, so it is available on this phone".
  The datasheet describes the *part*; this build has no SE-side MIFARE applet and
  no SE tech route (§3, §5).
* Do **not** write "MIFARE CE is impossible on this hardware". The earlier
  report's evidence does not cover the off-host path it never examined.
* MIFARE **reader** mode is a separate, proven-working feature
  (`pollTech=0x2f`, `nfa_rw_check_mifare_data()`, real-card tests) and is
  unaffected by everything above.

## 8. External references checked 2026-10-02

* ST21NFCJ product page — <https://www.st.com/en/secure-mcus/st21nfcj.html>
* ST21NFCL data brief (PDF) — <https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/7130/st21nfcl.pdf>
* ST54L product page — <https://www.st.com/en/secure-mcus/st54l.html>
* ST54L data brief (PDF) — <https://newsroom.st.com/wp-content/uploads/2023/11/Databrief-for-ST54L-NFC-controller.pdf>
