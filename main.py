import subprocess
import os
import json
from decimal import Decimal

def call_rpc(args):
    nud_path = 'nud'
    call_args = [nud_path] + args

    return subprocess.check_output(call_args)

CURRENCY_NBT = 0
CURRENCY_NSR = 1
CURRENCY_BTC = 2

class Address:
    def __init__(self, addr, unit):
        self.address = addr
        self.spendable = []
        self.unit = unit
        self.last_block = 0

        spendable = []

        addr_file_path = os.path.join("./addresses",addr)

        if os.path.isfile(addr_file_path):
            with open(addr_file_path,"r") as f:
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
    def get_spendable(self):
        return self.spendable

    def update(self):
        pass

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

a = Address("BT9AWq9r1i6kghZc6LtrvNb2wRFh7JLCdP", CURRENCY_NBT)
for s in a.get_spendable():
    print "    txid:",s[0]
    print "  Amount:",s[1]

print a.get_spend_info("11.1")
print create_raw_transaction("11.1", a, "testqqqqq")
