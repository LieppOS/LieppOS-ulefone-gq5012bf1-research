# U18 - Bluetooth revision, LE Audio and Auracast

**Current claim:** "service exists but BT disabled" - revision and LE Audio capability unknown.

**Previous confidence:** UNKNOWN.

**New evidence**
* **OEM specification**: Ulefone states **Bluetooth 5.4** for this model.
* **Controller identity**: the connectivity companion die is the **MT6637** (`vendor.connsys.wifi.adie.chipid = 0x6637`, `vendor.connsys.gps.adie.chipid = 0x6637`), and the Bluetooth firmware images shipped in `vendor/firmware/` are `soc7_0_ram_bt_1_1_hdr.bin`, `soc7_0_ram_bt_1a_1_hdr.bin`, `soc7_0_ram_bt_1b_1_hdr.bin` with matching `soc7_0_ram_mcu_*` images.
* **No external Bluetooth front-end module is fitted** (see `connfem-selected-fem.md`): the runtime ConnFem result is `nofem`, and the Bluetooth stack logged `CONNFEM BTvid/pid == 0, ignore`. BT therefore runs on the ADIE's internal PA/LNA.
* The Bluetooth radio was **off** for the whole capture (`conninfra ... BT&WIFI is off, schedule pre-cal`, `bgfsys_power_off`), so **no HCI feature mask, no LE feature page and no supported-commands bitmap were ever read**.
* **The LE Audio properties in the snapshot are not evidence about this device.** `bluetooth.profile.bap.unicast.client.enabled`, `bap.broadcast.source.enabled`, `bap.broadcast.assist.enabled`, `csip.set_coordinator.enabled`, `mcp.server.enabled`, `ccp.server.enabled` and `vcp.controller.enabled` were all read from the **LieppOS GSI system image**, not from Ulefone's stock build (see `00-snapshot-provenance-correction.md`). They describe AOSP/Lineage defaults, not the vendor's configuration and not the controller's capability.

**Contradicting evidence**
The original hidden-capability report listed "BT LE Audio/Auracast" as an unverified possibility on the strength of those properties. That basis is now invalid: the properties came from a GSI. The claim is neither confirmed nor refuted - it is simply unevidenced.

**Internet sources:** VI1, VI4 (Bluetooth 5.4).

**Local evidence:** VL5, VL25; firmware inventory in `vendor/firmware/`.

**Read-only live evidence:** none usable - the radio was powered off.

**Final conclusion**
* Bluetooth is provided by the **MT6637 companion die with no external FEM**, and the OEM specifies **Bluetooth 5.4** - LIKELY at the controller level, since 5.4 is an OEM claim that no local artefact corroborates.
* **LE Audio / Auracast capability is UNKNOWN.** Bluetooth 5.4 support is a necessary but not sufficient condition: LE Audio needs LE Isochronous Channels in the controller **and** vendor enablement in the stock stack, and neither was observable.

**Final confidence:** controller identity + no external FEM = **PROVEN**. Bluetooth 5.4 revision = **LIKELY** (OEM claim only). LE Audio / Auracast = **UNKNOWN**.

**Remaining uncertainty and how to close it (all read-only):** enable Bluetooth on the **stock** system, then capture `dumpsys bluetooth_manager`, an HCI snoop log containing `LE Read Local Supported Features` and `Read Local Supported Commands`, and check for the `bluetooth.profile.bap.*` properties in the *stock* property set. That sequence settles both the revision and LE Audio without any write operation.

**Impact on final inventory:** YES - the LE Audio entry in the hidden-capability report is re-based on the GSI caveat, and the capability matrix Bluetooth row is corrected to say the radio was never observed active.

**Answers:** (1) MT6637 BT, no FEM, OEM says 5.4; (2) HCI feature masks from stock; (3) no; (4) yes - enabling BT and dumping is read-only; (5) partially (OEM claim only); (6) no; (7) MT6637 integrated Bluetooth, revision 5.4 per OEM; (8) PROVEN controller / LIKELY revision / UNKNOWN LE Audio; (9) yes; (10) yes; (11) yes.
