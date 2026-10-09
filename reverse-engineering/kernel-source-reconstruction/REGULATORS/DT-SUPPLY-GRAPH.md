# Stock device-tree supply graph and consumer contracts

Operands: SHA-bound merged stock DTB + independent preserved live device-tree tar,
listed in evidence/hardware/mapping-summary.json. No new capture or DT modification.
All76 regulator-name nodes and48 genuine regulator-phandle supply relationships are
retained.42 nodes belong to these four driver scopes;32 supply links target them.
All target controller/descendant properties match across static/live operands:402/402.
114 independent fdtget crosschecks verify all target voltage constraints and supply handles.
84 source/DT checks match exact case-sensitive of_match/descriptor identities and voltage
intervals (82 voltage witnesses, two current-only ISINK nodes with no voltage constraint).

Full tables: DT-RAILS.tsv, DT-SUPPLIES.tsv, DT-SOURCE-CHECKS.tsv, CONTROLLERS.json,
PARENT-RESOURCES.json and SOURCE-DESCRIPTORS.json under evidence/hardware/.
Every node's parent-effective availability and raw flags/config are retained. A legal
selector within an interval is a configuration-consistency witness, not a measurement.

## Main configured relationships

| Regulator output / phandle | Configured interval (µV) | Consumer/property |
|---|---:|---|
|mt6363_vemc /0xb7|1200000..3500000|UFS.vcc-supply; MMC0.vmmc-supply|
|mt6363_vufs12 /0xb8|550000..1850000|UFS.vccq-supply|
|mt6363_vufs18 /0xdb|600000..2100000|MMC0.vqmmc-supply|
|mt6363_vbuck5 /0x47|300000..1193750|cpuhvfs.proc1-supply and proc3-supply|
|mt6363_vbuck6 /0x48|300000..1193750|cpuhvfs.proc2-supply|
|6_vbuck2 /0xc1|300000..1193750|gpufreq.vgpu-supply|
|mt6363_vsram_cpum /0xc2|400000..1193750|gpufreq.vsram-supply|
|6_vbuck1 /0x4d|300000..1193750|power-controller.isp-main-supply/cam-main-supply; vmmspm.vmm-pmic-supply; mmdvfs-debug.vmm-pmic-supply|
|6_vbuck4 /0x62|300000..1193750|dvfsrc-helper.vcore-supply; mmdvfs-debug.vcore-supply|
|dvfsrc-vcore /0x61|575000..725000|mmdvfs, display/SMI display, seninf-top, MMC0, venc/jpgenc, MML, MDP(two references), DVFSRC helper/MET, usb-boost-manager|
|mt6363_vbuck2 /0xba|300000..1193750|mddriver.md-vmodem-supply|
|mt6363_vsram_modem /0xbb|400000..1193750|mddriver.md-vsram-supply|
|mt6363_vbuck1 /0xbc|300000..1193750|mddriver.md-vdigrf-supply|
|mt6363_isink_load /0xe6|current-only, no voltage interval|MT6375 auxiliary ADC.isink-load-supply|

Long consumer paths and exact property names for every link are in DT-SUPPLIES.tsv; no
edge is inferred from a rail name alone. Target controllers supply no declared upstream
vin-supply relationships, so their input PCB power paths remain UNKNOWN. RT6160's two
configured outputs have no phandle/standard supply consumer; fixed3.25V is a node constraint,
not a measured output. MT6315 VBUCK3 and MT6363's three SSHUB descriptor variants have no
rail DT child; source registration attempts do not establish physical output usage.

## Important consumers and explicit limits

- **UFS / MMC:** VEMC and VUFS12 feed the configured UFS relationships above. The actual
  UFS voltage/settings/rail-enable sequencing must be confirmed separately. MMC0 is
  enabled in static DT but **disabled in the preserved live tree**; all its three links
  are SOURCE_REFERENCE_ONLY for that live operand. MSDC1's removable-card behavior must
  not be assigned MMC0's supplies just because both controllers use the same driver.
- **CPU:** proc1/3 share vbuck5; proc2 uses vbuck6. This table does not guess cluster
  operating voltages or which OPP vote is currently active.
- **GPU:** configured vgpu=slave6.vbuck2, vsram=MT6363.vsram_cpum; the name cpum does not
  authorize relabelling it as exclusively a CPU rail.
- **APUSYS/NPU:** MT6363.vsram_apu is declared0.4..1.19375V but has no standard supply
  consumer in the complete scan. Firmware/by-name power votes remain UNKNOWN; don't
  invent an APUSYS edge from the descriptor's name.
- **Camera ISP / camera domain:** cam-main/isp-main point to6_vbuck1, plus seninf DVFSRC
  voting. These are domain/request links, not the sensor analogue/I/O LDO topology.
- **Camera sensors:** existing canonical RT5133 work identifies WL2864C/WL2868C rather
  than RT5133 as the board LDO role. Neither is part of this four-module scope. Sensor
  names/voltage requests hidden behind ODM camera helpers are not invented here.
- **Display:** dispsys, MML/MDP and display SMI consumers vote through logical DVFSRC.
  LCD bias/backlight/AVDD/IO supplies are distinct out-of-scope providers.
- **Touch/NFC/audio/sensors:** no target standard supply edge is recorded. Other regulators
  and OEM GPIO/by-name control paths remain in existing canonical component research;
  absence of a target phandle edge is not proof of no electrical relationship.
- **USB:** usb-boost-manager's dvfsrc-vcore vote is explicit; it is not USB VBUS voltage
  and does not establish which physical boost converter drives USB power.
- **Connectivity/modem:** modem's three supplies are explicit. MT6363 VCN/VRF names alone
  do not establish connectivity PCB wiring or use, especially where firmware manages it.

## Clock and power-domain context

DT-CLOCK-POWER-REFERENCES.tsv follows provider-specific cell counts for clocks,
power-domains and interconnects of target controllers, their bus parents and supply
consumers:131 static /262 static+live references, all provider handles resolved.
RT6160 I2C5 bus clocks point to syscon0x11281000(specifier0) and0x11036000(specifier17);
I2C6 uses0x11e04000(specifier1) and0x11036000(specifier17). Display SCPSYS domain8,
VENC/JPEG9, modem0, SENINF13/3 and display SMI7 are explicit device-domain links.
These are configured dependencies, not clock-enable/power-state measurements. The four
regulators themselves import no clock API; bus/domain frameworks and DVFSRC policy are
separate from direct PMIC selector operations. Resolving a handle does not certify its
provider source or prove the domain is active.

## Avoiding false graph edges

120 properties end in `-supply`, but only48 reference a regulator-name node. SMI properties
often reference device phandles/arrays and `irtx-pwm.pwm-supply` is a by-name string.
They are retained with reference_kind, not treated as malformed regulators or physical rails.
A scalar such as I2C address0x48 can numerically equal a regulator phandle; all such
coincidences in DT-OTHER-RAIL-REFERENCES.tsv are explicitly **not reference evidence**.
Raw integer equality is never sufficient to create an edge.

No selected DT descriptor-name or voltage-interval conflict was found. Stock doesn't
select MT6363 STANDBY mode3, although its generic of_map_mode/set_mode pair is inconsistent
there. No DT was changed to hide that source-reference limitation. Runtime bindings for
PMIC/regulator platform devices remain UNKNOWN, and both RT6160 clients were unbound in
one preserved capture. Always-on/boot-on flags are per-node configuration, not status.
