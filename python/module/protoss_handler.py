import json
import base64
from module.memory import *
from pwn import *
from pwnlib.timeout import *
from build.protoss_pb2 import ProtossInterface, SignUp, SignIn

USER_HANDLER = 16 << 24
EXCHANGE_HANDLER = 32 << 24
MEMORY_MAP_LINES = 24


def prompt(r: tube):
    while (1):
        print("Hiring CTF ProtossInterface")
        print("1. Call User Handler")
        print("2. Call Exchange Handler")
        print("3. Call Custom Macro")
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
        elif user_input == "3":
            pass
        elif user_input == "4":
            print("Exit ProtossInterface ...")
            exit(0)
        else:
            print("Wrong Input")


def show_user_info(r: tube, interface: ProtossInterface, mode: int):
    interface.event_id = mode + 3
    req = interface.SerializeToString()
    # module.protoss_log.logging_request('Show_My_Information', req)
    r.send(req)


def user_signup(r: tube, interface: ProtossInterface,
                mode: int, signup: SignUp = None):
    if signup is None:
        signup = SignUp()
        signup.username = input('New Username: ')
        signup.password = input('New Password: ')

    interface.event_id = mode
    interface.event_signup.username = signup.username
    interface.event_signup.password = signup.password
    req = interface.SerializeToString()
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
        print('username: {}'.format(username))
        print('acc_id: {}'.format(json_res['acc_id']))
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
    # module.protoss_log.logging_request('Sign-In_Account', req)
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

def user_handler(r: tube, user_input: str, interface: ProtossInterface):
    mode = USER_HANDLER
    if user_input == "1":
        show_user_info(r, interface, mode)
    elif user_input == "2":
        user_signup(r, interface, mode)
    elif user_input == "3":
        user_signin(r, interface, mode)
