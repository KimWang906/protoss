from module.protoss_handler import *
from pwn import *

macros = []

def auto_set(p: tube):
    user_signup(p, ProtossInterface(), USER_HANDLER,
                set_signup('HyunBin', '1234'))
    user_signin(p, ProtossInterface(), USER_HANDLER,
                set_signin('HyunBin', '1234'))

# SIGSEGV Trigger --------------------------------------------------

def trigger_login_sigsegv(p: tube):
    user_signin(p, ProtossInterface(), USER_HANDLER, 
        set_signin('SIGSEGV_USERNAME', 'SIGSEGV_PASSWORD'))

def trigger_history_sigsegv(p: tube):
    auto_set(p)
    view_history(p, ProtossInterface(), EXCHANGE_HANDLER,
                 set_history(0, 1))
def trigger_invalid_access(p: tube):
    auto_set(p)
    user_signout(p, ProtossInterface(), USER_HANDLER)
    show_user_info(p, ProtossInterface(), USER_HANDLER)

def trigger_double_signout(p: tube):
    auto_set(p)
    user_signout(p, ProtossInterface(), USER_HANDLER)
    user_signout(p, ProtossInterface(), USER_HANDLER)

def trigger_cannot_deref(p: tube):
    auto_set(p)
    payload = ''
    for i in range(1, 11):
        add_addrbook(p, ProtossInterface(), EXCHANGE_HANDLER, set_addressbook(0, str(1) * 254, str(i)))
        sleep(1)
    pause()
    # for ascii_code in range(65, 91 - 9):
    #     payload += chr(ascii_code) * 8
    # payload += 'A' * 7 # + NULL-byte
    
    # for num in range(5):
    #     payload += str(num) * 8
    # payload += str(5) * 7
    before_payload = chr(65) * 255
    modify_addrbook(p, ProtossInterface(), EXCHANGE_HANDLER, set_modify_addressbook(-1, '1' * (255 - 8), before_payload, '0'))
    pause()
    for i in range(1, 11):
        modify_addrbook(p, ProtossInterface(), EXCHANGE_HANDLER, set_modify_addressbook(-1, before_payload, 'before_payload', '0'))


# -------------------------------------------------------------------

def try_sqli(p):
    user_signup(p, ProtossInterface(), USER_HANDLER,
            set_signup('\x00', 'SQLI_PASSWORD')) # inject null-byte
    user_signin(p, ProtossInterface(), USER_HANDLER,
            set_signin('SQLI', 'SQLI_PASSWORD'))

def dup_signup(p: tube):
    user_signup(p, ProtossInterface(), USER_HANDLER,
            set_signup('HyunBin', '1234'))
    user_signup(p, ProtossInterface(), USER_HANDLER,
            set_signup('HyunBin', '1234'))

def send_deposit(p: tube):
    auto_set(p)
    deposit(p, ProtossInterface(), EXCHANGE_HANDLER, 
            set_deposit('D' * 0x2700, 1, -1))

def send_max_bytes(p: tube):
    p.sendafter(b'> ', b'A' * 0x2800)


def fake_trade(p):
    auto_set(p)
    buy(p, ProtossInterface(), EXCHANGE_HANDLER, set_buy(0, 1))
    sell(p, ProtossInterface(), EXCHANGE_HANDLER, set_sell(0, 1))
    view_history(p, ProtossInterface(), EXCHANGE_HANDLER, set_history(0, 0))

def insert_addrbook(p):
    auto_set(p)
    for i in range(1, 11):
        add_addrbook(p, ProtossInterface(), EXCHANGE_HANDLER, set_addressbook(0, str(i), str(i)))
        sleep(1)

def max_value_mysql_func(p: tube):
    auto_set(p)
    pause()
    buy(p, ProtossInterface(), EXCHANGE_HANDLER, set_buy(0, 1, 0x7fffffff))

macros.append(auto_set)
macros.append(trigger_login_sigsegv)
macros.append(trigger_history_sigsegv)
macros.append(trigger_invalid_access)
macros.append(trigger_double_signout)
macros.append(trigger_cannot_deref)
macros.append(try_sqli)
macros.append(dup_signup)
macros.append(send_max_bytes)
macros.append(send_deposit)
macros.append(fake_trade)
macros.append(insert_addrbook)
macros.append(max_value_mysql_func)

def custom_payload(p: tube):
    print("Select Custom Payload")
    while(True):
        for (i, func) in enumerate(macros):
            print("{}. {}".format(i + 1, func.__name__))
        print("{}. Execute Protoss Prompt".format(len(macros) + 1))
        select = int(input("> "), 10)
        if select - 1 < len(macros):
            macros[select - 1](p)
        else:
            print('Done.')
            print('Executing Protoss Prompt')
            prompt(p)
