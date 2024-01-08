import re
from enum import IntFlag, auto


class VM_FLAGS(IntFlag):
    VM_READ = auto()
    VM_WRITE = auto()
    VM_EXEC = auto()
    VM_PRIVATE = auto()
    VM_SHARED = auto()

    def __str__(self) -> str:
        items = [(member.name, member.value) for member in VM_FLAGS]
        result = []
        for name, value in items:
            if self.value & value:
                result.append(name)
        return ', '.join(result)


class Device:
    def __init__(self, major, minor):
        self.major_num = major
        self.minor_num = minor

    def __str__(self) -> str:
        return f"Major Number: {self.major_num}, Minor Number: {self.minor_num}"


class VirtualMemoryLayout:
    def __init__(self, raw_data: bytes):
        data = self.__parse_raw_data(raw_data)
        self.__set_addr(data[0])
        self.__set_permission(data[1])
        self.__set_offset(data[2])
        self.__set_dev(data[3])
        self.__set_inode(data[4])
        self.__set_pathname(data[5])

    def __str__(self) -> str:
        return f"""===========================MemoryMap===========================
    start: {hex(self.start)}, end: {hex(self.end)}
    permissions: {self.permissions}
    offset: {hex(self.offset)}
    dev: {self.dev}
    inode: {self.inode}
    pathname: {self.pathname}\n==============================================================="""

    def __replace_multiple_spaces(self, input_bytes: bytes):
        pattern = re.compile(b"[ \t]+")
        self.__raw_data = pattern.sub(b' ', input_bytes)

    # Lines[attribute[data...]]
    def __parse_raw_data(self, raw_data: bytes) -> list[list[bytes]]:
        self.__replace_multiple_spaces(raw_data)
        return self.__raw_data.split(b' ')

    def __set_addr(self, raw_data: bytes):
        addr = raw_data.split(b'-')
        self.start = int(addr[0], 16)
        self.end = int(addr[1], 16)

    def __set_permission(self, raw_data: bytes):
        permissions = raw_data.decode()
        result = 0
        for perm in permissions:
            match perm:
                case 'r':
                    result |= VM_FLAGS.VM_READ
                case 'w':
                    result |= VM_FLAGS.VM_WRITE
                case 'x':
                    result |= VM_FLAGS.VM_EXEC
                case 'p':
                    result |= VM_FLAGS.VM_PRIVATE
                case 's':
                    result |= VM_FLAGS.VM_SHARED
        if result == 0:
            self.permissions = 'Empty'
        self.permissions = VM_FLAGS(result)

    def __set_offset(self, raw_data: bytes):
        self.offset = int(raw_data, 16)

    def __set_dev(self, raw_data: bytes):
        dev = raw_data.split(b':')
        self.dev = Device(int(dev[0], 10), int(dev[1], 10))

    def __set_inode(self, raw_data: bytes):
        self.inode = int(raw_data, 10)

    def __set_pathname(self, raw_data: bytes):
        if raw_data != b'':
            self.pathname = raw_data.decode()
        else:
            self.pathname = 'Empty'
