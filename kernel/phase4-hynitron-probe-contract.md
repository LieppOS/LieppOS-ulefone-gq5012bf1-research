# Hynitron probe contract

Relocation-aware stock order:

1. verify/match `hynitron,hyn_ts`; allocate 584-byte private state and publish
   global singleton/client data;
2. allocate/parse platform data, including GPIO 11/32/119, 340x340 and one
   contact;
3. request VDD GPIO, drive high; request IRQ/reset GPIOs and set IRQ input;
4. reset low 20 ms → high with stock settling delays;
5. initialize configured identity (CST820/0xb7, family 800), settle 60 ms and
   read running firmware via 0xa6; invoke the bootloader-presence detector only
   if that normal read fails, aborting only if fallback detection also fails;
6. allocate/configure/register `hyn_ts` input device and initialize its one
   workqueue/work item;
7. map GPIO11 to IRQ, request falling-edge oneshot threaded IRQ, enable wake,
   then disable IRQ for remaining initialization;
8. call `hyn_update_firmware_init`, which re-reads firmware information and
   resolves the configured chip table row; stock logs/ignores a negative return
   and does not invoke image selection or programming during probe;
9. create `/sys/hynitron_debug` five-node group and the two-node gesture group;
   install gesture key capabilities;
10. final reset, enable IRQ;
11. `yft_set_touch_device_used("hyn_ts",1)` (return ignored), success 0.

## Failure behavior

Allocation fails with `-ENOMEM`. Missing DT/match/GPIO/IRQ returns the underlying
negative errno (stock commonly normalizes interface-creation failure to `-EIO`).
An initial firmware-info failure aborts only when bootloader fallback detection also fails before input/IRQ; the later post-IRQ firmware-info re-read is logged and ignored. Input registration
failure frees the unregistered input object. IRQ failure unwinds input/GPIO.
Sysfs/gesture failure frees IRQ and follows stock cleanup labels. GPIOs are
freed in reverse reached order and private allocations are released; global
singleton is cleared. Stock's YFT candidate-add already occurred at module init
and is not rolled back; active/used is never marked on failed probe. No
firmware write is attempted on any failure path.

The final rail state on late failure can remain high until GPIO release because
stock does not drive VDD low before freeing it; this quirk is preserved rather
than 'fixed'.
