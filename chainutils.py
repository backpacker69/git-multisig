import subprocess
import os
import json
from decimal import Decimal

def NBTJSONtoAmount(value):
    return Decimal(round(value * 100))/Decimal(100)

def call_rpc(args):
    nud_path = 'nud'
    args = [str(arg) for arg in args]
    call_args = [nud_path] + args

    return subprocess.check_output(call_args)

class BlockchainStream:
    def __init__(self, start_height, monitor):
        self.height = start_height
        self.next_block = call_rpc(["getblockhash", start_height])
        self.monitor = monitor

    def advance(self):
        if self.next_block:
            s_json = json.loads(call_rpc(["getblock", self.next_block]))

            self.next_block = s_json.get(u'nextblockhash')

            if self.next_block:
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
            t_out = call_rpc(["getrawtransaction", txid, "1"])

            t_json = json.loads(t_out)

            if t_json[u'unit'] == u'B':
                #Remove used inputs:
                for vi_json in t_json.get(u'vin'):
                    vin_txid = vi_json.get(u'txid')
                    vin_tx_voutn = int(vi_json.get(u'vout'))

                    vin_tx_json = json.loads(call_rpc(["getrawtransaction", vin_txid, "1"]))

                    for vo_json in vin_tx_json.get(u'vout'):
                        spk_json = vo_json.get(u'scriptPubKey')
                        #if (vin_txid == u"b73c15c622c515c1e0bdf8d1609e5f7a9e44ce3f1930759fe1716a0687ca1237"):
                        #    print spk_json
                        #    print set(spk_json.get(u'addresses'))
                        
                        vout_n = int(vo_json.get(u'n'))
                        if vout_n == vin_tx_voutn:
                            vout_addresses = set(spk_json.get(u'addresses'))
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
