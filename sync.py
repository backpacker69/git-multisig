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
import chainutils as nbtutil
from decimal import Decimal
import os
import time
import json
import config

#import config
#TODO: load above from config file and sanitize
#      e.g. assume urls never end with /

class AddressSnapshot:
    #Snapshot of a multisig address

    def load_from_disk(self, root = config.DATA_DIR):
        #TODO: use json?
        addr_path = os.path.join(root, self.address)
        if os.path.isdir(addr_path):
            unspent_path = os.path.join(addr_path,'unspent')
            addr_tx_path = os.path.join(addr_path,'signers')

            if os.path.isfile(unspent_path):
                with open(unspent_path,"r") as f:
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
                return 1
        return 0

    def load_from_url(self, root = config.DATA_DIR):
        #TODO: handle http errors
        addr_path = os.path.join(root, self.address)
        if not os.path.exists(addr_path):
            os.makedirs(addr_path)
        elif not os.path.isdir(addr_path):
            #TODO: give error
            return 0

        best_height = 0
        best_page = "0\n"
        best_id = ""

        for key,u in config.REFERENCE_URLS.iteritems():
            url_unspent = "/".join([u,self.address,"unspent"])
            response = urllib2.urlopen(url_unspent)
            unspent_page = response.read()

            height = int(unspent_page.split()[0])
            if height > best_height:
                best_height = int(unspent_page.split()[0])
                best_page = unspent_page
                best_id = key

        if best_height > 0:
            print "Newest snapshot for", self.address, "found at:", best_id
            with open(os.path.join(addr_path,"unspent"),"w") as f:
                f.write(best_page)
            self.load_from_disk()
        else:
            #error message etc.
            return 0

    def __init__(self, address, addresses, root = config.DATA_DIR):
        self.address = address
        #The actual multisig address
        
        self.addresses = addresses
        #set([ ... ]) containing constituent addresses of multisig address
        #TODO: None if the address is not really multisig?

        self.unspent = set()
        #Each element is a tuple: txid, amount and vout number 

        self.last_block = 0

        if not self.load_from_disk():
            print "Snapshot of", self.address, "not found on disk."
            if config.GIT_ENABLED:
                #TODO: find better way to do this
                subprocess.call(['git','clone',config.MY_GIT,config.DATA_DIR])
            else:
                self.load_from_url()
            self.load_from_disk()

    def sync_with_blockchain(self):
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
        return flag_change

class TxSnapshot:
    #Work in progress
    def load_from_disk(self, root = config.DATA_DIR):
        #keys: txjson, signed_ids, address, hex
        tx_fp = os.path.join(config.DATA_DIR,'tx')
        with open(tx_fp, 'r') as f:
            ss_json = json.load(tx_fp)

    def load_from_url(self,root = config.DATA_DIR):
        pass

    def __init__(self, signed_ids = set([])):
        self.signed_ids = signed_ids

    def sync_signed(self):
        pass

    def get_json(self):
        pass

    def compare(self, other_snapshot):
        #Detect "same" transaction but with different signers
        if self.txjson.get(u'vout') == other_snapshot.txjson.get(u'vout'):
            if self.inputs == other_snapshot.inputs:
                return 1
        return 0

def git_update(git_folder):
    subprocess.call(['git', '-C', git_folder, 'add', '-A'])
    subprocess.call(['git', '-C', git_folder, 'commit', '-m', str(time.time())])
    subprocess.call(['git', '-C', git_folder, 'push', 'origin', 'master'])

def write_snapshot(address_snapshot):
    path = os.path.join(config.DATA_DIR, address_snapshot.address)
    if os.path.isdir(path):
        with open(os.path.join(path, "unspent"), 'w') as f:
            f.write(str(address_snapshot.last_block) + "\n")
            for t in address_snapshot.unspent:
                f.write(t[0] + "\n")
                f.write(str(t[1]) + "\n")
                f.write(str(t[2]) + "\n")
    if config.GIT_ENABLED:
        git_update(config.DATA_DIR)
