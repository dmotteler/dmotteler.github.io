#!/usr/bin/env python
'''
    $Id: muslibup.py,v 1.2 2022/09/01 03:51:02 dfm Exp dfm $
    $Log: muslibup.py,v $
    Revision 1.2  2022/09/01 03:51:02  dfm
    checked for changed fids

    Revision 1.1  2022/09/01 03:20:40  dfm
    Initial revision


    compare tracks info in musiclib.xml to that in mydrive.xml and report differences
'''

import os, sys
from xml.etree import ElementTree as ET
import urllib.request
import urllib.parse

def usage(msg=None):
    if msg:
        print(msg)

    print('''\nUsage: {} [git|dev][dump]
    where:
        if 'git' appears on the command, load musiclib from github, else
           if 'dev' appears, load from from ./musiclib
        if 'dump' appears on the command, list the tracks and sheets data.

'''.format(sys.argv[0]))
    sys.exit()

if len(sys.argv) < 2:
    usage()

dumps = False
fromgit = False

for a in sys.argv[1:]:
    if a == 'git':
        fromgit = True
    elif a == 'dev':
        fromgit = False
    elif a == 'dump':
        dumps = True
    else:
        usage("Unrecoginized argument {}".format(a))

if fromgit:
    url = "https://dmotteler.github.io/musiclib/musiclib.xml"

    # if we don't fake the browser type, git will reject us with a 405 error
    req = urllib.request.Request(url, data=None, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )

    with urllib.request.urlopen(req) as f:
        lib_xml = f.read().decode('utf-8')

    mlib = url
else:
    # use the development musiclib
    mlib = "/var/www/html/musiclib/musiclib.xml"
    with open(mlib, "r") as fo:
        lib_xml = fo.read()

print("\nread {} bytes from {}".format(len(lib_xml), mlib))

libtracks = {}
libsheets = {}

tree = ET.XML(lib_xml)

for el in tree:
    song = el.attrib['name']
    trax = el.findall("tracks")
    if len(trax) > 0:
        for trk in trax:
            voices = trk.findall("voice")
            for vel in voices:
                gdid = vel.attrib['gdid']
                pat = vel.attrib['path']
                # path attr has folder/filename of mp3
                libtracks[pat] = gdid

    shts = el.findall("sheet")
    if len(shts) > 0:
        for sht in shts:
            # sheet attr has simple file name of pdf
            gdid = sht.attrib["gdid"]
            shtpat = sht.attrib["sheet"]
            libsheets[shtpat] = gdid

libtrax = set(libtracks.keys())
if len(libtrax) != len(libtracks):
    print("must have duplicated track path in musiclib? {} tracks, {} trax".format(len(libtracks), len(libtrax)))

libshts = set(libsheets.keys())
if len(libshts) != len(libsheets):
    print("must have duplicated sheet path in musiclib? {} sheets, {} shts".format(len(libsheets), len(libshts)))

print("{} unique tracks paths in musiclib".format(len(libtrax)))
print("{} unique sheet paths in musiclib".format(len(libsheets)))

if dumps:
    print("\n musiclib tracks:")
    for pat in sorted(libtrax):
        print("  {}".format(pat))

    print("\n musiclib sheets:")
    for pat in sorted(libsheets):
        print("  {}".format(pat))

tsxml = "/home/dfm/devel/mydrive.xml"

with open(tsxml, "r") as fo:
    tands_xml = fo.read()
    print("\nread {} bytes from {}".format(len(tands_xml), tsxml))

tands = ET.XML(tands_xml)

tstracks = {}
tssheets = {}

tmt = "Tuners Music/Tracks/"
tmtl = len(tmt)
tmsm = "Tuners Music/sheet music"
tmsml = len(tmsm) + 1

