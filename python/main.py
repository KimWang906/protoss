import build.protoss_pb2
from pwn import *

r = remote("0.0.0.0", 5050)

USER_HANDLER = 16 << 24
EXCHANGE_HANDLER = 32 << 24

context.log_level = 'debug'

def prompt():
    while(1):
        ProtossInterface = build.protoss_pb2.ProtossInterface()
        print("Hiring CTF ProtossInterface")
        print("1. Call User Handler")
        print("2. Call Exchange Handler")
        print("3. Exit")
        user_input = input("Input: ")
        if user_input == "1":
            print("Select User Option")
            print("1. Show My Information")
            print("2. Sign-Up Account")
            print("3. Sign-In Account")
            print("4. Sign-Out Account")
            user_input = input("Input: ")
            user_handler(user_input, ProtossInterface)
        elif user_input == "2":
            print("Select Exchange Handler")
        elif user_input == "3":
            print("Exit ProtossInterface ...")
            exit(0)
        else: print("Wrong Input")

def user_handler(user_input: str, interface):
    mode = USER_HANDLER
    if user_input == "1":
        interface.event_id = mode + 3
    elif user_input == "2":
        interface.event_id = mode
        interface.event_signup.username = input("New Username: ")
        interface.event_signup.password = input("New Password: ")
    r.send(interface.SerializeToString())
    with open('my_file.txt', 'wb') as binary_file:
        binary_file.write(interface.SerializeToString())
    if r.can_recv:
        print(r.recvall())

# Execute prompt
prompt()

r.interactive()