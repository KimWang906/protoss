#include <iostream>
#include "proto/protoss.pb.h"

using namespace std;

int main()
{
    protoss::ProtossInterface *pi_obj = new protoss::ProtossInterface();

    protoss::EventHandler handler = pi_obj->event_handlers();

    handler.set_event_id(16);
    cout << pi_obj->event_handlers().event_id() << endl;

    return 0;
}