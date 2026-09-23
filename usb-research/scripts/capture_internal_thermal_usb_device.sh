#!/system/bin/sh
# Controlled GQ5012BF1 stock thermal-camera USB capture.
# Runs locally because GPIO 55 may route the shared USB2 fabric away from
# external Type-C, temporarily disconnecting ADB. The final writes restore the
# same two stock mode controls to their documented idle value (0).

OUT=/data/local/tmp/armol-usb-thermal
rm -rf "$OUT"
mkdir -p "$OUT"

snapshot() {
    tag="$1"
    file="$OUT/$tag.txt"
    {
        echo "tag=$tag"
        date -u +%Y-%m-%dT%H:%M:%SZ
        echo "[modes]"
        printf 'tiny2c_mode='; cat /sys/class/yft_extcon/tiny2c_mode 2>/dev/null
        printf 'tiny2c_usb_mode='; cat /sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode 2>/dev/null
        printf 'uvc_insert_status='; cat /sys/devices/platform/extcon-usb/uvc_insert_status 2>/dev/null
        echo "[udc]"
        for f in current_speed maximum_speed state; do
            printf '%s=' "$f"
            cat "/sys/class/udc/11201000.usb0/$f" 2>/dev/null || echo absent
        done
        echo "[typec]"
        for d in /sys/class/typec/*; do
            [ -e "$d" ] || continue
            printf '[%s]\n' "${d##*/}"
            for f in data_role power_role port_type power_operation_mode preferred_role orientation; do
                [ -r "$d/$f" ] && printf '%s=' "$f" && cat "$d/$f"
            done
        done
        echo "[usb-devices]"
        for d in /sys/bus/usb/devices/*; do
            [ -e "$d" ] || continue
            n=${d##*/}
            printf '[%s]\n' "$n"
            for f in busnum devnum devpath speed idVendor idProduct bcdUSB bDeviceClass bDeviceSubClass bDeviceProtocol product manufacturer serial; do
                [ -r "$d/$f" ] && printf '%s=' "$f" && cat "$d/$f"
            done
            for i in "$d":*; do
                [ -e "$i" ] || continue
                drv=$(readlink "$i/driver" 2>/dev/null)
                printf 'interface=%s driver=%s\n' "${i##*/}" "${drv##*/}"
                for f in bInterfaceNumber bAlternateSetting bNumEndpoints bInterfaceClass bInterfaceSubClass bInterfaceProtocol interface; do
                    [ -r "$i/$f" ] && printf '%s=' "$f" && cat "$i/$f"
                done
            done
        done
        echo "[platform-bindings]"
        for d in /sys/bus/platform/devices/11201000.usb0 /sys/bus/platform/devices/11200000.xhci0 /sys/bus/platform/devices/11f40000.usb-phy0; do
            [ -e "$d" ] || continue
            drv=$(readlink "$d/driver" 2>/dev/null)
            printf '%s driver=%s\n' "${d##*/}" "${drv##*/}"
        done
    } > "$file" 2>&1
}

snapshot pre
cat /proc/uptime > "$OUT/start-uptime.txt"
dmesg > "$OUT/dmesg-pre.txt"
logcat -d -v threadtime > "$OUT/logcat-pre.txt"

input keyevent WAKEUP
wm dismiss-keyguard
monkey -p com.energy.tc2c -c android.intent.category.LAUNCHER 1 > "$OUT/app-launch.txt" 2>&1
sleep 20
snapshot active
dmesg > "$OUT/dmesg-active.txt"
logcat -d -v threadtime > "$OUT/logcat-active.txt"

input keyevent HOME
sleep 10
snapshot home
am force-stop --user 0 com.energy.tc2c
sleep 2

# Fail-safe restoration to the exact pre-test idle values observed on this unit.
echo 0 > /sys/class/yft_extcon/tiny2c_mode
echo 0 > /sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode
sleep 10
snapshot restored
dmesg > "$OUT/dmesg-restored.txt"
logcat -d -v threadtime > "$OUT/logcat-restored.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/COMPLETE"
sync
