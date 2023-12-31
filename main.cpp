#include <iostream>
#include "protoss.pb.h"

using namespace std;

int main()
{
    protoss::ProtossInterface *pi_obj = new protoss::ProtossInterface();

    pi_obj->set_event_id(16);

    cout << pi_obj->event_id() << endl;

    return 0;
}
