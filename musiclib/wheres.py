#! env python
''' get gdids from musiclib '''

import os, sys
from xml.etree import ElementTree as ET

def main():
    cheatxml = "events.xml"

    with open(cheatxml, "rb") as f:
        cheatslist = f.read().decode('utf-8')

    cheats = {}
    tree = ET.XML(cheatslist)
    wheres = {}
    for ev in tree:
        where = ev.attrib['where']
        if "ehearsal" not in where:
            if where not in wheres:
                wheres[where] = 0
            wheres[where] += 1

    for ven in sorted(wheres):
        if wheres[ven] > 3:
            print(ven, wheres[ven])

if __name__ == "__main__":
    main()
