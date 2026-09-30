# vendor_boot recovery-fragment correction

The first vendor_boot comparison used the wrong field order for a version-4
vendor ramdisk table entry.

Correct entry layout:

- uint32 ramdisk_size
- uint32 ramdisk_offset
- uint32 ramdisk_type
- char ramdisk_name[32]
- uint32 board_id[16]

The values previously displayed as the first two board IDs decode as the
little-endian ASCII strings "reco" and "very". The type-2 fragment is therefore
the normal named `recovery` fragment.

This parser error affected the fragment filename/extraction step only.

The substantive structural comparison remains valid:

- DTB is byte-identical between stock and current vendor_boot.
- Platform fragment is byte-identical.
- Stock recovery fragment is 4,714,551 bytes compressed.
- Current recovery fragment is 33,582,922 bytes compressed.
- Current fastbootd lacks working BootControl/slot awareness while normal
  Android has a working AIDL BootControl HAL.

The recovery fragment is therefore the primary regression candidate.
