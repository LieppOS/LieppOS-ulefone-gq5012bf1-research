#!/bin/bash
# Dump demangled, non-STL exported API surface of the AC020 thermal native libs.
R="/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research"
B="$R/workspace/gq5012bf1/stock/partitions/system/app/FactoryMode/lib/arm64"
OUT="$R/qwen_hardware/qwen-thermal/re/calibration/native-api-inventory.md"
mkdir -p "$(dirname "$OUT")"
{
  echo "# Native radiometry / calibration / ISP API inventory (AC020 stack)"
  echo
  echo "Extracted with \`nm -C --defined-only\` from the FactoryMode-bundled arm64 copies"
  echo "(identical ELF set to the M170infisens APK payload). STL/cJSON noise filtered."
  for lib in libadvirtempac020 libadvirtemp libcommonsdk libdualcalibration \
             libadvirprocess libadvirparse libadvirutils libirpack_tool libframecache \
             libircam libirutilssdk; do
    echo
    echo "## $lib"
    if [ -f "$B/$lib.so" ]; then
      nm -C --defined-only "$B/$lib.so" 2>/dev/null \
        | awk 'NF>=3 { $1=""; $2=""; sub(/^ /,""); print }' \
        | grep -v '^_' \
        | grep -v 'cJSON' \
        | grep -v 'std::' \
        | grep -v '__a' \
        | sort -u
    else
      echo "(absent)"
    fi
  done
} > "$OUT" 2>&1
wc -l "$OUT"
