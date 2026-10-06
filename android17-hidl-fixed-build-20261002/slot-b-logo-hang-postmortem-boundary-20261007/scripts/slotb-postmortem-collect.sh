#!/usr/bin/env bash
# Slot-B post-failure forensic collector (run from the host while the phone is
# booted into healthy Slot A with adb + root).  STRICTLY READ-ONLY on the phone:
# no partition writes, no boot-control changes, no reboot, no temp files on device.
#
# usage: slotb-postmortem-collect.sh OUTDIR "B_WINDOW_START" "B_WINDOW_END"
#   times are device-local, e.g. "2026-10-03 14:25:30" "2026-10-03 14:47:00"
#   B_WINDOW_START = host time of the A->B reboot command
#   B_WINDOW_END   = time the rescue Slot-A boot started (see bootstat/last_boot_time_utc)
set -u
OUT=${1:?outdir}; WS=${2:?window start}; WE=${3:?window end}
mkdir -p "$OUT"
BB=/data/adb/ksu/bin/busybox
sh_root() { adb shell "su -c '$1'" 2>&1; }
log() { echo "== $*" >&2; }

adb get-state >/dev/null 2>&1 || { echo "FATAL: no adb device" >&2; exit 2; }
[ "$(adb shell getprop ro.boot.slot_suffix | tr -d '\r')" = "_a" ] || { echo "FATAL: not on slot A" >&2; exit 3; }

log identity
{ date -Iseconds; adb shell 'getprop ro.boot.slot_suffix; getprop ro.boot.bootreason; getprop persist.sys.boot.reason.history; uptime; getprop ro.build.fingerprint'; } > "$OUT/00-identity.txt"

# 1. Preloader/LK log of the CURRENT (rescue) boot.  It records the reset cause
#    of the failed attempt (PMIC POFFSTS / RGU / BOOT_REASON) and the A/B
#    metadata the preloader saw (priority / retry per slot).  Capture this from
#    the FIRST Slot-A boot after the failure; any later reboot overwrites it.
log pl_lk
sh_root 'cat /proc/pl_lk' > "$OUT/01-pl_lk.txt"
grep -a -E 'last_boot step|RAM_CONSOLE wdt status|POFFSTS|pmic_check_rst|metadata.slot_info|\[AB\]|BOOT_REASON:|Long Pressed|\[RGU\] (rst from|STA)' \
    "$OUT/01-pl_lk.txt" > "$OUT/01-pl_lk-key.txt"
sh_root 'cat /proc/bootprof' > "$OUT/01-bootprof-current.txt"

# 2. A/B metadata straight from misc (offset 0x800, struct bootloader_control).
log misc
adb exec-out "su -c 'dd if=/dev/block/by-name/misc bs=4096 count=1 2>/dev/null'" > "$OUT/02-misc-first-4096.bin"
python3 - "$OUT/02-misc-first-4096.bin" > "$OUT/02-bootctrl-decoded.txt" <<'EOF'
import sys,struct,zlib
b=open(sys.argv[1],'rb').read()[0x800:0x820]
suf,magic,ver,nb=b[0:4],b[4:8],b[8],b[9]
print("slot_suffix=%r magic=%r version=%d nb_slot=%d recovery_tries=%d"%(suf.rstrip(b'\0'),magic,ver,nb&7,(nb>>3)&7))
for i in range(2):
    lo,hi=b[12+2*i],b[13+2*i]
    print("slot_%s priority=%d tries_remaining=%d successful_boot=%d verity_corrupted=%d"%("ab"[i],lo&15,(lo>>4)&7,lo>>7,hi&1))
crc=struct.unpack('<I',b[28:32])[0]
print("crc_ok=%s"%(zlib.crc32(b[:28])&0xffffffff==crc))
EOF
sh_root 'bootctl get-current-slot; bootctl is-slot-marked-successful 1; echo b_successful_rc=$?' > "$OUT/02-bootctl.txt"

