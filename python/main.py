import build.protoss_pb2
import module.protoss_handler
from pwn import *

r = remote("0.0.0.0", 5050)
# context.log_level = 'debug'

sleep(1)
attach(r)

# Execute prompt
module.protoss_handler.prompt(r)

r.interactive()
