#include <iostream>
#include <cstdlib>

int main(int argc, char const *argv[])
{
    const char *data = new char[255];
    data = "99999999999999999999999999999999999999999999999999";
    printf("data: %X", atoi(data));
    return 0;
}
