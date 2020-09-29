import os
from datetime import datetime
class TunersProgram():

    nicknames = {"melanie.mcguire": "Mel"}
    dfltdir = "Gary"

    song_acts = [ 'Coaching', 'Closing song', 'Perform song', 'Polecats',
        'Rehearsal', 'Rehearse song', 'Run through', 'Run throughs', 'Teach song', 'Section rehearsal']

    break_acts = { 'Business break': 'Bus mtg', 'Coffee break': 'Break', 'Break': 'Intm'}

    other_acts = { 'Choreography work': 'Choreo', 'Quartet Perform': 'Qtet', 'Introduction': 'Intro',
            'Tags': 'Tags', 'Other': 'other',
            'Physical warm-ups': 'Phys_wrm', 'Vocal warm-ups': 'Voc_wrm', 'Warm-ups': 'warmups' }

    def __init__(self, htmlfile=None):

        self.htmfn = htmlfile

        if os.path.exists(self.htmfn):
            fo = open(self.htmfn, "rb")
            htm = fo.read()
            fo.close()

            # print("\nProcessing {}".format(self.htmfn))
        else:
            print("\nNo such file: {}".format(self.htmfn))
            return
            
        self.outhdrs = ['Key', 'Song Title', 'Starting Words', 'Start', 'Dur', 'Dir']
        self.rows = []

        # do a very rudimentary parse of the html, capture the program table rows
        if not b"Activity" in htm:
            print("No program found for {}".format(htmlfile))
        else:
            hlines = htm.decode("cp1252").split("\n")
            nt = htm.find(b"<title>")
            ntend = htm.find(b"</title>")
            self.title = htm[nt+7:ntend].decode("cp1252")
            lin = hlines.pop(0)
            # skip until we find the table header and the event start time
            self.progstart = "" # we should always find the start, but just in case...
            while True:
                if "Activity" in lin:
                    break
                elif "date-display-single" in lin:
                    n1 = lin.find('content="')+len('content="')
                    n2 = lin.find('">', n1)

                    self.progstart = datetime.strptime(lin[n1:n1+19], "%Y-%m-%dT%H:%M:%S")

                lin = hlines.pop(0)

            flds = lin.split("<th>")
            # discard the field before the first <th>
            flds.pop(0)

            # cols: Activity Music Start Mins Assignees Notes
            cols = [f[:f.find("<")] for f in flds]

            # get the next line
            lin = hlines.pop(0)
            nextstrt = self.progstart
            while True:
                if "<tr " in lin:
                    flds = lin.split("<td>")
                    flds.pop(0)
                    flds = [f[:f.rfind("</td")] for f in flds]
                    vals = []
                    for f in flds:
                        subflds = f.split(">")
                        if len(subflds) == 1:
                            vals.append(f)
                        else:
                            # song name is text value of <a href=...>song</a>.
                            # which is in subfld[1] with the > missing.
                            # now I want the node, too. subfld[0] looks like
                            # <a href="/node/13024"

                            ahrefnode = '<a href="/node/'
                            n = len(ahrefnode)

                            if subflds[0].startswith(ahrefnode):
                                node = subflds[0][n:-1]
                            else:
                                raise UserWarning("music field {} not <a href??".format(subflds))

                            song = subflds[1]
                            if song.endswith("</a"):
                                song = song[:-3]

                            # print(song)
                            if node == "0":
                                vals.append(0)
                            else:
                                vals.append(node)

                    # turn this row into a dict -
                    thisact = dict(zip(cols, vals))

                    act = thisact['Activity']
                    node = thisact['Music']

                    estrt = thisact['Start']
                    dur = thisact['Mins']
                    longdirs = thisact['Assignees'].split(",")
                    notes = thisact['Notes']

                    if act == "" and song == "":
                        lin = hlines.pop(0)
                        continue

                    sw = "??"
                    key = ""

                    # we get First.Last - if he's in nicknames, use that.
                    # otherwise, use First

                    dirs = []
                    for ldir in longdirs:
                        if ldir in self.nicknames:
                            dirs.append(self.nicknames[ldir])
                        else:
                            nm = ldir.split(".")
                            dirs.append(nm[0])

                    drctr = ",".join(dirs)
                    if drctr == "" or drctr == self.dfltdir:
                        # Special for Gary - he wants only non-default drctrs to appear
                        drctr = ""

                    estrt = nextstrt.strftime("%I:%M%p").lower()
                    if estrt[:1] == "0":
                        estrt = estrt[1:]

                    if act == "":
                        act = "Perform song"

                    if act in self.song_acts:
                        if song == "":
                            if notes == "":
                                song = "-- dir choice --"
                                if act == "Polecats":
                                    key = "Polecat"
                            else:
                                song = notes

                        if act == "Section rehearsal":
                            key = "Sec Reh"

                        self.rows.append((key, song, sw, estrt, dur, drctr))

                    elif act in self.break_acts:
                        abbr = "break"
                        if notes == "":
                            desc = ""
                        else:
                            desc = notes

                        self.rows.append((abbr, act, desc, estrt, dur, drctr))

                    elif act in self.other_acts:
                        abbr = self.other_acts[act]

                        if abbr == "Qtet":
                            if song == "":
                                # use Qtet for key, their choice of song
                                self.rows.append((abbr, "-- qtet choice --", "", estrt, dur, notes))
                            else:
                                self.rows.append((key, song, sw, estrt, dur, "Qtet:"+notes))

                        elif abbr in ["Choreo", "Sect"]: 

                            self.rows.append((abbr, song, sw, estrt, dur, drctr))

                        elif abbr in ["Voc_wrm", 'Phys_wrm', "warmups"]:
                            if song == "" and notes != "":
                                song = notes
                                sw = ""

                            self.rows.append(("warm", song, sw, estrt, dur, drctr))

                        # elif abbr == "Other":

                            # self.rows.append((abbr, act, notes, estrt, dur, drctr))

                        elif abbr == "run-thrus":
                            if notes != "":
                                song = notes
                                notes = ""
                        else:
                            # if drctr == "":
                                # drctr = estrt # ?? copied from progs.php

                            self.rows.append((abbr, notes, "", estrt, dur, drctr))

                    lin = hlines.pop(0)

                elif "<tbody>" in lin:
                    lin = hlines.pop(0)
                elif "</tbody>" in lin:
                    break
                else:
                    lin = hlines.pop(0)
