import os
from pubconfig import *

TXINDEX = 0
#Set to 1 if txindex = 1 is in nu.conf and you've run nu with -reindex

GIT_ENABLED = 0
DATA_DIR = os.path.join(".","flot-operations")
MY_GIT = "git@github.com:dc-tcs/flot-operations"
MY_ID = "dc-tcs"

RPC_PORT = 14002
#TEST_RPC_PORT = 15002
#defaults: 14002 for NBT (mainnet)
#          15002 for NBT (testnet)

RPC_USERNAME = ""
RPC_PASSWORD = ""
