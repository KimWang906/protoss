#include <iostream>
#include "protoss.pb.h"
#include <fcntl.h>

using namespace std;

int main()
{
    setvbuf(stdout, 0, 2, 0);
    setvbuf(stdout, 0, 2, 0);
    protoss::ProtossInterface *pi_obj = new protoss::ProtossInterface();
    char *data = new char[0x2800];
    int len;
    memset(data, 0, 0x2800);

    cout << "> ";
    len = read(0, data, 0x2800);

    if (pi_obj->ParseFromArray(data, len) != 1)
    {
        cout << "ERROR" << endl;
        cout << "data: " << data << endl;
        cout << "len: " << len << endl;
    };

    cout << pi_obj->event_id() << endl;
    if (pi_obj->has_event_signup())
    {
        protoss::SignUp signup = pi_obj->event_signup();
        cout << signup.username() << endl;
        cout << signup.password() << endl;
    }
    else if (pi_obj->has_event_signin())
    {
        protoss::SignIn signin = pi_obj->event_signin();
        cout << signin.username() << endl;
        cout << signin.password() << endl;
    }

    return 0;
}
