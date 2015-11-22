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
import config
import jsonrpc

rpc_server = jsonrpc.ServiceProxy("http://" + config.RPC_USERNAME + ":" +\
        config.RPC_PASSWORD + "@127.0.0.1:" + str(config.RPC_PORT))

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

if config.RPC_MODE == 0:
    call_rpc = RPCCaller(param = config.NUD_PATH, mode = 0)
elif config.RPC_MODE == 1:
    call_rpc  = RPCCaller(param = config.RPC_PORT, mode = 1)

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
            rpc_server.getblock(self.current_block)
            s_json = rpc_server.getblock(self.current_block)

            self.current_block = s_json.get(u'nextblockhash')

            if self.current_block:
                self.height += 1
            return self.monitor(s_json)
        else:
            return None

class UnspentMonitor:
    def __init__(self, address, addresses):
        self.address = address
        self.addresses = addresses
    def __call__(self, s_json):
        flag_changes = 0
        unspent_minus = set()
        unspent_plus = set()

        for txid in s_json[u'tx']:
            t_json = rpc_server.getrawtransaction(txid, 1)

            if t_json[u'unit'] == u'B':
                #Remove used inputs:
                for vi_json in t_json.get(u'vin'):
                    vin_txid = vi_json.get(u'txid')
                    vin_tx_voutn = int(vi_json.get(u'vout'))

                    if not vin_txid == '0000000000000000000000000000000000000000000000000000000000000000':
                        vin_tx_json = rpc_server.getrawtransaction(vin_txid, 1)

                        for vo_json in vin_tx_json.get(u'vout'):
                            spk_json = vo_json.get(u'scriptPubKey')
                            #if (vin_txid == u"b73c15c622c515c1e0bdf8d1609e5f7a9e44ce3f1930759fe1716a0687ca1237"):
                            #    print spk_json
                            #    print set(spk_json.get(u'addresses'))
                            
                            vout_n = int(vo_json.get(u'n'))
                            if vout_n == vin_tx_voutn:
                                try:
                                    vout_addresses = set(spk_json.get(u'addresses'))
                                except:
                                    vout_addresses = set([spk_json.get(u'unparkaddress')])
                                if vout_addresses == self.addresses \
                                        or vout_addresses == set([self.address]):
                                    #TODO: check actual specification of "addresses"
                                    amount = NBTJSONtoAmount(vo_json.get(u'value'))
                                    unspent_minus.add((vin_txid, amount, vout_n))

                #Add new outputs:
                for vo_json in t_json.get(u'vout'):
                    spk_json = vo_json.get(u'scriptPubKey')
                    vout_addresses = set(spk_json.get(u'addresses'))
                    if vout_addresses == self.addresses \
                            or vout_addresses == set([self.address]):
                        amount = NBTJSONtoAmount(vo_json.get(u'value'))
                        vout_n = int(vo_json.get(u'n'))
                        unspent_plus.add((txid, amount, vout_n))

        return (unspent_minus, unspent_plus)

def getfee(amount, address_info, recipient):
    #TODO: call getfee rpc when 2.1 is ready
    return Decimal("0.01")

def create_raw_transaction(amount, address_info, recipient):
    #amount should be a string or Decimal
    fee = getfee(amount, address_info, recipient)

    unspent_list = sorted(address_info.unspent, key=lambda x: x[1])
    sum = Decimal(0)
    amount = Decimal(amount)
    i = 0
    while sum < amount and i < len(unspent_list):
        sum += unspent_list[i][1]
        i += 1

    if sum < amount:
        return None

    unspent_list = unspent_list[0:i]

    if unspent_list:
        s = unspent_list[0] 
        
        st = "[{\"txid\":\"" + s[0] + "\",\"vout\": " + str(s[2]) + "}"
        for s in unspent_list[1:]:
            st = st + ",{\"txid\":\"" + s[0] + "\",\"vout\":" + str(s[2]) + "}"
        st = st + "]"

        sr = "{\"" + recipient +"\":" + str(amount) + ",\"" + address_info.address + "\":" + str(sum - fee - amount) + "}"

        return rpc_server.createrawtransaction(json.loads(st),json.loads(sr))
    else:
        return None

def decode_raw_transaction(hexstring):
    try:
        s_json = rpc_server.decoderawtransaction(hexstring)
    except:
        return None
