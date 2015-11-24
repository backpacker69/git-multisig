This is a command line tool, and you'll need to have nud running (or nu -server). There's very little error handling or robustness in the scripts, but enough for some actual use.

There are some basic personal settings in **config.py**. To start, you can rename **config-example.py** to **config.py**. Updates to the code will change config-example.py and pubconfig.py but not config.py.

## 1. Settings - Git
Skip this part if you don't know how to use git.

`GIT_ENABLED = 0`

To use git set this to 1. git is mainly used to synchronize with your own "flot-operations" repository, which maintains "snapshots" of the tracked address; I recommend to fork from mine: https://github.com/dc-tcs/flot-operations , and post the url here.

Then, you can use the parameter MY_GIT to set the address of your repository for pushing.

Note that in this script git is basically called just from the command line; not a good idea if you're using windows or OSX, because I don't know how git works on those. 

## 2. Set RPC port, username and password

```
RPC_PORT = 14002
RPC_USERNAME = "XXXXX"
RPC_PASSWORD = "YYYYY"
```

The script makes calls using jsonrpc. Remember to set rpcuser and rpcpassword in nu.conf, and use the same strings in place of XXXXX and YYYYY. Most likely the port is 14002 for the mainnet and 15002 for the testnet.

There are some other shared settings in **pubconfig.py** like the following:

```
ADDRESS = "BqyRzFtWXDmjxrYpyJD42MLE5xc8FrB4js"
ADDRESSES = set([])
PUBKEYS = ["034b0bd0f653d4ac0a2e9e81eb1863bb8e5743f6cb1ea40d845b939c225a1a80ff","02a144af74d018501f03d76ead130433335f969772792ec39ce389c8a234155259","03661a4370dfcfbcea25d1800057220f4572b6eecab95bb0670e8676a9e34451dc","0234139729dd413c84a71a0bfd6f236790be861b37311cef3240277c940e4b0c07","02547427fc2ea3a0ab9ef70f5e1640ff5112b113f65696948f992bd0770b942571"]
SIGN_THRESHOLD = 3
```

## 3. How to use

You can use this script running either nud or nu -server. In the latter case, you would still have access to the qt interface.

After setting the above, there's basically only one way to use this script:

`python main.py --recipient RECIPIENT_ADDRESS --amount SEND_AMOUNT`

The script first tries to sync the address balance with the blockchain (or download it from REFERENCE_URLS set in config.py), forms the transaction, and spits out the hex. Use decoderawtransaction to check that the content makes sense.

An example output:

```
$ python main.py --recipient B5Zi5XJ1sgS6mWGu7bWJqGVnuXwiMXi7qj --amount 999.9
Updating address snapshot...
Done.

This is your transaction hex:
010000004e05505601d1c30e31b4dd598332b155d9074f1ed98a75dacb39b1ee5aff5648f28a3ae2ab0000000000ffffffff0298929800000000001976a9140c390f04c4022947b6493cfa5beefa45e306970e88ac48a1a60b000000001976a914f8e77eac0ffff17e4294cdcae6e7b6e3c1fcb4d288ac0000000042
```
