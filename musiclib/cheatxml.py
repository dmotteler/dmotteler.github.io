#! python

import sys, os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re
import urllib.request
import itertools as IT
import io

# get the xml for the current list of events and parse it
# use the file in cwd - implies we'll eventually just execute in gitpages/musiclb
evfn = "events.xml"
with open(evfn, "r") as fo:
    xml = fo.read()

# url = "https://dmotteler.github.io/musiclib/events.xml"
# req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
# f = urllib.request.urlopen(req)
# xml = f.read()
# evfn = url
# print("\nread {} bytes from {}".format(len(xml), url))

tree = ET.fromstring(xml)

# make a dict of event dicts, indexed by event yyyymmddhhmm
eventlist = {}
for ev in tree.findall("event"):
    d = ev.attrib
    # get the dtndx, removing it from the event dict. parse into datetime.
    dtndx = d.pop('dtndx')
    dt = datetime.strptime(dtndx, "%Y%m%d%H%M")
    eventlist[dt] = d

print(f"read {len(eventlist)} events from {evfn}")

listchgd = False
oldest = (datetime.now() - timedelta(days=365)).timestamp()

cheatsdir = "../cheats"
_, _, files = next(os.walk(cheatsdir))
cheats = [cheat for cheat in files if cheat.endswith(".html") and os.path.getmtime(f"{cheatsdir}/{cheat}") > oldest]

for cheat in cheats:
    ch = f"{cheatsdir}/{cheat}"
    with open(ch, "r") as fo:
        html = fo.read()
        print(f"\nread {len(html)} bytes from {cheat}")

        # get venue and event time from the event title
        ttarg = '<title id="doctitle">'
        n = html.find(ttarg)
        n2 = html.find('</title>')
        title = html[n + len(ttarg):n2]
        where, when = title.split(" - ")
        print(f"new event is {when} at { where}")
        newevdt = datetime.strptime(when, "%B %d, %Y %I:%M%p")

        # isolate the table body (comprised of song rows)
        n = html.find("<tbody")
        n2 = html.rfind("</tbody>")

        # parse fails if resource key value not in quotes.
        # don't care about it - just remove it.
        text = re.sub(r"&resource.*'", "'", html[n:n2+8])

        # parse the table
        try:
            xml = ET.fromstring(text)
        except Exception as e:
            print(e)
            lineno, column = e.position
            StringIO = io.StringIO
            line = next(IT.islice(StringIO(text), lineno))
            caret = '{:=>{}}'.format('^', column)
            e.msg = '{}\n{}\n{}'.format(e, line, caret)
            print(f"parse failed for {cheat}")
            continue

        # tr data-sid has library song id (sid),
        # tr class has "qtet" if it's a quartet song.
        songlist = []
        qtetSongs = []
        for tr in xml:
            # ignore the header tr - it has no attributes.
            if len(tr.attrib) > 0:
                att = dict(tr.attrib)
                if 'data-sid' in att:
                    sid = att['data-sid']
                qtet = 'qtet' in att['class']

                songlist.append(sid)
                if qtet:
                    qtetSongs.append(sid)

        songlist = ' '.join(songlist)
        qtetSongs = ' '.join(qtetSongs)

        event = {'when': when, 'where':where, 'songlist':songlist, 'qtetSongs':qtetSongs}
        # add cheat to event list. this will replace an existing event
        # at the same date/time.

        if newevdt in eventlist and event == eventlist[newevdt]:
            print(f"ignoring cheat for existing event on {newevdt:%b %d, %Y}")
        elif newevdt in eventlist:
            # event has changed...
            print(f"replacing event def for {newevdt:%b %d, %Y}")
            eventlist[newevdt] = event
            listchgd = True
        else:
            eventlist[newevdt] = event
            listchgd = True

if listchgd:
    # re-create the xml file. rename the old one for backup,
    # at least until we gain some confidence in this new approach.
    backup = f"{evfn}~"
    os.replace(evfn, backup)

    with open(evfn, "w") as fo:
        fo.write('''<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet type="text/xsl" href="eventlist.xsl"?>
<eventlist name="Tuners Event List">
''')
        for dt in sorted(eventlist, reverse=True):
            ev = eventlist[dt]
            dtndx = f"{dt:%Y%m%d%H%M}"
            ev['dtndx'] = dtndx
            if 'qtetSongs' in ev:
                fo.write('  <event where="{where}" when="{when}" dtndx="{dtndx}" songlist="{songlist}" qtetSongs="{qtetSongs}" />\n'.format(**ev))
            else:
                fo.write('  <event where="{where}" when="{when}" dtndx="{dtndx}" songlist="{songlist}" />\n'.format(**ev))

        fo.write("</eventlist>\n")
        fo.close()
        print(f"wrote {len(eventlist)} events to {evfn}")
else:
    print(f"{where} {when} already in {evfn}")
