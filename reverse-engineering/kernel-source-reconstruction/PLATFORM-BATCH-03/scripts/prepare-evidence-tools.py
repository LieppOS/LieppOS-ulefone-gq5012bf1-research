#!/usr/bin/env python3
from pathlib import Path
P=Path(__file__).resolve().parents[1];H=P.parent/'PLATFORM-BATCH-02'
t=(H/'scripts/map-hardware.py').read_text().replace("'selected':27","'selected':34").replace('emi|dramc|smpu|pmif|spmi|sspm|mcupm|mailbox|mbox|tinysys|bp-thl|battery.*thrott|lbat|lvsys','thermal|lvts|temp|cpufreq|dvfs|dcm|cm-mgr|clkbuf|dcxo|watchdog|wdt|pmif|spmi|mt63|mt66|sspm|scmi|tinysys|charger|cooling|pbm|peak|qos|cpu|aee|mrdump')
(P/'scripts/map-hardware.py').write_text(t)
t=(H/'scripts/cleancheck.sh').read_text().replace('Eight','Ten').replace('four','five').replace('joint27','joint34').replace('BATCH02','BATCH03').replace('batch-02','batch-03').replace('JOBS=8','JOBS=12');(P/'scripts/cleancheck.sh').write_text(t)
t=(H/'scripts/check-determinism.py').read_text().replace('range(4)','range(5)').replace('==27','==34').replace(':27',':34').replace(':44',':89').replace(':19',':31').replace('PASS_ALL27_FOUR_INDEPENDENT_FAMILY_ENGINES_B1_B2','PASS_ALL34_FIVE_INDEPENDENT_FAMILY_ENGINES_B1_B2').replace('all_four_recipe_paths_unavailable_during_eight_compilations','all_five_recipe_paths_unavailable_during_ten_compilations').replace("'fresh_committed_source_clones':4","'fresh_committed_source_clones':5").replace("'fresh_complete_compilations':8","'fresh_complete_compilations':10").replace('all_27_accepted_each_run','all_34_accepted_each_run');(P/'scripts/check-determinism.py').write_text(t)
print('Prepared saved-hardware and ten-build independent verification tools')
