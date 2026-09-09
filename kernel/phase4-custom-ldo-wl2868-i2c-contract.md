# WL2868 raw-I2C contract

Stock imports only `i2c_transfer`; it has no SMBus, regmap, regulator, retry, mutex, or lock API.

## One-byte register read

Construct two stack `struct i2c_msg` entries:

1. address=`wl2864c_data.client->addr`, flags=0, len=1, buffer=&register;
2. same address, flags=`I2C_M_RD`, len=1, buffer=&value.

Call `i2c_transfer(client->adapter,msgs,2)` once. Any nonnegative return—including a short transfer—is treated as success. A negative return logs `_dev_info(&client->dev,"i2c transfer failed (%d)\n",ret)`.

## One-byte register write

Construct one stack message: current client address, flags=0, len=2, buffer=`{register,value}`. Call `i2c_transfer(client->adapter,&msg,1)` once. Any nonnegative result is treated as success; a negative result receives the same `_dev_info` log.

There is no delay inside either operation, no null-client test, no retry, and no register/value width beyond 8 bits. The operations are compiler-inlined into four LDO helpers and the misc read/write functions; there are no separate stock read/write-helper symbols.

## Caller-specific error mapping

| Caller | Read error | Write error |
|---|---|---|
| LDO vout helper | readback error logged/ignored for return | raw negative helper return |
| LDO enable helper | normalized to `-ENODEV` | raw negative helper return |
| misc read | raw negative return | n/a |
| misc write | n/a | normalized to `-ENODEV` |
| public `will_ldo_*` | helper result discarded; supported chip returns 0 | same |

Probe makes no I2C transfer. After GPIO sequencing it changes `client->addr` from the DT-created 0x29 to literal 0x2f, so all operational transfers use 0x2f.
