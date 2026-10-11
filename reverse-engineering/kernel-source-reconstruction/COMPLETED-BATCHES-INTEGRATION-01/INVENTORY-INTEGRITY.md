# Authentic private stock inventory

Unchanged STOCK-INVENTORY-INTEGRITY/scripts/verify-inventory.py PASS (`evidence/inventory.json`), with expectations read from committed f61ebf03, not from the checked files:

-458 exact SHA/size identities;471 occurrences;457 filenames.
-60 system_dlkm;215 vendor_dlkm;196 vendor_boot_platform.
-60/60 authentic appended721-byte signatures;411/411 vendor occurrences unsigned.
-Exact path set, no missing/unexpected/substituted identity.
-System bluetooth d2659fb3… remains the prior A identity; vendor bluetooth2df021ea… is the selected C identity. No filename-only deduplication.

Every occurrence was copied/reflinked into this staging checkout from the existing authenticated private restoration (fallback candidates are accepted only on exact committed hash and size), then made read-only. `evidence/private-stock.json` records every source/destination/hash/size. This run did not rewrite signatures or change expected hashes. It reused the previously authenticated image extraction; integrity research preserves image SHA300f24c5550be110d0161583fa56d3c36ae61b8b2da4b44c128350c6e22b9f2a and the60-row repair manifest.

Read-only comparison confirms **all60 canonical shared system_dlkm copies are still damaged**,721 bytes short; the other411 occurrences are authentic. See `evidence/canonical-stock-damage.json`. We did not repair the live shared path or alter an owner's inputs. The owner-only restoration/quarantine/dry-run/image authentication procedure is preserved unchanged in STOCK-INVENTORY-INTEGRITY/MERGE-INSTRUCTIONS.md. Owner must quiesce competing users before applying it and then rerun the live validator.

Root cause is Codex's historical in-place llvm-objcopy section census, not stale inventory or another agent. Original research explains both incidents and the unsafe commands. Original census values are preserved, but its procedure is not repeated. New checks read bytes/readelf only; mutation tests alter temporary copies exclusively. Never invoke objcopy/strip on canonical or immutable stock operands without an explicit separate output operand.

Stage/replay private validation PASS must not be described as restoration of shared canonical files. No original image, stock inventory definition, phone, firmware or partition was changed.
