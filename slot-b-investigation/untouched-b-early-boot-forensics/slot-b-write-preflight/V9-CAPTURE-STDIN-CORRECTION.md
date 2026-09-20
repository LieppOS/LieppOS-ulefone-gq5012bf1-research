# V9 runtime capture stdin correction

The first V9 runtime capture used:

    grep ... | while read M; do adb shell ...; done

`adb` inherited the pipeline stdin and consumed remaining marker names, so only
the first V9 marker was printed.

That output cannot be used to infer that later V9 marker files were absent or
zero.

What is already proven independently:

    v9-system-pfsd-start=1

with a fresh Slot-B timestamp.

Therefore the main system `on post-fs-data` action definitely began.

The corrected capture first materializes the marker list in the host shell and
redirects adb stdin from /dev/null.

PHONE_MODIFIED=0
