# Function containing “non ISO_DEP and non Mifare”

## Identification

- Binary: `analysis/st21-gemini-audit/runtime-blobs/libnfc_nci_jni.so`
- SHA-256: `b11bdea0ac537778f437810d43133f1f5b9240383c639d308e551a71b921cd8e`
- String file/VA: `0x7dc16`
- Source function: static `nativeNfcTag_doConnect(JNIEnv*, jobject, jint targetIdx, jboolean force)`
- Source: `aosp-reference/packages-modules-Nfc/NfcNci/nci/jni/NativeNfcTag.cpp:542-625`; relevant branch at lines 580-605.
- Inferred installed code extent: `0x13a4f4` through terminal/unreachable block at `0x13b008`; next prologue begins `0x13b00c`.
- Exact disassembly: `evidence/non-isodep-non-mifare.disasm.txt`.

The local function is stripped from the ELF symbol table, so LLVM labels it as part of the nearest preceding exported symbol. The identification is instead based on the unique string xref, matching control flow, JNI method name/signature (`doConnect`, `(IZ)I`), and source correspondence. A previous note incorrectly called `0x13a7e8` the JNI method entry; that address is inside this function, not its start.

## Caller and important callee

Java reaches it through `com.android.nfc.dhimpl.NativeNfcTag.doConnect(int, boolean)` from the tag endpoint connect flow. The native method can call static `reSelect(tNFA_INTF_TYPE, bool)`, which deactivates and reselects a discovered remote tag on the requested RF interface.

## Control-flow summary

Source-equivalent behavior:

```cpp
sCurrentConnectedTargetType = natTag.mTechList[targetIdx];
sCurrentConnectedTargetProtocol = natTag.mTechLibNfcTypes[targetIdx];

if (sCurrentConnectedTargetProtocol != NFC_PROTOCOL_ISO_DEP &&
    sCurrentConnectedTargetProtocol != NFC_PROTOCOL_MIFARE &&
    sCurrentConnectedTargetProtocol == sCurrentActivatedProtocl) {
  // log unique string and return success without reselection
}

if (target type is ISO14443-3A or ISO14443-3B) {
  if (protocol != MIFARE) intfType = NFA_INTERFACE_FRAME;
} else if (target type is MIFARE_CLASSIC) {
  intfType = NFA_INTERFACE_MIFARE;
} else {
  intfType = NFA_INTERFACE_ISO_DEP;
}
retCode = reSelect(intfType, force);
```

## Exact comparison evidence

At `0x13a970`, the installed function first compares the current protocol with immediate `0x04` (`NCI_PROTOCOL_ISO_DEP`). If unequal, it enters the out-of-line branch:

```asm
13aa50: ldrb w11, [x11, #0x5]  ; p_nfa_proprietary_cfg->pro_protocol_mfc
13aa58: cmp  w8, w11            ; current protocol vs configured MIFARE (0x90)
13aa5c: b.eq 0x13a980           ; MIFARE: continue to interface selection
13aa64: ldrb w11, [x11, #0x6c4]
13aa68: cmp  w8, w11            ; current vs sCurrentActivatedProtocl
13aa6c: b.ne 0x13a980           ; different protocol: reselect
```

The final load at `0x13aa64` is `sCurrentActivatedProtocl`, as required by the matching source condition. A previous draft incorrectly annotated it as another ISO-DEP load.

## Classification

**STATIC IMPLEMENTATION — reader/poller-side tag connection handling.**

- `0x90` is checked dynamically via byte 5 of `p_nfa_proprietary_cfg`.
- MIFARE Classic target type selects interface `0x90` and invokes `reSelect`.
- ISO-DEP selects interface `0x02`.
- Other protocols already active on the current interface return success without reselection; if the requested protocol differs from the active one, reselection continues.

Nothing in this function handles Listen-A activation, host card emulation, PICC-side authentication, or card-side Crypto1. It proves reader-side use of protocol/interface `0x90`, not MIFARE Classic PICC support.
