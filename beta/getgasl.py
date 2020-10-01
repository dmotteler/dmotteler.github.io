#! env python

import os, sys
from datetime import datetime
import json
from tprogclass import TunersProgram

voices = ['bass', 'bari', 'lead', 'tenor', 'mix', 'all']

evlist = {}

if False: # set True to include progs from progcache
    cdir = "C:/cygwin64/home/Del/php_ws/lastperf/progcache"

    _, _, files = next(os.walk(cdir))
    for fn in files:
        if not fn.endswith(".html"):
            continue
        if fn.startswith("perf2020"):
            dts = fn[4:-5]
        elif fn.startswith("reh2020"):
            dts = fn[3:-5]
        else:
            continue

        path = "{}/{}".format(cdir, fn)
        tp = TunersProgram(path)
        if len(tp.rows) < 1:
            continue

        # title is <venue> - <date> | Two Town Tuners
        if tp.title.endswith(" | Two Town Tuners"):
            vendts = tp.title[:-18].split(" - ")
            if len(vendts) != 2:
                print(" >>> what's this? {}".format(vendts))
                continue
            else:
                ven, dts = vendts
                dt = datetime.strptime(dts, "%Y-%b-%d")
        else:
            print(" >>> {} doesn't end with Two Town Tuners?!".format(tp.title))
            continue

        if tp.progstart < datetime(2020, 6, 1):
            continue
        songlist = []
        for row in tp.rows:
            song = row[1].replace("&#039;", "'")

            if song in ["", "-- qtet choice --", "Break"]:
                continue

            n1 = song.find("(")
            n2 = song.find("[")
            if n1 > 0:
                if n2 > 0:
                    song = song[:min(n1, n2)]
                else:
                    song = song[:n1]
            else:
                if n2 > 0:
                    song = song[:n2]

            for v in voices:
                n1 = song.lower().find(v)
                if n1 > 0:
                    song = song[:n1]

            song = song.strip()
            if song not in songlist:
                songlist.append(song)

        ev = {'when': tp.progstart.strftime("%B %d, %Y %H%M%p"), 'where': ven, 'songlist': songlist}
        evlist[tp.progstart.strftime("%Y%m%d")] = ev

cdir = "C:/cygwin64/home/Del/trygitpages/dmotteler.github.io/cheats"

_, _, files = next(os.walk(cdir))

for fn in files:
    if fn == "index.html":
        continue
    elif not fn.endswith(".html"):
        print("skipping {}".format(fn))
        continue

    ven, tim = fn[:-5].split(" - ")
    if not tim.endswith("PM"):
        tim += " 0700PM"
    dt = datetime.strptime(tim, "%B %d, %Y %H%M%p")
    dtndx = dt.strftime("%Y%m%d")
    when = dt.strftime("%B %d, %Y %H:%M")
    songlist = []

    pat = "{}/{}".format(cdir, fn)
    with open(pat, "r") as fo:
        lines = fo.readlines()

        for l in lines:
            if not "class='key'" in l and not 'class="key"' in l:
                continue
            flds = l.split(">")
            flds.pop(0) # <tr
            flds.pop(0) # <td key
            flds.pop(0) # key
            flds.pop(0) # <td

            if flds[0].startswith("<a "):
                flds.pop(0) # <a

            song = flds.pop(0)

            if song.startswith("`") or song.startswith("$"):
                continue

            if song.endswith("</a"):
                song = song[:-3]
            elif song.endswith("</td"):
                song = song[:-4]
            elif song.endswith("\n"):
                song = song[:-1]

            n1 = song.find("(")
            n2 = song.find("[")
            if n1 > 0:
                if n2 > 0:
                    song = song[:min(n1, n2)]
                else:
                    song = song[:n1]
            else:
                if n2 > 0:
                    song = song[:n2]

            for v in voices:
                n1 = song.lower().find(v)
                if n1 > 0:
                    song = song[:n1]

            song = song.strip()
                
            if not song in songlist:
                songlist.append(song)

        ev = {'when': when, 'where': ven, 'songlist': songlist}
        evlist[dtndx] = ev

with open("evlist.json", "w") as fo:
    json.dump(evlist, fo)

print("created evlist.json")
sys.exit()

for dtndx in sorted(evlist):
    print()
    # print(dtndx)
    # print(evlist[dtndx])
    ev = evlist[dtndx]
    print(ev['where'])
    print(ev['when'])
    print(ev['songlist'])
