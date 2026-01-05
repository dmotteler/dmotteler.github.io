#! python

import sys, os
import xml.etree.ElementTree as ET
from datetime import datetime
import re

# fn of cheat to add is argv[1]
fn = sys.argv[1]
with open(fn, "r") as fo:
    html = fo.read()
    print(f"read {len(html)} bytes from {fn}")

    # get venue and event time from the event title
    ttarg = '<title id="doctitle">'
    n = html.find(ttarg)
    n2 = html.find('</title>')
    title = html[n + len(ttarg):n2]
    where, when = title.split(" - ")
    print(when, where)
    newevdt = datetime.strptime(when, "%B %d, %Y %I:%M%p")
    dtndx = f"{newevdt:%Y%m%d%H%M}"

    # isolate the table body (comprised of song rows)
    n = html.find("<tbody")
    n2 = html.rfind("</tbody>")

    # parse fails due to resource key value not in quotes.
    # don't care about it - just remove it.
    text = re.sub(r"&resource.*'", "'", html[n:n2+8])

    # parse the table
    xml = ET.fromstring(text)

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
    # print(f'dtndx="{dtndx}" where="{where}" when="{when}" songlist="{songlist}" qtetSongs="{qtetSongs}"')

    newevent = {'when': when, 'where':where, 'songlist':songlist, 'qtetSongs':qtetSongs}

    # get the current list of events from the git repository and parse it
    # evfn = os.path.expanduser("~/gitpages/musiclib/events.xml")
    evfn = os.path.expanduser("/srv/www/htdocs/musiclib/events.xml")
    tree = ET.parse(evfn)

    # make a dict of event dicts, indexed by event yyyymmddhhmm
    eventlist = {}
    isrepl = None
    for ev in tree.getroot().findall("event"):
        d = ev.attrib
        # get the dtndx, removing it from the event dict. parse into datetime.
        dt = datetime.strptime(d.pop('dtndx'), "%Y%m%d%H%M")
        eventlist[dt] = d

        # if new event is within 4 hours of existing one, assume
        # the time got changed. new event will be added, old one removed.
        diff = abs(newevdt - dt).seconds
        if not isrepl and newevdt != dt and abs(newevdt - dt).seconds < 4 * 3600:
            print(f"new {newevdt} exist {dt} diff {diff}")
            isrepl = dt

    # add new event to event list. this will replace an existing event 
    # at the same date/time.
    listchgd = False
    if newevdt not in eventlist or eventlist[newevdt] != newevent:
        eventlist[newevdt] = newevent
        listchgd = True
        print("added event")

    if isrepl:
        eventlist.pop(isrepl)
        listchgd = True
        print(f"removed {isrepl}")

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
                dt = f"{dt:%Y%m%d%H%M}"
                ev['dtndx'] = dt
                if 'qtetSongs' in ev:
                    fo.write('  <event where="{where}" when="{when}" dtndx="{dtndx}" songlist="{songlist}" qtetSongs="{qtetSongs}" />\n'.format(**ev))
                else:
                    fo.write('  <event where="{where}" when="{when}" dtndx="{dtndx}" songlist="{songlist}" />\n'.format(**ev))


            fo.write("</eventlist>\n")
            fo.close()
            print(f"wrote {len(eventlist)} events to {evfn}")
    else:
        print(f"{where} {when} already in {evfn}")
