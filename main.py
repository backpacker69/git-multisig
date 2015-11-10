import subprocess
import os
import json
import time
from decimal import Decimal

test_address ="BT9AWq9r1i6kghZc6LtrvNb2wRFh7JLCdP"

reference_gits =  {"dc-tcs" : "https://github.com/dc-tcs/flot-operations.git",
        "test" : "https://github.com/dc-tcs/flot-operations-test.git"}

my_id = "dc-tcs"
my_git = os.path.join(".","flot-operations")

def call_rpc(args):
    nud_path = 'nud'
    call_args = [nud_path] + args

    return call_args
    #return subprocess.check_output(call_args)

CURRENCY_NBT = 0
CURRENCY_NSR = 1
CURRENCY_BTC = 2

class AddressInfo:
    def __init__(self, addr, unit, root = my_git):
        self.address = addr
        self.spendable = []
        self.unit = unit
        self.last_block = 0
        self.signed_tx = ""
        self.signed_ids = []

        spendable = []

        addr_path = os.path.join(root, addr)

        if os.path.isdir(addr_path):
            addr_unspent_path = os.path.join(addr_path,'unspent')
            addr_tx_path = os.path.join(addr_path,'tx')

            if os.path.isfile(addr_unspent_path):
                with open(addr_unspent_path,"r") as f:
                    l = 0
                    cur_tx = ""
                    for line in f:
                        if l == 0:
                            self.last_block = int(line)
                        elif l % 2 == 1:
                            cur_tx = line.strip()
                        else:
                            spendable.append((cur_tx,Decimal(line)))
                        l += 1
            self.spendable = sorted(spendable, key=lambda x: x[1])

        else:
            if not os.path.exists(addr_path):
                os.makedirs(addr_path)
                #TODO: initialize unspent and tx files
    def get_spendable(self):
        return self.spendable

    def update_outputs(self):
        pass
        #TODO: push to own repo

    def get_spend_info(self, amount):
        sum = Decimal(0)
        amount = Decimal(amount)
        i = 0
        while sum < amount and i < len(self.spendable):
            sum += self.spendable[i][1]
            i += 1
        if sum >= amount:
            #returns (change, list of inputs to spend)
            return (sum - amount, self.spendable[0:i])
        else:
            return None

def create_raw_transaction(amount, my_addr, recipient):
    #Note that amount should be a string
    spend_info = my_addr.get_spend_info(amount)

    st = "'["
    if spend_info:
        s = spend_info[1][0]
        st = st + "{\"txid\": \"" + s[0] + "\", \"vout\": " + str(s[1]) + "}"

        for s in spend_info[1][1:]:
            st = st + ",{\"txid\": \"" + s[0] + "\", \"vout\": " + str(s[1]) + "}"

        st = st + "]'"

        sr = "'{\"" + recipient +"\": " + str(amount) + ", \"" + my_addr.address + "\": " + str(spend_info[0]) + "}'"

        return call_rpc(["create_raw_transaction",st,sr])
    else:
        return None

def sign_raw_transaction(raw_tx):
    return call_rpc(["signrawtransaction", raw_tx])

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

def fetch_data(address_info):
    newest_spendable = address_info.spendable
    current_last_block = address_info.last_block

    for key, value in reference_gits.iteritems():
        git_folder = os.path.join(root_ref,key)

        if not os.path.exists(git_folder):
            subprocess.call(['git', 'clone', value, git_folder])

        try:
            s = subprocess.check_output(['git', '-C', git_folder, 'fetch', '--dry-run'])
            if s == "":
                print "Reference", key, "is up-to-date."
            else:
                subprocess.call(['git', '-C', git_folder, 'fetch'])

            if not os.path.exists(git_folder):
                subprocess.call(['git', 'clone', value, git_folder])

            a = AddressInfo(address_info.address, CURRENCY_NBT, root = git_folder)

            if a.last_block > current_last_block:
                print "Newer snapshot found for spendable from:", key
                newest_spendable = a.spendable
                current_last_block = a.last_block
        except:
            print "Error!"


    return newest_spendable
    #TODO: return latest transaction?

a = AddressInfo(test_address, CURRENCY_NBT)

a.spendable = fetch_data(a)

print a.get_spend_info("11.1")
print create_raw_transaction("11.1", a, "testqqqqq")
