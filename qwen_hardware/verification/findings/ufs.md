# U2 - UFS vendor / device / gear / health

**Current claim:** "512 GB claim; package not captured".

**Previous confidence:** UNKNOWN.

**New evidence**
* `lpddr_used_name=MT512GBCAV8U31` - the same Micron uMCP part carries the **512 GB UFS** die.
* `[ro.boot.boot_devices]: [bootdevice, soc/112b0000.ufshci, 112b0000.ufshci]` and kernel arg `ufshcd_core.poll_queues=0` -> the boot device is a **UFSHCI** controller, not eMMC.
* **UFS health is directly present in the live bootargs**: `PreEOLInfo = 0x1`, `LifeTimeEstA = 0x1`, `LifeTimeEstB = 0x1`.
  Per JEDEC UFS 2.x/3.x: `bPreEOLInfo = 0x01` = **Normal** (reserved-block consumption < 80 %); `bDeviceLifeTimeEstA/B = 0x01` = **0-10 % of the rated device lifetime used**.
* `flash_type=12` is MediaTek's internal storage-type enumerant for this build.
* Preloader contains UFS RPMB and boot-LU write-protect routines (`rpmb_ufs_set_wp`, `UFS_LU_BOOT1/BOOT2`), confirming a UFS device with RPMB and boot LUs.

**Contradicting evidence:** none.

**Internet sources:** VI23, VI24 (Micron uMCP = UFS + LPDDR in one package), VI6 (512 GB SKU).

**Local evidence:** VL1; `../evidence/live-devicetree-extracts.md`.

**Read-only live evidence:** bootargs health fields above - these are genuine device-descriptor values read by the bootloader.

**Final conclusion**
Storage is the **UFS die inside the Micron `MT512GBCAV8U31` uMCP, 512 GB**, attached to the MT6878 UFSHCI at `0x112b0000`, with RPMB and two boot LUs. **Health at capture time: PreEOL Normal, life-time estimates A and B both in the 0-10 % band, i.e. an essentially unworn device** (consistent with the 26 battery cycles observed). The **negotiated UFS version and gear/lane configuration (HS-G3 vs G4, 1 vs 2 lanes) are not recorded anywhere in the captured data**.

**Final confidence:** vendor/package/density/health = **PROVEN**; UFS version and negotiated gear = **UNKNOWN**.

**Remaining uncertainty:** read `/sys/bus/platform/devices/112b0000.ufshci/.../{model,rev,manufacturer}` plus `ufs_version`/`current_gear` or `/sys/kernel/debug/ufshcd*` on a rooted stock boot; alternatively the Micron datasheet.

**Impact on final inventory:** YES - storage row rewritten with capacity, package, controller and health.

**Answers:** (1) 512 GB UFS inside a Micron uMCP, healthy; (2) UFS version + gear/lanes; (3) yes for identity/health; (4) yes for gear; (5) partially; (6) no; (7) `MT512GBCAV8U31` (UFS die); (8) PROVEN identity+health / UNKNOWN gear; (9) yes; (10) yes; (11) no.

## Second-pass update (2026-09-08)

The exact Micron identifier remains absent from public catalogues (Q19). Preloader strings contain both UFS
3.0/3.1 option paths and generic PHY/equalisation diagnostics, but no runtime-selected generation, HS-GEAR
or lane count. Those strings prove only that the shared MT6878 bootloader supports several configurations.
**UFS revision, negotiated gear and lane count remain UNKNOWN**; package, 512 GB density and health remain
PROVEN.
