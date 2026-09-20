# V13 size-neutral correction

The first V13 diagnostic source was logically correct but added comments and
increased vendor.img from:

    816349184

to:

    816357376

an 8192-byte overshoot relative to the existing Slot-B vendor logical extent.

No V13 image was written to the phone.

The corrected V13 keeps init.insmod.sh exactly the same byte length as the
pre-V13 script and changes only the six bytes spelling "vendor" in:

    for partition in system_dlkm vendor

to spaces, leaving a shell loop containing only system_dlkm.

This preserves the intended V13 experiment without requiring any super metadata
or logical-partition resize.

V12 system remains unchanged.

PHONE_MODIFIED=0
