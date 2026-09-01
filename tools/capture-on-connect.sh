#!/bin/bash
# The OrangeFox USB gadget only survives ~3 seconds, so diagnostics must be
# fired the instant adb appears, prioritised by value.
#
# PASS 1 (must succeed within ~1s): the three files that explain the USB
#        teardown and the dead touchscreen.
# PASS 2: everything else, best effort.
OUT="$1"
mkdir -p "$OUT"
echo "watching -> $OUT"

grab() { # grab <file> <shell command>
    local f="$OUT/$1"; shift
    # only overwrite if we get something bigger than what we already have
    local tmp; tmp=$(mktemp)
    if timeout 8 adb shell "$@" > "$tmp" 2>&1; then
        if [ ! -s "$f" ] || [ "$(stat -c%s "$tmp")" -gt "$(stat -c%s "$f")" ]; then
            mv "$tmp" "$f"
        else rm -f "$tmp"; fi
    else rm -f "$tmp"; fi
}

while true; do
    if adb devices 2>/dev/null | sed -n '2p' | grep -q 'recovery\|device'; then
        echo "[$(date +%H:%M:%S)] UP - pass 1"
        grab of-recovery.txt      'cat /tmp/recovery.log' &
        grab of-input-devices.txt 'cat /proc/bus/input/devices' &
        grab of-dmesg.txt         'dmesg' &
        wait
        echo "[$(date +%H:%M:%S)] pass 1 done - pass 2"
        grab of-modules.txt       'cat /proc/modules' &
        grab of-getprop.txt       'getprop' &
        grab of-input-names.txt   'for x in /sys/class/input/input*/name; do echo "$x: $(cat $x 2>/dev/null)"; done' &
        grab of-dev-input.txt     'ls -l /dev/input' &
        grab of-byname.txt        'ls -l /dev/block/by-name/' &
        grab of-mounts.txt        'mount; echo ===DF===; df -h' &
        grab of-logcat.txt        'logcat -b all -d' &
        wait
        echo "[$(date +%H:%M:%S)] captured:"
        for f in "$OUT"/*.txt; do
            [ -f "$f" ] && printf "   %-24s %6s bytes\n" "$(basename "$f")" "$(stat -c%s "$f")"
        done
    fi
    sleep 0.3
done
