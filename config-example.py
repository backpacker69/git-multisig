import os

GIT_ENABLED = 0
DATA_DIR = os.path.join(".","flot-operations")
MY_GIT = u"git@github.com:dc-tcs/flot-operations"

#ADDRESS: Multisig address
#ADDRESSESS: Constituents of the Multisig address
#These scripts can only track 1 addresses for now
ADDRESS = u"BqyRzFtWXDmjxrYpyJD42MLE5xc8FrB4js"
ADDRESSES = set([])

#URLs of folders from which to download address snapshots (spendable outputs etc)
#Format should be like this:
#REFERENCE_URLS = {"foo" : "https://bar", "foo2" : "https://bar2", "foo3" : "https://bar3"}
REFERENCE_URLS = {"dc-tcs" : "https://raw.githubusercontent.com/dc-tcs/flot-operations/master"}

RPC_PORT = 14002
#TEST_RPC_PORT = 15002
#defaults: 14002 for NBT (mainnet)
#          15002 for NBT (testnet)

RPC_USERNAME = "nurpc"
RPC_PASSWORD = ""
