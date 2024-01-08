import build.protoss_pb2
import module.protoss_handler
from pwn import *

r = remote("0.0.0.0", 5050)
# r = remote("host3.dreamhack.games", 20391)
# context.log_level = 'debug'

# Execute prompt
module.protoss_handler.prompt(r)

r.interactive()
