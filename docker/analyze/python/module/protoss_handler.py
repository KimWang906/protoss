import json
import base64
from datetime import *
from module.memory import *
from module.protoss_log import *
from pwn import *
from pwnlib.timeout import *
from build.protoss_pb2 import ProtossInterface, SignUp, SignIn, Buy, Sell

USER_HANDLER = 16 << 24
EXCHANGE_HANDLER = 32 << 24


def prompt(r: tube):
    while (1):
        print("Hiring CTF ProtossInterface")
        print("1. Call User Handler")
        print("2. Call Exchange Handler")
        print("3. Call Custom Macros")
        print("4. Exit")
        user_input = input("Input: ")
        if user_input == "1":
            print("Select User Option")
            print("1. Show My Information")
            print("2. Sign-Up Account")
            print("3. Sign-In Account")
            print("4. Sign-Out Account")
            user_input = input("Input: ")
            user_handler(r, user_input, ProtossInterface())
        elif user_input == "2":
            print("Select Exchange Handler")
            print("1. Buy")
            print("2. Sell")
            print("3. History")
            print("4. Insert Address Book")
            print("5. Modify Address Book")
            print("6. Delete Address Book")
            print("7. Deposit")
            user_input = input("Input: ")
            exchange_handler(r, user_input, ProtossInterface())
        elif user_input == "3":
            print("Exit ProtossInterface ...")
            exit(0)
        else:
            print("Wrong Input")


def show_user_info(r: tube, interface: ProtossInterface, mode: int):
    interface.event_id = mode + 3
    req = interface.SerializeToString()
    # module.protoss_log.logging_request('Show_My_Information', req)
    r.send(req)
    data = r.recvrepeat(1)
    print('============================')
    print(data.decode().replace('\n>', ''))
    print('============================')


def user_signup(r: tube, interface: ProtossInterface,
                mode: int, signup: SignUp = None):
    if signup == None:
        signup = SignUp()
        signup.username = input('New Username: ')
        signup.password = input('New Password: ')
    interface.event_id = mode
    interface.event_signup.username = signup.username
    interface.event_signup.password = signup.password
    req = interface.SerializeToString()
    # with open("signup", "wb") as f:
    #     f.write(bytes(req))
    # module.protoss_log.logging_request('Sign-Up_Account', req)
    r.send(req)
    # try catch ...
    sign_up_response(r)


def sign_up_response(r: tube):
    try:
        r.recvuntil(b'\n')
        raw_data = r.recvuntil(b'> ')[:-3]
        json_res = json.loads(raw_data)
        raw_username = base64.b64decode(json_res['username'])
        username = raw_username.decode('UTF-8')
        print('============================')
        print('username: {}'.format(username))
        print('acc_id: {}'.format(json_res['acc_id']))
        print('============================')
    except:
        print("Failed Response Data. Received: {}".format(r.recvrepeat(3)))


def user_signin(r: tube, interface: ProtossInterface,
                mode: int, signin: SignIn = None):
    if signin == None:
        signin = SignIn()
        signin.username = input("Username: ")
        signin.password = input("Password: ")
    interface.event_id = mode + 1
    interface.event_signin.username = signin.username
    interface.event_signin.password = signin.password
    req = interface.SerializeToString()
    # with open("signin", "wb") as f:
    #     f.write(bytes(req))
    r.send(req)
    data = r.recvrepeat(1)
    if data.decode() != '> ':
        for memory_map in sigsegv_parse(data):
            print(memory_map)
    else:
        print(f'{data.decode()}')


def sigsegv_parse(data: bytes) -> list[VirtualMemoryLayout]:
    result = []
    for line in data.replace(b'\x00', b'')[2:].split(b'\n'):
        if line == b'':
            continue
        result.append(VirtualMemoryLayout(line))
    return result


def user_signout(r: tube, interface: ProtossInterface, mode: int):
    interface.event_id = mode + 2
    req = interface.SerializeToString()
    r.send(req)
    r.recvrepeat(1)

# def custom_macros(r: tube):
#     user_input = input("Select custom macros: ")
#     if user_input == "1":
#         call_sigsegv(r)
#     else:
#         print("Wrong Input.")


def user_handler(r: tube, user_input: str, interface: ProtossInterface):
    mode = USER_HANDLER
    if user_input == "1":
        show_user_info(r, interface, mode)
    elif user_input == "2":
        user_signup(r, interface, mode)
    elif user_input == "3":
        user_signin(r, interface, mode)
    elif user_input == "4":
        user_signout(r, interface, mode)


def buy(r: tube, interface: ProtossInterface, mode: int, buy: Buy = None):
    if buy == None:
        buy = Buy()
        buy.symbol = int(input("Input symbol: "), 10)
        buy.amount = int(input("Input Amount: "), 10)
        # buy.timestamp = todo
    interface.event_id = mode + 1
    interface.event_buy.symbol = buy.symbol
    interface.event_buy.amount = buy.amount
    req = interface.SerializeToString()
    # with open("buy", "wb") as f:
    #     f.write(bytes(req))
    r.send(req)
    print(r.recvrepeat(1).decode())


def sell(r: tube, interface: ProtossInterface, mode: int, sell: Sell = None):
    if sell == None:
        sell = Sell()
        sell.symbol = int(input("Input symbol: "), 10)
        sell.amount = int(input("Input Amount: "), 10)
    interface.event_id = mode + 1
    interface.event_sell.symbol = sell.symbol
    interface.event_sell.amount = sell.amount
    req = interface.SerializeToString()
    r.send(req)
    print(r.recvrepeat(1).decode())


def exchange_handler(r: tube, user_input: str, interface: ProtossInterface):
    mode = EXCHANGE_HANDLER
    if user_input == "1":
        buy(r, interface, mode)
    elif user_input == "2":
        sell(r, interface, mode)


def set_signup(username: str, password: str) -> SignUp:
    user = SignUp()
    user.username = username
    user.password = password
    return user


def set_signin(username: str, password: str) -> SignIn:
    user = SignIn()
    user.username = username
    user.password = password
    return user


def set_sell(symbol: int, amount: int,
             timestamp: int = int(datetime.datetime.now().timestamp())) -> Sell:
    sell = Sell()
    sell.symbol = symbol
    sell.amount = amount
    sell.timestamp = timestamp
    return sell


def set_buy(symbol: int, amount: int,
            timestamp: int = int(datetime.datetime.now().timestamp())) -> Buy:
    buy = Buy()
    buy.symbol = symbol
    buy.amount = amount
    buy.timestamp = timestamp
    return buy
