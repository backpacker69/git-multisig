import os
from pubconfig import *

#Enable if you wish to push/pull/clone address snapshots with MY_GIT
GIT_ENABLED = 0

#Where to keep the unspent outputs list
DATA_DIR = os.path.join(".","flot-operations")

#For git clone and git pushing DATA_DIR
MY_GIT = "git@github.com:dc-tcs/flot-operations"
MY_ID = "dc-tcs"

#RPC settings - consult nu.conf
#defaults: port 14002 for NBT (mainnet)
#          port 15002 for NBT (testnet)
RPC_PORT = 14002
RPC_USERNAME = ""
RPC_PASSWORD = ""
