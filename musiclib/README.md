These are the development files for the Tuners xml music library support.

catplay.html  - allows selection of a category and a voice part. plays the training tracks implied.

ch.html     - was cheat.html. invoked by picksongs (ps.html) to create the cheat-sheet html.
                get the event from the "opener", displays the cheat sheet, invokes editlist (el)
                and provides download of finished product.

                also invoked by index.html and songperfs.html

el.html     - editlist. get songlist from the "opener" (ch.html). allows add, move, remove, replace.
                right-click on an entry toggles quartet setting

events.xml  - has a list of event descriptors, with the when and where, a list of song ids
                for the event, and a list of song ids to be done by a quartet.

eventlist.xsl - rudimentary xslt formatter for events.xml

events.py     - creates a new events.xml, usually from the old one plus new cheat sheets in the
                github cheats folder.

evtplay.html  - allows selection of an event and a voice part. plays the training tracks implied.

getqv.js    - parses the query string (url args after ?)

index.html  - allow selection of "any" event, displays the cheat sheet for the event.

mlids.html  - displays range of songids in musiclib, and lists those available for use.

muslibup.py  - compares paths to track files from musiclib.xml and mydrive.xml, displays
                needed xml to update the library. mydrive.xml requires Google Drive access
                and needs permissions that only Del currently (9/2022) has.

musiclib.xml - the crown jewels.

musiclib.xsl - rudimentary xslt formatter for the library.

newsong.xml - copy and edit for each new song, if desired. has skeleton of all of the fields.

ps.html     - was picksongs. allows selection of venue, date/time, and song list for an event.

sm.html     - song matrix generator. accepts cat= on url to select categories to list.

songperfs.html - displays a summary of songs by category, showing the number of times each song has been
                rehearsed or performed. Category(s) and date range may be selected.

                also displays a list of events at a selected venue during a date range 

songxml.py  - kicked off this activity by turning music.db3 into musiclib.xml

wheres.py   - shows a list of all venues in the events xml with a count of times performed there.

xmlpick.css - formatting for picksongs display

xmlsm.css   - formatting for song matrix display

General cheat-sheet flow:
    ps.html allows songs for an event to be selected, in the order to be performed. Right-click on
        a song to turn "quartet song" on and off. A venue must be given before "Save" is clicked. It may be
        picked from an option list, or entered. The date-picker defaults to the next Tuesday. Selecting "Save"
        creates an event dict and invokes ch.html. The event has when and where info, plus the song list
        and the list of songs to be done by a quartet.

    ch.html is invoked by ps.html after the event has been updated. It loads the musiclib.xml,
        loops through the song list to create the cheat-sheet for the event. Buttons are
        included to allow the cheat-sheet to be downloaded or edited.

    el.html is invoked by the Edit button on a cheat sheet, to allow songs to be added, moved, removed, or
        replaced. Right-clicking an entry toggles the "quartet song" setting for that song. Cancel and Done
        buttons are provided.

    sm.html just reads in musiclib.xml and creates the song matrix. cat= may be given one or more times on
        the url to specify which categories to include. Default is all songs that have at least one track or
        sheet music file.

The only permanent result is the downloaded cheat sheet. When Gary creates one and distributes it,
I save it to the github cheats folder and run cheatindex.py in that folder, which updates the index.html file.

ps.html is the only file that is usually accessed directly, at https://dmotteler.github.io/musiclib/ps.html

The musiclib categories were compacted in Sept. 2022, as follows:
    moved songs from Song category to Current
    moved songs from Other category to Old
    changed TTS to Quartet
    moved songs from PoleCatII to PoleCat
    moved songs from YF2 category to Christmas

The libraray now has only the Current, Old, Quartet, PoleCat, and Christmas categories. I assume we'll
re-introduce the Show category, if we get brave.

The handling of song aliases was also changed: rather than a list of aliases as part of a song definition,
there is now one definition of the song attributes, and the alias has its own song id and name, and
an "aliasfor" attribute that give the song id of the main definition.
