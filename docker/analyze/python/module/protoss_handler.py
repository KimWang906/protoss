import json
import base64
import regex
from datetime import *
from module.memory import *
from numpy import *
from module.protoss_log import *
from pwn import *
from pwnlib.timeout import *
from build.protoss_pb2 import ProtossInterface, \
    SignUp, SignIn, Buy, Sell, History, AddressBook, \
    ModifyAddressBook, Deposit

USER_HANDLER = 16 << 24
EXCHANGE_HANDLER = 32 << 24

def print_raw_data(data: bytes):
    hex_chars = [data.hex()[i:i+2] for i in range(0, len(data.hex()),  2)]
    print('============================')
    print('Received raw data: ')
    for i in range(0, len(hex_chars), 8):
        line = ' '.join(hex_chars[i:i+8])
        print(line)
    print('============================')

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
            print_raw_data(r.recv())
        elif user_input == "4":
            print("Exit ProtossInterface ...")
            exit(0)
        else:
            print("Wrong Input")

def show_user_info(r: tube, interface: ProtossInterface, mode: int):
    interface.event_id = mode + 3
    req = interface.SerializeToString()
    # module.protoss_log.logging_request('Show_My_Information', req)
    r.sendafter(b'> ', req)
    data = r.recv()
    if '> ' not in data.decode():
        for memory_map in sigsegv_parse(data):
            print(memory_map)
    else:
        print_raw_data(data)
        print('============================')
        print(data.decode().replace('\n>', ''))
        print('============================')
        r.unrecv(b'> ')

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
    r.sendafter(b'> ', req)
    # try catch ...
    sign_up_response(r)
    r.unrecv(b'> ')

def is_base64_encoded(s):
    try:
        base64.b64decode(s)
        return True
    except binascii.Error:
        return False

def sign_up_response(r: tube):
    r.recvuntil(b'\n')
    raw_data = r.recvuntil(b'>')[:-1]
    try:
        pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')
        matches = pattern.findall(raw_data.decode())
        print('============================')
        print(f"Received: {raw_data.decode()}")
        print('============================')
        print_raw_data(raw_data)
        for json_fmt in matches:
            json_res = json.loads(json_fmt)
            print('============================')
            for key, value in json_res.items():
                if is_base64_encoded(value):
                    b_val = base64.b64decode(value)
                    value = b_val.decode()
                print(f"{key}: {value}")
            print('============================')
    except json.JSONDecodeError:
        print_raw_data(raw_data)
        print(f"JsonDecodeError.\nReceived: {raw_data}")

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
    r.sendafter(b'> ', req)
    print_raw_data(r.recv())
    r.unrecv(b'> ')

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
    r.sendafter(b'> ', req)
    data = r.recv()
    if '> ' not in data.decode():
        for memory_map in sigsegv_parse(data):
            print(memory_map)
    else:
        print_raw_data(data)
        print('============================')
        print(data.decode().replace('\n>', ''))
        print('============================')
    r.unrecv(b'> ')

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
    interface.event_id = mode
    interface.event_buy.symbol = buy.symbol
    interface.event_buy.amount = buy.amount
    req = interface.SerializeToString()
    # with open("buy", "wb") as f:
    #     f.write(bytes(req))
    r.sendafter(b'> ', req)
    print(r.recv().decode())


def sell(r: tube, interface: ProtossInterface, mode: int, sell: Sell = None):
    if sell == None:
        sell = Sell()
        sell.symbol = int(input("Input symbol: "), 10)
        sell.amount = int(input("Input Amount: "), 10)
    interface.event_id = mode + 1
    interface.event_sell.symbol = sell.symbol
    interface.event_sell.amount = sell.amount
    req = interface.SerializeToString()
    r.sendafter(b'> ', req)
    data = r.recv()
    print_raw_data(data)
    print('============================')
    print(data.decode())
    print('============================')

def view_history(
    r: tube,
    interface: ProtossInterface,
    mode: int,
    history: History = None):
    if history == None:
        history = History()
        history.symbol = int(input("Input symbol: "), 10)
        history.type = int(input("Input type: "), 10)
    interface.event_id = mode + 2
    interface.event_history.symbol = history.symbol
    interface.event_history.type = history.type
    req = interface.SerializeToString()
    r.sendafter(b'> ', req)
    data = r.recv()
    if '> ' not in data.decode():
        for memory_map in sigsegv_parse(data):
            print(memory_map)
    else:
        print_raw_data(data)
        print('============================')
        print(f'{data.decode()}')
        print('============================')

def add_addrbook(
    r: tube,
    interface:ProtossInterface,
    mode: int,
    addrbook: AddressBook = None):
    if addrbook == None:
        addrbook = AddressBook()
        addrbook.symbol = int(input("Input symbol: "), 10)
        addrbook.address = input("Input address: ")
        addrbook.memo = input("Input memo: ")
    interface.event_id = mode + 3
    interface.event_addressbook.symbol = addrbook.symbol
    interface.event_addressbook.address = addrbook.address
    interface.event_addressbook.memo = addrbook.memo
    req = interface.SerializeToString()
    r.sendafter(b'> ', req)
    data = r.recv()
    print_raw_data(data)
    print('============================')
    print(f'{data.decode()}')
    print('============================')

