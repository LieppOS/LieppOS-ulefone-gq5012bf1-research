#!/bin/bash
# fd.sh <module> <function> [built.ko] : diff stock vs rebuilt disassembly (relocs inline, addresses normalised)
export PATH=/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
cd /home/armol/kernel-work/gki-12901745-workspace/lieppos/usb
M=$1; F=$2; B=${3:-$(find trees/5e41 -name "$M.stripped.ko" | head -1)}
D(){ llvm-objdump -dr --no-show-raw-insn --disassemble-symbols=$F $1 | tail -n +7 | sed -E 's/^ +[0-9a-f]+:\s*//; s/^\s*[0-9a-f]{16}:\s*/  R: /; s/ <[^>]*>//; s/0x[0-9a-f]+ *$/ADDR/' ; }
D stock/$M.ko > /tmp/fd.a; D $B > /tmp/fd.b
if [ "$4" = "a" ]; then cat /tmp/fd.a; else diff /tmp/fd.a /tmp/fd.b; fi
