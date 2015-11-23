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
import chainutils as nbtutil
import sync
import argparse
import config

parser = argparse.ArgumentParser(description="A tool to use git repositories to do multisig")
parser.add_argument("--init", action="store_true")
parser.add_argument("--sync", action="store_true")
parser.add_argument("--nogit", action="store_true")
parser.add_argument("--recipient", type=str, action="store")
parser.add_argument("--amount", type=str, action="store")
cli_args = parser.parse_args()

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

a = sync.AddressSnapshot(config.ADDRESS, config.ADDRESSES)
print "Updating address snapshot..."
if a.sync_with_blockchain():
    sync.write_snapshot(a)
else:
    print "Blockchain sync failed. Going online..."
    b = a
    b.load_from_url()
    if b.last_block > a.last_block:
        a = b
    else:
        print "Remote snapshots not newer. Not updating."
    #if a.load_from_url():
    #    sync.write_snapshot(a)
#print "Checking other channels..."
#sync_multiple(a)
print "Done.\n"

if cli_args.amount and cli_args.recipient:
    print "This is your transaction hex:"
    print nbtutil.create_raw_transaction(cli_args.amount, a, cli_args.recipient)
else:
    print "Please specify recipient and amount!"

