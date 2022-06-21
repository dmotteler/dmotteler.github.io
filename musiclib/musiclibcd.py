#! env python
'''
    $Id: musiclibcd.py,v 1.1 2022/06/13 01:10:31 dfm Exp dfm $
    $Log: musiclibcd.py,v $
    Revision 1.1  2022/06/13 01:10:31  dfm
    Initial revision


    build shell file to copy training tracks to a folder 
    for CD creation, based on category and voice part.
'''

import os, sys
from xml.etree import ElementTree as ET
from shutil import copyfile
import taglib

# step 1: get song categories and voice parts from command line
parts = ['bass', 'bari', 'lead', 'tenor', 'mix']
cats = ['Christmas', 'Current', 'Old', 'Other', 'PoleCat', 'PoleCatII', 'Show', 'TTS', 'YF2']
wantpart = []
wantcat = []
timeonly = False
nodups = True

for arg in sys.argv[1:]:
    if arg in parts:
        wantpart.append(arg)
    elif arg in cats:
        wantcat.append(arg)
    elif arg == "-n":
        nodups = False
    elif arg == "-t":
        timeonly = True
    else:
        sys.exit("{} not recognized.".format(arg))

if len(wantpart) == 0 or len(wantcat) == 0:
    print('\nAt least one part and one category must be specified. Choose part from')
    print("\n  " + ", ".join(parts))
    print('\nand category from')
    print("\n  " + ", ".join(cats))
    print('\nMore than one part and more than one category may be given.')
    print('''
A CD can usually hold 70-80 minutes of playing time. If the
reported total time is more than that, manually split up
the folder contents, moving the files into subfolders so that
each subfolder will fit on a CD. Also remove any tracks you
don't want at this time.

I used Windows Media Player to burn the CDs. It has a burn 
panel, and you can drag-and-drop files into that panel. Then
select "start burn". Repeat for each CD.

I had problems with some tracks refusing to burn. Listening
to a little of the track seemed to clear the problem.
''')

    sys.exit()

# step 2: read the current musiclib.xml, copy relevant tracks to folder
mlib = "C:/cygwin64/home/Del/php_ws/musicxml/musiclib.xml"
with open(mlib, "r") as fo:
    lib_xml = fo.read()

tree = ET.XML(lib_xml)

if not timeonly:
    # folder = "_".join(wantcat) + "_" + "_".join(wantpart)
    folder = "_".join(wantcat + wantpart)
    if os.path.exists(folder):
        print("reusing {}".format(folder))
    else:
        os.mkdir(folder)
        print("Created folder {}".format(folder))

fromdir = "G:/My Drive/Tuners Music/Tracks"
playtime = 0

for el in tree:
    cats = el.findall("category")
    keep = False
    for cat in cats:
        keep = keep or cat.text in wantcat

    if keep:
        trax = el.findall("tracks")
        path = ""
        for track in trax:
            voices = track.findall("voice")
            for voice in voices:
                if voice.attrib["voice"] in wantpart:
                    # voice path is relative to Tracks - i.e., has part/filename
                    _, fn = os.path.split(voice.attrib["path"])
                    if nodups and (" no " in fn or "Missing" in fn):
                        continue
                    fromfil = "{}/{}".format(fromdir, voice.attrib["path"])
                    if not timeonly:
                        tofil = "{}/{}".format(folder, fn)
                        copyfile(fromfil, tofil)

                    tags = taglib.File(fromfil)
                    if 'TITLE' in tags.tags and tags.tags['TITLE'][0] != "":
                        tit = tags.tags['TITLE'][0]
                    else:
                        tit = fn
                    mins, sec = divmod(tags.length, 60)
                    print("{:2}:{:02} {}".format(mins, sec, tit))
                    playtime += tags.length

mins, sec = divmod(playtime, 60)
print("{:2}:{:02} total playing time".format(mins, sec))
