# Batch03 power-policy and cooling source findings

13 selected CPU/DVFS/sugov/core_ctl/QoS/PBM/PPB/CM/DCM modules have independent
whole-ELF stock parity in the maintained power-policy repository at
`de4756ceb05c882be10bb8096d581d114dc2837a`. Complete per-module evidence:
../kernel-source-reconstruction/PLATFORM-BATCH-03/POWER-POLICY/.

Stock PPB lacks a callback and its registration present in the public ALPS donor.
The full C patch removes that behavior at source level; no machine-code transplant
or CRC override is used. For charger cooling, actual stock policy and source-level
warning locations are now preserved and fully accepted through the thermal engine
at `75f8c710dcb605a47e657b20b2782bd9c4dc0b3c`.

68 actual compiled units across the complete batch are indexed with hashes and API
calls in SOURCE-TO-HARDWARE-CONTRACTS.json. Enabled PBM/cooling/OPP and CPU policy
DT configuration does not measure CPU transitions, voltage/current safety, charger
operation or physical thermal response. External charger declarations are genuine
preserved producer-source witnesses only; the whole producer remains separately owned.

The genuine common thermal-generic-adc implementation is source-complete and
instruction/data/ABI-exact, but 21 split-BTF reference bytes prevent full acceptance:
it remains C, never normalized. See Batch03 BLOCKERS.tsv and HARDWARE-CONTRACT.md.
Prior calibration/firmware/runtime boundaries remain unchanged; no phone interaction.
