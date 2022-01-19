These are the development files for the Tuners xml music library support.

catcher.php - not used. I was expecting to create an editor for the library xml,
                but finally decided it will be as easy to do it with vi.

ch.html     - was cheat.html. invoked by picksongs (ps) to create the cheat-sheet html.
                get event info from localStorage, displays the cheat sheet, invokes editlist (el)
                and provides download of finished product.

el.html     - editlist. get songlist from localStorage, allows add, move, remove, replace.
                right-click on an entry toggles quartet setting

getqv.js    - parses the query string (url args after ?)

libtrax.py  - compares paths to mp3 track files from musiclib.xml and Tracks.json, displays
                needed xml to update the library.

musiclib.xml - the crown jewels.

musiclib.xsl - rudimentary xlst formatter for the library.

newsong.xml - copy and edit for each new song.

ps.html     - was picksongs. allows selection of venue, date/time, and song list for an event.

savexml.html - not used. Was going to allow modified lib to be uploaded to server.

sm.html     - song matrix generator. accepts cat= on url to select categories to list.

songxml.py  - kicked off this activity by turning music.db3 into musiclib.xml

xmlpick.css - formatting for picksongs display

xmlsm.css   - formatting for song matrix display

General flow:
    ps.html allows songs for an event to be selected, in the order to be performed. Right-click on
        a song to turn "quartet song" on and off. A venue must be given before "Save" is clicked. It may be
        picked from an option list, or entered. The date-picker defaults to the next Tuesday. Selecting "Save"
        updated the showEvent and TunersEvents localStorage items. showEvent is used to index the TunersEvents
        array of events. Each event has when and where info, plus the song list and the list of quartet songs.

    ch.html is invoked by ps.html after the showEvent and TunersEvents info has been updated. It load the
        musiclib.xml, loops through the song list to create the cheat-sheet for the event. Buttons are
        included to allow the cheat-sheet to be downloaded or edited.

    el.html is invoked by the Edit button on a cheat sheet, to allow songs to be added, moved, removed, or
        replaced. Right-clicking an entry toggles the "quartet song" setting for that song. Cancel and Done
        buttons are provided. Note that current implementation saves each edit to localStorage, and there's
        no good way to get Cancel to mean "ignore all edits". 

    sm.html just reads in musiclib.xml and creates the song matrix. cat= may be given one or more times on
        the url to specify which categories to include. Default is Current.

"Production support" is provided by copying the files to my github repository. Since localStorage
    is on the users device, users are isolated from one another. That's a good thing most of the time,
    but it makes it hard for me to fix another user's problems.

savexml.html, catcher.php, libtrax.py, songxml.py, and newsong.xml have no "production" value. I decided
    to include them in the git repository for safekeeping.

ps.html is the only file that is usually accessed directly, at https://dmotteler.github.io/musiclib/ps.html
