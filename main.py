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
import time
from decimal import Decimal
import chainutils as nbtutil

CURRENCY_NBT = 0
CURRENCY_NSR = 1
CURRENCY_BTC = 2

test_address = "BT9AWq9r1i6kghZc6LtrvNb2wRFh7JLCdP"
test_addresses = set(["BT9AWq9r1i6kghZc6LtrvNb2wRFh7JLCdP"])

test_address2 = "BXKidrUiYNgRmDeDX61k6CASEJ2HjM8pUF"
test_addresses2 = set(["B4bABJCsG4nBpk7Hiaw4yX3Fs4LfeS2f16",\
                        "BHaPLPkrd6ZaJV9Kj3pykwDz76YVgNtkvN"])

reference_gits =  {"dc-tcs" : "https://github.com/dc-tcs/flot-operations.git"}

my_id = "dc-tcs"
my_git = os.path.join(".","flot-operations")

class AddressInfo:
    def __init__(self, addr, addrs, unit, root = my_git):
        self.address = addr
        self.addresses = addrs

        self.unspent = set()
        self.unit = unit
        self.last_block = 0
        self.signed_tx = ""
        self.signed_ids = []

        addr_path = os.path.join(root, addr)

        if os.path.isdir(addr_path):
            addr_unspent_path = os.path.join(addr_path,'unspent')
            addr_tx_path = os.path.join(addr_path,'tx')

            if os.path.isfile(addr_unspent_path):
                with open(addr_unspent_path,"r") as f:
                    l = 0
                    cur_tx = ""
                    amount = Decimal(0)
                    for line in f:
                        if l == 0:
                            self.last_block = int(line)
                        elif l % 3 == 1:
                            cur_tx = line.strip()
                        elif l % 3 == 2:
                            amount = Decimal(line)
                        else:
                            self.unspent.add((cur_tx,amount,int(line.strip())))
                        l += 1

        else:
            if not os.path.exists(addr_path):
                os.makedirs(addr_path)
                #TODO: initialize unspent and tx files
    def get_unspent(self):
        return self.unspent

    def update_outputs(self):
        flag_change = 0
        bstream = nbtutil.BlockchainStream(self.last_block + 1,\
                nbtutil.UnspentMonitor(self.address, self.addresses))
        while 1:
            delta = bstream.advance()
            if delta:
                flag_change = 1
                self.last_block = bstream.height
                if len(delta[0]) + len(delta[1]) > 0:
                    #print bstream.next_block
                    #print "delta = ", delta
                    #TODO: prompt difference
                    self.unspent.difference_update(delta[0])
                    self.unspent.update(delta[1])

                    print "new unspent = ", self.unspent
            else:
                break
        #TODO: push to own repo?
        return flag_change

def getfee(amount, my_addr, recipient):
    #TODO: call getfee rpc when 2.1 is ready
    return Decimal(0.01)

def sign_raw_transaction(raw_tx):
    return nbtutil.call_rpc(["signrawtransaction", raw_tx])

def git_update(git_folder):
    subprocess.call(['git', '-C', git_folder, 'add', '-A'])
    subprocess.call(['git', '-C', git_folder, 'commit', '-m', str(time.time())])
    subprocess.call(['git', '-C', git_folder, 'push', 'origin', 'master'])

def sign_and_push(raw_tx, my_addr, list_signed):
    s = sign_raw_transaction(raw_tx)
    if s:
        git_folder = os.path.join('.', my_git)
        tx_path = os.path.join('.', my_git, my_addr,'tx')

        with open(tx_path,'w') as f:
            f.writeline(s)
            for p in list_signed:
                f.writeline(p)
            f.writeline(my_id)
        git_update(git_folder)

root_ref = os.path.join(".","notmine")

def sync_multiple(address_info):
    newest_unspent = address_info.unspent
    newest_rawtx = ""
    newest_signed_ids = []

    current_last_block = address_info.last_block

    for key, value in reference_gits.iteritems():
        git_folder = os.path.join(root_ref,key)

        if not os.path.exists(git_folder):
            subprocess.call(['git', 'clone', value, git_folder])

        #try:
        s = subprocess.check_output(['git', '-C', git_folder, 'fetch', '--dry-run'])
        if s != "":
            subprocess.call(['git', '-C', git_folder, 'fetch'])

        a = AddressInfo(address_info.address, address_info.addresses, CURRENCY_NBT, root = git_folder)

        if a.last_block > current_last_block:
            yes = set(['yes','y', 'ye', ''])
            no = set(['no','n'])

            choice = raw_input("Newer snapshot found for unspent from: " + key + " - accept (Y/n)? ").lower()
            if choice in yes:
                newest_unspent = a.unspent
                current_last_block = a.last_block
        #except:
        #    print "Error!"

    print ""
    return newest_unspent

def write_address_info (address_info):
    path = os.path.join(my_git, address_info.address)
    if os.path.isdir(path):
        with open(os.path.join(path, "unspent"), 'w') as f:
            f.write(str(address_info.last_block) + "\n")
            for t in address_info.unspent:
                f.write(t[0] + "\n")
                f.write(str(t[1]) + "\n")
                f.write(str(t[2]) + "\n")

a = AddressInfo(test_address, test_addresses, CURRENCY_NBT)
print "Updating address snapshot..."
if a.update_outputs():
    write_address_info(a)
    git_update(my_git)
print "Checking other channels..."
sync_multiple(a)
test_recipient = "B5Zi5XJ1sgS6mWGu7bWJqGVnuXwiMXi7qj"

print nbtutil.create_raw_transaction("1000", a, test_recipient)

print "Done."
