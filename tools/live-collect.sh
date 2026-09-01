#!/usr/bin/env bash
set -u

MODE="${1:-recovery}"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="$HOME/android/gq5012bf1-live-${MODE}-${STAMP}"

mkdir -p "$OUT"

echo "[*] Waiting for device..."


run() {
    local name="$1"
    shift
    echo "[*] $name"
    adb shell "$@" >"$OUT/$name.txt" 2>&1 || true
}

adb devices -l > "$OUT/adb-devices.txt" 2>&1

run identity '
echo "=== ID ==="
id
echo
echo "=== SELINUX ==="
getenforce 2>/dev/null
echo
echo "=== UNAME ==="
uname -a
echo
echo "=== VERSION ==="
cat /proc/version 2>/dev/null
'

run properties 'getprop'

run boot '
echo "===== CMDLINE ====="
cat /proc/cmdline 2>/dev/null
echo
echo "===== BOOTCONFIG ====="
cat /proc/bootconfig 2>/dev/null
echo
echo "===== SLOT ====="
getprop ro.boot.slot_suffix
echo
echo "===== BOOT PROPS ====="
getprop | grep -Ei "ro.boot|hardware|platform|product|build|crypto|vndk|treble|virtual_ab|dynamic" | sort
'

run proc '
echo "===== FILESYSTEMS ====="
cat /proc/filesystems 2>/dev/null
echo
echo "===== PARTITIONS ====="
cat /proc/partitions 2>/dev/null
echo
echo "===== MODULES ====="
cat /proc/modules 2>/dev/null
echo
echo "===== INTERRUPTS ====="
cat /proc/interrupts 2>/dev/null
echo
echo "===== INPUT DEVICES ====="
cat /proc/bus/input/devices 2>/dev/null
echo
echo "===== MOUNTS ====="
cat /proc/mounts 2>/dev/null
'

run block-devices '
echo "===== BY-NAME ====="
ls -la /dev/block/by-name 2>/dev/null
echo
echo "===== MAPPER ====="
ls -la /dev/block/mapper 2>/dev/null
echo
echo "===== BOOTDEVICE ====="
ls -la /dev/block/bootdevice/by-name 2>/dev/null
echo
echo "===== UFS ====="
find /sys/class/scsi_device /sys/class/scsi_disk /sys/class/block \
    -maxdepth 2 -type l -print 2>/dev/null | sort
'

