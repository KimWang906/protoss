#include <cstdio>
#include <cstdlib>
#include <string>

static char victim[] = "secret";

int main()
{
    std::string str;
    unsigned long *p = (unsigned long *)&str;
    unsigned long x;

    str = "12345678";
    p[0] = (unsigned long)&victim;
    printf("%s\n", str.c_str());

    exit(1);
}