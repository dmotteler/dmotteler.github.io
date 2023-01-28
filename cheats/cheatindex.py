#!/usr/bin/env python

import os, sys
from datetime import datetime as dt

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
    mtim = os.path.getmtime(pat)

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
            if not d in reh:
                reh[d] = []
            reh[d].append((fn, titl, mtim))

        except Exception as e:
            # print("didn't like {}".format(dats))
            pass

fo = open("index.html", "w")
fo.write(html)

n = 0
for d in sorted(reh, reverse = True):
    # get the file with latest mod-time for this date/time
    fn, titl, mtim = max(reh[d], key=lambda x: x[2])
    fn = fn.replace("'", "%27")
    lin = "<a href='{}'>{}</a><br/>\n".format(fn, titl)
    fo.write(lin)
    n += 1
    if n >= 12:
        break

fo.close()

print("Created index.html")
