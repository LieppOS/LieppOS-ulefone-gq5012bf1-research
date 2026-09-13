# ffa_v10 driver registration/unregistration contract

Exact behaviour of the two hard-gate exports, since these are what
`tkcore_drv` (and `tmem_ffa`/`gz_main_mod`) call directly.

## `ffa_driver_register(driver, owner, mod_name)`

```c
int ffa_driver_register(struct ffa_driver *driver, struct module *owner,
			const char *mod_name)
{
	driver->driver.bus = &ffa_bus_type;
	driver->driver.name = driver->name;
	driver->driver.owner = owner;
	driver->driver.mod_name = mod_name;

	return driver_register(&driver->driver);
}
EXPORT_SYMBOL_GPL(ffa_driver_register);
```

* **arguments** - `driver` (the caller's static `struct ffa_driver`, embedding
  `.name`, `.probe`, `.remove`, `.id_table`), `owner` (always `THIS_MODULE`
  from the caller), `mod_name` (always `KBUILD_MODNAME` from the caller - both
  confirmed by tkcore_drv's exact call
  `ffa_driver_register(&tkcore_ffa_driver, THIS_MODULE, KBUILD_MODNAME)`,
  which is unchanged and still builds/links against this exact contract).
* **validation** - none beyond what `driver_register()` itself performs; no
  NULL check on `driver`, no duplicate-name check here (the driver core's own
  bus/name uniqueness enforcement applies).
* **module owner handling** - stored verbatim into `driver.owner`; this is
  what lets `driver_register()`'s reference counting keep the *caller's*
  module (e.g. `tkcore_drv.ko`) pinned while its `struct ffa_driver` is
  registered on the bus - not `ffa_v10.ko` itself.
* **driver name** - `driver->driver.name = driver->name`, i.e. the caller
  supplies the display/bus name (tkcore_drv's is `"tkcore_ffa"` per its own
  driver struct), not the caller's module name.
* **bus binding** - `driver.bus = &ffa_bus_type` always; a `struct ffa_driver`
  can only ever bind to the FF-A bus.
* **probe/remove wrappers** - not wrapped again here; `ffa_bus_type.probe`/
  `.remove` (`ffa_device_probe`/`ffa_device_remove`, set once at bus-register
  time) are the actual entry points the driver core calls, and *those* cast
  `to_ffa_driver(dev->driver)`/`to_ffa_device(dev)` before invoking the
  caller's `->probe(ffa_dev)`/`->remove(ffa_dev)`.
* **ID matching** - deferred entirely to `ffa_device_match()`, called by the
  driver core during `driver_register()`'s bus walk and on every subsequent
  device registration; matches `driver->id_table[i].uuid` against each
  `ffa_device.uuid`.
* **error propagation** - the `int` return of `driver_register()` is passed
  straight through, unmodified.
* **locking** - none added here; relies on the driver core's own
  bus/subsys-internal locking inside `driver_register()`.
* **lifecycle** - a registration has no separate teardown of its own; it is
  torn down by the paired `ffa_driver_unregister()` call.

## `ffa_driver_unregister(driver)`

```c
void ffa_driver_unregister(struct ffa_driver *driver)
{
	driver_unregister(&driver->driver);
}
EXPORT_SYMBOL_GPL(ffa_driver_unregister);
```

* **arguments** - the same `struct ffa_driver *` passed to `register()`.
* **validation** - none; a NULL or never-registered pointer is passed straight
  to `driver_unregister()`, whose own behaviour then applies.
* **error propagation** - `void`; nothing to propagate.
* **lifecycle** - unwinds `driver_register()`'s bus attachment; any bound
  `ffa_device` currently probed by this driver is removed first via the bus's
  own remove path (`ffa_device_remove()`), which the driver core drives.

## tkcore_drv's exact call, verified

`tkcore_drv` calls `ffa_driver_register(&tkcore_ffa_driver, THIS_MODULE,
KBUILD_MODNAME)` - this is a **direct pass of all three parameters this
contract expects**, and the tkcore_drv acceptance rebuild (§8 of the
reconstruction report) proves the CRC this call resolves to
(`0x0d53cde9`) is produced by exactly this function body, unmodified, from
real C. `tkcore_drv` was not touched by this closure.
