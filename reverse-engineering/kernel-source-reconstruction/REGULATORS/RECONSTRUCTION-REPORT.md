# REGULATORS — complete four-module source reconstruction

**Result: four complete stock-equivalent builds, class A / BUILD_METADATA_ONLY.**
All behavior-bearing file bytes match. Independent clean-clone B1/B2 is deterministic.
Runtime regulator operations are untested and deferred; source certification is not a
claim that every DT device is populated, bound, or necessary for the first mount.

| Module | Functions | Data objects | Imports/exports | KCFI absolute IDs | Relocations | ELF sections incl. null | Only permitted residue |
|---|---:|---:|---:|---:|---:|---:|---|
| mt6315-regulator.ko | 11/11 | 33/33 | 22/0 | 5/5 | 165/165 | 38 | GNU ID @0x3610+20 |
| mt6363-regulator.ko | 18/18 | 34/34 | 35/0 | 11/11 | 505/505 | 39 | GNU ID @0x8890+20 |
| mtk-dvfsrc-regulator.ko | 5/5 | 88/88 | 17/0 | 1/1 | 177/177 | 42 | GNU ID @0x4a90+20;19 bytes differ |
| rt6160-regulator.ko | 14/14 | 19/19 | 26/0 | 3/3 | 108/108 | 38 | GNU ID @0x2b10+20 |
| **Total** | **48/48** | **174/174** | **100/0** | **20/20** | **955/955** | **157** | **0 unexplained** |

The exact four SHA-bound identities and every stock occurrence are in MODULE-PARITY.tsv
and evidence/inventory/audit-baseline-four.tsv. All occur only in vendor_boot's platform
ramdisk, with existing COVERED-GENERIC ownership. No extra regulator is certified here.
No alias collision or ownership error was found. RT6160's inherited audit load_order=133
is stale: actual normal/recovery file positions are124/122 (BOOT-DEPENDENCIES.md).

## Maintained reconstruction

Repository: `../android_kernel_modules_regulators_ulefone_gq5012bf1`.
Accepted commit: `33130d53c94404f65e1661ffa4113bde21cb4b08`.
Compiled C: immutable ALPS5e415e059253ce0d2e61c97108e5f5785d71f06f. No C changes.
Config: NothingOSS957dac185efe46cbf6336b0fff9516d84c8cd78f plus GKI common6b18f0b574ab….
Two explicit scope-only Kbuild patches isolate the four targets and the separate provider
object witness. The latter independently regenerates all four DVFSRC import CRCs from
real source; two plain and two GPL exports are checked against actual object sections.
It does not certify the provider module, which remains D.

Newer NothingOSS changes MT6315 n_voltages192→191, despite retaining selectors0..191 in
its range. The older public descriptor matches stock. Three other main C files are
identical between these pins. No OEM algorithm rewrite, guessed voltage table, ELF repair,
stock-byte injection or Ulefone-specific C patch was required.

## Acceptance axes and reproduction

- Complete stripped ELF comparison, not function-size similarity: headers, section layout,
  contents, function order/instructions/call relocations, all data/BSS layout, symbols,
  strings, CRCs, KCFI prefixes/IDs, modinfo, vermagic and LLVM address signatures match.
- Relocations compare both raw bytes and semantic(offset,type,target,addend) tuples.
- Raw differences are enumerated before normalization in acceptance.json; only the parsed
  GNU/NT_GNU_BUILD_ID20-byte descriptor is normalized. A coincidental equal byte accounts
  for DVFSRC's19 rather than20 differing bytes.
- No srcversion or appended module signature exists in these stock operands/rebuilds.
- Initial fresh clone ran with development tree moved away throughout bootstrap/build/
  acceptance. Final clean commit (generated Python bytecode removed, no C/build logic changes)
  passed a second fresh clone/empty workspace from the separate regulator recovery mirror.
- B1 and B2 independently reconstruct both source trees, kout, config, host tools and
  provider object. Four raw + four stripped modules, every **8 target.o**, provider.o,
  all symvers, CRC witnesses, config and source tree hashes compare identical.
- **9/9 verifier mutation tests pass**: pristine and GNU descriptor accepted; instruction,
  voltage/descriptor data, import CRC, metadata, relocation, symbol and KCFI edits rejected
  on disposable copies. No true stock/build operand is mutated.

## Device-specific evidence

- MT6363 SPMI slave4:39 compiled descriptors,36 declared DT rails (SSHUB variants not declared).
- MT6319-labelled SPMI slave6 uses the MT6315_6 regulator ABI. Stock overrides buck-size3→4
  and buck1-mode mask0xb→1; three rails declared, VBUCK3 lacks its own rail DT node.
- MT6878 DVFSRC is a logical voltage-request interface, not another physical PMIC.
- Two enabled RT6160 I2C nodes (5/6 address0x75) are **unbound in the existing capture**.
  Their always-on declarations do not prove regulator registration or physical population.
-42 target regulator nodes and32 target supply links mapped; all76 regulator-name nodes
  and48 genuine regulator-phandle supply links retained to show out-of-scope providers.
-84 source/DT matches:82 voltage interval witnesses plus two current-only ISINK entries.
-402 target controller/descendant properties identical across independent static/live DT
  operands;114 fdtget checks independently verify voltages and target supply handles.
- The MMC0 consumer remains enabled in static DT but disabled in the preserved live tree.
  Numeric collisions with phandles, by-name properties and SMI device references are not
  promoted into regulator relationships.

See POWER-RAIL-MAPPING.md, DT-SUPPLY-GRAPH.md, ABI-PARITY.md and BOOT-DEPENDENCIES.md.
This is an audit/reconstruction group, not a registered component promotion. Existing
clock/storage/pinctrl packages and unrelated component statuses remain untouched.
All work was offline: no ADB, regulator/PMIC operation, firmware/calibration access, reboot,
flash, experimental module load, slot switch or push.
