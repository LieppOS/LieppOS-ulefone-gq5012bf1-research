# stock order (sub-driver link order in stock imgsensor.ko)
ALL="imx989 imx989cts s5kgm2sp s5kgn1sp ov32b40 s5kjn1 s5kjn1cts s5kjn1main2 ov64b"
L=""; for s in $ALL; do [ -d $B/common/${s}_mipi_raw ] && L="$L ${s}_mipi_raw"; done
echo $L
