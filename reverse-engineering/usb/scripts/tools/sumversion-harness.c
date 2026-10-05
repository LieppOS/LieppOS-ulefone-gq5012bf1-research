#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include "modpost.h"
void *do_nofail(void *ptr, const char *expr){ if(!ptr){fprintf(stderr,"nofail %s\n",expr);exit(1);} return ptr; }
void modpost_log(enum loglevel l, const char *fmt, ...){ va_list a; va_start(a,fmt); vfprintf(stderr,fmt,a); va_end(a); }
char *read_text_file(const char *filename)
{
	struct stat st;
	size_t nbytes;
	int fd;
	char *buf;

	fd = open(filename, O_RDONLY);
	if (fd < 0) {
		perror(filename);
		exit(1);
	}

	if (fstat(fd, &st) < 0) {
		perror(filename);
		exit(1);
	}

	buf = NOFAIL(malloc(st.st_size + 1));

	nbytes = st.st_size;

	while (nbytes) {
		ssize_t bytes_read;

		bytes_read = read(fd, buf, nbytes);
		if (bytes_read < 0) {
			perror(filename);
			exit(1);
		}

		nbytes -= bytes_read;
	}
	buf[st.st_size] = '\0';

	close(fd);

	return buf;
}
char *get_line(char **stringp)
{
	char *orig = *stringp, *next;

	/* do not return the unwanted extra line at EOF */
	if (!orig || *orig == '\0')
		return NULL;

	/* don't use strsep here, it is not available everywhere */
	next = strchr(orig, '\n');
	if (next)
		*next++ = '\0';

	*stringp = next;

	return orig;
}
int main(int argc,char**argv){ char sum[25]; get_src_version(argv[1], sum, 24); printf("%s\n", sum); return 0; }
