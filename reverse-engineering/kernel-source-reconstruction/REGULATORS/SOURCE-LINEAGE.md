# Public source lineage

The authoritative audit pointed to NothingOSS957dac185efe46cbf6336b0fff9516d84c8cd78f,
not a proven stock build. Existing ALPS5e415e059253ce0d2e61c97108e5f5785d71f06f was examined
because it already explained unrelated storage/clock/pinctrl stock implementations; those
components were not rebuilt or edited.

| Main C file |5e41 blob|957dac blob|Outcome|
|---|---|---|---|
|mt6315-regulator.c|be53b4271d4feaf56dea87a8a76198e3d331f89a|a4d1597f1a3bed7f188f31b29b3361aea46825fa|different n_voltages|
|mt6363-regulator.c|1069f505b7ed29646c732e147441dca3df50a345|same|identical main C|
|mtk-dvfsrc-regulator.c|f19e3702d4dc4863b507fda7494a16bf9a6912b9|same|identical main C|
|rt6160-regulator.c|3bc7f00f21a68eeb6ed208bb8a41d764f2dae8f4|same|identical main C|

The only main-C diff between these pins is MT6315 MT_BUCK.n_voltages0xc0→0xbf.
5e41 represents192 selectors,0..191,6,250µV steps, encoded range0..1,193,750µV.
957dac has191 descriptors but the same0..191 linear-range endpoints. This is behavior-bearing
descriptor data, not ignorable metadata; 5e41's complete compiled module matches stock.
No claim is made that the newer full donor build was stock-accepted.

All48 functions and174 data objects in the chosen four outputs are stock-exact. The binary
oracle establishes which public implementation belongs to GQ5012BF1; commit proximity,
matching function size and the PMIC's marketing name alone would not establish this.
No missing implementation, Ulefone-specific C delta or equivalent rewrite was needed.

Ulefone-specific power configuration belongs to the stock DT, not a C patch: MT6319@6
parent with MT6315_6-compatible child, buck-size4/mask1 override, declared rail/consumer
relationships, two RT6160 nodes, and MT6878 DVFSRC profile. Generic other PMIC slaves,
SSHUB descriptors and other SoC DVFSRC voltage tables remain reference capabilities, not
instantiated hardware claims. Exact DT evidence and conflicts are in the power documents.
