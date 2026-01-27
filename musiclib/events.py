#!/usr/bin/python
'''
    $Id: events.py,v 1.6 2022/10/22 19:39:38 dfm Exp $
    $Log: events.py,v $
    Revision 1.6  2022/10/22 19:39:38  dfm
    implement -f and -u options
    fix the handling of obsolete gdids
    improve the messages listed

    Revision 1.5  2022/07/18 22:54:38  dfm
    print fn in cdir loop

    Revision 1.4  2022/07/05 22:45:26  dfm
    complete overhaul to make xml loads more like the .js version


    Create list of events by parsing cheat files.
    All cheats from the github cheats folder are parsed,
    and other xml event lists and zip files may be included.
    Also, a folder name may be given, to include cheat htmls
    from that folder.

    a list of songs by category, with last time and number of times performed, is output,
    unless an xml file is requested.

    the events will be saved to an xml file, if the -x file option is given.

'''

import os, sys
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
import getopt
import zipfile
import load_config

musiclib = {}

config = load_config.load_config("obs")

# load map of old gdid => new gdid
obsgdid = config.config['obsgdid']

def loadlib(lib_xml):
    global musiclib

    musiclib['cats'] = {}
    musiclib['songs'] = {}
    musiclib['bygdid'] = {} # map gdid to the sid it belongs to (several gdids to an sid)
    musiclib['byname'] = {} # map name to the sid(s) it belongs to

    with open(lib_xml, "r") as lib:
        xml = lib.read()

    tree = ET.XML(xml)
    for songel in tree:
        sid = songel.attrib['id']

        song = {}
        name = songel.get('name')
        song['name'] = name

        # add song to the byname list (may have more than one sid...)
        if song['name'] not in musiclib['byname']:
            musiclib['byname'][name] = []
        musiclib['byname'][name].append(sid)

        aliasfor = songel.get('aliasfor')
        # if this song element just gives another name for another song,
        # all other attributes must come from that song
        if aliasfor:
            song['aliasfor'] = aliasfor

        else:
            for subel in songel:
                if subel.tag == "category":
                    cat = subel.text
                    if not 'category' in song:
                        song['category'] = []
                    song['category'].append(cat)
                    if cat not in musiclib['cats']:
                        musiclib['cats'][cat] = set()
                    musiclib['cats'][cat].add(song['name'])

                elif subel.tag == "sheet":
                    song['sheet'] = {}
                    atts = dict(subel.items())
                    for att in atts:
                        val = subel.get(att)
                        song['sheet'][att] = val

                    gdid = atts['gdid']
                    musiclib['bygdid'][gdid] = sid

                elif subel.tag == "tracks":
                    song['tracks'] = {}
                    voice = {}
                    for voiceel in subel:
                        atts = dict(voiceel.items())
                        voice = atts.pop('voice')
                        song['tracks'][voice] = atts
                        gdid = atts['gdid']
                        musiclib['bygdid'][gdid] = sid
                else:
                    song[subel.tag] = subel.text

        musiclib['songs'][sid] = song

    if False:
        for cat in sorted(musiclib['cats']):
            print(cat)
            for nam in sorted(musiclib['cats'][cat]):
                print("  {}".format(nam))

        print()

    if False: # songs in sid order
        for sid in sorted(musiclib['songs']):
            song = musiclib['songs'][sid]
            print("\n{} {}".format(sid, song['name']))
            for k in song:
                print("  {}: {}".format(k, song[k]))
        print()

    if False: # songs in name order
        for sid in sorted(musiclib['songs'], key=lambda x: musiclib['songs'][x]['name']):
            song = musiclib['songs'][sid]
            print("\n{} {}".format(sid, song['name']))
            for k in song:
                print("  {}: {}".format(k, song[k]))

    if False:
        # sid = '1178' # Seven Bridges Road
        sid = '1011' # Breaking Up
        song = musiclib['songs'][sid]
        print("\n{} {}".format(sid, song['name']))
        for k in song:
            if k == "sheet":
                out = ", ".join("{}: {}".format(l, song[k][l]) for l in song[k])
                print("  {}: {}".format(k, out))
            elif k == "tracks":
                for v in song[k]:
                    out = ", ".join("{}: {}".format(l, song[k][v][l]) for l in song[k][v])
                    print("  {}: {}".format(v, out))
            else:
                print("  {}: {}".format(k, song[k]))

    return musiclib

