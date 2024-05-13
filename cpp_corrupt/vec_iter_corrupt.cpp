#include <iostream>
#include <cstdio>
#include <vector>
#include <unistd.h>

static char buf[16];
static std::vector<long>::iterator it;
static std::vector<long> v;
static long x;

int main()
{
    v = std::vector<long>(10);
    v[0] = 10;
    v[1] = 20;
    it = v.begin();
    *(long *)&buf[16 + 0] = (long)&x; // BUFFER OVERFLOW: it == x
    *it = 0x41414141;                 // x = 0x41414141
    printf("%lx\n", x);
    _exit(0);
}