run device-nodes '
echo "===== VIDEO ====="
ls -l /dev/video* /dev/v4l-subdev* /dev/media* 2>/dev/null
echo
echo "===== INPUT ====="
ls -l /dev/input/* 2>/dev/null
echo
echo "===== SOUND ====="
ls -l /dev/snd/* 2>/dev/null
echo
echo "===== TEE ====="
ls -l /dev/*tee* /dev/*tkcore* /dev/rpmb* /dev/*trust* 2>/dev/null
echo
echo "===== OTHER CHAR/BLOCK NODES ====="
find /dev -maxdepth 2 \( -type b -o -type c \) -print 2>/dev/null | sort
'

run power-supply '
for d in /sys/class/power_supply/*; do
    [ -e "$d" ] || continue
    echo
    echo "################################################"
    echo "$d -> $(readlink -f "$d")"
    echo "################################################"

    echo "-- available attributes --"
    ls "$d" 2>/dev/null | sort

    echo "-- values --"
    for f in "$d"/*; do
        [ -f "$f" ] || continue
        b=$(basename "$f")
        printf "%s=" "$b"
        cat "$f" 2>/dev/null || true
        echo
    done
done
'

run thermal '
echo "===== THERMAL ZONES ====="
for d in /sys/class/thermal/thermal_zone*; do
    [ -e "$d" ] || continue
    echo
    echo "### $d -> $(readlink -f "$d")"
    for f in type temp mode policy passive; do
        [ -f "$d/$f" ] && {
            printf "%s=" "$f"
            cat "$d/$f" 2>/dev/null
        }
    done
    grep -H . "$d"/trip_point_*_type "$d"/trip_point_*_temp 2>/dev/null
done

echo
echo "===== COOLING DEVICES ====="
for d in /sys/class/thermal/cooling_device*; do
    [ -e "$d" ] || continue
    echo
    echo "### $d -> $(readlink -f "$d")"
    for f in type cur_state max_state; do
        [ -f "$d/$f" ] && {
            printf "%s=" "$f"
            cat "$d/$f" 2>/dev/null
        }
    done
done
'

run leds '
for d in /sys/class/leds/*; do
    [ -e "$d" ] || continue
    echo
    echo "### $d -> $(readlink -f "$d")"
    echo "-- attributes --"
    ls "$d" 2>/dev/null
    for f in brightness max_brightness trigger color multi_index multi_intensity function; do
        [ -f "$d/$f" ] && {
            printf "%s=" "$f"
            cat "$d/$f" 2>/dev/null
            echo
        }
    done
done
'

run backlight '
for d in /sys/class/backlight/*; do
    [ -e "$d" ] || continue
    echo
    echo "### $d -> $(readlink -f "$d")"
    for f in brightness actual_brightness max_brightness bl_power type scale; do
        [ -f "$d/$f" ] && {
            printf "%s=" "$f"
            cat "$d/$f" 2>/dev/null
        }
    done
done
'

run drm '
echo "===== DRM TREE ====="
ls -la /sys/class/drm 2>/dev/null

for d in /sys/class/drm/card*-*; do
    [ -e "$d" ] || continue
    echo
    echo "### $d -> $(readlink -f "$d")"
    for f in status enabled modes connector_id dpms subconnector; do
        [ -f "$d/$f" ] && {
            echo "--- $f ---"
            cat "$d/$f" 2>/dev/null
        }
    done
done
'

run video4linux '
for d in /sys/class/video4linux/*; do
    [ -e "$d" ] || continue
    echo
    echo "### $d -> $(readlink -f "$d")"
    [ -f "$d/name" ] && cat "$d/name"
    [ -f "$d/dev" ] && cat "$d/dev"
    [ -f "$d/device/uevent" ] && cat "$d/device/uevent"
    echo -n "driver="
    readlink -f "$d/device/driver" 2>/dev/null || true
    echo
done
'

run sound '
echo "===== CARDS ====="
cat /proc/asound/cards 2>/dev/null
echo
echo "===== PCM ====="
cat /proc/asound/pcm 2>/dev/null
echo
echo "===== DEVICES ====="
cat /proc/asound/devices 2>/dev/null
echo
echo "===== SOUND SYSFS ====="
for d in /sys/class/sound/*; do
    echo "$d -> $(readlink -f "$d")"
done 2>/dev/null
'

run input '
for d in /sys/class/input/input*; do
    [ -e "$d" ] || continue
    echo
    echo "### $d -> $(readlink -f "$d")"

    for f in name phys uniq properties; do
        [ -f "$d/$f" ] && {
            printf "%s=" "$f"
            cat "$d/$f" 2>/dev/null
        }
    done

    if [ -d "$d/id" ]; then
        grep -H . "$d"/id/* 2>/dev/null
    fi

    if [ -d "$d/capabilities" ]; then
        grep -H . "$d"/capabilities/* 2>/dev/null
    fi

    echo -n "driver="
    readlink -f "$d/device/driver" 2>/dev/null || true
done
'

run i2c '
for d in /sys/bus/i2c/devices/*; do
    [ -e "$d" ] || continue
    echo
    echo "### $d"
    echo "real=$(readlink -f "$d")"
    echo -n "driver="
    readlink -f "$d/driver" 2>/dev/null || echo NONE
    echo -n "module="
    readlink -f "$d/driver/module" 2>/dev/null || echo BUILTIN_OR_NONE
    [ -f "$d/name" ] && { echo -n "name="; cat "$d/name"; }
    [ -f "$d/modalias" ] && { echo -n "modalias="; cat "$d/modalias"; }
    [ -f "$d/uevent" ] && cat "$d/uevent"
done
'

run spi '
for d in /sys/bus/spi/devices/*; do
    [ -e "$d" ] || continue
    echo
    echo "### $d"
    echo "real=$(readlink -f "$d")"
    echo -n "driver="
    readlink -f "$d/driver" 2>/dev/null || echo NONE
    echo -n "module="
    readlink -f "$d/driver/module" 2>/dev/null || echo BUILTIN_OR_NONE
    [ -f "$d/modalias" ] && { echo -n "modalias="; cat "$d/modalias"; }
    [ -f "$d/uevent" ] && cat "$d/uevent"
done
'

run platform-drivers '
for d in /sys/bus/platform/devices/*; do
    [ -e "$d" ] || continue
    drv=$(readlink -f "$d/driver" 2>/dev/null || true)

    if [ -n "$drv" ]; then
        printf "%s | %s" "$(basename "$d")" "$(basename "$drv")"
        mod=$(readlink -f "$d/driver/module" 2>/dev/null || true)
        [ -n "$mod" ] && printf " | module=%s" "$(basename "$mod")"
        printf "\n"
    fi
done | sort
'

run misc-buses '
echo "===== IIO ====="
for d in /sys/bus/iio/devices/*; do
    [ -e "$d" ] || continue
    echo "$d -> $(readlink -f "$d")"
    [ -f "$d/name" ] && cat "$d/name"
done

echo
echo "===== HWMON ====="
for d in /sys/class/hwmon/*; do
    [ -e "$d" ] || continue
    echo "$d -> $(readlink -f "$d")"
    grep -H . "$d"/name "$d"/temp*_label "$d"/temp*_input 2>/dev/null
done

echo
echo "===== TYPE-C ====="
for d in /sys/class/typec/*; do
    [ -e "$d" ] || continue
    echo "$d -> $(readlink -f "$d")"
    grep -H . "$d"/data_role "$d"/power_role "$d"/port_type "$d"/power_operation_mode 2>/dev/null
done

echo
echo "===== UDC ====="
for d in /sys/class/udc/*; do
    [ -e "$d" ] || continue
    echo "$d -> $(readlink -f "$d")"
    grep -H . "$d"/state "$d"/current_speed "$d"/maximum_speed 2>/dev/null
done

echo
echo "===== EXTCON ====="
for d in /sys/class/extcon/*; do
    [ -e "$d" ] || continue
    echo "$d -> $(readlink -f "$d")"
    grep -H . "$d"/name "$d"/state 2>/dev/null
done

echo
echo "===== RTC ====="
for d in /sys/class/rtc/*; do
    [ -e "$d" ] || continue
    echo "$d -> $(readlink -f "$d")"
    grep -H . "$d"/name "$d"/date "$d"/time 2>/dev/null
done
'

run kernel-modules '
for d in /sys/module/*; do
    [ -e "$d" ] || continue
    printf "%s" "$(basename "$d")"
    [ -f "$d/refcnt" ] && printf " refcnt=%s" "$(cat "$d/refcnt" 2>/dev/null)"
    printf " holders="
    ls "$d/holders" 2>/dev/null | tr "\n" ","
    printf "\n"
done | sort
'

run services '
echo "===== SERVICE LIST ====="
service list 2>/dev/null
echo
echo "===== PS ====="
ps -A -Z 2>/dev/null
echo
echo "===== INIT SERVICES ====="
getprop | grep "^\[init.svc." | sort
'

run getevent '
getevent -lp 2>/dev/null
'

run dmesg 'dmesg'

echo "[*] Capturing live flattened device tree..."
adb exec-out '
if [ -d /sys/firmware/devicetree/base ]; then
    cd /sys/firmware/devicetree/base &&
    tar -cf - .
fi
' > "$OUT/devicetree.tar" 2>"$OUT/devicetree.err" || true

if [ ! -s "$OUT/devicetree.tar" ]; then
    rm -f "$OUT/devicetree.tar"
fi

if [ "$MODE" = "stock" ]; then
    run hal-list '
echo "===== LSHAL ====="
lshal 2>/dev/null
echo
echo "===== SERVICE LIST ====="
service list 2>/dev/null
echo
echo "===== DUMPSYS LIST ====="
dumpsys -l 2>/dev/null
'

    run battery-dump 'dumpsys battery 2>/dev/null'
    run thermal-dump 'dumpsys thermalservice 2>/dev/null'
    run sensors-dump 'dumpsys sensorservice 2>/dev/null'
    run camera-dump 'dumpsys media.camera 2>/dev/null'
    run display-ids 'dumpsys SurfaceFlinger --display-id 2>/dev/null'
    run display-dump 'dumpsys display 2>/dev/null'
    run input-dump 'dumpsys input 2>/dev/null'
    run vibrator-dump 'dumpsys vibrator_manager 2>/dev/null; dumpsys vibrator 2>/dev/null'
    run usb-dump 'dumpsys usb 2>/dev/null'
fi

ARCHIVE="${OUT}.tar.gz"

tar -C "$(dirname "$OUT")" \
    -czf "$ARCHIVE" \
    "$(basename "$OUT")"

echo
echo "=============================================="
echo "DONE"
echo "Directory: $OUT"
echo "Archive:   $ARCHIVE"
echo "=============================================="
sha256sum "$ARCHIVE"
