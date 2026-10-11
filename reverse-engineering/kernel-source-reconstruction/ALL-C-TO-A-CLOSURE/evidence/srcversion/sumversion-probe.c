/* SPDX-License-Identifier: GPL-2.0-only
 * Read-only diagnostic wrapper around the unmodified pinned kernel sumversion.c.
 * This never writes generated module source, modinfo, ELF bytes or fingerprints.
 * Build with -I<pinned-common>/scripts/mod -I<prepared-kout>/scripts/mod.
 */
#include "sumversion.c"

static int trace_reads;
void *do_nofail(void *p, const char *expr)
{
	if (!p) { fprintf(stderr, "allocation failure: %s\n", expr); exit(2); }
	return p;
}
void modpost_log(enum loglevel level, const char *fmt, ...)
{
	va_list ap;
	va_start(ap, fmt); vfprintf(stderr, fmt, ap); va_end(ap);
	if (level == LOG_FATAL) exit(2);
}
char *read_text_file(const char *name)
{
	FILE *f = fopen(name, "rb");
	long n;
	char *b;
	if (!f) { perror(name); exit(2); }
	if (trace_reads) fprintf(stderr, "READ\t%s\n", name);
	fseek(f, 0, SEEK_END); n = ftell(f); rewind(f);
	b = NOFAIL(malloc(n + 1));
	if (fread(b, 1, n, f) != (size_t)n) exit(2);
	b[n] = 0; fclose(f); return b;
}
char *get_line(char **p)
{
	char *s = *p, *n;
	if (!s || !*s) return NULL;
	n = strchr(s, '\n'); if (n) *n++ = 0;
	*p = n; return s;
}
/* For candidate comparison, call the exact upstream parser in explicit dependency
 * order established by an actual get_src_version trace, not a guessed hash.
 */
void hash_paths(const char **paths, char out[25])
{
	struct md4_ctx md;
	md4_init(&md);
	while (*paths) parse_file(*paths++, &md);
	md4_final_ascii(&md, out, 24); /* sizeof(mod->srcversion)-1 in modpost.c */
}
int main(int argc, char **argv)
{
	char out[25] = {0};
	if (argc == 3 && !strcmp(argv[1], "--module")) {
		trace_reads = 1;
		get_src_version(argv[2], out, 24);
	} else if (argc > 1) {
		hash_paths((const char **)(argv + 1), out);
	} else return 2;
	puts(out); return 0;
}