# 3. pstore / last_kmsg (only useful if the failed attempt ended in a WARM reset;
#    a long-press PMIC cold reset loses DRAM and leaves ~60-byte stubs).
log pstore
sh_root 'ls -la /sys/fs/pstore/; for f in /sys/fs/pstore/*; do echo "=== $f"; cat "$f"; done' > "$OUT/03-pstore.txt"

# 4. Persistent-storage timestamp sweep over the B window.  /metadata is mounted
#    in first-stage init and is shared by both slots, so B userspace writes there
#    survive a cold reset.  mtime/ctime of files AND directories are listed.
log sweep
cat > "$OUT/.sweep.sh" <<EOF
now=\$(date +%s); s=\$($BB date -d "$WS" +%s); e=\$($BB date -d "$WE" +%s)
older=\$(( (now-s)/60 + 1 )); newer=\$(( (now-e)/60 - 1 ))
echo "# window $WS .. $WE  (mmin -\$older +\$newer)"
for fs in /metadata /mnt/vendor/protect_f /mnt/vendor/protect_s /mnt/vendor/nvdata /mnt/vendor/nvcfg /mnt/vendor/persist /mnt/vendor/mdota /data; do
  $BB find \$fs -xdev \( -mmin -\$older -a -mmin +\$newer \) -o \( -cmin -\$older -a -cmin +\$newer \) 2>/dev/null |
  while read f; do $BB stat -c "%y|%z|%s|%U:%G|%n" "\$f"; done
done
EOF
adb shell "su -c sh" < "$OUT/.sweep.sh" > "$OUT/04-window-sweep.txt" 2>&1
rm -f "$OUT/.sweep.sh"
sh_root "$BB find /metadata -xdev -exec $BB stat -c \"%y|%z|%s|%U:%G|%n\" {} +" | sort > "$OUT/04-metadata-full-stat.txt"

# 5. Stage markers that need no logs:
#    - /metadata/aconfig/boot dir mtime: Android 17 aconfigd (early-init) rewrites
#      boot/*.val via remove+create, so a dir mtime inside the window = B second-stage init ran.
#    - /metadata/aconfig/early_init_done: created only if early platform init succeeded.
#    - /data/apex/decompressed/*@<B apex version>*: created only once B mounted /data
#      and apexd ran its post-fs-data activation.
log stage-markers
sh_root "ls -la --full-time /metadata/aconfig /metadata/aconfig/boot; ls -la --full-time /data/apex /data/apex/decompressed /data/apex/active" > "$OUT/05-stage-markers.txt"

# 6. Android-side persistent logs (stale entries must be date-filtered).
log android-logs
sh_root 'ls -la --full-time /data/misc/bootstat /data/system/dropbox | tail -80' > "$OUT/06-bootstat-dropbox.txt"
sh_root 'logcat -L -d -v year 2>/dev/null | tail -400' > "$OUT/06-logcat-last-boot-tail.txt"
sh_root 'ls -la --full-time /data/vendor/aee_exp /data/aee_exp /data/vendor/mtklog 2>&1 | tail -60' > "$OUT/06-aee.txt"

# 7. Identity of the B payload that actually booted (read-only hashes).
log identities
sh_root 'for p in system_b system_ext_b product_b vendor_b vendor_dlkm_b system_dlkm_b odm_dlkm_b; do echo "$p $(sha256sum /dev/block/mapper/$p | cut -d" " -f1)"; done; for p in boot_b init_boot_b vendor_boot_b vbmeta_b vbmeta_system_b vbmeta_vendor_b dtbo_b; do echo "$p $(sha256sum /dev/block/by-name/$p | cut -d" " -f1)"; done' > "$OUT/07-slot-b-hashes.txt"

( cd "$OUT" && sha256sum * > SHA256SUMS 2>/dev/null )
echo "COLLECTION_DONE=$OUT"
