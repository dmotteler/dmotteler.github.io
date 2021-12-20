#! env python
''' convert music library db to xml '''

import os, sys
import sqlite3
from xml.etree import ElementTree as ET
from datetime import datetime

def main():
    dbfile = 'C:/cygwin64/home/Del/php_ws/music/music.db3'

    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    cats = {}
    sql = "SELECT Cat_ID, category FROM validCats"
    resp = c.execute(sql)
    for catid, cat in resp:
        cats[catid] = cat

    voices = {}
    sql = "SELECT Voice_ID, voice FROM validVoices"
    resp = c.execute(sql)
    for vid, voice in resp:
        voices[vid] = voice

    songcats = {}
    sql = "SELECT Song_ID, Cat_ID FROM categories"
    resp = c.execute(sql)
    for sid, cid in resp:
        if sid not in songcats:
            songcats[sid] = []
        songcats[sid].append(cid)

    aliases = {}
    sql = "SELECT aka, Song_ID FROM aliases"
    resp = c.execute(sql)
    for aka, sid in resp:
        if sid not in aliases:
            aliases[sid] = []
        aliases[sid].append(aka)

    tracks = {}
    sql = "SELECT Song_ID, voice, gdid, path, mods FROM songTracks"
    resp = c.execute(sql)
    for sid, voice, gdid, path, mods in resp:
        if sid not in tracks:
            tracks[sid] = {}
        if voice not in tracks[sid]:
            tracks[sid][voice] = []
        tracks[sid][voice].append([gdid, path, mods])

    sheets = {}
    sql = "SELECT Song_ID, gdid, sheet FROM sheetMusic"
    resp = c.execute(sql)
    for sid, gdid, sheet in resp:
        if sid not in sheets:
            sheets[sid] = []
        sheets[sid].append([gdid, sheet])

    songs = {}
    songcols = ["songName", "notes", "location", "key", "pitch", "words", "learn_by",
            "arranger", "composer", "lyricist", "copyright", "crdate", "stockID", "copies", "source", "ordered"]
    sql = "SELECT Song_ID, {} FROM songs".format(", ".join(songcols))
    resp = c.execute(sql)

    for row in resp:
        lrow = list(row)
        sid = lrow.pop(0)
        song = dict(zip(songcols, lrow))
        songs[sid] = song

    print("{} songs.".format(len(songs)))
    
    musiclib = "Tuners Music Library"
    root = ET.Element("musiclib", attrib={'name': musiclib})

    def byname(a):
        return songs[a]['songName']

    for sid in sorted(songs, key=byname):
        s = songs[sid]
        nam = s.pop('songName')
        songatts = {"name": nam, "id": str(sid)}
        songel = ET.SubElement(root, "song", attrib=songatts)
        # print("song {}".format(nam))
        if sid in aliases:
            for aka in aliases[sid]:
                alel = ET.SubElement(songel, "alias")
                alel.text = aka
        if sid in songcats:
            for catid in songcats[sid]:
                catel = ET.SubElement(songel, "category")
                catel.text = cats[catid]
                # print("  cat {}".format(catel.text))

        for prop in sorted(s):
            if s[prop] and s[prop] != "":
                propel = ET.SubElement(songel, prop)
                propel.text = str(s[prop])
                # print("  {} {}".format(prop, propel.text))

        if sid in tracks:
            trackel = ET.SubElement(songel, "tracks")
            # print("    tracks")
            for voice in tracks[sid]:
                for gdid, path, mods in tracks[sid][voice]:
                    tvatts = {"voice": voice, "gdid": gdid, "path": path, "mods": mods}
                    tvel = ET.SubElement(trackel, "voice", attrib=tvatts)
                    # print("    tracks voice {}".format(voice))

        if sid in sheets:
            for gdid, sheet in sheets[sid]:
                shatts = {"gdid": gdid, "sheet": sheet}
                sheetel = ET.SubElement(songel, "sheet", attrib=shatts)
                # print("     sheet {}".format(sheet))

    ''' should use tree.write, but it won't do pretty-print, and
        (more importantly) there's no way to output the stylesheet line.
    '''

    sl = ET.tostringlist(root, encoding="unicode")
    lines = []
    lines.append("""<?xml version="1.0" encoding="utf-8"?>\n""")
    lines.append("""<?xml-stylesheet type="text/xsl" href="musiclib.xsl"?>\n""")

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

    xmlfn = "musiclib.xml"
    with open(xmlfn, "w", encoding="utf-8") as xo:
        for l in lines:
            xo.write(l)

    print("Created {}".format(xmlfn))

if __name__ == "__main__":
    main()
