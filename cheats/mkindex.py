#! env python

import os, sys

fromdir = "C:/cygwin64/home/Del/trygitpages/dmotteler.github.io/cheats"
_, _, files = next(os.walk(fromdir))

cheats = []
for f in files:
    if f != "index.html":
        if f.endswith(".html"):
            cheats.append(f)

head = '''<html><head><title>Tuners Cheats</title>
<style>
body { font-size: 20px; font-weight: bold; }
</style>
</head><body>
'''

ofn = "index.html"
with open(ofn, "w") as fo:
    fo.write(head)
    for f in cheats:
        fo.write("<a href='{}'>{}</a><br/>\n".format(f, f))

print("Created {}".format(ofn))
