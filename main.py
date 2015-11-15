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
import urllib2
import os
import json
import time
from decimal import Decimal
import chainutils as nbtutil
import sync
import argparse

parser = argparse.ArgumentParser(description="A tool to use git repositories to do multisig")
parser.add_argument("--init", action="store_true")
parser.add_argument("--sync", action="store_true")
parser.add_argument("--nogit", action="store_true")
cli_args = parser.parse_args()

####Configuration and constants; TODO: use config file
nbtutil.call_rpc.set_nudpath('nud')

test_address = "BT9AWq9r1i6kghZc6LtrvNb2wRFh7JLCdP"
test_addresses = set([]) #TODO: make this None
test_address2 = "BXKidrUiYNgRmDeDX61k6CASEJ2HjM8pUF"
test_addresses2 = set(["B4bABJCsG4nBpk7Hiaw4yX3Fs4LfeS2f16",\
                        "BHaPLPkrd6ZaJV9Kj3pykwDz76YVgNtkvN"])
test_recipient = "B5Zi5XJ1sgS6mWGu7bWJqGVnuXwiMXi7qj"

my_id = "dc-tcs"
my_git = os.path.join(".","flot-operations")
####End Configuration

def sign_and_push(raw_tx, my_addr, list_signed):
    #TODO
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

a = sync.AddressSnapshot(test_address, test_addresses)
print "Updating address snapshot..."
if a.sync_with_blockchain():
    sync.write_snapshot(a)
#print "Checking other channels..."
#sync_multiple(a)

print nbtutil.create_raw_transaction("1000", a, test_recipient)

print "Done."
