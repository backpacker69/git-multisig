# Copyright 2015 dc-tcs
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
#    Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.


import subprocess
import os
import json
from decimal import Decimal
import math
import config
import jsonrpc

rpc_server = jsonrpc.ServiceProxy("http://" + config.RPC_USERNAME + ":" +\
        config.RPC_PASSWORD + "@127.0.0.1:" + str(config.RPC_PORT))

try:
    for account in config.ACCOUNTS:
        if account['coin']=='NBT':
            s = rpc_server.addmultisigaddress(account['sign_threshold'], account['pubkeys'], account['name'])
            print "Added multisig address to client, label =", account['name']
            if s == account['address']:
                print "Multisig address seems valid."
            else:
                print "Address does not match given public keys (note that order matters)"
except:
    print "Error verifying multisig address!"

#rpc_server.addmultisigaddress(config.SIGN_THRESHOLD, json.dumps(list(config.PUBKEYS)))

def NBTJSONtoAmount(value):
    return Decimal(round(value * 10000))/Decimal(10000)

class RPCCaller:
    #Deprecated?
    def __init__(self, param = 'nud', mode = 0):
        if mode == 0:
            self.nudpath = param
        self.mode = mode

    def __call__(self, args):
        if self.mode == 0:
            args = [str(arg) for arg in args]
            call_args = [self.nudpath] + args

            return subprocess.check_output(call_args)
        else:
            #TODO: use rpc port etc.
            return None

class Block:
    #TODO
    def __init__(self, blockhash):
        self.json = rpc_server.getblock(self.current_block)

class BlockchainStream:
    def __init__(self, start_height, monitor):
        self.height = start_height

        try:
            self.current_block = rpc_server.getblockhash(int(start_height))
        except:
            self.current_block = None
        self.monitor = monitor

    def advance(self):
        if self.current_block:
            s_json = rpc_server.getblock(self.current_block,True,True)

            self.current_block = s_json.get(u'nextblockhash')

            if self.current_block:
                self.height += 1
            return self.monitor(s_json)
        else:
            return None

class RPCError(Exception):
    def __init__(self):
        pass

class UnspentMonitor:
    def __init__(self, address, addresses, unspent):
        self.address = address
        self.addresses = addresses
        self.unspent = unspent
    def __call__(self, s_json):
        flag_changes = 0
        unspent_minus = set()
        unspent_plus = set()

        for tx_json in s_json.get(u'tx'):

            #Add new outputs:
            unit = None
            for vo_json in tx_json.get(u'vout'):
                spk_json = vo_json.get(u'scriptPubKey')

                if spk_json.get('addresses'):
                    vout_addresses = set(spk_json.get('addresses'))
                    if vout_addresses == self.addresses \
                            or vout_addresses == set([self.address]):
                        amount = NBTJSONtoAmount(vo_json.get(u'value'))
                        vout_n = int(vo_json.get(u'n'))
                        txid = tx_json.get('txid')
                        unspent_plus.add((txid, amount, vout_n))
                    if next(iter(vout_addresses)).startswith("B"):
                        unit = 'B'

            if unit == 'B':
                #Remove used inputs:
                for vin_json in tx_json.get(u'vin'):
                    vin_txid = vin_json.get(u'txid')

                    vin_tx_voutn = vin_json.get(u'vout')

                    if vin_tx_voutn:
                        vin_tx_voutn = int(vin_tx_voutn)
                        for tup in self.unspent:
                            if tup[0] == vin_txid and tup[2] == vin_tx_voutn:
                                unspent_minus.add(tup)
                                break

        return unspent_minus, unspent_plus

def getkbfee():
    #TODO: call getfee rpc when 2.1 is ready
    return Decimal("0.01")

def getnkb(n_vins):
    #overestimate number of bytes of transaction
    n_bytes = 126 + 44 * (n_vins-1) + 80 * config.SIGN_THRESHOLD + len(config.PUBKEYS) * 34
    return int(math.ceil(n_bytes/1024)/2)

def create_raw_transaction(amount, address_info, recipient):
    #amount should be a string or Decimal
    kbfee = getkbfee() #fee per byte
    
    kbsize = 1
    fee = getkbfee()
    amount = Decimal(amount)

    while 1:
        unspent_list = sorted(address_info.unspent, key=lambda x: x[1])
        my_sum = Decimal(0)
        i = 0
        while my_sum < amount + fee and i < len(unspent_list):
            my_sum += unspent_list[i][1]
            i += 1

        if my_sum < amount + fee:
            print "Error: Send amount exceeds balance."
            return None
        elif kbsize < getnkb(i):
            kbsize = getnkb(i)
            fee = kbsize * getnkb(i)
        else:
            fee = kbsize * getnkb(i)
            break

    unspent_list = unspent_list[0:i]

    if unspent_list:
        s = unspent_list[0] 
        
        st = "[{\"txid\":\"" + s[0] + "\",\"vout\": " + str(s[2]) + "}"
        for s in unspent_list[1:]:
            st = st + ",{\"txid\":\"" + s[0] + "\",\"vout\":" + str(s[2]) + "}"
        st = st + "]"

        sr = "{\"" + recipient +"\":" + str(amount) + ",\"" + address_info.address + "\":" + str(my_sum - fee - amount) + "}"

        try:
            tx_hex = rpc_server.createrawtransaction(json.loads(st),json.loads(sr))
            return rpc_server.createrawtransaction(json.loads(st),json.loads(sr))
        except:
            #print "nud -unit=B createrawtransaction " + st + " " + sr
            return None
    else:
        return None

def decode_raw_transaction(hexstring):
    try:
        s_json = rpc_server.decoderawtransaction(hexstring)
    except:
        return None
