#!/usr/bin/env python3
"""Diagnostic fixtures: show exact pinned parser semantics, not candidate preimages."""
from pathlib import Path
import ctypes,hashlib,json,subprocess,tempfile
P=Path(__file__).resolve().parents[1];W=Path('/home/armol/kernel-work/usb-typec-closure-01')
lib=ctypes.CDLL(str(W/'sumversion-probe.so'));lib.hash_paths.argtypes=[ctypes.POINTER(ctypes.c_char_p),ctypes.c_char_p]
with tempfile.TemporaryDirectory(prefix='sumversion-semantics-',dir=W) as td:
 d=Path(td)
 def checksum(content):
  f=d/'input.c';f.write_text(content);a=(ctypes.c_char_p*2)(str(f).encode(),None);o=ctypes.create_string_buffer(25);lib.hash_paths(a,o);return o.value.decode()
 base='int value = 1;\n';b=checksum(base);cases=[]
 for n,s,e in [('whitespace',' int\t value=1 ;\n',True),('block-comment',base+'/* provenance comment */\n',True),('line-comment',base+'// provenance comment\n',False),('inactive-token-stream',base+'#if 0\nint unused = 7;\n#endif\n',False),('line-continuation','int value = \\\n1;\n',True),('string-whitespace-a','const char *p="a b";\n',False),('string-whitespace-b','const char *p="ab";\n',False)]:
  h=checksum(s);assert (h==b)==e;cases.append({'case':n,'checksum':h,'equal_base':h==b,'expected_equal_base':e})
 s=base+'#if 0\nint unused = 7;\n#endif\n';f=d/'fixture.c';f.write_text(base);a=subprocess.check_output(['gcc','-E','-P',str(f)]);f.write_text(s);z=subprocess.check_output(['gcc','-E','-P',str(f)]);assert a==z and checksum(base)!=checksum(s)
 result={'result':'PASS','parser':'unmodified pinned common/scripts/mod/sumversion.c','digest':'MD4 upper-case ASCII truncated to23characters by sumlen24','base_checksum':b,'cases':cases,'inactive_tokens_change_fingerprint_with_identical_preprocessed_translation_unit':True,'limits':'Fixtures prove parser semantics, not OEM token provenance or permission to waive metadata differences'}
(P/'evidence/srcversion/parser-semantics.json').write_text(json.dumps(result,indent=2)+'\n');print('Seven parser fixtures PASS; inactive source tokens affect fingerprint even when compiler sees identical source')
