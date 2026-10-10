#!/usr/bin/env python3
"""Every compiled source unit and real hardware/firmware interface, not runtime guesses."""
from pathlib import Path
import csv,re,json,hashlib
P=Path(__file__).resolve().parents[1];R=P.parents[2];W=Path('/home/armol/kernel-work/platform-batch-03-cleancheck/ws');T=W/'src/kdm';rows=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));out=[]
for r in rows:
 m=r['filename'].removesuffix('.ko');base=W/'native-kout/drivers/thermal' if m=='thermal-generic-adc' else T/r['candidate_directory'];mod=base/(m+'.mod');assert mod.exists(),mod;units=[]
 for o in mod.read_text().splitlines():
  obj=Path(o);obj=obj if obj.is_absolute() else W/'native-kout'/obj if m=='thermal-generic-adc' else T/obj
  cmd=obj.with_name('.'+obj.name+'.cmd');assert cmd.exists(),cmd;txt=cmd.read_text();src=re.search(r'^source_\S+\s*:=\s*(.+)$',txt,re.M);assert src,cmd;f=Path(src[1]);f=f if f.is_absolute() else W/'common'/f;assert f.exists(),f
  text=f.read_text(errors='replace');compat=re.findall(r'\.compatible\s*=\s*"([^"]+)"',text);interfaces=sorted(set(re.findall(r'\b((?:arm_smccc|of_|devm_|regmap_|clk_|regulator_|scmi_|ioread|iowrite|readl|writel|dma_|thermal_|power_supply_|iio_|sspm_|mtk_tinysys_)\w*)\s*\(',text)));exports=re.findall(r'EXPORT_SYMBOL(?:_GPL|_NS|_NS_GPL)?\s*\(\s*(\w+)',text)
  units.append({'source_path':str(f.relative_to(W)),'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'object':str(obj.relative_to(W)),'compiler_command_sha256':hashlib.sha256(cmd.read_bytes()).hexdigest(),'source_compatibles':compat,'actual_source_interface_calls':interfaces,'exported_names':exports,'evidence_level':'STOCK_BINARY_IMPLEMENTATION' if m!='thermal-generic-adc' else 'PUBLIC_SOURCE_ONLY_FULL_INSTRUCTIONS_EXACT_BTF_UNCLOSED','limits':'Source call presence/static implementation; not performed MMIO, DMA, firmware, thermal/voltage or RNG transaction'})
 out.append({'module_id':r['module_id'],'canonical_owner':r['canonical_owner'],'family':r['dependency_group'],'source_revision':r['public_source_commit'],'patches':'all patches at exact SOURCE-REPOSITORIES.tsv owned commit','compiled_units':units,'hardware_evidence':'hardware/DT-PROPERTIES.tsv,CONFIGURED-NODE-PROPERTIES.tsv,TYPED-RESOURCES.tsv,SAVED-RUNTIME-BOUNDARIES.json','loading_evidence':'hardware/LOAD-LIST-EVIDENCE.tsv','runtime_control_tested':False,'firmware_boundary':'Secure services/coprocessor firmware and communication not reconstructed or invoked; host-side source only'})
E=P/'evidence';(E/'SOURCE-TO-HARDWARE-CONTRACTS.json').write_text(json.dumps(out,indent=2)+'\n');print('Source-to-hardware contracts',len(out),'compiled source units',sum(len(x['compiled_units']) for x in out))
