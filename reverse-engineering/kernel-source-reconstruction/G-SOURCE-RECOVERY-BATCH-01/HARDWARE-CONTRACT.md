# Saved GQ5012BF1 hardware and software boundaries — no phone access

Labels: PROVEN_RUNTIME (saved live capture, not newtesting), ENABLED_IN_STOCK_DT (explicit savedstock node), STOCK_BINARY_IMPLEMENTATION (ELF), PUBLIC_SOURCE_ONLY (notphoneproof), UNKNOWN (missing evidence).

## Camera lens7

Existing saved livebus/DT/HAL/calibration evidence in reverse-engineering/camera/vcm and camera/ois plus DONE/CAMERA-VCMS andDW9781C notes is reused, not rewritten. Three actuators implement DW9800Wcommand set: cam0imx989 bus7main_vcm, cam2s5kjn1main2 bus2main4_vcm, cam3ov64b bus4main2_vcm. Cam1fronts5kjn1 fixedfocus. Wireaddress0x0c comes fromdecodedHAL lens table; placeholder DTreg0x0a/0x0b/0x0d aren't wireaddressproof. AFpower usesimgsensors AFVDD2.8V, WL2864Cchannels5/6; module doesn'townGPIO/pinctrl/regulator driver. main3/subVCM platformonly; nohardwarepresenceinferred fromshipped .ko.

DW9781C savedstockDT camera-ois-main@e on i2c4, driver-forcedaddress0x0a and hf_manager OIS1. Driverbinding notphysicalpopulation/activeservo proof: oldreachability evidence saysstockHAL OISlistsDummy, no S_OIS_INIT/UNINIT caller; probe/open/runtimePM make nochipbusaccess. Chipfirmware/servo closedoutsidekernel source. No motor, EEPROM orOISaccess performed. ExactsourceELFdoesn'tprovephysicalOISoperation. AFmedia/VCMuserspace V4L2camera-HALboundary remainsunchanged.

## Modem interfaces7

Savedstock modem DT/HAL/runtime notes in reverse-engineering/modem showMD1gen6299, CCIF+DPMAIFv3, namedregulators/IRQs/sharedmemory; use exactsaved moduleprovider/load-order records in ABI-PROVIDERS.tsv. Thisbatchownsnormal-world C2K/rawbulk/MDDP/modemthermalpolicy Linuximplementations only. SignedMD/DRDI/NVRAM/carrier MCF/AndroidRIL/IMS source notreconstructed. C2Kfunctions shippedevidence is not CDMAhardware/RFcapability proof. No firmware/IMEI/NVRAM/carrierdata/partitionmodification. Per-target unverifiedregisterranges/clocks/IRQs/DMA topology remainUNKNOWN unlessreferencedstockcaptureproves them; publicsourcecapability aloneisPUBLIC_SOURCE_ONLY.

## GenieZone/FF-A/trusted-memory9

Normal-worldLinuxFF-Abus/GZ transport/KREE/sharedmemory implementation, notsecureworldTEEfirmware. Stockmodule/import/alias/string evidence is STOCK_BINARY_IMPLEMENTATION; savedDT/runtime records distinguishactivebinding fromjustloadedmodule. FF-A SMCconduit/UUID/bus/tablecode incompiledsource doesnotcertifysecurepayloads. Publicsource reserveheap/secureIOMMUfeatures notassumed fitted/enabled. TkcoreCsevenAPI provider andmtk_sec_heapD memoryhandle boundary remainoutsideownedmodulecertification. Androidioctl/SELinux/clientcontracts savedunderexistinggeniezone/TrustKernel research are retained; no phone, runtimecall, securemonitorinvocation, TAinstallorHALexperiment.

## Exact per-target runtime bindings

G-REMAINING-INVENTORY.tsv preservescanonical runtime_status and observed_bindings for everyGidentity; BATCH-MANIFEST.tsv preservesexact23bindings/providergraphs. Mandatory sourcecertification doesnotalterruntime/component/hardwarestatus. Registerrange/IRQ/clock/regulator/pinctrl/DMA/sharedmemory details lackingactualstockcaptureevidence remainUNKNOWN, neverfilled froma similarpublicSoCdriver.
