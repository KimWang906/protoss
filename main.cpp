#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include "protoss_3.pb.h"
#include <fcntl.h>
using namespace std;

#define PORT 5050
#define USER_HANDLER 16 >> 24
#define EXCHANGE_HANDLER 32 >> 24

int main()
{
    protoss::ProtossInterface *pi_obj = new protoss::ProtossInterface();
    protoss::SignUp *user_signup = new protoss::SignUp();
    user_signup->set_username("HyunBin");
    user_signup->set_password("12345678");

    pi_obj->set_event_id(USER_HANDLER);
    pi_obj->set_allocated_event_signup(user_signup);

    cout << "Set Event ID: " << pi_obj->event_id() << endl;
    cout << "Set Event SignUp\nUsername: " << pi_obj->event_signup().username() << endl;
    cout << "Passowrd: " << pi_obj->event_signup().password() << endl;


    pi_obj->has_event_addressbook();
    pi_obj->has_event_buy();

    return 0;
}