def modify_addrbook(
    r: tube,
    interface: ProtossInterface,
    mode: int,
    mod_addrbook: ModifyAddressBook = None):
    if mod_addrbook == None:
        mod_addrbook = ModifyAddressBook()
        mod_addrbook._id = int(input("Input _id: "), 10)
        mod_addrbook.origin_addr = input("Input origin address: ")
        mod_addrbook.new_addr = input("Input new address: ")
        mod_addrbook.memo = input("Input memo: ")
    interface.event_id = mode + 4
    interface.event_modify_addressbook._id = mod_addrbook._id
    interface.event_modify_addressbook.origin_addr = mod_addrbook.origin_addr
    interface.event_modify_addressbook.new_addr = mod_addrbook.new_addr
    interface.event_modify_addressbook.memo = mod_addrbook.memo
    req = interface.SerializeToString()
    r.sendafter(b'> ', req)
    data = r.recv()
    print_raw_data(data)
    print('============================')
    print(f'{data.decode()}')
    print('============================')

def del_addrbook(
    r: tube,
    interface: ProtossInterface,
    mode: int,
    addrbook: AddressBook = None):
    if addrbook == None:
        addrbook = AddressBook()
        addrbook.symbol = int(input("Input symbol: "), 10)
        addrbook.address = input("Input address: ")
        addrbook.memo = input("Input memo: ")
    interface.event_id = mode + 5
    interface.event_addressbook.symbol = addrbook.symbol
    interface.event_addressbook.address = addrbook.address
    interface.event_addressbook.memo = addrbook.memo
    req = interface.SerializeToString()
    r.sendafter(b'> ', req)
    data = r.recv()
    print_raw_data(data)
    print('============================')
    print(f'{data.decode()}')
    print('============================')

def deposit(
    r: tube,
    interface: ProtossInterface,
    mode: int,
    deposit: Deposit = None):
    if deposit == None:
        deposit = Deposit()
        deposit.address = input("Input address: ")
        deposit.symbol = int(input("Input symbol: "), 10)
        deposit.memo = int(input("Input memo: "))
    interface.event_id = mode + 6
    interface.event_deposit.address = deposit.address
    interface.event_deposit.symbol = deposit.symbol
    interface.event_deposit.memo = deposit.memo
    req = interface.SerializeToString()
    r.sendafter(b'> ', req)
    data = r.recv()
    print_raw_data(data)
    print('============================')
    print(f'{data.decode()}')
    print('============================')

def exchange_handler(r: tube, user_input: str, interface: ProtossInterface):
    mode = EXCHANGE_HANDLER
    if user_input == "1":
        buy(r, interface, mode)
    elif user_input == "2":
        sell(r, interface, mode)
    elif user_input == "3":
        view_history(r, interface, mode)
    elif user_input == "4":
        add_addrbook(r, interface, mode)
    elif user_input == "5":
        modify_addrbook(r, interface, mode)
    elif user_input == "6":
        del_addrbook(r, interface, mode)
    elif user_input == "7":
        deposit(r, interface, mode)

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


def set_sell(
    symbol: uint,
    amount: uint,
    timestamp: uint64 = uint64(
        datetime.datetime.now().timestamp())
    ) -> Sell:
    sell = Sell()
    sell.symbol = symbol
    sell.amount = amount
    sell.timestamp = timestamp
    return sell


def set_buy(
    symbol: uint,
    amount: uint,
    timestamp:  uint64 = uint64(
        datetime.datetime.now().timestamp())
    ) -> Buy:
    buy = Buy()
    buy.symbol = symbol
    buy.amount = amount
    buy.timestamp = timestamp
    return buy

def set_history(
    symbol: uint,
    type: uint8,
    timestamp: uint64 = uint64(
        datetime.datetime.now().timestamp())
    ) -> History:
    history = History()
    history.symbol = symbol
    history.type = type
    history.ts = timestamp
    return history

def set_addressbook(
    symbol: uint,
    address: str,
    memo: str,
    create_at_timestamp: uint64 = uint64(
        datetime.datetime.now().timestamp())
    ) -> AddressBook:
    addrbook = AddressBook()
    addrbook.symbol = symbol
    addrbook.address = address
    addrbook.memo = memo
    addrbook.create_at_ts = create_at_timestamp
    return addrbook

def set_modify_addressbook(
    id: int, 
    origin_addr: str,
    new_addr: str,
    memo: str
    ) -> ModifyAddressBook:
    mod_addrbook = ModifyAddressBook()
    mod_addrbook._id = id
    mod_addrbook.origin_addr = origin_addr
    mod_addrbook.new_addr = new_addr
    mod_addrbook.memo = memo
    return mod_addrbook

def set_deposit(
    addr: str,
    symbol: uint,
    memo: int64
    ) -> Deposit:
    deposit = Deposit()
    deposit.address = addr
    deposit.symbol = symbol
    deposit.memo = memo
    return deposit
