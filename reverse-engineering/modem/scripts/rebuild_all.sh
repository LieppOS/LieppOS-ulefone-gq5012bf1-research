#!/bin/bash
# rebuild_all.sh -- reproduce every modem-related kernel module and run parity (stock vs rebuilt)
# KDM must be at research commit 67c7da4 (or later) - see notes/PROVENANCE.md
. "$(dirname "$0")/modemenv.sh"
E=drivers/misc/mediatek
rm -rf $KDO
"$MR/scripts/build_kdm.sh" "$E/ccci_util/ $E/eccci/ $E/ccmni/ $E/rps/ $E/mdpm/ $E/usb/c2k_usb/ drivers/thermal/mediatek/ $E/mddp/ $E/power_throttling/" -k > /tmp/md_rebuild.log 2>&1
for m in ccci_util_lib ccci_md_all ccci_auxadc ccci_ccif ccci_dpmaif ccci_fsm_scp ccmni rps_perf mddp mtk_mdpm md_cooling_all \
         c2k_usb c2k_usb_f_via_atc c2k_usb_f_via_ets c2k_usb_f_via_modem mtk_md_power_throttling; do
  "$MR/scripts/parity_modem.sh" $m
  s=$(find "$VD" -name $m.ko); off=$(llvm-readelf -S "$s" | awk '$2==".note.gnu.build-id"{print strtonum("0x"$5)}')
  echo "$m whole-file: $(cmp -l "$s" /tmp/mstripped/$m.ko | awk -v o=$off '{p=$1-1; if(p<o+16||p>=o+36) x++} END{print NR+0" bytes differ, "x+0" outside build-id"}')"
done
