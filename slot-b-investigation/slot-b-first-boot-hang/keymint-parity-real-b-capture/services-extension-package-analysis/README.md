# Slot-B services-extension package blocker

The prior controlled Product-B test successfully removed the previous fatal:

`Unknown source permission
com.google.android.gms.permission.ACTIVITY_RECOGNITION in split permissions`

That causal hypothesis is now confirmed.

Slot B progressed further but still did not complete boot.

The next hard PackageManager failure is:

`java.lang.RuntimeException: Required services extension package is missing,
config_servicesExtensionPackage had defined with
com.google.android.ext.services, but can not find the package info on the
system image`

This directory records read-only provenance work to identify the exact RRO or
resource configuration assigning `config_servicesExtensionPackage` to the
Google ExtServices package.

No partitions are modified by this investigation.
