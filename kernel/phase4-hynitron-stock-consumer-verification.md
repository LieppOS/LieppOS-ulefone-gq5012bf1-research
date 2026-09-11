# Stock spi_tiny_co5300_lcd consumer verification

Offline MODVERSION resolution was performed between frozen stock consumer
`workspace/phase4-hynitron/oracle/spi_tiny_co5300_lcd.ko` and rebuilt provider
`workspace/phase4-hynitron/rebuild/hynitron.ko`.

| import | consumer-required CRC | rebuilt export CRC | type/KCFI | result |
|---|---:|---:|---|---|
| `tiny_tp_gesture_contorl` | `0x4e4b7919` | `0x4e4b7919` | `void(int)`, `0x019c0cac` | ACCEPT |
| `tiny_tp_power_contorl` | `0xfcc94fc7` | `0xfcc94fc7` | `void(int)`, `0x019c0cac` | ACCEPT |

Names preserve stock misspelling. CRCs are emitted naturally by genksyms from
the reconstructed prototypes; there was no `__versions`, ELF, consumer, or CRC
patch. All eight stock call relocations remain resolvable. Result: **2/2 stock
consumer edges ABI-compatible without modification**.
