import subprocess
import urllib2
import chainutils as nbtutil
from decimal import Decimal
import os
import time

GIT_ENABLED = 1
DATA_DIR = os.path.join(".","flot-operations")
REFERENCE_URLS = {"dc-tcs" : "https://raw.githubusercontent.com/dc-tcs/flot-operations/master"} 

#import config
#TODO: load above from config file and sanitize
#      e.g. assume urls never end with /

class AddressSnapshot:
    #Snapshot of a multisig address

    def load_from_disk(self, root = DATA_DIR):
        addr_path = os.path.join(root, self.address)
        if os.path.isdir(addr_path):
            unspent_path = os.path.join(addr_path,'unspent')
            addr_tx_path = os.path.join(addr_path,'tx')

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

    def load_from_url(self, root = DATA_DIR):
        addr_path = os.path.join(root, self.address)
        if not os.path.exists(addr_path):
            os.makedirs(addr_path)
        elif not os.path.isdir(addr_path):
            #TODO: give error
            return None

        best_height = 0
        best_page = "0\n"
        best_id = ""

        for key,u in REFERENCE_URLS.iteritems():
            url_unspent = u + self.address + "/unspent" #TODO: make this more robust
            response = urllib2.urlopen(url_unspent)
            unspent_page = response.read()

            height = int(unspent_page.split()[0])
            if height > best_height:
                best_height = int(unspent_page.split()[0])
                best_page = unspent_page
                best_id = key
        print best_page

        if best_height > 0:
            print "Newest snapshot for", self.address, "found at:", best_id
            with open(os.path.join(path_dir,"unspent"),"w") as f:
                f.write(best_page)
        else:
            #error message etc.
            return None

    def __init__(self, address, addresses, root = DATA_DIR):
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
            self.load_from_url()

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

def git_update(git_folder):
    subprocess.call(['git', '-C', git_folder, 'add', '-A'])
    subprocess.call(['git', '-C', git_folder, 'commit', '-m', str(time.time())])
    subprocess.call(['git', '-C', git_folder, 'push', 'origin', 'master'])

def write_snapshot(address_snapshot):
    path = os.path.join(DATA_DIR, address_snapshot.address)
    if os.path.isdir(path):
        with open(os.path.join(path, "unspent"), 'w') as f:
            f.write(str(address_snapshot.last_block) + "\n")
            for t in address_snapshot.unspent:
                f.write(t[0] + "\n")
                f.write(str(t[1]) + "\n")
                f.write(str(t[2]) + "\n")
    if GIT_ENABLED:
        git_update(DATA_DIR)
