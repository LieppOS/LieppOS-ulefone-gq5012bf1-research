# U23 - eSIM / eUICC presence

**Current claim:** "physical dual-SIM services only" - eUICC presence unknown.

**Previous confidence:** UNKNOWN.

**New evidence - consistent negatives across four independent layers**
1. **No platform feature is declared.** A search of every permissions directory in the stock images (`vendor/etc/permissions`, `system/etc/permissions`, `product/etc/permissions`, `system_ext/etc/permissions`) finds **no `android.hardware.telephony.euicc`** and no `android.hardware.telephony.euicc.mep`.
2. **No LPA / eUICC application ships.** There is no `EuiccSupportPixel`, no carrier LPA, and no `com.android.euicc*` package anywhere in `system`, `system_ext`, `product` or `vendor`.
3. **The only secure-element feature declared is `android.hardware.se.omapi.uicc`** - the removable-SIM OMAPI channel. There is no `android.hardware.se.omapi.ese` and no `.sd`. An eUICC is a form of embedded secure element and would normally appear here.
4. **The OEM's own SIM description is "Nano + Nano + microSD"** - two physical trays plus a dedicated microSD slot, with no eSIM mentioned in any Ulefone or independent listing.

Related hardware context: `MD1-SIM1-HOT-PLUG-EINT` and `MD1-SIM2-HOT-PLUG-EINT` nodes exist for the two physical trays, and NFC off-host routing targets `OFFHOST_ROUTE_UICC = {81, 83}` - two **UICC** routes, i.e. two removable SIMs, not an embedded profile container.

**Contradicting evidence:** none.

**Internet sources:** VI4 (Nano + Nano + microSD), VI6.

**Local evidence:** VL21, VL20.

**Read-only live evidence:** the frozen capture shows two physical SIM slots and no eUICC service.

**Final conclusion**
**The GQ5012BF1 has no eSIM / eUICC and no embedded secure element.** It provides two physical Nano-SIM slots plus a separate microSD slot, with UICC-based OMAPI secure-element access only. Any custom ROM work must assume physical SIMs; adding eSIM in software is impossible without the hardware.

**Final confidence:** **PROVEN absent** (four mutually independent negatives plus the OEM's affirmative alternative description).

**Remaining uncertainty:** none material.

**Impact on final inventory:** YES - the SIM row states the tray configuration positively and the "eSIM unknown" question is closed.

**Answers:** (1) no eSIM, 2 physical nano-SIM + microSD; (2) nothing further; (3) yes; (4) yes; (5) yes; (6) no; (7) none fitted; (8) PROVEN (absent); (9) yes; (10) yes; (11) no.

## Second-pass update (2026-09-08)

Two further runtime negatives (VL28): `telephony.txt` contains **`Euicc enabled=false`**, and the only live
subscription object reports **`isEmbedded=0 isRemovableEmbedded=0`** with `simSlotIndex=0`. With pass 1's
four structural negatives (no `se.omapi.ese` permission, no `android.hardware.telephony.euicc` feature, no
Euicc service, no eUICC ES102-X objects) the verdict is now corroborated at framework-runtime level too:
**no eSIM / eUICC on this device.**
