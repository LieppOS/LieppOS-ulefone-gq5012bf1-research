# Shared Tethering decompression cache branch closed

Exact Android 15 apexd production source establishes that:

`GetPackageId(manifest) = name + "@" + version`

Current Slot B ships:

`com.android.tethering@352090000`

Therefore its normal decompression-cache path is:

`/data/apex/decompressed/com.android.tethering@352090000.decompressed.apex`

Working Slot A currently has:

`/data/apex/decompressed/com.android.tethering@361099999.decompressed.apex`

These are different package IDs and different filesystem paths.

Additionally, the live shared `/data/apex/active` directory contains no APEX
files at all. Therefore there is no higher-version Tethering data APEX entering
normal `AddDataApex()` / `SelectApexForActivation()` selection.

The v361 decompressed APEX is not considered a normal data APEX. The exact
apexd implementation explicitly treats decompressed files separately.

For a compressed preinstalled APEX, `ProcessCompressedApex()` constructs the
cache filename from that CAPEX's own package ID and validates any matching
candidate against:

- bundled public key
- exact manifest version
- CAPEX `originalApexDigest`

Current B's CAPEX expected digest is:

`90bdb41cfbca2972205415394c7fa5b785e636bff8be76195d4dc5489f2f9738`

and its extracted original APEX has that exact AVB root digest.

Conclusion:

The stock-A v361 decompressed Tethering cache cannot be selected as B's v352
decompression candidate and there is no active data-APEX override.

Shared stale Tethering decompression-cache reuse is CLOSED as an explanation
for the Slot-B boot failure.

The remaining Tethering/BPF question is limited to B's own v352 payload and
whether its netbpfload invocation succeeds on this device.
