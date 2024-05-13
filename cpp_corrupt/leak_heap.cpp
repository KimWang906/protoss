#include <iostream>
#include <vector>
#include <string>

using namespace std;

int main()
{
    /*
        dummy -> dummy -> victim -> data...
    */
    void ****victim = new void ***;
    *victim = new void **;              // dereference once
    **victim = new void *;              // dereference twice
    ***victim = (void *)string("HELLO WORLD!").data(); // dereference thrice

    cout << "Victim: " << **victim << endl;

    return 0;
}