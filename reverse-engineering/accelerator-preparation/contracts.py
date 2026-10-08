#!/usr/bin/env python3
"""Extract pinned donor ABI/firmware/clock/IRQ evidence references, not stock-equivalence claims."""
import csv
import json
import re
from pathlib import Path
from inventory import HERE, ROOTS, table, sha

# Whole source text stays local. Only single relevant evidence lines are emitted.
PATTERNS = {
    'IOCTL/UAPI': r'(?<!\w)_IO(?:R|W|WR)?\s*\(|unlocked_ioctl|compat_ioctl',
    'device/queue': r'\.name\s*=|video_register_device|v4l2_m2m|misc_register|cdev_add',
    'firmware/boot/reset': r'request_firmware|rproc_boot|rproc_shutdown|firmware-name|\.bin"|\.img"|reset_control',
    'memory/IOMMU': r'dma_buf_(attach|map|mmap)|dma_alloc|iommu_(map|attach)|memory-region',
    'IRQ/power/clocks': r'devm_request.*irq|request_threaded_irq|platform_get_irq|clk_(prepare|enable|get)|pm_runtime',
    'codec formats': r'V4L2_PIX_FMT_(H264|H265|HEVC|VP8|VP9|AV1|MPEG|H263)',
    'transport/recovery': r'rpmsg_(send|register)|ipi_(send|register)|mbox_|recover|watchdog|timeout',
}

def main():
    scopes=json.loads((HERE/'scopes.json').read_text())['scopes']
    for s in scopes:
        out=[]; seen=set()
        for m,loc in s['sources'].items():
            key,rel=loc.split(':',1);root=ROOTS[key];path=root/rel
            files=[path] if path.is_file() else sorted(p for p in path.rglob('*') if p.is_file() and p.suffix in ('.c','.h'))
            for p in files:
                digest=sha(p)
                for i,line in enumerate(p.read_text(errors='replace').splitlines(),1):
                    for kind,regex in PATTERNS.items():
                        if re.search(regex,line) and (str(p),i,kind) not in seen:
                            seen.add((str(p),i,kind));out.append(dict(kind=kind,file=str(p),line=i,source_sha256=digest,text=line.strip(),status='DONOR EVIDENCE / validate stock control flow and layout before treating as contract'))
        table(HERE/s['component']/'abi-source-witnesses.tsv',out)
        print(s['component'],len(out),'pinned donor reference lines')

if __name__=='__main__':main()
