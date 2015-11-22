import os

GIT_ENABLED = 1
DATA_DIR = os.path.join(".","flot-operations")
MY_GIT = u"git@github.com:dc-tcs/flot-operations"

#ADDRESS: Multisig address
#ADDRESSESS: Constituents of the Multisig address
#These scripts can only track 1 addresses for now
ADDRESS = u"BT9AWq9r1i6kghZc6LtrvNb2wRFh7JLCdP"
ADDRESSES = set([])

#URLs of folders from which to download address snapshots (spendable outputs etc)
#Format should be like this:
#REFERENCE_URLS = {"foo" : "https://bar", "foo2" : "https://bar2", "foo3" : "https://bar3"}
REFERENCE_URLS = {"dc-tcs" : "https://raw.githubusercontent.com/dc-tcs/flot-operations/master"}

RPC_PORT = 14002
TEST_RPC_PORT = 15002
#defaults: 14002 for NBT (mainnet)
#          15002 for NBT (testnet)

RPC_USERNAME = ""
RPC_PASSWORD = ""
