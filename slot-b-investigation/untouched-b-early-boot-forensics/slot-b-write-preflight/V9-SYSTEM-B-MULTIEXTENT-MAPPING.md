# V9 system_b multi-extent mapping validation

system_b consists of three non-contiguous extents in super:

    logical 0       +58208  -> super 6301696
    logical 58208   +673216 -> super 14474368
    logical 731424  +568168 -> super 15154088

Total:

    1299592 sectors
    665391104 bytes

A temporary device-mapper alias was created using all three extents and
compared against the existing system_b mapper.

MULTIEXTENT_MAPPING_VALID=i

No partition data was written.

PHONE_MODIFIED=0
