# post-fs-data boundary correction

The existing `50-post-fs-data` marker is an action in a vendor init rc file.

Its remaining value of zero does not, by itself, prove that the
`post-fs-data` event was never queued or dispatched.

Earlier-parsed `on post-fs-data` actions may execute first and may block
synchronously before the LieppOS checkpoint action gets CPU time.

Known candidates include:

- the MT6878 `on post-fs-data` action, including
  `wait_for_prop vendor.all.modules.ready 1`;
- the system `on post-fs-data` action, including synchronous `vdc`
  checkpoint operations.

V7 already proves the real MT6878 late-fs action completes, including
`mount_all --late`.

The next diagnostic must instrument an earlier post-fs-data action directly,
rather than treating the later vendor checkpoint as proof that the event was
not entered.

PHONE_MODIFIED=0
