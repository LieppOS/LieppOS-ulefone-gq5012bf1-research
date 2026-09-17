# Slot-B apexd investigation boundary

Static Slot-B diagnosis has moved to apexd after the direct vold daemon
reboot hypothesis was demoted.

Current B has explicit apexd-related init failure/reboot authorities which must
be distinguished from ordinary APEX activation errors and from rollback/revert
logic.

This investigation records:

- exact current-B apexd init definitions;
- exact current-B apexd binary identity;
- direct shared-library resolution;
- current-B preinstalled APEX/CAPEX inventory;
- shared `/data/apex` and `/metadata/apex` state metadata;
- Android-15 apexd reboot/revert semantics;
- preserved TIER3 failure evidence.

Previous work already established an important shared-state fact for
Tethering: a decompressed APEX cache filename includes package name and
version, and apexd validates cached decompressed APEX identity before reuse.
The working-A Tethering cache therefore could not be silently substituted for
B's different-version Tethering package.

No conclusion that apexd caused the Slot-B reset is made until the newly
captured evidence is reviewed.
