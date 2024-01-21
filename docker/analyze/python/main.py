import module.protoss_handler
from pwn import *
from pwn import p64


def slog(n, m): return success(': '.join([n, hex(m)]))


# set breakpoint...
breakpoint = {
    'call_validate_user_krw': '_ZN8Exchange10handle_buyERKN7protoss3BuyE+711',
    'case_user_handler': '_Z13parse_handlerPKci+203',
    'case_exchange_handler': '_Z13parse_handlerPKci+231',
    'call_handle_my_info': '_Z12user_handlerPN7protoss16ProtossInterfaceE+458',
    'call_handle_signout': '_Z12user_handlerPN7protoss16ProtossInterfaceE+380',
    'call_handle_signin': '_Z12user_handlerPN7protoss16ProtossInterfaceE+322',
    'call_handle_signup': '_Z12user_handlerPN7protoss16ProtossInterfaceE+198',
    'call_handle_buy': '_Z16exchange_handlerPN7protoss16ProtossInterfaceE+270',
    'call_handle_sell': '_Z16exchange_handlerPN7protoss16ProtossInterfaceE+366',
    'call_handle_deposit': '_Z16exchange_handlerPN7protoss16ProtossInterfaceE+462',
    'call_handle_view_history': '_Z16exchange_handlerPN7protoss16ProtossInterfaceE+558',
    'call_handle_add_addressbook': '_Z16exchange_handlerPN7protoss16ProtossInterfaceE+654',
    'call_handle_modify_addressbook': '_Z16exchange_handlerPN7protoss16ProtossInterfaceE+750',
    'call_handle_del_addressbook': '_Z16exchange_handlerPN7protoss16ProtossInterfaceE+840',
}

gdbscript = ''

for bp in breakpoint.values():
    fmt = 'b *{}\n'.format(bp)
    gdbscript += fmt

gdbscript += 'c\n'

context.terminal = [
    'tmux',
    'new-window',
    '-n',
    'DEBUG-{}'.format(sys.argv[0])
]

p = process('/home/user/protoss')
# context.log_level = 'debug'


if len(sys.argv) > 1:
    if sys.argv[1] == 'debug':
        context.log_level = 'debug'
        attach(p, gdbscript)
else:
    pass

# Write exploit code!
def custom_payload():
    pass

select = input('Run prompt mode? [Y/N]: ')
if select == 'Y' or 'y':
    print('Run Protoss Handler prompt..')
    # Execute prompt
    module.protoss_handler.prompt(p)
elif select == 'N' or 'n':
    print('Run Custom Code')
    custom_payload()

p.interactive()
