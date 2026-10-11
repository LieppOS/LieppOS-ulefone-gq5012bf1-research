# Batch04 charger/Type-C integration source reproduction

Whole mtk_charger_framework and MT6375 charger/battery/ADC sources now have independent
complete stock acceptance. The old declaration-only boundary is superseded for these
selected producers by full preserved implementations; it does not promote external gauge,
charge-pump, firmware or unrelated modules. Genuine yft_usb_flag and camera/long-charge
exports are derived from their real C definitions, not copied symvers.

charger_class, mtk_chg_type_det and rt_pd_manager instruction/data/CRC/KCFI/relocation
bodies reproduce, but srcversion differs. tcpc_mt6375 has exact66 functions/ABI/relocations,
with source-token/counter symbol metadata unclosed. tcpc_class has701/709 exact named
bodies in the independently reproduced source; a separate bounded experiment improves
to702/709 but fails full ELF and is not substituted into certification. All five remain C.

Actual public TCPC2.0.31 pin:2d6f27aa19d521409f443c8d821e2d475bdc72b6, subtree tree
5166ca2ab7fba22712731484a80657f27641818c, with full archived source and historical deltas.
Maintained usb_typec commit:d41a2436c15fc53c25061dd9cd19d0e08f11ffbb.

Detailed branch/metadata/ABI mismatches, failed experiments and exact next experiments:
../kernel-source-reconstruction/PLATFORM-BATCH-04/BLOCKERS.tsv and evidence/blocker-revisit/.
USB-C, uSmart and thermal have separate detection/rails but shared role/fabric. Last queued
role and non-atomic route changes are source behavior, not new physical concurrency tests.
No PD, charger, GPIO, firmware or live phone operation; existing owners/statuses preserved.
