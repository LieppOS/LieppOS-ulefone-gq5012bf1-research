#!/usr/bin/env python3
"""Source-reproduction mixedclassification gate; strictverifier remainsUNCHANGED."""
from pathlib import Path
import sys,subprocess,csv,json,os
R=Path(__file__).resolve().parents[1];out,stock,report=map(Path,sys.argv[1:4]);report.mkdir(parents=True,exist_ok=True);plan=json.loads((R/'reference/acceptance-plan.json').read_text());results={}
for row in csv.DictReader((R/'reference/stock-normalized.tsv').open(),delimiter='\t'):
 m=row['module'];assert (out/(m+'.ko')).exists() and (out/(m+'.stripped')).exists(),'Complete targetnotbuilt '+m
 p=subprocess.run([sys.executable,str(R/'scripts/verify.py'),str(out),str(stock),str(report/m)],capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',LIEPPOS_VERIFY_MODULE=m));(report/(m+'-strict.log')).write_text(p.stdout+p.stderr);accepted=m in plan['A'];assert (p.returncode==0)==accepted,(m,'Unexpectedstrictresult',p.stdout,p.stderr);results[m]=dict(stock_acceptance='PASS' if accepted else 'REJECT_NOT_WAIVED',strict_exit=p.returncode,proposed_class='A' if accepted else 'C',source_reproduction='Complete raw/stripped present; independentB1/B2 allaxes stillrequired',residual=plan['C'].get(m,'GNU20only'))
assert set(results)==set(plan['A'])|set(plan['C']);(report/'MIXED-RESULTS.json').write_text(json.dumps(dict(result='PASS_EXPECTED_MIXED_RESULTS',modules=results),indent=2)+'\n');print(json.dumps(results,indent=2))
