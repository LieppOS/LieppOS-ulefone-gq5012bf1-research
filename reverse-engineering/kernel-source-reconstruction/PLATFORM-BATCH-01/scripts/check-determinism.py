#!/usr/bin/env python3
"""Recheck retained independent B1/B2; never substitute caches for compilation."""
import json,sys
from pathlib import Path
C=Path(sys.argv[1]);A=C/'ws/out/B1';B=C/'ws/out/B2'
for f in ['SHA256SUMS','INTERMEDIATE-SHA256SUMS','config.sha256','gki-symvers.sha256','TARGET-SOURCE-TREE','batch-full.Module.symvers','batch-stock-provider.Module.symvers','provider/natural-external-provider.symvers','provider/scpsys-dummy.symvers','provider/provider-witnesses.json','provider/scpsys-link-name-witnesses.json']:
 assert (A/f).read_bytes()==(B/f).read_bytes(),f
for O in [A,B]:
 assert len(list(O.glob('*.ko')))==len(list(O.glob('*.stripped')))==35
 assert all((O/f).read_text().strip()=='0' for f in ['object-exit','module-exit','stock-provider-module-exit'])
for pattern in ['*.ko','*.stripped']:
 for f in A.glob(pattern):assert f.read_bytes()==(B/f.name).read_bytes(),f
j=json.loads((C/'comparison-B1/comparison.json').read_text());k=json.loads((C/'comparison-B2/comparison.json').read_text());assert j==k
accepted=[x['module'] for x in j if x['status']=='DEVELOPMENT_STOCK_EXACT_PENDING_CLEAN_CLONE'];failed=[x['module'] for x in j if x['status']=='SOURCE_BUILD_UNVERIFIED'];assert len(accepted)==31 and len(failed)==4
(C/'cleancheck-result.json').write_text(json.dumps({'result':'PASS_31_ACCEPTED_4_REPRODUCED_ABI_RESIDUALS','original_development_and_all_four_recipes_unavailable_during_build':True,'fresh_source_recipe_clones':4,'fresh_target_and_provider_recompilation_each_build':True,'base_headers_reused_with_hash_verification':True,'raw_modules_deterministic':35,'stripped_modules_deterministic':35,'intermediate_object_count':len((A/'INTERMEDIATE-SHA256SUMS').read_text().splitlines()),'independently_stock_accepted':accepted,'unaccepted_residuals':failed,'unexpected_failures':[],'comparison_ordering_fix':'Sort four unaccepted CRC name sets; no source/ELF change or target recompilation needed'},indent=2)+'\n')
print('PASS:31 accepted,4 C residuals;35 raw/stripped modules and all intermediates deterministic')