evlist = {}
evmtime = {} # mod time of source file for event - latest wins

def parsecheat(lines, fn, musiclib):
    songlist = []
    qtetSongs = []

    title = ""
    n1 = lines.find('<title')
    if n1 > 0:
        n1 = lines.find(">", n1) + 1
        n2 = lines.index('</title')
        title = lines[n1:n2]

    if title != "" and " - " in title:
        # print("from <title> {}".format(title))
        tflds = title.replace("_", "").replace(":", "").replace(" @ ", " ").split(" - ")
        ven = tflds[0]
        tim = tflds[-1]
        if not tim.endswith("PM") and not tim.endswith("AM"):
            tim += " 0700PM"

        try:
            # print("1 {}".format(tim))
            dt = datetime.strptime(tim, "%B %d, %Y %I%M%p")
            dtndx = dt.strftime("%Y%m%d%H%M")
            when = dt.strftime("%B %d, %Y %I:%M%p")
            # print("1 {} {}".format(dtndx, when))
        except Exception as e:
            try:
                dt = datetime.strptime(tim, "%b %d, %Y %I%M%p")
                dtndx = dt.strftime("%Y%m%d%H%M")
                when = dt.strftime("%B %d, %Y %I:%M%p")
                # print("2 {} {}".format(dtndx, when))
            except Exception as e:
                print(e)
                title = ""

    elif " - " in fn:
        ven, tim = fn[:-5].replace("_", "").replace(":", "").split(" - ")
        # print(" >>> from fn {} {}".format(ven, tim))
        if not tim.endswith("PM"):
            tim += " 0700PM"

        try:
            # print("2 {}".format(tim))
            dt = datetime.strptime(tim, "%B %d, %Y %I%M%p")
            dtndx = dt.strftime("%Y%m%d%H%M")
            when = dt.strftime("%B %d, %Y %I:%M%p")
            # print("3 {} {}".format(dtndx, when))
        except:
            title = ""

    else:
        # print("skipping {} - can't find date?".format(fn))
        return

    if title == "":
        # print("skipping {} - can't find title?".format(fn))
        return

    # split the sheet into rows
    songrows = lines.split('<tr')

    # toss everything before the first <tr
    songrows.pop(0)

    rownum = -1
    # print("{} songrows.".format(len(songrows)))
    for songrow in songrows:
        # ignore <tr if not a song row
        if "evtitl" in songrow or "butts" in songrow:
            continue
        if 'partsel' in songrow or "colspan" in songrow:
            continue
        if songrow.startswith("><th"):
            continue

        isqtet = "qtet" in songrow

        rownum += 1
        # print(rownum, songrow[:70])

        # the most foolproof way of getting the song name
        # for songs for which we have tracks is to find
        # the song for each gdid.
        trax = songrow.split("?id=")

        if len(trax) > 1:
            # this row has tracks. toss everything up to first id
            trax.pop(0)

            # print("{} tracks".format(len(trax)))
            for track in trax:
                # track starts with gdid. find its end.
                n = track.find('&amp;res')
                if n < 0:
                    n = track.find("'>")
                if n < 0:
                    n = track.find('">')
                if n < 0:
                    sys.exit("couldn't find end of gdid in {} (row {} of {})".format(track, rownum, fn))

                # isolate it, and get the associated song name
                sid = None
                gdid = track[:n]
                if gdid in musiclib['bygdid']:
                    sid = musiclib['bygdid'][gdid]
                elif gdid in obsgdid:
                    gdid = obsgdid[gdid]

                    if gdid in musiclib['bygdid']:
                        sid = musiclib['bygdid'][gdid]
                else:
                    if not "fid" in gdid:
                        print("gdid {} not in bygdid, from {} row {}".format(gdid, fn, rownum))
                    continue

                # add the song id to the song list, if it's not there
                if sid and not sid in songlist:
                    songlist.append(sid)

                    if isqtet:
                        # if flagged as qtet, also add to list of quartet songs
                        qtetSongs.append(sid)

        else:
            # this row has no tracks. split the row by <td.
            # the next-to-last cell is either just the song name or
            # a collection of divs containing track refs (handled above). a div
            # may not have a gdid if we don't have a track for that voice,
            # but the song will be in the songlist for those that do.
            # we only want the song in the list once, so we can ignore those without tracks.

            tds = songrow.split("<td")
            if len(tds) < 4:
                # print("\n{} {} {}".format(fn, rownum, tds))
                continue
            
            # early sheets had start time in last column
            cell = tds[-3] if ":" in tds[-1] else tds[-2]
            n1 = cell.find(">") + 1
            if n1 >= 0:
                n2 = cell.find("<", n1)
                if n2 > 0:
                    song = cell[n1:n2].strip()
                    # print("n1 {} n2 {} cell |{}| song <{}>".format(n1, n2, cell, song))
                else:
                    print("couldn't isolate song in <{}>".format(songrow))
                    continue

                song = stripsong(song)

                if song == "Caroline_2":
                    song = "Caroline"

                if song not in musiclib['byname']:
                    print("song {} not in byname? Bye! {} {} {}".format(song, fn, rownum, songrow[:70]))
                    sys.exit()

                # add the song id to the song list, if it's not there
                songid = musiclib['byname'][song][0]
                if not songid in songlist:
                    songlist.append(songid)

                    if isqtet:
                        # if flagged as qtet, also add to list of quartet songs
                        qtetSongs.append(songid)

    ev = {'when': when, 'where': ven, 'songlist': songlist, 'qtetSongs': qtetSongs }
    return dtndx, ev

