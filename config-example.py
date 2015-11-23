import os
from pubconfig import *

DATA_DIR = os.path.join(".","flot-operations")

GIT_ENABLED = 0

#This is only used with GIT_ENABLED = 1
MY_GIT = "git@github.com:dc-tcs/flot-operations"

#How others will identify you. Not used yet.
MY_ID = "dc-tcs"

#SET RPC port
RPC_PORT = 14002
#TEST_RPC_PORT = 15002
#defaults: 14002 for NBT (mainnet)
#          15002 for NBT (testnet)

RPC_USERNAME = "nurpc"
RPC_PASSWORD = ""
