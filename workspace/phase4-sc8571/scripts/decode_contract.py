#!/usr/bin/env python3
"""Emit SC8571 register/DT contracts from the frozen stock tables.

Names are assigned only where the stock binary or the register-map donor gives
an unambiguous identity. Raw register/bit coordinates are decoded directly
from section-_rodata.bin and asserted against the frozen table.
"""
from pathlib import Path
import csv, struct

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
raw = (ROOT / "raw/section-_rodata.bin").read_bytes()

names = [
 "VBAT_OVP_DIS","VBAT_OVP","VBAT_OVP_ALM_DIS","VBAT_OVP_ALM",
 "IBAT_OCP_DIS","IBAT_OCP","IBAT_OCP_ALM_DIS","IBAT_OCP_ALM",
 "IBUS_UCP_DIS","VBUS_IN_RANGE_DIS","VBUS_PD_EN","VBUS_OVP",
 "VBUS_OVP_ALM_DIS","VBUS_OVP_ALM","IBUS_OCP_DIS","IBUS_OCP",
 "TSHUT_DIS","TDIE_ALM_DIS","TSBUS_FLT_DIS","TSBAT_FLT_DIS",
 "TDIE_ALM","TSBUS_FLT","TSBAT_FLT","VAC1_OVP","VAC2_OVP",
 "VAC1_PD_EN","VAC2_PD_EN","REG_RST","OTG_EN","CHG_EN","CHARGE_MODE",
 "ACDRV1_STAT","ACDRV2_STAT","FSW_SET","WD_TIMEOUT","WD_TIMEOUT_DIS",
 "IBAT_SNS_R","SS_TIMEOUT","IBUS_UCP_FALL_DG","VOUT_OVP_DIS","VOUT_OVP",
 "MS","CP_SWITCHING_STAT","VBUS_ERR_HI_STAT","VBUS_ERR_LO_STAT","DEVICE_ID",
 "ADC_EN","ACDRV_MANUAL_EN","ACDRV1_EN","ACDRV2_EN","SS_TIMEOUT_DIS",
 "PMID2OUT_OVP_DIS","PMID2OUT_OVP","VBUS_OVP_DIS","PMID2OUT_UVP",
 "PMID2OUT_UVP_DIS","PMID2OUT_UVP_FLAG","PMID2OUT_OVP_FLAG",
]
assert len(names) == 58
fields = []
for i, name in enumerate(names):
    reg, lsb, msb, id_size, id_offset = struct.unpack_from("<5I", raw, 0x248 + 20*i)
    assert id_size == id_offset == 0
    fields.append((i,name,reg,lsb,msb))

# Stock init-table target field for each config member in private-struct order.
cfg = [
("vbat-ovp-dis",0),("vbat-ovp",1),("vbat-ovp-alm-dis",2),("vbat-ovp-alm",3),
("ibat-ocp-dis",4),("ibat-ocp",5),("ibat-ocp-alm-dis",6),("ibat-ocp-alm",7),
("ibus-ucp-dis",8),("vbus-in-range-dis",9),("vbus-pd-en",10),("vbus-ovp",11),
("vbus-ovp-alm-dis",12),("vbus-ovp-alm",13),("ibus-ocp-dis",14),("ibus-ocp",15),
("tshut-dis",16),("tsbus-flt-dis",18),("tsbat-flt-dis",19),("tdie-alm",20),
("tsbus-flt",21),("tsbat-flt",22),("vac1-ovp",23),("vac2-ovp",24),
("vac1-pd-en",25),("vac2-pd-en",26),("fsw-set",33),("wd-timeout",34),
("wd-timeout-dis",35),("ibat-sns-r",36),("ss-timeout",37),("ibus-ucp-fall-dg",38),
("vout-ovp-dis",39),("vout-ovp",40),("ss-timeout-dis",50),("vbus-ovp-dis",53),
("pmid2out-ovp-dis",51),("pmid2out-ovp",52),("pmid2out-uvp-dis",55),("pmid2out-uvp",54),
]
master = [0,90,1,70,0,81,1,80,0,0,0,64,1,64,0,25,1,1,1,200,21,21,7,7,0,0,4,0,1,1,7,1,1,3,0,0,0,7,0,7]
slave  = [0,90,1,70,0,81,1,80,0,0,0,38,1,34,0,25,1,1,1,200,21,21,7,7,0,0,4,0,1,0,7,1,1,3,0,0,0,7,0,7]
assert len(cfg) == len(master) == len(slave) == 40

