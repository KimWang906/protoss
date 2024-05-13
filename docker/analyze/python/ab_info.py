import gdb # type: ignore

modify_all_address_sym = 'modify_all_address(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >)'

def run_once_decorator(func):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

class AddressBook(gdb.Command):
    def __init__(self):
        super(AddressBook, self).__init__('addrbook', gdb.COMMAND_USER)
        self.mod_all_addr_lvals = None
        # heap_base, heap_end = gdb.execute('vmmap', to_string=True).split('\n')[7][9:43].split(' ' * 5)
        # self.heap_base = int(heap_base, 16)
        # self.heap_end = int(heap_end, 16)

    def invoke(self, arg = None, from_tty = False):
        if not arg:
            print('Usage: addrbook [function_idx]')
            print('Function list:')
            print(' 0. modify_all_address')
            print('\n' + 'Please input argument')
            return
        if arg == '0':
            self.modify_all_address_info()
        cpp_corrupt
    def get_local_value(self, symbol: str) -> dict[str, list[int]]:
        rbp = gdb.parse_and_eval('$rbp')
        data = dict()
        if symbol == 'modify_all_address':
            data.update({'idx_vector': [rbp - 0xE0, gdb.parse_and_eval(f"*(size_t *){rbp - 0xE0}")]})
            data.update({'address_vector': [rbp - 0xC0, gdb.parse_and_eval(f"*(size_t *){rbp - 0xC0}")]})
        return data
    
    @run_once_decorator
    def get_mod_all_addr_lvals(self):
        self.mod_all_addr_lvals = self.get_local_value('modify_all_address')

    def print_vector(self, address, vector_len, offset):
        for i in range(vector_len):
            try:
                print(f'    - {i}th value({hex(address + i * offset)}): {hex(gdb.parse_and_eval(f"*(size_t *){address + i * offset}"))}')
            except gdb.MemoryError:
                print(f'    - {i}th value({hex(address + i * offset)}): {hex(0)}')

    def modify_all_address_info(self):
        if self.mod_all_addr_lvals is None:
            if gdb.selected_frame().name() == modify_all_address_sym:
                self.get_mod_all_addr_lvals()
            else:
                print('Please set breakpoint at modify_all_address')
                return
        
        print('modify_all_address')

        vector_len = int(input('Input vector length: '))

        print('  - idx vector address: ' + hex(self.mod_all_addr_lvals['idx_vector'][0]))
        self.print_vector(self.mod_all_addr_lvals['idx_vector'][1], vector_len, 4)
        print('  - address vector address: ' + hex(self.mod_all_addr_lvals['address_vector'][0]))
        self.print_vector(self.mod_all_addr_lvals['address_vector'][1], vector_len + 1, 0x20) # OOB(idx + 1)

AddressBook()