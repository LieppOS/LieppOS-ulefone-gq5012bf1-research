/* Shared tool: brute-force an unknown named type tag in a KCFI-instrumented
 * stock module.  The four hard-coded target type ids below are the
 * GQ5012BF1 yft_devinfo *_device_add families; edit them for other modules.
 * See kernel/phase4-yft-devinfo-kcfi-typeid.md.  Build: cc -O3 -o x ko-kcfi-brute-dict.c
 */
// dict2 WORDS DEPTH CASE PART NPART [FIRSTWORD]
//   CASE 0=lower 1=UPPER 2=Capitalised   seps: "_" and ""
//   tag = [FIRSTWORD sep] w1 [sep w2 [sep w3]]   (DEPTH = number of free words)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "ko-kcfi-xxh64.h"
static char W[4000][24]; static int WL[4000]; static int NW; static long cnt;
static int verify(const char*s,int L){char b[256];int n;
 n=sprintf(b,"_ZTSFiP10i2c_driver%d%.*sE",L,L,s); if((uint32_t)xxh64(b,n)!=0x076247bdu) return 0;
 n=sprintf(b,"_ZTSFiP10spi_driver%d%.*sE",L,L,s); if((uint32_t)xxh64(b,n)!=0x73f54704u) return 0;
 n=sprintf(b,"_ZTSFiP11sensor_info%d%.*sE",L,L,s); if((uint32_t)xxh64(b,n)!=0x16318e3fu) return 0; return 1;}
static void test(const char*s,int L){char b[256]; int n=sprintf(b,"_ZTSFiPc%d%.*sE",L,L,s); cnt++;
 if((uint32_t)xxh64(b,n)==0x803f8280u) printf("%s %.*s\n",verify(s,L)?"VERIFIED":"camera-only",L,s),fflush(stdout);}
int main(int argc,char**argv){FILE*f=fopen(argv[1],"r");
 int depth=atoi(argv[2]),cs=atoi(argv[3]),part=atoi(argv[4]),np=atoi(argv[5]);
 const char*fw=argc>6?argv[6]:NULL; int fwl=fw?strlen(fw):0;
 char line[64];
 while(fgets(line,64,f)&&NW<4000){int l=strcspn(line,"\n"); if(!l||l>20)continue; line[l]=0;
  for(int i=0;i<l;i++) line[i]=cs==1?toupper(line[i]):tolower(line[i]);
  if(cs==2) line[0]=toupper(line[0]);
  strcpy(W[NW],line); WL[NW]=l; NW++;}
 char s[160];
 for(int sp=0;sp<2;sp++){ const char*S=sp?"":"_"; int sl=strlen(S); int base=0;
  if(fw){memcpy(s,fw,fwl); base=fwl;}
  for(int a=0;a<NW;a++){ if(a%np!=part) continue;
   int p=base; if(base){memcpy(s+p,S,sl);p+=sl;} memcpy(s+p,W[a],WL[a]); p+=WL[a]; test(s,p);
   if(depth<2) continue;
   for(int b=0;b<NW;b++){ int q=p; memcpy(s+q,S,sl); q+=sl; memcpy(s+q,W[b],WL[b]); q+=WL[b]; test(s,q);
    if(depth<3) continue;
    for(int c=0;c<NW;c++){ int r=q; memcpy(s+r,S,sl); r+=sl; memcpy(s+r,W[c],WL[c]); r+=WL[c]; test(s,r);} } } }
 fprintf(stderr,"part %d tested %ld\n",part,cnt); return 0;}
