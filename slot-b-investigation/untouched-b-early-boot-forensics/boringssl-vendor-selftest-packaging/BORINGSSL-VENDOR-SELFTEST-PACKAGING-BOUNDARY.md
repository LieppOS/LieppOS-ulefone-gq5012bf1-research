# Slot-B BoringSSL vendor self-test packaging boundary

## Background

Current B defines six BoringSSL services with:

`reboot_on_failure reboot,boringssl-self-check-failed`

The system self-test binaries differ from working A, which is expected to be
possible across different Android builds and is not by itself evidence of a
failure.

The more important static observation is that the prior audit did not resolve
the vendor self-test executables:

- `/vendor/bin/boringssl_self_test32`
- `/vendor/bin/boringssl_self_test64`

while current B contains vendor init service definitions referencing those
paths.

## Current selected configuration

Derived B zygote mode:

`UNRESOLVED`

Selected vendor self-test trigger file:

`NOT_FOUND`

Selected services whose executable cannot be found in the current-B mounted
vendor filesystem:

`0`

## Why this matters

The vendor BoringSSL rc files use `exec_start` during early-init and their
service definitions use:

`reboot_on_failure reboot,boringssl-self-check-failed`

If the active B zygote-specific trigger selects a vendor service whose
executable is genuinely absent, and Android init's child exec failure reaches
the service failure/reap path covered by `reboot_on_failure`, this becomes a
concrete deterministic Slot-B reboot candidate.

This report does not call the cause proven until:

1. the current-B zygote/ABI selection is established;
2. the corresponding vendor trigger is present and selected;
3. the selected executable is confirmed absent;
4. exact Android init source semantics prove the missing-executable failure
   reaches `reboot_on_failure`.

## APEX state

Shared active/staged APEX update state is already closed:

- active data APEX count: 0
- data session count: 0
- metadata session count: 0
- metadata images/active child count: 0

## Safety

This investigation is read-only on the device.

No B binary is executed.
No slot is changed.
No partition or persistent Android state is modified.
