"""Explicit accelerator ownership transfer policy, not source/parity completion.
Input ledgers are committed preparation metadata; generic/DONE dependencies are not new targets.
"""
import csv
import json
from pathlib import Path

PREP=Path(__file__).resolve().parents[2]/'accelerator-preparation'
SCOPES=json.loads((PREP/'scopes.json').read_text())['scopes']
COMPONENTS={s['component'] for s in SCOPES}
KERNEL_OVERRIDES={m[:-3]:(s['component'],'B','authorized accelerator preparation: '+s['justification']) for s in SCOPES for m in s['modules']}
KERNEL_OVERRIDES.update({
 'camera_eeprom_v4l2':('CAMERA-EEPROMS','A','sole EEPROM driver closed in camera/eeprom; not camera HAL kernel ownership'),
 'dw9781c':('DW9781C-OIS','A','exact named OIS driver source closure; not camera HAL ownership'),
 'aw36515':('AW36515-FLASH','A','existing named flash driver scope; preserve DONE'),
 'custom-ldo':('WL2868-CAMERA-LDO','A','two-module LDO wrapper/provider closure already owned by WL2868-CAMERA-LDO'),
 'custom-ldo-wl2868':('WL2868-CAMERA-LDO','A','existing closed camera-rail provider; do not duplicate in ISP child'),
 'scp':('SENSOR-HUB-KERNEL','B','scp host source/ABI closed in sensors; TinySys IPI only provides transport'),
 'sensorhub':('SENSOR-HUB-KERNEL','B','existing sensorhub Linux source closure'),
 'hf_manager':('SENSOR-HUB-KERNEL','B','existing sensor 2.0 core source/ABI closure'),
 'adsp':('AUDIO-DSP-KERNEL','B','existing ADSP host source scope; not transport framework ownership'),
})
for m in ('clk-mt6878-cam','clk-mt6878-img','clk-mt6878-ccu','i2c-mt65xx','mt6363-regulator','mtk-mmdvfs-v3','mtk-smi','mtk_iommu','pinctrl-mt6878','flashlight'):
 KERNEL_OVERRIDES[m]=('COVERED-GENERIC','C','shared MTK source-carried platform dependency, not proprietary camera HAL or claimed module parity')
DT_OVERRIDES={x['compatible']:(x['new_owner'],'B','authorized singleton accelerator DT transfer: '+x['evidence']) for x in csv.DictReader((PREP/'dt-ownership.tsv').open(),delimiter='\t')}
# PMIC infrastructure mentioned by a camera inventory is not camera execution IP.
for c in ('consys','dynamic_loading_throttling','efuse','keys','lvsys-notify','pinctrl','pmic-temp'):
 DT_OVERRIDES['mediatek,mt6363-'+c]=('COVERED-GENERIC','C','shared PMIC infrastructure; historical camera mention is not primary ownership')
