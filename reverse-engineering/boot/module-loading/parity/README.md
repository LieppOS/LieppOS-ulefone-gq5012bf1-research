# Parity

No target in this cluster contains a dedicated kernel module: there is no module-loader
`.ko`. Kernel-module (`.ko`) parity is therefore not applicable, and none is claimed.

Userspace parity substitute:

- `init.insmod.sh`, `init.insmod.mt6878.cfg`, `init.mtkgki.rc`, `init.touch.rc` are stock
  text files used verbatim (sha256 in `../README.md`); the LieppOS device tree cfg
  (`device/ulefone/armol/configs/vendor/init.insmod.mt6878.cfg`) is byte-identical to stock.
- Behavioural parity of the loader is established by `../scripts/modprobe_sim.py`
  (AOSP libmodprobe rules): normal boot 443 insertions = the 443 stock modules in the
  captured `/proc/modules` (set-equal, 0 missing, 0 extra besides user-added `kernelsu`);
  recovery 192 = `init: Loaded 192 kernel modules` in two recovery `last_kmsg`.
