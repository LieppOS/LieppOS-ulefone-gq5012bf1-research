# U7 - selected ConnFem RF front-end pair

**Current claim:** "10 candidates, 8 HWID states, values unread" - selected FEM unknown.

**Previous confidence:** UNKNOWN.

**New evidence**
1. **The full selection table was decoded from the live device tree.** `connfem/epa-elna-mtk/parts` is a 96-byte phandle array = 12 pairs; resolving the phandles against the `connfem` child nodes gives:
   | HWID index | 2.4 GHz part | 5/6 GHz part |
   |---:|---|---|
   | 0, 1, 2 | **nofem** | **nofem** |
   | 3 | mxd7751s | mxd7751s |
   | 4, 5 | sky85320 | sky85720 |
   | 6 | qm42195 | qm45197 |
   | 7 | wlan7207h | wlan7207c |
   | 8-11 | (nofem+sky85732, nofem+qm45197, rtc7620+nofem) | unreachable, see below |
   `hwid/gpio = <ctrl 131 0>, <ctrl 132 0>, <ctrl 92 0>` - **three** GPIOs, so only indices **0-7** are addressable; entries 8-11 are reference-design leftovers.
2. **The runtime result is recorded in the kernel log**:
   `[connfem][API]connfem_is_available: FEM is not available`, `connfem_epaelna_get_fem_info, Not support`, `connfem_epaelna_get_pin_info, Not support`, `connfem_epaelna_get_flags, Not support`, and from the Bluetooth stack `[btmtk_info] CONNFEM BTvid/pid == 0, ignore`.
3. **Driver semantics confirm what that means.** In the matching MT6878 ConnFem source, `result->available = true` is set **only if** `result->fem_info.id` is non-zero (`connfem_dt_parser.c:340-342`), and the `nofem` node carries empty `vid`/`pid` properties, so a nofem pair yields `id == 0`. The alternative config-file path cannot override this: `vendor/firmware/connfem.cfg` is **0 bytes**.
4. Consistently, no external Wi-Fi/BT PA or LNA appears on any enumerated I2C/SPI bus.

**Contradicting evidence:** none.

**Internet sources:** none required - this is settled locally. (VI1 confirms the product is Wi-Fi 6E, which the MT6637 ADIE provides without an external FEM.)

**Local evidence:** VL4, VL5, VL6, VL7; `../evidence/live-devicetree-extracts.md`.

**Read-only live evidence:** the dmesg lines above from the frozen capture.

**Final conclusion**
The board straps its ConnFem HWID to one of indices **0, 1 or 2**, all of which map to **`nofem` + `nofem`**. **No external ePA/eLNA front-end module is fitted for Wi-Fi or Bluetooth**; the design relies on the MT6637 companion die's integrated PA/LNA for 2.4 GHz, 5 GHz and 6 GHz. The seven alternative FEM pairings in the device tree are ODM options for other boards, not fitted hardware here.

**Final confidence:** **PROVEN** that no Wi-Fi/BT FEM is active or available; **STRONGLY_SUPPORTED** that none is physically populated (an installed-but-unstrapped FEM would be an unpowered, unbypassed part in the RF path - not a workable design). The exact numeric HWID (0, 1 or 2) is unknown and immaterial.

**Remaining uncertainty:** the literal GPIO 131/132/92 levels; readable with `cat /sys/kernel/debug/gpio` on a rooted stock boot. This would not change the conclusion.

**Impact on final inventory:** YES - "selected FEM UNKNOWN" is replaced by "no external Wi-Fi/BT FEM". The capability matrix Wi-Fi/BT row and hidden-capability item 9 ("alternate RF FEMs") are corrected: there is no alternate FEM to unlock, and 6 GHz performance is bounded by the ADIE's own PA.

**Answers:** (1) table decoded, runtime says no FEM; (2) only the numeric HWID; (3) yes - fully; (4) yes, trivially; (5) no; (6) no; (7) `nofem` + `nofem` (MT6637 internal PA/LNA only); (8) PROVEN; (9) yes; (10) yes; (11) yes.
