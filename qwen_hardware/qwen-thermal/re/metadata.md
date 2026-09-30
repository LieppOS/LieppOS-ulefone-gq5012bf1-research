# Stream metadata

## Proven layouts
- Factory test: 256x384 at 25 fps, `YUYV_AND_TEMP_OUTPUT`; interpreted as 256x192 YUYV plus 256x192 LE16 radiometric plane.
- Calibration SOP constant: width 256, height 386, `IR_SENSOR_LINE_HEIGHT=2`; this indicates a 384-line combined payload plus two device-metadata lines for that dual/factory path.
- WN640 V2 radiometry consumes high and low NUC arrays of 8192 shorts each; geometry-specific metadata parsing occurs in `get_tempinfo_wn640_v2`.

## Format enum
`YUYV_IMAGE_OUTPUT=0`, `NV12_IMAGE_OUTPUT=1`, `NV12_AND_TEMP_OUTPUT=2`, `YUYV_AND_TEMP_OUTPUT=3`.

Frame validation in `libusbuvccamera020.so` compares `actual_bytes` with format/width/height expectations and logs broken frames. UVC status callbacks report disconnect/control errors.

## Unknowns
No live UVC descriptor dump or frame capture from the powered Armor module exists. Therefore interface numbers, endpoint address, alternate settings, packet size, exact thermal-plane offset for the shipping module and the two metadata lines' field layout remain unresolved. Passive steps needed: power using stock UI, capture `lsusb -v`/sysfs descriptors and one unmodified UVC frame without issuing vendor commands.
