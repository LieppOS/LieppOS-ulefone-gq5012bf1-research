#include <stdint.h>
#include <string.h>
#define P1 11400714785074694791ULL
#define P2 14029467366897019727ULL
#define P3 1609587929392839161ULL
#define P4 9650029242287828579ULL
#define P5 2870177450012600261ULL
static inline uint64_t rotl(uint64_t x,int r){return (x<<r)|(x>>(64-r));}
static inline uint64_t rnd(uint64_t a,uint64_t i){a+=i*P2;a=rotl(a,31);return a*P1;}
static inline uint64_t mrg(uint64_t a,uint64_t v){v=rnd(0,v);a^=v;return a*P1+P4;}
static inline uint64_t rd64(const uint8_t*p){uint64_t v;memcpy(&v,p,8);return v;}
static inline uint32_t rd32(const uint8_t*p){uint32_t v;memcpy(&v,p,4);return v;}
static uint64_t xxh64(const void*in,size_t n){const uint8_t*p=in,*e=p+n;uint64_t h;
 if(n>=32){uint64_t v1=P1+P2,v2=P2,v3=0,v4=-P1;const uint8_t*l=e-32;do{v1=rnd(v1,rd64(p));p+=8;v2=rnd(v2,rd64(p));p+=8;v3=rnd(v3,rd64(p));p+=8;v4=rnd(v4,rd64(p));p+=8;}while(p<=l);
  h=rotl(v1,1)+rotl(v2,7)+rotl(v3,12)+rotl(v4,18);h=mrg(h,v1);h=mrg(h,v2);h=mrg(h,v3);h=mrg(h,v4);}else h=P5;
 h+=n; while(p+8<=e){h^=rnd(0,rd64(p));h=rotl(h,27)*P1+P4;p+=8;}
 if(p+4<=e){h^=(uint64_t)rd32(p)*P1;h=rotl(h,23)*P2+P3;p+=4;}
 while(p<e){h^=(*p)*P5;h=rotl(h,11)*P1;p++;}
 h^=h>>33;h*=P2;h^=h>>29;h*=P3;h^=h>>32;return h;}
