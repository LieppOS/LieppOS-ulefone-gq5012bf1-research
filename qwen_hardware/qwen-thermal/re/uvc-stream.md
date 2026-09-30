# UVC stream

`libusbuvccamera020.so` implements UVC descriptor scanning, interface claiming, alternate-setting selection, stream control, transfer assembly and frame-byte-count validation. Supported host outputs in Java are YUYV, NV12, NV12+temperature and YUYV+temperature.

FactoryMode exact configuration: 256x384, 25 fps, bandwidth 1.0, USB driver, YUYV+temperature. This is consistent with stacked 256x192 image and LE16 temperature planes. M170infDlp factory constants add two metadata lines (`height=386`, line height=2). The SDK also carries 384x288 and 640x512 WN modes, including V2 variants.

A complete shipping-module descriptor map cannot be truthfully produced offline. Required passive capture: after stock power-up, save `/sys/bus/usb/devices/*/{idVendor,idProduct,manufacturer,product,serial,bConfigurationValue}`, raw descriptors and `lsusb -v`; record one frame per negotiated mode and match byte lengths. No vendor writes are needed for this descriptor step.
