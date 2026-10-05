import itertools, sys
sys.path.insert(0,'tools'); from svtext import sv
base=open('trees/5e41/drivers/misc/mediatek/typec/tcpc/rt_pd_manager.c').read()
TARGET='C4301583FE25F39BA52E75D'
def variants():
    for inc, decl, wd, vsc, alert, prot, hdrwrap in itertools.product(range(2), range(5), range(2), range(2), range(2), range(2), range(2)):
        s=base
        # decl
        dl={0:'\tint boot_mode = rpmd->tcpc[idx]->bootmode;\n',
            1:'\t// int bootmode = rpmd->tcpc[idx]->bootmode;\n\tint boot_mode = rpmd->tcpc[idx]->bootmode;\n',
            2:'\tint bootmode = rpmd->tcpc[idx]->bootmode;\n',
            3:'\t// int bootmode = rpmd->tcpc[idx]->bootmode;\n',
            4:'\tint bootmode = rpmd->tcpc[idx]->bootmode;\n'}[decl]
        bm='bootmode' if decl in (2,4) else 'boot_mode'
        s=s.replace('\tint boot_mode = rpmd->tcpc[idx]->bootmode;\n', dl if decl!=3 else dl, 1)
        if decl==3:  # commented early + real one after state decl (klee layout)
            s=s.replace('\tstruct typec_mux_state state = {.mode = 0, .data = &dp_data};\n','\tstruct typec_mux_state state = {.mode = 0, .data = &dp_data};\n\tint boot_mode = rpmd->tcpc[idx]->bootmode;\n',1)
        s=s.replace('boot_mode == 8 || boot_mode == 9', f'{bm} == 8 || {bm} == 9')
        if wd: s=s.replace(f'\t\tif ({bm} == 8 || {bm} == 9)\n\t\t\tbreak;\n', f'\t\tif ({bm} == 8 || {bm} == 9) {{\n\t\t\tbreak;\n\t\t}}\n')
        if vsc:
            old='''		if (!noti->vsc_status) {
			dev_info(rpmd->dev, "%s exit short status\\n", __func__);
			break;
		}
		dev_info(rpmd->dev, "%s enter short status, CC%s%s\\n", __func__,
			 noti->vsc_status & BIT(TCPC_POLARITY_CC1) ? "1" : "",
			 noti->vsc_status & BIT(TCPC_POLARITY_CC2) ? "2" : "");
'''
            assert old in s
            s=s.replace(old,'''		if (noti->vsc_status)
			dev_info(rpmd->dev, "%s enter short status, CC%s%s\\n", __func__,
				 noti->vsc_status & BIT(TCPC_POLARITY_CC1) ? "1" : "",
				 noti->vsc_status & BIT(TCPC_POLARITY_CC2) ? "2" : "");
		else
			dev_info(rpmd->dev, "%s exit short status\\n", __func__);
''')
        if alert:  # move alert case before CC_HI
            a='''	case TCP_NOTIFY_ALERT_RATELIMITED:
		dev_info(rpmd->dev, "%s alert_ratelimited = %d\\n",
				    __func__, noti->alert_ratelimited);
		break;
'''
            i=s.index('\tcase TCP_NOTIFY_ALERT_RATELIMITED:'); j=s.index('break;',i)+len('break;')+1
            blk=s[i:j]; s=s[:i]+s[j:]; k=s.index('\tcase TCP_NOTIFY_CC_HI:'); s=s[:k]+blk+s[k:]
        if prot:
            s=s.replace('''		if (new_state == TYPEC_UNATTACHED ||
		    new_state == TYPEC_PROTECTION) {''','''		if (new_state == TYPEC_UNATTACHED || new_state == TYPEC_PROTECTION) {''')
        if inc:
            s=s.replace('#include <linux/kernel.h>\n#include <linux/module.h>\n','#include <linux/module.h>\n#if IS_ENABLED(CONFIG_TCPC_CLASS)\n#include <linux/kernel.h>\n',1)
            s=s.replace('MODULE_VERSION(RT_PD_MANAGER_VERSION);\n','MODULE_VERSION(RT_PD_MANAGER_VERSION);\n#endif\t/* CONFIG_TCPC_CLASS */\n',1)
        if hdrwrap:
            s=s.replace('#include "inc/tcpci_typec.h"\n','#include <inc/tcpm.h>\n\n#include "inc/tcpci_typec.h"\n',1)
        yield (inc,decl,wd,vsc,alert,prot,hdrwrap), s
n=0
for k,s in variants():
    n+=1; r=sv([s])
    if r==TARGET: print('MATCH',k); open('/tmp/rpm_match.c','w').write(s); break
print('tried',n)
