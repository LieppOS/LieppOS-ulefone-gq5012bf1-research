# GQ5012BF1 saved hardware contract — no physical hardware access

Labels refer onlyto captured evidence: PROVEN_RUNTIME (savedmodule/sysfs/kernelobservations), ENABLED_IN_STOCK_DT (savedFDT, not activity), STOCK_BINARY_IMPLEMENTATION (disassembly/fullsourceparity), PUBLIC_SOURCE_ONLY (unprovenplatformcapability), UNKNOWN (notcaptured). The2026-08-31capture ranLieppOSGSI onthedevicekernel: do notclaimstockUlefoneframework/camera/calibrationbehavior fromGSIuserspace. Originalcanonicalruntime/binding/componentfieldsnotchangedbysourcecertification.

## Board I/O

RT5133/extdev: originalALPS RT5133dtsi andGQmt6878 mergedexcerpt preservedhistorically in ../Reverse Engineer - DONE/RT5133-POWER-IC/source. Historical68/68DTpropertiescomparison recorded. Node rt5133@18 enabled in stockDT (ENABLED_IN_STOCK_DT), butsomecapture notes sayunbound; do notupgradephysicalpopulation/live railbehavior. Regulator8LDO/extdev sysfs/registeraccess is STOCK_BINARY_IMPLEMENTATION, exactpublicsource support. GenericpublicGPO1.8V/EINT187/HWEN188 differfromstockexcerpt; PUBLIC_SOURCE_ONLY notdevicefact. Live regulator voltage/currentrails UNKNOWN; no probing. Oldpower-support-ics.md noteclaimingnomodulecontradictsactualsignedinventory with2modules; preservechronology, exactstockELFwinsmodulepresence.

SPI-MT65XX: historicalphase4-spi-mt65xx-lineage/clock/PM/transfercontracts source andsavedFDT show8controllers compatiblemediatek,mt6989-spi (ENABLED_IN_STOCK_DT). Vendorheader adds cs_setuptime/holdtime/idletime, 3genuineexports,14OF matches, MT6989enhancepacket/timing/DMAext/quad/swCS settings STOCK_BINARY_IMPLEMENTATION. Register addresses/individualIRQ/clocknames requireexactsavednodes; notinventedhere (UNKNOWN). ParentSPIbusdriver sourceclosure notsecureTA orperipheralFWclosure. Runtime sourcecapabilities donotproveeverytransfermode active.

AW2013RGB: saved11-0045 I2Cdevice underi2c@11d71000 PROVEN_RUNTIME, RGBLEDsysfs brightness/delay/trigger observed. StockGPIO188 aw2013-pwd-gpio andGPIOhighpower path ENABLED_IN_STOCK_DT/STOCK_BINARY_IMPLEMENTATION. Itdoesnotconsumeupstreamvccregulator; physicalsupplyrail/activecurrent UNKNOWN. 8sourcefunctions/all21objects strictmatch, noilluminationtest.

YFTGPIOkeys: historicalPM/IRQ/probe/input/debounce/lifecyclecontracts retained. GPIOkeyF1/F2codes59/60, wake-capable/device_may_wakeup andirqwake logic STOCK_BINARY_IMPLEMENTATION/DTlabelasrecorded. Driverbody23functions/configsource nowstrictmatches. GPIO/IRQnumbers andwakeup-event-action mustbequotedfromsavednode, notpublicgenerickeys. No keypress/suspend/reboot qualification.

## Camera auxiliaries

AW36515/18/18v2: saved6-0063 and8-0063 I2Cbindings in prior54inventory PROVEN_RUNTIME; v2physicalselection UNKNOWN. Flashlightframeworkprovider parent andOEMregister/controlsource implementSTOCK_BINARY_IMPLEMENTATION. Privatecalibration/exposure/HAL currentconfiguration notsourcecertified. ExactsourceCresiduals22/23 functions and3objectscheduling/order cannotbe calledwholeequivalence orA; no flash pulse, currentorGPIOtest.

CameraEEPROM: saved2-0050,4-0050,4-0051,7-0051 clients andnormalmoduleload#107 PROVEN_RUNTIME. NKM complete126functions/141objects/calibrationparsers/layout source recovered andstrictstockgate passes. FourNothing-onlylayoutunitsexcludedperactualGQsource-list;14ODMCunits codedasparsers/structs, no compiledcalibrationdata transplant. SavedHALlibfeatureiodrv_mem.so CamCalHelper andimgsensorQSC/4-cell clients fromhistoricalCAMERA-EEPROMS notes. PhysicalOTPcontents/calibrationvalidity/modulepopulation UNKNOWN; no rawEEPROMreads. Fullsourcecompilation doesnotcertifyISP/HAL/tuning/OTP firmware.

## Normal-world biometrics/TEE

MicroArray: savedspi1.0fingerprintnode, /dev/madev0/read/write/ioctl/mmap, IRQ/input/sysfs andSELinuxuserspaceclients inhistoricalREADME PROVEN_RUNTIME/STOCK_BINARY_IMPLEMENTATION asrecorded. Genuinev4.0.06 twoTUs and80BlegacyMTK20xu32config (timing10,6MHz) stock-exactsource, naturaltee_spi_transfer sourceCRC verified. OriginalsecureSPIproxyTA966d3f7c andMicroArrayTAedcf9395 remainoutsideGPLsourceproof; opcodemeaning secureworld UNKNOWN.

YFTfingerprintplatform: recoveredGPLglue pinsreset/SPI/EINT states; EINTGPIO3/rising DTspecifier andpull-down/up/disabled states historicalphase4-fingerprint-irqcontract ENABLED_IN_STOCK_DT. Itsets pinctrl/bias, notrequest_irq/enable_irq itself; actualIRQownerMicroArray. Sixteenfunctionbytes match butnewline/string/include-counter metadata gaps remainC, notwholeA. ExactoriginalOEMheaderlist UNKNOWN; nocounterstub/header coercion.

Tkcorebackend: hardware-contract.md recordsFFAv1.0directmessage SPuuid8bf0ccc3-42a3-5271-860d-66580469479c fromsavedtee.img spmcmanifest (metadataonly). /reserved-memory/tkcore_shared_mem dynamic32MiB size0x2000000/alignment0x1000 andallocationrange fromsavedFDT ENABLED_IN_STOCK_DT; actualallocatedphysicalbase UNKNOWNunlesssavedcapture. Cacheablemappedsharedmemory/logring128KiB/coprocessorRPC normalworld STOCK_BINARY_IMPLEMENTATION. Trustkernel,tkcore lognodeabsent inrecordedDT, logirq0 path; secureGICdistributor0x0c400000/redist0x0c440000 metadata doesnotproveexecution. No clock/regulator/GPIO ownership inferredfromthismodule. Whole50functionbackend source notprivateTEEcontext/providerABI/srcversionclosure;5naturalCRCerrors andoriginalTEEC4blocked remainexplicitC.

No phone, GPIO/register probes, reflashing, reboot,moduleloading, securefirmwareextraction or deployment. Thesecontracts preserve originalboundaries andUNKNOWNs, notruntimepromotion.
