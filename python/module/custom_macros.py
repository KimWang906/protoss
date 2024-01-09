import os
from build.protoss_pb2 import *

random_user = SignIn()


def generate_password(length):
    password = ''
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_-+=<>?"
    for i in range(length):
        random_number = int.from_bytes(os.urandom(
            4), byteorder="big") % len(characters) + 0
        password += characters[random_number]
    return password


user_password = generate_password(10)
print("Generated Password:", user_password)
