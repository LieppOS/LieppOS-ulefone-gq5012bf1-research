#!/usr/bin/env python3
"""Adapt existing complete source-symbol graph, preserving core/runtime uncertainty."""
from pathlib import Path
P=Path(__file__).resolve().parents[1];H=P.parent/'PLATFORM-BATCH-02';t=(H/'scripts/provider-graph.py').read_text().replace('All898 imports','All1434 imports').replace('platform-batch-02-cleancheck','platform-batch-03-cleancheck').replace('android_kernel_modules_memory_platform_ulefone_gq5012bf1','android_kernel_modules_secure_diagnostics_ulefone_gq5012bf1')
t=t.replace("'source_revision':'5e415e059253ce0d2e61c97108e5f5785d71f06f','source_definition':r['candidate_directory']", "'source_revision':r['public_source_commit']+' plus full preserved patches at owned source commit','source_definition':r['candidate_directory']")
(P/'scripts/provider-graph.py').write_text(t)
print('Prepared actual1434-import source dependency ledger tool')
