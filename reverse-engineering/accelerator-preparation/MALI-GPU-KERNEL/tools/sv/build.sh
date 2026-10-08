#!/bin/bash
# Builds the modpost srcversion reference harness and libmd4sv.so from the exact GKI
# common scripts/mod/sumversion.c (not copied into this repo).
set -e; cd "$(dirname "$0")"; C=${COMMON:-/home/armol/kernel-work/gki-12901745-workspace/common}
cp $C/scripts/mod/sumversion.c .
gcc -O1 -o sumversion harness.c sumversion.c
python3 - <<'PY'
s=open('sumversion.c').read(); a=s.index('struct md4_ctx {'); b=s.index('static int parse_string')
open('md4lib.c','w').write('#include <stdint.h>\n#include <string.h>\n#include <stdio.h>\n#include <arpa/inet.h>\n#define MD4_DIGEST_SIZE 16\n#define MD4_HMAC_BLOCK_SIZE 64\n#define MD4_BLOCK_WORDS 16\n#define MD4_HASH_WORDS 4\n'+s[a:b]+'\nvoid sv(const unsigned char *buf, unsigned long n, char *out){ struct md4_ctx md; md4_init(&md); md4_update(&md, buf, n); md4_final_ascii(&md, out, 24); }\n')
PY
gcc -O2 -shared -fPIC -o libmd4sv.so md4lib.c