for el in tands:
    # el is a <folder> element. get the folder path rel. to My Drive.
    # only interested in tracks and sheets...

    folder = el.attrib['path']
    if folder.startswith(tmt):
        foldtyp = "t"

        # in tracks, what's left is voice
        voice = folder[tmtl:]

        if voice.startswith("dupes") or voice.startswith("wsntag") or voice.startswith("Lida Rose"):
            print("skipping {}".format(voice))
            continue

    elif folder == tmsm:
        foldtyp = "m"

    else:
        continue

    # for all the <file>s in this <folder>
    for fel in el:
        # fel is a <file> element -
        fid = fel.attrib['id']
        fnam = fel.attrib['name']

        if foldtyp == "t" and not fnam.endswith(".mp3"):
            print("skipping {} in trax".format(fnam))
            continue

        if foldtyp == "m" and not fnam.endswith(".pdf"):
            print("skipping {} in sheets".format(fnam))
            continue

        if foldtyp == "m":
            tssheets[fnam] = fid
        
        elif foldtyp == "t":
            relpat = "{}/{}".format(voice, fnam)
            tstracks[relpat] = fid

print("found {} sheets and {} tracks.".format(len(tssheets), len(tstracks)))

if dumps:
    print("\n  tracksandsheet tracks:")
    for pat in sorted(tstracks):
        voice, fnam = pat.split("/")
        ffid = tstracks[pat]
        print("{}  {} {}".format(voice, fnam, ffid))

    print("\n  tracksandsheet sheets:")
    for pat in sorted(tssheets):
        ffid = tssheets[pat]
        print("{}  {}".format(pat, ffid))

tstrax = set(tstracks.keys())
if len(tstrax) != len(tstracks):
    print("must have duplicated track path in mydrive? {} tracks, {} trax".format(len(tstracks), len(tstrax)))

tsshts = set(tssheets.keys())
if len(tsshts) != len(tssheets):
    print("must have duplicated sheet path in mydrive? {} sheets, {} shts".format(len(tssheets), len(tsshts)))

print("\n{} tracks appear in both musiclib.xml and tracksandsheets.xml!".format(len(libtrax & tstrax)))
print("{} sheets appear in both musiclib.xml and tracksandsheets.xml!".format(len(libshts & tsshts)))

ntdiff = 0
ntsame = 0

for pat in sorted(libtracks):
    if pat in tstracks:
        if libtracks[pat] == tstracks[pat]:
            ntsame += 1
        else:
            ntdiff += 1
            print("track fid changed for {}:\n  lib {}\n   ts {}".format(pat, libtracks[pat], tstracks[pat]))

print("{} track fids agreed, {} were different.".format(ntsame, ntdiff))

nsdiff = 0
nssame = 0
for pat in sorted(libsheets):
    if pat in tssheets:
        if libsheets[pat] == tssheets[pat]:
            nssame += 1
        else:
            nsdiff += 1
            print("sheet fid changed for {}:\n  lib {}\n   ts {}".format(pat, libsheets[pat], tssheets[pat]))

print("{} sheet fids agreed, {} were different.".format(nssame, nsdiff))

notOnGD = libtrax - tstrax
if len(notOnGD) > 0:
    print("\nmusiclib refers to these tracks that aren't on Google Drive??")
    for x in sorted(notOnGD):
        print(x)
else:
    print("\nfound all musiclib tracks on Google Drive")

needThese = tstrax - libtrax
if len(needThese) > 0:
    def bysong(a):
        v, s = a.split("/")
        t = s.split("-")
        if len(t) > 1:
            return "".join(t[1:])
        else:
            return t[0]

    print("\nadd these tracks to musiclib.xml")
    for pat in sorted(needThese, key=bysong):
        voice, fnam = pat.split("/")
        ffid = tstracks[pat]
        print('      <voice gdid="{}" mods="{}" path="{}" voice="{}" />'.format(ffid, voice, pat, voice))

notOnGD = libshts - tsshts
if len(notOnGD) > 0:
    print("\nmusiclib refers to these sheets that aren't on Google Drive??")
    for x in sorted(notOnGD):
        print(x)
else:
    print("\nfound all musiclib sheets on Google Drive")

needThese = tsshts - libshts
if len(needThese) > 0:
    print("\nadd these sheets to musiclib.xml")
    for sht in sorted(needThese):
        ffid = tssheets[sht]
        print('      <sheet gdid="{}" sheet="{}" />'.format(ffid, sht))
