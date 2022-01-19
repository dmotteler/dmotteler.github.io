#! env python
''' compare sheets info in musiclib.xml to that in "Tuners Music/sheet music" and report differences '''

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
req = urllib.request.Request(url, data=None, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
)

with urllib.request.urlopen(req) as f:
    lib_xml = f.read().decode('utf-8')

libsongs = {}
libshts = set()
tree = ET.XML(lib_xml)
for el in tree:
    song = el.attrib['name']
    libsongs[song] = []
    shts = el.findall("sheet")
    if len(shts) > 0:
        for sht in shts:
            pat = sht.attrib['sheet']
            libsongs[song].append(pat)
            libshts.add(pat)

if False:
    for song in libsongs:
        if len(libsongs[song]) > 0:
            print(song, libsongs[song])
    sys.exit()

gdshts = set()
nsh = 0
_, _, files = next(os.walk("G:/My Drive/Tuners Music/sheet music"))
for fn in files:
    if fn.lower().endswith(".pdf"):
        gdshts.add(fn)
        nsh += 1

print("\n{} sheets appear in both musiclib.xml and sheet music!".format(len(libshts & gdshts)))

if libshts == gdshts:
    print("musiclib is up to date!")

else:
    if len(libshts - gdshts) > 0:
        print("\nmusiclib refers to these sheets that aren't on Google Drive??")
        for x in libshts - gdshts:
            print("  {}".format(x))

    if len(gdshts - libshts) > 0:
        print("\nGoogle Drive files not in musiclib - add to musiclib.xml?")
        for pat in gdshts - libshts:
            print("  {}".format(pat))
