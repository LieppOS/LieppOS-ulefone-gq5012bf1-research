# Hynitron I2C/protocol contract

The live instance is adapter 0, 7-bit address `0x15`, bus clock 400 kHz.

## Framing

`hyn_i2c_read(client,wbuf,wlen,rbuf,rlen)` performs one
`i2c_master_send` followed by one `i2c_master_recv`; there is no repeated-start
combined message. A negative send is logged but stock still attempts receive.
A negative receive is returned. Positive short transfers are treated as
success exactly as stock. `hyn_i2c_write` is one `i2c_master_send` and likewise
accepts any nonnegative result. Byte helpers send `[register,value]` or send
one register then receive one byte.

Generic 16-bit helpers serialize register addresses big-endian, prepend them
to a 600-byte stack buffer for writes, and use the same send/receive rules.
Legacy CST3xx direct helpers retry at most twice and stop on a positive return.
Multi-byte coordinates are nibble-packed big-endian as documented in the input
contract.

## Firmware protocol finding

The frozen ELF contains image selection, running-info and bootloader-detection
entry points, but **no reachable erase, block-program, program-status poll, or
checksum-verify I2C sequence**. Relocation-aware call-site enumeration proves
all stock I2C calls belong to touch, identity, gesture, sleep, sysfs raw access,
or bootloader detection. Therefore no block size/address/status values are
invented. See `phase4-hynitron-firmware-update.md`.

Every observed register is tabulated in `phase4-hynitron-register-map.tsv`.
No live I2C operation was performed.
