#! env python

import os, sys
from datetime import datetime as dt

mname = [dt(2020, mo, 1).strftime("%B") for mo in range(1,13)]

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

    targ = '"tabletitle">'
    n = data.find(targ)
    if n < 0:
        targ = "'tabletitle'>"
        n = data.find(targ)
        if n < 0:
            continue

    n += len(targ)
    n2 = data.find("</td>", n)
    titl = data[n:n2]

    n = titl.rfind(" - ")
    if n > 0:
        dats = titl[n+3:]
        try:
            d = dt.strptime(dats, "%B %d, %Y %I:%M%p")
            reh[d] = (fn, titl)
        except Exception as e:
            # print("didn't like {}".format(dats))
            pass

fo = open("index.html", "w")
fo.write(html)

n = 0
for d in sorted(reh, reverse = True):
    fn, titl = reh[d]
    lin = "<a href='{}'>{}</a><br/>\n".format(fn, titl)
    fo.write(lin)
    n += 1
    if n >= 12:
        break

fo.close()

print("Created index.html")
