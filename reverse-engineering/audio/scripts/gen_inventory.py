#!/usr/bin/env python3
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "binary-analysis/per-module"
mods = [
("snd-soc-mt6369","MT6369 codec","ACTIVE","sound/soc/codecs/mt6369.c","e38092245fb4","none"),
("mt6369-accdet","MT6369 jack/keys/FM switch","ACTIVE","sound/soc/codecs/mt6369-accdet.c","e38092245fb4","YFT FM-switch GPIO + forced EINT0 HIRENB"),
("mt6878-mt6369","machine card","ACTIVE","sound/soc/mediatek/mt6878/mt6878-mt6369.c","e38092245fb4","AW883XX/AW882XX speaker types; RT5512 off"),
("snd-soc-mt6878-afe","MT6878 AFE","ACTIVE","sound/soc/mediatek/mt6878/*.c","e38092245fb4","none"),
("snd-soc-mtk-common","MTK ASoC common","ACTIVE","sound/soc/mediatek/common/*.c","7d4daf43ac24","ALPS09780515 fixes"),
("mtk-sp-spk-amp","speaker-amp dispatcher","ACTIVE","sound/soc/mediatek/common/mtk-sp-spk-amp.c","e38092245fb4","AW883XX type 5/imports"),
("mtk-afe-external","external AFE bridge","CONFIGURED","sound/soc/mediatek/common/mtk-afe-external.c","e38092245fb4","none"),
("audio_ipi","audio IPI transport","ACTIVE","drivers/misc/mediatek/audio_ipi/*","e38092245fb4","none"),
("adsp","ADSP core/mailbox/IPI","ACTIVE","drivers/misc/mediatek/adsp/*","e38092245fb4","none"),
("snd-soc-audiodsp-common","ADSP ALSA PCM","CONFIGURED","sound/soc/mediatek/audio_dsp/*","e38092245fb4","none"),
("mtk-soc-offload-common","compressed-offload transport","CONFIGURED","sound/soc/mediatek/audio_dsp/*","e38092245fb4","none"),
("mtk-scp-audiocommon","SCP audio common","CONFIGURED","sound/soc/mediatek/audio_scp/*","e38092245fb4","none"),
("mtk-scp-vow","SCP VOW DAI","ACTIVE","sound/soc/mediatek/vow/*","e38092245fb4","none"),
("mtk-vow","VOW control/transport","ACTIVE","drivers/misc/mediatek/vow/ver02/*","e38092245fb4","stock user config: SCP debug off"),
("snd-soc-mtk-scp-ultra","ultrasound ALSA PCM","CONFIGURED","sound/soc/mediatek/ultrasound/*","e38092245fb4","none"),
("mtk-scp-ultra","ultrasound SCP common","CONFIGURED","sound/soc/mediatek/ultrasound/*","e38092245fb4","none"),
("snd-soc-tfa98xx","TFA compatibility driver","DORMANT","sound/soc/codecs/tfa98xx/*","e38092245fb4","loaded but no fitted TFA device"),
("clk-mt6878-adsp","ADSP clock provider","ACTIVE","drivers/clk/mediatek/clk-mt6878-adsp.c","existing Nothing/MTK","none"),
("mt6685-audclk","MT6685 audio clock","CONFIGURED","drivers/mfd/mt6685-audclk.c","existing Nothing/MTK","none"),
("mtk-spmi-pmic","SPMI PMIC MFD","ACTIVE","drivers/mfd/mtk-spmi-pmic.c","existing Nothing/MTK","MT6369 VPA_OC IRQ index 1"),
("mt6369-regulator","MT6369 regulators","ACTIVE","drivers/regulator/mt6369-regulator.c","existing Nothing/MTK","none"),
("mtk-spmi-pmic-adc","MT6369 AUXADC","ACTIVE","drivers/iio/adc/mtk-spmi-pmic-adc.c","existing Nothing/MTK","none"),
]

def count(path):
    rows=list(csv.DictReader(path.open(),delimiter='\t'))
    return sum(r['class']=='EXACT' for r in rows),len(rows)

def abi(name):
    rows=list(csv.DictReader((P/f'{name}.abi-parity.tsv').open(),delimiter='\t'))
    return 'EXACT' if all(r['result'].startswith('EXACT') for r in rows) else 'DIFF'

with (ROOT/'kernel/module-inventory.tsv').open('w') as o:
    o.write('module\trole\tboard_state\tfunctions_exact\tfunctions_total\tdata_exact\tdata_total\tabi\tdonor\tulefone_delta\tstatus\n')
    for name,role,state,src,donor,delta in mods:
        fe,ft=count(P/f'{name}.function-parity.tsv'); de,dt=count(P/f'{name}.data-parity.tsv')
        o.write(f'{name}\t{role}\t{state}\t{fe}\t{ft}\t{de}\t{dt}\t{abi(name)}\t{donor}\t{delta}\tDONE\n')
with (ROOT/'kernel/source-map.tsv').open('w') as o:
    o.write('module\tsource\tresearch_copy\tstock_scope\n')
    for name,role,state,src,donor,delta in mods:
        area='mt6369' if name in {'snd-soc-mt6369','mt6369-accdet','mt6369-regulator','mtk-spmi-pmic','mtk-spmi-pmic-adc'} else ('afe' if name in {'mt6878-mt6369','snd-soc-mt6878-afe','snd-soc-mtk-common','mtk-sp-spk-amp','mtk-afe-external','clk-mt6878-adsp','mt6685-audclk'} else 'dsp')
        o.write(f'{name}\t{src}\t{area}/source/\t{role}\n')
