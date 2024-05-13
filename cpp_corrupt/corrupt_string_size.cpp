#include <cstdio>
#include <cstdlib>
#include <string>

#define N (0x40)

struct struct_s
{
    std::string str;
    unsigned long victim;
};

static struct struct_s s;

int main()
{
    unsigned long *p = (unsigned long *)&s.str;
    unsigned long x;

    s.str = std::string("12345678");
    s.victim = 0x1122334455667788;

    p[1] = N;
    for (int i = 16; i < (16 + 8); i++)
    {
        x <<= 8;
        x |= (unsigned char)s.str[i];
    }
    printf("%lx\n", x);
    exit(1);
}