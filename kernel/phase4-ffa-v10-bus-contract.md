# ffa_v10 bus/device contract

Everything below is confirmed byte-identical to stock (function-parity table)
and lives entirely inside `ffa_v10.ko` - the bus/device model is **not**
split between GKI and the vendor module: GKI does not build
`CONFIG_ARM_FFA_TRANSPORT` at all on this device, so `ffa_v10.ko` supplies the
whole bus.

## Bus registration (`arm_ffa_bus_init` / `arm_ffa_bus_exit`)

```c
struct bus_type ffa_bus_type = {
	.name		= "arm_ffa",
	.match		= ffa_device_match,
	.uevent		= ffa_device_uevent,
	.probe		= ffa_device_probe,
	.remove		= ffa_device_remove,
};
EXPORT_SYMBOL_GPL(ffa_bus_type);

int arm_ffa_bus_init(void)  { return bus_register(&ffa_bus_type); }
void arm_ffa_bus_exit(void) {
	ffa_devices_unregister();       /* __ffa_devices_unregister over bus_for_each_dev */
	bus_unregister(&ffa_bus_type);
}
```
Called once from `ffa_init()`; torn down once from `ffa_exit()`.

## Device registration (`ffa_device_register` / `ffa_device_unregister`)

```c
struct ffa_device *ffa_device_register(const uuid_t *uuid, int vm_id,
					const struct ffa_ops *ops)
{
	dev = kzalloc(...);
	dev->vm_id = vm_id;
	uuid_copy(&dev->uuid, uuid);
	dev->ops = ops;
	id = ida_alloc_range(&ffa_bus_id, 0, U32_MAX, GFP_KERNEL);
	dev_set_name(&dev->dev, "arm-ffa-%d", id);
	dev->dev.bus = &ffa_bus_type;
	dev->dev.release = ffa_release_device;
	device_register(&dev->dev);
	return dev;
}

void ffa_device_unregister(struct ffa_device *ffa_dev)
{
	if (!ffa_dev) return;
	device_unregister(&ffa_dev->dev);
}
```
`ffa_release_device()` frees the ID (`ida_free`) and `kfree`s the device on
final `put_device()`.

## Device matching

* `ffa_device_match(dev, drv)` - `uuid_equal(&ffa_dev->uuid, &ffa_drv->id_table[i].uuid)` scan.
* `ffa_device_match_uuid(ffa_dev, uuid)` - `EXPORT`-free public helper letting a
  consumer probe function re-check the UUID (used by drivers that register
  more than one device instance, not by tkcore_drv).
* `partition_id_show` / `uuid_show` - `DEVICE_ATTR_RO`, expose `id`/`uuid` at
  `/sys/bus/arm_ffa/devices/*/{partition_id,uuid}`. This IS present in the
  stock strings table (`partition_id`, `uuid`) - the only sysfs surface this
  module owns.

## Driver attach/detach (`ffa_driver_register` / `ffa_driver_unregister`)

See `phase4-ffa-v10-registration-contract.md` below in the reconstruction
report for the full call contract; summary here:

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

void ffa_driver_unregister(struct ffa_driver *driver)
{
	driver_unregister(&driver->driver);
}
```
Probe/remove wrapping (`ffa_device_probe`/`ffa_device_remove`) is the bus's
own `.probe`/`.remove`, which cast `dev`/`drv` to `ffa_device`/`ffa_driver`
and call the consumer's `->probe(ffa_dev)` / `->remove(ffa_dev)` (guarding
`->remove` against NULL - see `ad73dc7263ea` "Check if ffa_driver remove is
present before executing", already present in the vendor snapshot).

## Refcount / lifetime

Standard `struct device` refcounting via `get_device`/`put_device` (called
transitively through `device_register`/`device_unregister`); no extra
refcounting layer is added.

## PM

None. No `.pm` ops on `ffa_bus_type`, no suspend/resume hooks in either
`driver.c` or `bus.c`.

## Split with GKI

None - GKI builds zero FF-A code on this device (`CONFIG_ARM_FFA_TRANSPORT`
unset in `gki_defconfig`). `ffa_v10.ko` is the entire bus, device and
transport layer.
