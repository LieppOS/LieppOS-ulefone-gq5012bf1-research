/* Shared tool: brute-force an unknown named type tag in a KCFI-instrumented
 * stock module.  The four hard-coded target type ids below are the
 * GQ5012BF1 yft_devinfo *_device_add families; edit them for other modules.
 * See kernel/phase4-yft-devinfo-kcfi-typeid.md.  Build: cc -O3 -o x ko-kcfi-brute-affix.c
 */
// brute4 PREFIX SUFFIX MAXMID NA FIRSTIDX : tag = PREFIX + mid(len 0..MAXMID over AL[0..NA)) + SUFFIX
// camera hit -> verified against i2c/spi/sensor families
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ko-kcfi-xxh64.h"
static const char *AL="abcdefghijklmnopqrstuvwxyz_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
static int verify(const char*s,int L){char b[256];int n;
 n=sprintf(b,"_ZTSFiP10i2c_driver%d%.*sE",L,L,s); if((uint32_t)xxh64(b,n)!=0x076247bdu) return 0;
 n=sprintf(b,"_ZTSFiP10spi_driver%d%.*sE",L,L,s); if((uint32_t)xxh64(b,n)!=0x73f54704u) return 0;
 n=sprintf(b,"_ZTSFiP11sensor_info%d%.*sE",L,L,s); if((uint32_t)xxh64(b,n)!=0x16318e3fu) return 0; return 1;}
int main(int argc,char**argv){
 const char*P=argv[1],*S=argv[2]; int maxm=atoi(argv[3]),na=atoi(argv[4]),f=atoi(argv[5]);
 int pl=strlen(P),sl=strlen(S);
 for(int m=1;m<=maxm;m++){
  int L=pl+m+sl; char b[256]; int pre=sprintf(b,"_ZTSFiPc%d",L);
  char*t=b+pre; memcpy(t,P,pl); char*mid=t+pl; memcpy(mid+m,S,sl); t[L]='E'; int n=pre+L+1;
  int idx[32]; for(int i=0;i<m;i++) idx[i]=0; idx[0]=f; if(f>=na) break;
  for(;;){ for(int i=0;i<m;i++) mid[i]=AL[idx[i]];
    if((uint32_t)xxh64(b,n)==0x803f8280u) printf("%s %.*s\n",verify(t,L)?"VERIFIED":"camera-only",L,t),fflush(stdout);
    int k=m-1; while(k>=1 && ++idx[k]==na){idx[k]=0;k--;} if(k<1)break; }
 }
 return 0;}
