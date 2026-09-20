# V10 marker seeding correction

The first V10 launch printed an empty `V10 SEEDED` section.

Post-test inspection confirmed that all eight V10 marker paths were absent,
although the built system init.rc contains all eight write commands.

Therefore the first V10 boot cannot localize execution using the V10 markers.

The launch-side dynamic sed extraction was faulty. Critical runtime markers
will now be seeded from an explicit host array and every marker will be read
back as zero before Slot B is activated.

No V10 rebuild or reflash is required.

PHONE_MODIFIED=0
