#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#define NOFAIL(p) (p)
#define warn(...) fprintf(stderr, __VA_ARGS__)
char *read_text_file(const char *filename);
char *get_line(char **stringp);
void get_src_version(const char *modname, char sum[], unsigned sumlen);
