#! env python

import os, sys
import json

voices = ['mix', 'bass', 'bari', 'lead', 'tenor']

fn = "songlib.json"
with open(fn, "r") as fo:
    txt = fo.read()
    songs = json.loads(txt)

    for nam in sorted(songs):
        print(songs[nam])
        sys.exit()
        print("name: {}".format(nam))
        print("  title: {}".format(songs[nam]['title']))
        print("  cat: {}".format(songs[nam]['cat']))
        print("  swds: {}".format(songs[nam]['firstwords']))
        print("  key: {}".format(songs[nam]['key']))

        for voice in voices:
            print("  voice: {}".format(voice))
            if not voice in songs[nam]:
                continue

            for mod in songs[nam][voice]:
                wtf = songs[nam][voice][mod]
                # print("type: {}, len: {}, val: {}".format(type(wtf), len(wtf), wtf))
                print("    mod: {}".format(mod))
                print("    fid: {}".format(wtf[0]))
                print("    path: {}".format(wtf[1]))
