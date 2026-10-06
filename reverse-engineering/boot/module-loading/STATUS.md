# module-loading — STATUS (2026-10-06)

| component | status | closure basis |
|---|---|---|
| MTK-MODULE-LOADER | **DONE (static)** | implementation identified (no `.ko`; MTK `init.mtkgki.rc` + `insmod_sh` + `init.insmod.sh`/cfg over AOSP toolbox `modprobe`/libmodprobe; first stage AOSP); inputs/outputs, search roots, dependency/softdep/alias/blocklist handling, errors, logging (bootprof START/DONE), property, exit conditions mapped; boot role proven against stock `/proc/modules` (443/443) and recovery kmsg (192) |
| INIT-INSMOD | **DONE (static)** | every stock insertion path inventoried in `init-insmod-map.tsv` (first stage, insmod_sh ×2, init.touch.rc, connsys rc ×3, on-boot ×2, pstore service, META/factory trees, commented legacy); triggers, order, conditions, failure behaviour mapped; no unresolved loader path |
| VENDOR-ALL-MODULES-READY | **DONE (static)** | setters (3 + META/factory), exact values/order, prerequisites (both modprobe passes return), coverage, single consumer (post-fs-data `wait_for_prop`, no timeout), SELinux and stock timing proven |

Not claimed: runtime confirmation of the *normal-boot* first-stage count (187 is simulated;
recovery 192 and total 443 are observed); the parallel touch/vendor race outcome varies per
boot (stock capture: touch modprobe won `hynitron`).

## Workspace

Moved `Reverse Engineer - PARTIAL/{MTK-MODULE-LOADER,INIT-INSMOD,VENDOR-ALL-MODULES-READY}` →
`Reverse Engineer - DONE/` on 2026-10-06 (index totals 72/58/3 → 75/55/3). Existing evidence and
notes kept; closure notes copied with provenance; README/EVIDENCE-INDEX/PROVENANCE regenerated;
`notes/CLASSIFICATION-CHANGE.md` added. manifest-audit: 3846/3846 rows resolve, status trees
75/55/3, the three packs have no drift (pre-existing drift in 5 unrelated packs untouched).