def stripsong(song):
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

    return song.strip()

def eventxml(xfile, evlist, musiclib, brief):
    eventlist = "Tuners Event List"
    root = ET.Element("eventlist", attrib={'name': eventlist})

    for dtndx in sorted(evlist, reverse=True):
        if dtndx.startswith("20200321"):
            continue # show songlist that never was real
        ev = evlist[dtndx]

        venue = ev['where']
        evdate = ev['when']
        eventatts = {"where": venue, "when": evdate, "dtndx": dtndx}
        if brief:
            eventatts['songlist'] = " ".join(ev['songlist'])
            if 'qtetSongs' in ev and len(ev['qtetSongs']) > 0:
                eventatts['qtetSongs'] = " ".join(ev['qtetSongs'])

        eventel = ET.SubElement(root, "event", attrib=eventatts)

        if not brief:
            for sid in ev['songlist']:
                songname = musiclib['songs'][sid]['name']
                songatts = {"name": songname, "sid": sid}
                if 'qtetSongs' in ev and sid in ev['qtetSongs']:
                    songatts['qtet'] = 'y'
                songel = ET.SubElement(eventel, "song", attrib=songatts)

    sl = ET.tostringlist(root, encoding="unicode")
    lines = []
    lines.append("""<?xml version="1.0" encoding="utf-8"?>\n""")
    lines.append("""<?xml-stylesheet type="text/xsl" href="eventlist.xsl"?>\n""")

    leveltags = []

    t = sl.pop(0).rstrip()
    line = [t]
    lastwastag = t.startswith("<")
    assert lastwastag, "first line in writexml not <tag, but {}".format(t)

    # push <tag onto leveltags
    leveltags.append(t)

    putoutline = False
    while len(sl) > 0:
        t = sl.pop(0).rstrip()

        if putoutline:
            nind = len(leveltags)
            # if this line will dedent, adjust now, pop later.
            if t.startswith("</"):
                nind -= 1
            # start a new line, indented by tag level
            line = ["  " * nind, t]
        else:
            line.append(t)

        if t == ">":
            if lastwastag:
                # this just closes the previous <tag line - next will be tag text
                putoutline = False
                poptag = False
            else:
                # this closes an element with children. put line out, but don't pop tag
                putoutline = True
                poptag = False
        elif t == " />":
            # end of closed element. put out line, pop tag
            putoutline = True
            poptag = True
        elif t.startswith("</"):
            if t.endswith(">"):
                # this is </tag> - closes complex tag. put line out, pop tag.
                putoutline = True
                poptag = True
            else:
                raise UserWarning("looks like </tag with no > - didn't expect it! {}".format(t))
        elif t.startswith("<"):
            # this is <tag with no > - push tag, don't put out line
            leveltags.append(t)
            putoutline = False
            poptag = False
        else:
            # no < or > - don't put out line, or pop tag
            putoutline = False
            poptag = False

        if poptag:
            leveltags.pop()

        if putoutline:
            line.append("\n")
            lines.append("".join(line))

        lastwastag = t.startswith("<")

    with open(xfile, "w", encoding="utf-8") as xo:
        for l in lines:
            xo.write(l)

    print("Wrote {} events to {}".format(len(evlist), xfile))

