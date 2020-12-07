#! env python

import os, sys
from datetime import datetime
import json

# start each voice with ' ' so we don't match Call, for example
voices = [' bass', ' bari', ' lead', ' tenor', ' mix', ' all', ' full']

evlist = {}

cdir = "C:/cygwin64/home/Del/trygitpages/dmotteler.github.io/cheats"

_, _, files = next(os.walk(cdir))

for fn in files:
    if fn == "index.html":
        continue
    elif not fn.endswith(".html"):
        print("skipping {}".format(fn))
        continue

    songlist = []

    pat = "{}/{}".format(cdir, fn)
    with open(pat, "r") as fo:
        when = ""
        lines = fo.readlines()

        title = ""
        for l in lines:
            n1 = l.find('<title')
            if n1 < 0:
                continue

            n1 = l.find(">", n1) + 1
            n2 = l.index('</title')
            title = l[n1:n2]
            break

        if title != "" and " - " in title:
            # print("from <title> {}".format(title))
            ven, tim = title.replace("_", "").replace(":", "").replace(" @ ", " ").split(" - ")
            if not tim.endswith("PM"):
                tim += " 0700PM"

            try:
                dt = datetime.strptime(tim, "%B %d, %Y %H%M%p")
                dtndx = dt.strftime("%Y%m%d%H%M")
                when = dt.strftime("%B %d, %Y %H:%M")
            except Exception as e:
                try:
                    dt = datetime.strptime(tim, "%b %d, %Y %H%M%p")
                    dtndx = dt.strftime("%Y%m%d%H%M")
                    when = dt.strftime("%B %d, %Y %H:%M")
                except Exception as e:
                    print(e)
                    title = ""

        elif " - " in fn:
            ven, tim = fn[:-5].replace("_", "").replace(":", "").split(" - ")
            print(" >>> from fn {} {}".format(ven, tim))
            if not tim.endswith("PM"):
                tim += " 0700PM"

            try:
                dt = datetime.strptime(tim, "%B %d, %Y %H%M%p")
                dtndx = dt.strftime("%Y%m%d%H%M")
                when = dt.strftime("%B %d, %Y %H:%M")
            except:
                title = ""

        else:
            print("skipping {} - can't find date?".format(fn))
            continue

        if title == "":
            print("skipping {} - can't find title?".format(fn))
            continue

        for l in lines:
            if not "class='key'" in l and not 'class="key"' in l:
                continue
            flds = l.split(">")
            while not flds[0].startswith("<tr class"):
                flds.pop(0)
            flds.pop(0) # <tr
            flds.pop(0) # <td key
            flds.pop(0) # key
            flds.pop(0) # <td

            if flds[0].startswith("<a "):
                flds.pop(0) # <a

            song = flds.pop(0)

            if song.startswith("`") or song.startswith("$") or song.startswith("</tr"):
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
                if n1 > 0 and not song.startswith("O Come"):
                    song = song[:n1]

            song = song.strip()
                
            if not song in songlist:
                songlist.append(song)

        ev = {'when': when, 'where': ven, 'songlist': songlist}
        evlist[dtndx] = ev
        print(dtndx,when,ven)

with open("evlist.json", "w") as fo:
    json.dump(evlist, fo)

print("wrote {} events to evlist.json".format(len(evlist)))
sys.exit()

for dtndx in sorted(evlist):
    print()
    # print(dtndx)
    # print(evlist[dtndx])
    ev = evlist[dtndx]
    print(ev['where'])
    print(ev['when'])
    print(ev['songlist'])
