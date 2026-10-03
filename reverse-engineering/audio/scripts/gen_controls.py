#!/usr/bin/env python3
from pathlib import Path
import xml.etree.ElementTree as ET
import sys
src=Path(sys.argv[1])
out=Path(__file__).resolve().parents[1]/'afe/controls.tsv'
r=ET.parse(src).getroot()
with out.open('w') as f:
    f.write('path\taction\telement\tname\tvalue\n')
    for p in r.iter('path'):
        pn=p.get('name',''); act=p.get('value','')
        for x in p:
            if x.tag in ('kctl','path'):
                f.write('\t'.join((pn,act,x.tag,x.get('name',''),x.get('value','')))+'\n')