def loadxml(fn):
    global evlist, evmtime, musiclib

    nadd = 0
    with open(fn, "r") as elist:
        xml = elist.read()
        tree = ET.XML(xml)
        for ev in tree:
            songlist = []
            qtetSongs = []

            dtndx = ev.attrib['dtndx']
            when = ev.attrib['when']
            where = ev.attrib['where']
            if 'songlist' in ev.attrib:
                songlist = ev.attrib['songlist'].split(" ")
                if 'qtetSongs' in ev.attrib:
                    qtetSongs = ev.attrib['qtetSongs'].split(" ")
            else:
                for sel in ev.findall("song"):
                    song = sel.attrib["name"]
                    sid = sel.attrib["sid"]
                    songlist.append(sid)
                    if 'qtet' in sel.attrib:
                        qtetSongs.append(sid)

            ev = {'when': when, 'where': where, 'songlist': songlist }
            if len(qtetSongs) > 0:
                ev['qtetSongs'] = qtetSongs
            
            mtim = datetime.fromtimestamp(os.path.getmtime(fn))
            if dtndx not in evlist or mtim > evmtime[dtndx]:
                evlist[dtndx] = ev
                evmtime[dtndx] = mtim 
                nadd += 1

    print("Added {} events from {}".format(nadd, fn))

def loadzip(zfn):
    global evlist, evmtime, musiclib

    print("Loading {}".format(zfn))

    zf = zipfile.ZipFile(zfn, "r")
    # for each archive element...
    for info in zf.infolist():
        # just skip the folder entries
        if info.is_dir():
            continue

        fn = info.filename

        # read the element and parse it 
        if not fn.endswith(".html"):
            continue
        if fn == "index.html":
            continue
        lines = zf.read(info).decode()
        mtim = datetime(*info.date_time)
        # print("read {} lines from zfn {}".format(len(lines), fn))
        dtndx, ev = parsecheat(lines, fn, musiclib)

        if dtndx not in evlist or mtim > evmtime[dtndx]:
            evlist[dtndx] = ev
            evmtime[dtndx] = mtim

            print("  added {}".format(fn))

def expanduser(pat):
    rv = pat
    if pat.startswith("~/"):
        home = os.environ["HOME"].replace("\\", "/")
        rv = "{}/{}".format(home, rv[2:])
    return rv

def usage(msg=None):
    if msg is not None:
        print("\n{}".format(msg))

    print("""\nUsage: {} [-c cat][-d dir][-f][-h][-l lfile][-n][-q qopt][-s sheet][-u][-v venue[,n]][-x xfile][file]
   where:
      -c cat     => name of a category to list. may be given more than once. default is all cats in music lib.
      -d dir     => directory containing cheats. default is github cheats.
      -f         => do full load. new events.xml will be created from cheats in cheatscache,
                    cheatscache/cheats.zip, and cheatscache/gaevents.xml (dev only!)
      -h         => show this help and exit.
      -l lfile   => use lfile for musiclib xml. default is musiclib.xml in current folder.
      -n         => "not brief" songlist is replaced by song subelements including name in xml.
      -q qopt    => quartet song handling. inc => include, only => quartet only. default is skip quartet songs.
      -s sheet   => name of a cheat sheet to process. may be given more than once.
                    default is all html in cheats folder.
      -u         => do normal update (i.e., add new cheat from d dir)
      -v venue[,n] => display most recent event at places matching venue. add , and a number to 
                    show that many most recent events there, default 1.
      -x xfile   => write xml of events list to xfile. default is no xml file.

      "file" may appear more than once, and must end with either .zip or .xml, or name a folder containing
      cheats. The event list will be pre-loaded with the contents. zip files are processed first,
      then xml, and then folders. the -d folder will be done last.

      during loading, events will be overwritten, so last one in wins.

""".format(sys.argv[0]))
    sys.exit(1)

