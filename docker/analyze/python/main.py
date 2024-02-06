from module.protoss_handler import *
from pwn import *
from pwn import p64
from build.protoss_pb2 import ProtossInterface, SignUp, SignIn, Buy, Sell
from module.custom import *

def slog(n, m): return success(': '.join([n, hex(m)]))


# set breakpoint...
breakpoint = {
    'call_validate_user_krw': '_ZN8Exchange10handle_buyERKN7protoss3BuyE+711',
    'case_user_handler': '_Z13parse_handlerPKci+203',
    'case_exchange_handler': '_Z13parse_handlerPKci+231',
    'call_handle_my_info': '_Z12user_handlerPN7protoss16ProtossInterfaceE+458',
    'call_handle_signout': '_Z12user_handlerPN7protoss16ProtossInterfaceE+397',
    'call_handle_signin': '_Z12user_handlerPN7protoss16ProtossInterfaceE+322',
    'call_handle_signup': '_Z12user_handlerPN7protoss16ProtossInterfaceE+198',
    'call_handle_buy': '_Z16exchange_handlerPN7protoss16ProtossInterfaceE+270',
    'call_handle_sell': '_Z16exchange_handlerPN7protoss16ProtossInterfaceE+366',
    'call_handle_deposit': '_Z16exchange_handlerPN7protoss16ProtossInterfaceE+462',
    'call_handle_view_history': '_Z16exchange_handlerPN7protoss16ProtossInterfaceE+558',
    'call_handle_add_addressbook': '_Z16exchange_handlerPN7protoss16ProtossInterfaceE+654',
    'call_handle_modify_addressbook': '_Z16exchange_handlerPN7protoss16ProtossInterfaceE+750',
    'call_handle_del_addressbook': '_Z16exchange_handlerPN7protoss16ProtossInterfaceE+840',
    'signal_handler': '_Z7handleri',
    'SIGSEGV_view_history': '_ZN8Exchange19handle_view_historyERKN7protoss7HistoryE+458',
    'SIGSEGV_singin': '_ZN4User13handle_signinERKN7protoss6SignInE+649',
}

gdbscript = ''

gdbscript += 'handle SIGSEGV pass\n'

for bp in breakpoint.values():
    fmt = 'b *{}\n'.format(bp)
    gdbscript += fmt

# gdbscript += 'c\n'

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


select = input('Run prompt mode? [Y/N]: ').lower()
if select == 'y':
    print('Run Protoss Handler prompt..')
    # Execute prompt
    prompt(p)
elif select == 'n':
    print('Run Custom Code')
    custom_payload(p)
else:
    print('Wrong Input.')

p.interactive()
