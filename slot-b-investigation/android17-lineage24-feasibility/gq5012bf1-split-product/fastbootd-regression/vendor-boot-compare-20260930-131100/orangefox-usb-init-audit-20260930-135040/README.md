# OrangeFox USB fastbootd init audit

Previous runtime testing proved:

- the MTK AIDL BootControl service is healthy after OrangeFox initialization
- a manually late-started fastbootd successfully obtains AIDL IBootControl
- fastbootd opens the fastboot FunctionFS endpoints
- the host remains connected over ADB
- no `ffs.fastboot` configfs function was visible under the USB gadget

This audit records the exact OrangeFox recovery USB/init rules and current
configfs topology before attempting an in-place USB gadget transition.

No partition or runtime USB configuration changes are performed.
