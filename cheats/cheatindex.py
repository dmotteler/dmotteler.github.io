#! env python

import os, sys
from datetime import datetime as dt

mname = [dt(2020, mo, 1).strftime("%B") for mo in range(1,13)]

# cdir = "C:/cygwin64/home/Del/trygitpages/dmotteler.github.io/cheats"
cdir = "."

html = '''<html><head><title>Tuners Cheats</title>
<style>
body { font-size: 20px; font-weight: bold; }
</style>
</head><body>
'''

_, _, files = next(os.walk(cdir))

reh = {}
for fn in files:
    if not fn.endswith(".html"):
        continue
    if fn == "index.html":
        continue

    pat = "{}/{}".format(cdir, fn)
    with open(pat, "r") as fo:
        data = fo.read()

    targ = "'tabletitle'>"
    n = data.find(targ)
    if n < 0:
        continue

    n += len(targ)
    n2 = data.find("</td>", n)
    titl = data[n:n2]
    if titl == 'Tuners Rehearsal':
        continue

    for m in range(12):
        n = titl.find(mname[m])
        if n > 0:
            n2 = titl.find("202", n)
            dat = titl[n:n2+4]
            d = dt.strptime(dat, "%B %d, %Y").date()
            reh[d] = fn

fo = open("index.html", "w")
fo.write(html)

n = 0
for d in sorted(reh, reverse = True):
    fn = reh[d]
    disp = fn[:-5]
    lin = "<a href='{}'>{}</a><br/>\n".format(fn, disp)
    fo.write(lin)
    n += 1
    if n > 12:
        break

fo.close()

print("Created index.html")
