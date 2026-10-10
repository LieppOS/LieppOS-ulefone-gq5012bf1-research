#!/usr/bin/env python3
"""Record source-level semantic clock delta; never transplant compiled arrays."""
from pathlib import Path
import subprocess,difflib,json,hashlib
P=Path(__file__).resolve().parents[1];R=P.parents[2];N=R.parent/'android_kernel_modules_power_platform_ulefone_gq5012bf1';W=Path('/home/armol/kernel-work/platform-batch-01-dev');T=W/'src/kdm';pin='5e415e059253ce0d2e61c97108e5f5785d71f06f';parts=[];proof=[]
for name in ['clkchk-mt6878.c','clkdbg-mt6878.c']:
 p='drivers/clk/mediatek/'+name;old=subprocess.check_output(['git','-C',str(W/'kernel_device_modules-6.1'),'show',pin+':'+p]);new=(T/p).read_bytes()
 parts.extend(difflib.unified_diff(old.decode().splitlines(keepends=True),new.decode().splitlines(keepends=True),fromfile='a/'+p,tofile='b/'+p))
 proof.append({'source':p,'public_pin':pin,'public_blob':subprocess.check_output(['git','-C',str(W/'kernel_device_modules-6.1'),'rev-parse',pin+':'+p],text=True).strip(),'public_sha256':hashlib.sha256(old).hexdigest(),'patched_sha256':hashlib.sha256(new).hexdigest()})
(N/'patches/0002-gq5012bf1-display-pwm-debug-names.patch').write_text(''.join(parts))
(P/'evidence/clock-source-lineage.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Preserved typed C initializer/index changes plus source blank-line position reproducing three BUG diagnostic lines; no compiled byte input')
