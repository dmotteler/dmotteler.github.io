#! env python
''' compare tracks info in musiclib.xml to that in Tracks.json and report differences '''

import os, sys
from xml.etree import ElementTree as ET
import json
import urllib.request
import urllib.parse

# mlib = "C:/cygwin64/home/Del/php_ws/musicxml/musiclib.xml"
# with open(mlib, "r") as fo:
    # lib_xml = fo.read()
    # print("read {} bytes from {}".format(len(lib_xml), mlib))

url = "https://dmotteler.github.io/musiclib/musiclib.xml"

# if we don't fake the browser type, git will reject us with a 405 error
req = urllib.request.Request(url, data=None, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
)

with urllib.request.urlopen(req) as f:
    lib_xml = f.read().decode('utf-8')

libsongs = {}
libtrax = set()
tree = ET.XML(lib_xml)
for el in tree:
    song = el.attrib['name']
    libsongs[song] = {}
    trax = el.findall("tracks")
    if len(trax) > 0:
        for trk in trax:
            voices = trk.findall("voice")
            for vel in voices:
                v = vel.attrib['voice']
                pat = vel.attrib['path']
                if v not in libsongs[song]:
                    libsongs[song][v] = []
                libsongs[song][v].append(pat)
                libtrax.add(pat)

print("{} unique paths in musiclib".format(len(libtrax)))

if False:
    for song in sorted(libsongs):
        print(song)
        for voice in sorted(libsongs[song]):
            print("  {}".format(voice))
            for pat in libsongs[song][voice]:
                print("    {}".format(pat))

voices = ['mix', 'bass', 'bari', 'lead', 'tenor']

with open("C:/cygwin64/home/Del/src/devel/Tracks.json") as f:
    sljson = f.read()
    print("read {} bytes for Tracks.json".format(len(sljson)))

jsongs = json.loads(sljson)

tfid = None
voices = ['mix', 'bass', 'bari', 'lead', 'tenor']
for fid in jsongs:
    if jsongs[fid]['name'] == "Tracks":
        tfid = fid
        break

if not tfid:
    sys.exit("never found Tracks?")

trackstrax = {}
for fid in jsongs:
    # get the fid for each voice folder
    if jsongs[fid]['name'] in voices and jsongs[fid]['parentid'] == tfid:
        voice = jsongs[fid]['name']
        # print("found Tracks/{}".format(voice))

        # get path to each track, relative to Tracks
        for ffid in jsongs[fid]['files']:
            song = jsongs[fid]['files'][ffid]
            nam = song['name']
            pat = "{}/{}".format(voice, nam)
            trackstrax[pat] = (voice, ffid)

traxset = set(trackstrax.keys())

print("\n{} tracks appear in both musiclib.xml and Tracks.json!".format(len(libtrax & traxset)))

print("\nmusiclib refers to these tracks that aren't on Google Drive??")
for x in libtrax - traxset:
    print(x)

print("\nadd these tracks to musiclib.xml")
for pat in traxset - libtrax:
    voice, ffid = trackstrax[pat]
    print('<tracks><voice gdid="{}" mods="{}" path="{}" voice="{}" /></tracks>'.format(ffid, voice, pat, voice))