usage = {field: prop for (prop,field) in cfg}
notes = {
 0:"boolean; 1 disables",1:"7000 mV + code*20 mV",2:"boolean; 1 disables",
 3:"7000 mV + code*20 mV",4:"boolean; 1 disables",5:"code*100 mA",
 6:"boolean; 1 disables",7:"code*100 mA",8:"boolean",9:"slave is forced to 1 after DT init",
 10:"VBUS pull-down enable",11:"2:1 base 14000 mV + code*100 mV",
 12:"boolean; 1 disables",13:"2:1 base 14000 mV + code*100 mV",
 14:"boolean; 1 disables",15:"1000 mA + code*250 mA",16:"boolean; 1 disables",
 18:"boolean; 1 disables",19:"boolean; 1 disables",20:"25 C + code*5 C",
 23:"6500 mV + code*2500 mV",24:"6500 mV + code*2500 mV",
 27:"software reset",29:"charge-enable command",33:"300/350/400/450/500/550/600/750 kHz",
 34:"0.65/1.3/6.5/39 s",35:"1 disables watchdog",36:"0=2 mohm, 1=5 mohm",
 37:"6.5/13/26/52/104/416/1600/13000 ms",38:"10 us/5 ms/50 ms/150 ms",
 39:"boolean; 1 disables",40:"code 0..3 = 9.4/9.6/9.8/10.0 V",
 42:"read as charger enabled",44:"read by is_vbuslowerr",45:"must equal 0x41",46:"toggled around each ADC read",
 50:"boolean; 1 disables",51:"boolean; 1 disables",52:"125 mV + code*50 mV",
 53:"boolean; 1 disables",54:"50 mV + code*25 mV",55:"boolean; 1 disables",
}

out = REPO / "kernel/phase4-sc8571-register-fields.tsv"
with out.open("w", newline="") as f:
    w=csv.writer(f,delimiter="\t",lineterminator="\n")
    w.writerow(["field_id","name","register","bits","stock_use","dt_property","master_raw","slave_raw","interpretation"])
    value_by_field={field:(master[i],slave[i]) for i,(_,field) in enumerate(cfg)}
    for i,name,reg,lsb,msb in fields:
        vals=value_by_field.get(i,("","")); prop=usage.get(i,"")
        use=("DT_INIT" if prop else "ALLOCATED_ONLY")
        if i in (27,29,42,44,45,46): use={27:"RESET",29:"CHARGE_WRITE",42:"STATUS_READ",44:"STATUS_READ",45:"PROBE_ID",46:"ADC_GATE"}[i]
        w.writerow([i,name,f"0x{reg:02x}",f"{msb}:{lsb}" if msb!=lsb else str(lsb),use,
                    ("sc,sc8571,"+prop) if prop else "",vals[0],vals[1],notes.get(i,"")])

out = REPO / "kernel/phase4-sc8571-dt-contract.tsv"
with out.open("w", newline="") as f:
    w=csv.writer(f,delimiter="\t",lineterminator="\n")
    w.writerow(["parse_order","property","required","field_id","register","bits","master_raw","slave_raw"])
    fm={i:(reg,lsb,msb) for i,_,reg,lsb,msb in fields}
    # Parse order differs from cfg private-member order at ss-timeout-dis.
    parse_names=[x[0] for x in cfg[:30]]+["ss-timeout-dis"]+[x[0] for x in cfg[30:34]]+["vbus-ovp-dis"]+[x[0] for x in cfg[36:]]
    by_name={n:(field,master[i],slave[i]) for i,(n,field) in enumerate(cfg)}
    for order,n in enumerate(parse_names):
        field,m,s=by_name[n]; reg,lsb,msb=fm[field]
        w.writerow([order,"sc,sc8571,"+n,"yes",field,f"0x{reg:02x}",f"{msb}:{lsb}" if msb!=lsb else str(lsb),m,s])
    w.writerow([40,"sc8571,intr_gpio","yes","-","-","-","GPIO137 line4 flags2","GPIO137 line18 flags2"])
    w.writerow([41,"charger_name","no (fallback charger)","-","-","-","primary_dvchg","secondary_dvchg"])
print("wrote", REPO / "kernel/phase4-sc8571-register-fields.tsv")
print("wrote", REPO / "kernel/phase4-sc8571-dt-contract.tsv")
