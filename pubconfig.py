import os

#ADDRESS: Multisig address
#ADDRESSESS: Constituents of the Multisig address
#These scripts can only track 1 address for now
ACCOUNT = "FLOT NBT multisig"
ADDRESS = "BqyRzFtWXDmjxrYpyJD42MLE5xc8FrB4js"
ADDRESSES = set(["BHaPLPkrd6ZaJV9Kj3pykwDz76YVgNtkvN", "BKV6t6mw23n1puZUeefY56wZjqcQjvEBKH","BCtHqEGDjrc5sZXJogpxdUDhMcokZunXZs", "BAg28y78t2FyQKsWuFoTpHFuXdFjMyGeCs", "BTR6mGmw16fWpigLh8YZ3GRnfc3EZSSqgD"])
PUBKEYS = ["034b0bd0f653d4ac0a2e9e81eb1863bb8e5743f6cb1ea40d845b939c225a1a80ff","02a144af74d018501f03d76ead130433335f969772792ec39ce389c8a234155259","03661a4370dfcfbcea25d1800057220f4572b6eecab95bb0670e8676a9e34451dc","0234139729dd413c84a71a0bfd6f236790be861b37311cef3240277c940e4b0c07","02547427fc2ea3a0ab9ef70f5e1640ff5112b113f65696948f992bd0770b942571"]
SIGN_THRESHOLD = 3

#URLs of folders from which to download address snapshots (spendable outputs etc)
#Format should be like this:
#REFERENCE_URLS = {"foo" : "https://bar", "foo2" : "https://bar2", "foo3" : "https://bar3"}
REFERENCE_URLS = {"dc-tcs" : "https://raw.githubusercontent.com/dc-tcs/flot-operations/master",
        "jooize" : "https://raw.githubusercontent.com/jooize/flot-operations/master",
        "Lamz0rNewb" : "https://raw.githubusercontent.com/Lamz0rNewb/flot-operations/master"}

