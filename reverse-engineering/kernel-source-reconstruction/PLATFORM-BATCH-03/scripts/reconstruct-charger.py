#!/usr/bin/env python3
"""Recover source-level charger cooling board policy from exact stock instructions.
No compiled bytes, CRCs, symbol tables or module metadata are patched/copied.
"""
from pathlib import Path
import difflib,subprocess,json,hashlib,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[2];N=R.parent/'android_kernel_modules_secure_diagnostics_ulefone_gq5012bf1';T=Path('/home/armol/kernel-work/platform-batch-03-dev/kernel_device_modules-6.1');p='drivers/thermal/mediatek/charger_cooling.c';rev='5e415e059253ce0d2e61c97108e5f5785d71f06f';a=subprocess.check_output(['git','show',rev+':'+p],cwd=T,text=True);b=a
b=b.replace('#include "charger_cooling.h"','#include "charger_cooling.h"\n\nextern int yft_long_charger_flag;\nextern bool yft_cam_open_flag;')
b=b.replace('prop_bat_chr.intval = master_charger_state_to_current_limit[chg->target_state];','prop_bat_chr.intval = master_charger_state_to_current_limit[chg->target_state];\n\tif (yft_long_charger_flag == 0)\n\t\tprop_bat_chr.intval = 0;')
b=b.replace('\tret = power_supply_set_property(chg->chg_psy,\n\t\tPOWER_SUPPLY_PROP_INPUT_CURRENT_LIMIT, &prop_input);','\tif (yft_long_charger_flag == 0x1234 || yft_long_charger_flag == 0) {\n\t\tpr_notice(" chr limit input %d,yft_long_charger_flag=%d\\n",\n\t\t\tprop_input.intval, yft_long_charger_flag);\n\t\tprop_input.intval = -1;\n\t}\n\tret = power_supply_set_property(chg->chg_psy,\n\t\tPOWER_SUPPLY_PROP_INPUT_CURRENT_LIMIT, &prop_input);')
b=b.replace('\tif (prop_bat_chr.intval == 0)\n\t\tprop_vbus.intval = 0;','\tif (yft_cam_open_flag)\n\t\tprop_vbus.intval = 0;')
# Recover source positions from genuine BUG table line operands: WARN at75, probe at223.
# This is source whitespace, not #line directives or patched compiled metadata.
b=b.replace('#include "charger_cooling.h"\n\nextern int yft_long_charger_flag;\nextern bool yft_cam_open_flag;\n\nstruct', '#include "charger_cooling.h"\nextern int yft_long_charger_flag;\nextern bool yft_cam_open_flag;\nstruct')
b=b.replace('static int cooling_state_to_charger_limit_v1(', '\n'*17+'static int cooling_state_to_charger_limit_v1(')
patch=''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+p,tofile='b/'+p));(N/'patches/0004-charger-cooling-board-policy.patch').write_text(patch)
E=P/'evidence/charger-reconstruction';E.mkdir(parents=True,exist_ok=True);stock=R/'workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/charger_cooling.ko';bin=Path('/home/armol/kernel-work/platform-batch-03-dev/prebuilts/clang/host/linux-x86/clang-r487747c/bin/llvm-objdump');out=subprocess.check_output([str(bin),'--disassemble','--reloc','--disassemble-symbols=cooling_state_to_charger_limit_v1',str(stock)],text=True);(E/'stock-policy-disassembly.txt').write_text(out);(E/'source-policy-recovery.json').write_text(json.dumps({'source_candidate':rev,'stock_sha256':hashlib.sha256(stock.read_bytes()).hexdigest(),'source_patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'evidence':'Stock relocations/type-width loads: yft_long_charger_flag int; yft_cam_open_flag bool. Constant charge current forced0 for longflag0; input current override-1 when0x1234 or0 with exact notice string; voltage control follows camera bool rather than candidate battery-current zero branch. Genuine historical producer declaration types preserved. No runtime camera/charging transaction inferred.','next':'Compile C and accept entire stock ELF; no semantic/function-count shortcut'},indent=2)+'\n')
ref=N/'reference/kdm-tree.txt'
if ref.exists():shutil.copyfile(ref,E/'prior-source-tree.txt');ref.unlink()
print('Recovered charger board source policy; full stock validation required')
