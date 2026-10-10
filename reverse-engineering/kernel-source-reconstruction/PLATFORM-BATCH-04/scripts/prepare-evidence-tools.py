#!/usr/bin/env python3
"""Saved capture/source graph tools scoped to actual30 charging/Type-C/USB IDs."""
from pathlib import Path
P=Path(__file__).resolve().parents[1];H=P.parent/'PLATFORM-BATCH-03'
t=(H/'scripts/map-hardware.py').read_text().replace("'selected':34","'selected':30").replace('thermal|lvts|temp|cpufreq|dvfs|dcm|cm-mgr|clkbuf|dcxo|watchdog|wdt|pmif|spmi|mt63|mt66|sspm|scmi|tinysys|charger|cooling|pbm|peak|qos|cpu|aee|mrdump','usb|xhci|mtu3|phy|typec|tcpc|pd-manager|charger|charging|mt6375|battery|gauge|extcon|usmart|tiny2c|pe[0-9]|otg|mux|vbus|adsp|iommu');(P/'scripts/map-hardware.py').write_text(t)
t=(H/'scripts/provider-graph.py').read_text().replace('platform-batch-03-cleancheck','platform-batch-04-cleancheck').replace('android_kernel_modules_secure_diagnostics_ulefone_gq5012bf1','android_kernel_modules_charging_battery_ulefone_gq5012bf1').replace('All1434 imports','All1912 imports');(P/'scripts/provider-graph.py').write_text(t)
print('Prepared source/DT/import-export ledgers for actual30; no live commands')
