# dmotteler.github.io
./cheats:
cheatindex.py   # builds a new index.html with list of 12 most recent cheats
cheats.zip      # archive of the cheats folder before getting rid of older cheats
index.html      # invoked by https://dmotteler.github.io/cheats/ to list recent cheats

./musiclib:
catplay.html    # make playlist for a song category
ch.html         # make a cheat sheet
el.html         # edit the list of songs for a cheat sheet
eventlist.xsl   # rudimentary formatter for events.xml
events.py       # manage the events.xml file
events.xml      # list of tuners events, with when, where, and songlists
evtplay.html    # play the songs for an event
formatDate.js   # format a javascipt date for display
getEventList.js # load the events.xml file
getMusicLib.js  # load the music library file
getqv.js        # get usr arguments
index.html      # very similar to cheats/index, but built from event data
makeEvents.md   # help file for creating/updating events.xml
musiclibcd.py   # 
musiclib.xml    # the music library on which all the others depend
musiclib.xsl    # basic formatter for musiclib.xml
muslibup.py     # aids in updating musiclib, by reporting changes 
newsong.xml     # xml with all of the elements for a song in musiclib
pick.css        # formatting for song picker
ps.html         # picksongs - gather info for cheat sheets
README.md       # this file
select.css      # formatting for select lists and date pickers
sm.html         # build the song matrix
songperfs.html  # display song performance histories and summaries
songperfs.md    # help file for songperfs.html
songsumm.css    # formatting for songperfs.html
songxml.py      # musiclib used to be in a sqlite db. This converted that to .xml
weekly.md       # how-to for weekly cheat sheet processing
wheres.py       # reads events.xml, produces list of events by venue
xmlpick.css     # formatting for song picker
xmlsm.css       # formatting for song matrix

./perfcal:
event_changes.py # hangs on to differences in events, with methods to output them
perfcal.py       # main program for performance calendar management
README.md        # 
SingoutInfo.xlsx # excel file basis for singout dates and times
tuner_events.py  # inputs events from various formats (excel, ics)
tuners2023.ics   # Tuners 2023 calendar exported from Google
