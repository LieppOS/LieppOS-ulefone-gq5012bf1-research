# Hynitron asynchronous behavior

Stock allocates one private `workqueue_struct` and one `work_struct` in the
584-byte state. `hyn_input_dev_int` initializes the report callback according
to chip family; configured CST820 uses `cst8xx_touch_report`. The threaded IRQ
disables IRQ then queues this work. The work performs all I2C reads and input
reporting and reenables IRQ on every terminal path.

The queue is single-purpose: no delayed work, timer, hrtimer, kthread,
completion, waitqueue, or firmware-program worker exists. Firmware selection is
synchronous during probe/sysfs handling. Probe's freshly created queue is
flushed; remove flushes queued work before releasing input/memory. Stock uses a
mutex for sysfs operations and guarded IRQ state; no spinlock-backed second
async state machine was found.
