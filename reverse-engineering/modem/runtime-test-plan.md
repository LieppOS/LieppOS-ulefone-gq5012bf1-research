# Future read-only runtime validation plan

Not executed during this offline/static pass. Requires explicit authorization and a stock boot.
No RF state changes, calls, modem reset, SIM changes or writes are permitted.

## Safety gate

* Do not use service-call/AT/MIPC ioctls, sysfs writes, flight-mode toggles, network attachment,
  packet generation, call/SMS actions or NVRAM tools.
* Never print/capture IMEI, IMSI, ICCID, phone numbers, subscriber/carrier identifiers or NVRAM
  contents. Redact properties/log lines before storage.
* Prefer existing captures. If a new capture is approved, use shell-readable metadata only.

## Read-only checks

| goal | safe source | expected static prediction |
|---|---|---|
| module/load state | `/proc/modules`, `/sys/module/<name>`, `dmesg` filtered to driver init only | 16 modules as packaged; c2k USB function activity may vary |
| CCCI boot | read `/sys/kernel/ccci/{version,lk_md,md_en,boot}` and property names only | MD1 gen6299, READY after HS1/HS2 |
| LK tags / smem | read `/proc/ccci_dump` sections limited to layout/address metadata; do not retain payload bytes | 28 tags, base 0xbfdf0000, cache/non-cache layout matching DT |
| port nodes | `find /dev -maxdepth 1` names/mode/owner only | nodes in `kernel/ccci-port-map.tsv`; dynamic major/minors |
| netdevs | `/sys/class/net/ccmni*/{mtu,queues/*/rps_cpus}` and `/proc/interrupts` names/counters | ccmni0–7,9–20; rps mask 0d; one active DPMAIF RX IRQ |
| DPMAIF | read `/proc/dpmaif_debug` only if it is side-effect free on the tested build; otherwise skip | v3, 4 TX queues, 1 RX queue |
| SIM topology | framework dumpsys output with all identifiers/redacted | two removable DSDS slots, no embedded slot |
| IMS capability | package/service declarations and CarrierConfig booleans with carrier IDs redacted | VoLTE/WFC/ViLTE enabled by SKU config; registration state must not be captured |
| RF-set straps | GPIO debug name/direction/value only if permitted and no pin export/write is needed | GPIO99/100 levels would identify selected board strap, but decoding still needs authorized DRDI docs |
| exception path | existing historical crash logs only | mdee v6 + AEE/proc/mrdump route; never force an exception |

## Acceptance

Runtime validation may confirm initialization and topology. It cannot improve source parity (already
exact) and must not be used to reverse/circumvent signed MD firmware or inspect private NV.