def main():
    global evlist, evmtime

    brief = True
    allevents = False
    doupdate = False
    docats = []
    ddir = "../cheats"
    # lfile = "C:/cygwin64/home/Del/trygitpages/dmotteler.github.io/musiclib/musiclib.xml"
    lfile = "musiclib.xml"
    qtopt = None
    docheats = []
    venues = {}
    xfile = None
    predir = []
    prexml = []
    prezip = []

    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:d:fhj:l:nq:s:uv:x:")
    except getopt.GetoptError as err:
        # print help information and exit:
        usage(str(err)) # will print something like "option -a not recognized"

    if len(opts) == 0 and len(args) == 0:
        usage()

    for o, a in opts:
        if o == "-h":
            usage()
        elif o == "-c":
            docats.append(a)
        elif o == "-d":
            ddir = a
        elif o == "-f":
            allevents = True
        elif o == "-l":
            lfile = a
        elif o == "-n":
            brief = False
        elif o == "-q":
            if a in ['inc', 'only']:
                qtopt = a
            else:
                usage("unrecognized option {} given with -q".format(a))
        elif o == "-s":
            docheats.append(a)
        elif o == "-u":
            doupdate = True
        elif o == "-v":
            n = a.find(",")
            if n > 0:
                ven = a[:n]
                nev = int(a[n+1:])
            else:
                ven = a
                nev = 1
            venues[ven] = nev
        elif o == "-x":
            xfile = a

    for a in args:
        if a.endswith(".xml"):
            prexml.append(a)
        elif a.endswith(".zip"):
            prezip.append(a)
        elif os.path.isdir(a):
            predir.append(a)
        else:
            sys.exit("I don't know what you meant by {}".format(a))

    if not os.path.exists(ddir):
        usage("default cheats folder {} does not exist.".format(ddir))

    predir.append(ddir)

    musiclib = loadlib(lfile)

    if len(musiclib) < 2:
        sys.exit("lib not set up")

    if allevents and doupdate:
        usage("don't give -f and -u together.")

    if allevents or doupdate:
        cdir = "/cygdrive/d/cheatscache"
        if not os.path.exists(cdir):
            usage("cheatscache not found.")

        if len(prezip) > 0 or len(prexml) > 0 or len(docheats) > 0 or len(predir) > 1:
            usage("files/folders must not be given when -f or -u is given.")

        if not xfile:
            xfile = "events.xml"

    if doupdate:
        prexml = ["events.xml"]

    if allevents:
        prezip = ["{}/cheats.zip".format(cdir)]
        prexml = ["{}/gaevents.xml".format(cdir)]
        predir = [cdir, ddir]
        docheats = []

    for z in prezip:
        loadzip(z)

    for x in prexml:
        loadxml(x)

    for d in predir:
        print("Loading {}".format(d))
        _, _, files = next(os.walk(d))

        for fn in files:
            if fn == "index.html":
                continue
            elif not fn.endswith(".html"):
                continue

            pat = "{}/{}".format(d, fn)
            with open(pat, "r") as fo:
                when = ""
                lines = fo.read()
                dtndx, ev = parsecheat(lines, fn, musiclib)
                mtim = datetime.fromtimestamp(os.path.getmtime(pat))

                if dtndx not in evlist or mtim > evmtime[dtndx]:
                    evlist[dtndx] = ev
                    evmtime[dtndx] = mtim
                    print("  added {}".format(fn))

    for fn in docheats:
        when = ""
        with open(fn, "r") as fo:
            lines = fo.read()

        dtndx, ev = parsecheat(lines, fn, musiclib)
        mtim = datetime.fromtimestamp(os.path.getmtime(fn))

        if dtndx not in evlist or mtim > evmtime[dtndx]:
            evlist[dtndx] = ev
            evmtime[dtndx] = mtim

            print("Added {}".format(fn))

    if not xfile:
        print("{} events".format(len(evlist)))

    if False: # set True to list composite input and quit
        for dt in evlist:
            ev = evlist[dt]
            print("{when} {where} {songlist}".format(**ev))
        print("{} events.".format(len(evlist)))
        sys.exit()

    if xfile:
        eventxml(xfile, evlist, musiclib, brief)
        if len(docats) < 1 and len(venues) == 0:
            # -x processed. no cats or venues requested => we're done.
            sys.exit()

    if len(docats) > 0 or len(venues) == 0:
        # list by category if specific categories requested, or
        # list them all by default if no venue lists requested.
        # first, create a list of all songs rehearsed and/or performed,
        # with a list of dates performed for each.
        # songs flagged as qtet are included in both songlist and qtetSongs.
        # we only want to include them in the count if qtopt is "inc" or "only"
        practice = {}
        for dtndx in evlist:
            ev = evlist[dtndx]
            if qtopt == "only":
                if 'qtetSongs' in ev:
                    for songid in ev['qtetSongs']:
                        name = musiclib['songs'][songid]['name']
                        if name not in practice:
                            practice[name] = []
                        practice[name].append(dtndx)
            else:
                # qtopt is not set or is "inc". if qtetSongs is present, we want
                # to add songs it contains only if qtopt is "inc"
                for songid in ev['songlist']:
                    if ('qtetSongs' not in ev) or (songid not in ev['qtetSongs']) or qtopt == "inc":
                        name = musiclib['songs'][songid]['name']
                        if name not in practice:
                            practice[name] = []
                        practice[name].append(dtndx)

        print("{} songs in {} categories".format(len(practice), len(musiclib['cats'])))

        first = datetime.strptime(min(evlist.keys()), "%Y%m%d%H%S")
        last = datetime.strptime(max(evlist.keys()), "%Y%m%d%H%S")
        print("{} events from {:%b %d, %Y} to {:%b %d, %Y}".format(len(evlist), first, last))

        curr = datetime.today().replace(hour=18, minute=0)

        # special-case KTWWS - always sung with LGTA
        ktwws = "Keep The Whole World Singing"
        lgta = "Let's Get Together Again"
        if lgta in practice and ktwws not in practice:
            practice[ktwws] = practice[lgta]

        if len(docats) == 0:
            # no cats requested - do them all,
            # except only do "Christmas", "Old", "Other",
            # "TTS", and "YF2" if specifically requested.
            suppress = [ "Christmas", "Old", "Other", "TTS", "YF2"]
            docats = sorted(musiclib['cats'].keys())
            for cat in suppress:
                docats.remove(cat)
            print("Note: categories {} are shown only if specifically requested.".format(", ".join(suppress)))

        for cat in docats:
            hdrout = False
            for song in sorted(musiclib['cats'][cat]):
                if song in practice:
                    if not hdrout:
                        print("\n{}".format(cat))
                        hdrout = True

                    first = datetime.strptime(min(practice[song]), "%Y%m%d%H%S")
                    last = datetime.strptime(max(practice[song]), "%Y%m%d%H%S")
                    daysago = (curr - last).days
                    num = len(practice[song])
                    print("{:45} {:3} times, last was {:3} days ago on {:%b %d, %Y} ".format(song, num, daysago, last))
                else:
                    if qtopt != "only":
                        if not hdrout:
                            print("\n{}".format(cat))
                            hdrout = True

                        print("{:45} <<<<<<<< none".format(song))

    for venue in venues:
        ven = venue.lower()
        n = 0
        for dtndx in sorted(evlist, reverse=True):
            if ven in evlist[dtndx]['where'].lower():
                ev = evlist[dtndx]
                print("\n{where} - {when}".format(**ev))
                for sid in ev['songlist']:
                    print("  {}".format(musiclib['songs'][sid]['name']))
                n += 1
                if n >= venues[venue]:
                    break
        else:
            # if we did break inner loop, continue (else the inner break exits the outer loop, too)
            continue

if __name__ == "__main__":
    main()
