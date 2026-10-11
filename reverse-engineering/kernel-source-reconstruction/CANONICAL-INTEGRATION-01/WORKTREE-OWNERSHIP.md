# Worktree ownership and concurrency

Preflight (read-only) found 11 linked worktrees: canonical master f61ebf03; codex/all-c-to-a-closure
652e4195; codex/audio-batch-01 f00bd8af; codex/audio-dependencies-batch-02 fb558640;
codex/scp-connectivity-batch-01 40bfedda; codex/completed-batches-integration 55dab18a;
integration-replay (detached f61ebf03); codex/stock-inventory-integrity 143a6db2;
codex/next-dg-source-batch 437ebd57; next-dg-replay (detached 55dab18a); codex/usb-typec-closure 7e196c32.

Process check: three `pi` processes had the canonical checkout as cwd. PID 3944048 is this task.
PID 18921 (tmux, 2+ days) and PID 3944691 had no tool child processes, no open repository/stock
files, and no working-tree writes in the preceding hour; canonical HEAD unchanged since
2026-10-11 03:33. No process had any `android_kernel_modules_*` repository as cwd. The checkout
was judged idle; the check was repeated immediately before stock restoration.

No other worktree, branch or source repository was reset, rebased, cleaned or checked out.
Created by this task: worktree/branch `ulefone-gq5012bf1-research-canonical-integration`
(`integration/canonical-01`) and two detached replay worktrees (removed after evidence capture).
Source repositories: only fast-forwards of four clean maintained repositories (SOURCE-PROVENANCE.md)
and a fetched read-only ref `refs/remotes/allc-bundle/codex-all-c-closure` from each verified bundle.
`android_kernel_modules_smi_platform` has an untracked `scripts/__pycache__/` (not source drift;
left untouched).
