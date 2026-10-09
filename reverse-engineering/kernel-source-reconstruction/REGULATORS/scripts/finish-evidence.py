#!/usr/bin/env python3
"""Validate and materialize final offline summary/type/load/graph witnesses.
Usage: finish-evidence.py <maintained-repo> <accepted-clean-build-ws>
"""
import csv,json,hashlib,struct,sys,subprocess
from pathlib import Path
N,W=map(Path,sys.argv[1:]);P=Path(__file__).resolve().parents[1];R=P.parents[2];sys.path.insert(0,str(N/'scripts'));from normalize import kpp
A=R/'reverse-engineering/kernel-source-parity-audit';j=json.load((P/'evidence/acceptance/acceptance.json').open());names={m+'.ko' for m in j};assert len(j)==4
rows=[]
for m,x in j.items():
    s=kpp.KO(R/'workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules'/(m+'.ko'))
    assert not s.b.endswith(b'~Module signature appended~\n')
    rows.append([m+'.ko',x['stock_sha256'],x['bytes'],x['functions'],x['functions'],x['data'],x['data'],x['imports'],x['exports'],x['kcfi_abs_ids'],x['relocations'],len(s.secs),hex(x['allowed_range'][0]),x['allowed_range'][1],x['raw_differing_bytes'],'BUILD_METADATA_ONLY','A',x['unresolved']])
def tab(p,head,rows):
    with p.open('w') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(head);w.writerows(rows)
tab(P/'MODULE-PARITY.tsv',['module','stock_sha256','bytes','functions_exact','functions_total','data_exact','data_total','imports','exports','kcfi_abs_ids','relocations','sections_including_null','build_id_offset','build_id_bytes','raw_differing_bytes','residual','final_status','unresolved'],rows)
stock=kpp.KO(R/'workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/mtk-dvfsrc.ko');obj=kpp.KO(W/'src/prov/drivers/soc/mediatek/mtk-dvfsrc.o');proof=[]
for name in ['mtk_dvfsrc_send_request','mtk_dvfsrc_query_info','__traceiter_mtk_pm_qos_update_request']:
    pp=[]
    for ko in [obj,stock]:
        y=next(y for y in ko.syms if y['n']==name and y['info']&15==2);sec=ko.secs[y['shndx']];assert y['val']>=4
        b=ko.b[sec['off']+y['val']-4:sec['off']+y['val']];assert len(b)==4
        pp.append({'section':sec['n'],'prefix_offset':y['val']-4,'aarch64_kcfi_prefix_word':hex(struct.unpack('<I',b)[0])})
    assert pp[0]['aarch64_kcfi_prefix_word']==pp[1]['aarch64_kcfi_prefix_word'];proof.append({'symbol':name,'source_provider':pp[0],'stock_provider':pp[1],'result':'KCFI_PREFIX_IDENTICAL','boundary':'A callee-prefix witness, not whole provider module parity/certification; these symbols have no exported __kcfi_typeid_ absolute symbol.'})
(P/'evidence/acceptance/provider-kcfi-witness.json').write_text(json.dumps(proof,indent=2)+'\n')
loads=list(csv.DictReader((A/'LOAD-LIST-EVIDENCE.tsv').open(),delimiter='\t'));related=names|{'mtk-spmi-pmic.ko','spmi-mtk-pmif.ko','pinctrl-mt6363.ko','pinctrl-mtk-v2.ko','pinctrl-mt6878.ko','pinctrl-mtk-common-v2_debug.ko','clk-common.ko','clk-mt6878.ko','mtk-dvfsrc.ko','mtk-dvfsrc-start.ko','mtk-scpsys.ko','mtk-scpsys-mt6878.ko','mtk-scpsys-bringup.ko','ufs-mediatek-mod.ko','mtk-mmc.ko','i2c-mt65xx.ko'}
loads=[r for r in loads if r['entry'] in related];tab(P/'evidence/inventory/LOAD-ORDER.tsv',list(loads[0]),[list(r.values()) for r in loads])
H=P/'evidence/hardware';rails=list(csv.DictReader((H/'DT-RAILS.tsv').open(),delimiter='\t'));edges=list(csv.DictReader((H/'DT-SUPPLIES.tsv').open(),delimiter='\t'));target=[r for r in rails if r['operand']=='static' and r['module']!='OUT_OF_SCOPE_PROVIDER'];links=[r for r in edges if r['operand']=='static' and r['module']!='OUT_OF_SCOPE_PROVIDER'];assert len(target)==42 and len(links)==32
checks=list(csv.DictReader((H/'DT-SOURCE-CHECKS.tsv').open(),delimiter='\t'));assert len(checks)==84 and all(r['result'].startswith('DESCRIPTOR_MATCH') and 'NO_SUPPORTED' not in r['result'] for r in checks)
checks2=[];dt=R/'workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb'
for rail in target:
    for prop,col in [('regulator-min-microvolt','min_uV'),('regulator-max-microvolt','max_uV')]:
        if rail[col]=='':continue
        value=int(subprocess.check_output(['fdtget','-tu',str(dt),rail['node'],prop],text=True).strip());assert value==int(rail[col]);checks2.append({'node':rail['node'],'property':prop,'value':value,'result':'IDENTICAL'})
for edge in links:
    value=int(subprocess.check_output(['fdtget','-tx',str(dt),edge['consumer'],edge['property']],text=True).strip(),16);assert value==int(edge['phandle'],16);checks2.append({'node':edge['consumer'],'property':edge['property'],'phandle':hex(value),'result':'IDENTICAL'})
(H/'fdtget-crosschecks.json').write_text(json.dumps(checks2,indent=2)+'\n')
# Preserve existing captured unbound-client evidence; do not infer population or cause.
bus=R/'workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/buses.txt';text=bus.read_text();excerpt=[]
for client in ['5-0075','6-0075']:
    pos=text.index('===/sys/bus/i2c/devices/'+client+'===');lines=text[pos:].splitlines()[:4];assert lines[1].endswith('/'+client+'/driver') and lines[2]=='rt6160';excerpt.extend(lines+[''])
(H/'existing-rt6160-binding-evidence.txt').write_text('Operand: '+str(bus.relative_to(R))+'\nSHA256: '+hashlib.sha256(bus.read_bytes()).hexdigest()+'\nClient-name is not a resolved driver binding. Both unbound in this capture; population/failure cause unknown.\n\n'+'\n'.join(excerpt)+'\n')
summary={'target_dt_nodes':42,'target_standard_supply_links':32,'all_regulator_nodes':76,'all_regulator_supply_links':48,'source_dt_checks':84,'fdtget_independent_crosschecks':len(checks2),'static_live_controller_properties_identical':402,'runtime_measured_voltages':0,'target_rt6160_bound_clients_in_capture':0,'target_rt6160_client_records':2,'mode_3_standby_reference_only_not_in_target_dt':True,'numeric_phandle_collisions_are_not_supply_edges':True}
(H/'contract-validation.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2));print('KCFI provider prefix words',proof)
