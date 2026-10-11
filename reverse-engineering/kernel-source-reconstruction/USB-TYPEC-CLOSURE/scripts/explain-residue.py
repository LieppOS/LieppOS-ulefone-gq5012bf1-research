#!/usr/bin/env python3
"""Classify remaining real ELF differences without modifying/accepting operands."""
from pathlib import Path
import csv,sys,json,struct,collections,re
P=Path(__file__).resolve().parents[1];N,ROOT,O=map(Path,sys.argv[1:4]);sys.dont_write_bytecode=True;sys.path.insert(0,str(N/'scripts'));from normalize import kpp
r=next(r for r in csv.DictReader((P/'evidence/baseline/ALL-458-MODULES.tsv').open(),delimiter='\t') if r['filename']=='tcpc_class.ko');a=kpp.KO(ROOT/r['stock_paths'].split(';')[0]);b=kpp.KO(O/'tcpc_class.stripped')
rows=[];unclassified=[]
for sec in a.secs:
 if sec['type']!=4:continue
 other=b.sec(sec['n']);assert other is not None
 xs,ys=list(a.rela_entries(sec)),list(b.rela_entries(other));assert len(xs)==len(ys)
 for i,(x,y) in enumerate(zip(xs,ys)):
  if x==y:continue
  sx,sy=a.syms[x[1]>>32],b.syms[y[1]>>32]
  tx=a.secs[sx['shndx']]['n'] if 0<sx['shndx']<len(a.secs) else sx['n'];ty=b.secs[sy['shndx']]['n'] if 0<sy['shndx']<len(b.secs) else sy['n']
  if x[:2]!=y[:2] or tx!=ty or tx!='.rodata.str1.1':unclassified.append({'section':sec['n'],'index':i,'stock':x,'source':y,'targets':[tx,ty]});continue
  ax=sx['val']+x[2];by=sy['val']+y[2];xx=a.data(tx)[ax:].split(b'\0')[0].decode(errors='replace');yy=b.data(ty)[by:].split(b'\0')[0].decode(errors='replace')
  rows.append({'section':sec['n'],'index':i,'stock_offset':ax,'source_offset':by,'stock_string':xx,'source_string':yy,'literal_equal':xx==yy})
xs,ys=a.data('__bug_table'),b.data('__bug_table');assert len(xs)==len(ys) and len(xs)%12==0
bugs=[]
for i in range(len(xs)//12):
 x,y=struct.unpack_from('<iiHH',xs,i*12),struct.unpack_from('<iiHH',ys,i*12)
 if x!=y:bugs.append({'index':i,'stock':x,'source':y,'only_source_line_differs':x[:2]==y[:2] and x[3]==y[3]})
changes=[r for r in rows if not r['literal_equal']];unique=sorted({(r['stock_string'],r['source_string']) for r in changes});j={'changed_relocation_records':len(rows),'resolved_literal_equal':sum(r['literal_equal'] for r in rows),'different_literals':unique,'unclassified_relocations':unclassified,'bug_entries':len(xs)//12,'changed_bug_entries':bugs,'all_changed_bug_entries_only_source_lines':all(r['only_source_line_differs'] for r in bugs),'relocations':rows,'scope':'Diagnostic target resolution is not ELF normalization or full stock acceptance. Raw source-line strings, BUG records, symbol positions and srcversion remain mismatches; no B equivalence/certification is inferred.'}
D=P/'evidence/metadata';(D/'tcpc-class-residue.json').write_text(json.dumps(j,indent=2)+'\n');print('Relocation residues',len(rows),'equal literals',j['resolved_literal_equal'],'unequal literal pairs',len(unique),'unclassified',len(unclassified),'BUG line records',len(bugs),'/',len(xs)//12)
for x,y in unique:print(x,'->',y)
