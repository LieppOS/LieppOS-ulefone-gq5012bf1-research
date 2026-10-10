# Batch03 charger declaration and parent boundaries

The selected charger-cooling consumer now passes whole stock ELF acceptance; MT6375
parent/MFD and SPMI ADC source are independently reproduced too. This does not close
`charger_class`, `mtk_charger_framework`, `mtk_chg_type_det`, MT6375 charger/battery
or the Type-C/USB child modules.

The batch preserves genuine full historical charger C inputs, their SHA256s and
exact declaration line provenance. A freshly compiled declaration-only witness
regenerates the narrow source-derived external CRC slots. Nothing is assigned an
invented CRC, and narrow symbol agreement never promotes the whole provider.

Evidence: ../kernel-source-reconstruction/PLATFORM-BATCH-03/evidence/PROVIDER-GRAPH.tsv,
evidence/source-preservation-result.json, HARDWARE-CONTRACT.md and the maintained
recipes' reference/charger-declaration-provenance.json.33 consumers pass complete
stock acceptance; common ADC remains C for 21 BTF reference bytes.

Use the completed parent APIs for the proposed next charging/Type-C/USB preservation
batch; inspect historical whole implementations before new reverse engineering.
Existing component ownership/status and electrical/firmware/runtime limits remain
unchanged. No charger, USB role, mailbox, voltage or current control was exercised.
