#include "modpost.h"
char *read_text_file(const char *filename){ struct stat st; int fd=open(filename,O_RDONLY); if(fd<0){perror(filename);exit(1);} fstat(fd,&st); char*b=malloc(st.st_size+1); size_t n=st.st_size, o=0; while(n){ssize_t r=read(fd,b+o,n); if(r<=0){perror(filename);exit(1);} n-=r;o+=r;} b[st.st_size]=0; close(fd); return b;}
char *get_line(char **sp){ char*o=*sp,*n; if(!o||!*o) return NULL; n=strchr(o,'\n'); if(n)*n++=0; *sp=n; return o;}
int main(int c,char**v){ char s[25]; get_src_version(v[1],s,sizeof(s)-1); printf("%s\n",s); return 0;}
