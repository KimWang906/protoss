#include <protoss.pb.h>

using namespace std;
using namespace protoss;

int main()
{
    char values[56];

    cout << "ProtossInterface Object Size: " << sizeof(protoss::ProtossInterface) << endl;
    cout << "SignUp Object Size: " << sizeof(protoss::SignUp) << endl;
    cout << "SignIn Object Size: " << sizeof(protoss::SignIn) << endl;
    cout << "Buy Object Size: " << sizeof(protoss::Buy) << endl;
    cout << "Sell Object Size: " << sizeof(protoss::Sell) << endl;
    cout << "History Object Size: " << sizeof(protoss::History) << endl;
    cout << "AddressBook Object Size: " << sizeof(protoss::AddressBook) << endl;
    cout << "ModifyAddressBook Object Size: " << sizeof(protoss::ModifyAddressBook) << endl;
    cout << "Deposit Object Size: " << sizeof(protoss::Deposit) << endl;


    return 0;
}