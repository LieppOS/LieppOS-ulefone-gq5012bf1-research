# Host probe drift — not a stock ELF normalization

Initial public bootstrap rejected the prior Batch02 config hash. A byte-level comparison
found exactly one changed line: CONFIG_PAHOLE_VERSION=131 ->132 (current genuine host
pahole). No target C, vendor feature, compiler or kernel input changed. Batch03 will use
and freeze the genuine freshly generated config, not fake pahole's version or override
its probe. Required Batch02 candidate hash remains in the immutable manifest; this
observed integration difference is explicitly preserved here.

Batch02 candidate config:8f9d1d2901dfbc77062764b4f9e21bc1000097392a36f8ba1eebd9c47d35f50e.
Fresh Batch03 config:414cbd58794b6aae24ed2ac0beee4090fcc49967003d940822e72a376900a5fc.

No resulting target difference is excused. Every code/data/ABI/metadata/layout byte must
still pass the existing complete stock acceptance, allowing only a structurally parsed
20-byte GNU build ID. Independent builds must reproduce this exact configuration.
No binary or modversion/CRC was altered to accommodate the host probe.
