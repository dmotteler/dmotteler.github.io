#! env python
'''
    started with
    $Id: event_changes.py,v 1.16 2022/04/04 03:33:00 dfm Exp dfm $

'''

import os, sys
from zipfile import ZipFile
from icalendar import Calendar, Event, tools
from datetime import datetime, timedelta, timezone
import pytz
from os.path import splitext
from csv import DictWriter

class event_changes():
    def __init__(self, complist, show_detail=True):
        ''' complist has two event classes to be compared '''

        self.events = {}
        self.venue_addrs = complist[0].venue_addrs
        self.complist = complist

        self.class1 = complist[0].event_class
        self.class2 = complist[1].event_class

        self.show_detail = show_detail

    def add(self, s_e, event):
        self.events[s_e] = event
        if self.show_detail:
            evfrom, evto = s_e
            print("New event: {} from {:%b %d, %Y at %I:%M%p} to {:%b %d, %Y at %I:%M%p}".format(event['title'], evfrom, evto))
    
    def drop(self, s_e, event):
        if 'uid' in event and event['uid'].endswith('google.com'):
            (evstrt, evend) = s_e
            dt = evend - evstrt
            print("\nrefusing to drop this manually added event:")
            pfmt = "%b %d, %Y at %I:%M%p"
            print("  %s from %s to %s (%s)" % (event['title'], evstrt.strftime(pfmt),
                evend.strftime(pfmt), dt))
            return

        self.events[s_e] = event
        self.events[s_e]['status'] = 'CANCELLED'

        if self.show_detail:
            (evstrt, evend) = s_e
            print("Deleted event: {} from {:%b %d, %Y at %I:%M%p} to {:%b %d, %Y at %I:%M%p}".format(self.class2.events[s_e]['title'], evstrt, evend))

    def modify(self, s_e, event, field):
        self.events[s_e] = event
        self.events[s_e]['status'] = 'MODIFIED'
        if self.show_detail:
            oldf = self.class2.events[s_e].get(field, "")
            newf = event.get(field, "")
            (evstrt, evend) = s_e
            print("{} changed from {} to {} on event at {:%b %d, %Y at %I:%M%p}".format(field, oldf, newf, evstrt))

    def dump_events(self, logfile=None):
        with open(logfile, "a") as log:
            log.write("\nDumping changed events\n")
            for s_e in sorted(self.events):
                (evstrt, evend) = s_e
                dt = evend - evstrt
                log.write("\n%s %s %s\n%s\n" % (evstrt, evend, dt, self.events[s_e]))

    def cal_events(self, ofn=None):
        ''' write a new ics file with the changed events '''

        cal = Calendar()
        cal.add('prodid', '-//Tuners Calendar//dfm//')
        cal.add('version', '2.0')

        uidgen = tools.UIDGenerator()
        dtstamp = datetime.utcnow()
        
        nev = 0
        for s_e in sorted(self.events):
            (evstrt, evend) = s_e
            event = Event()

            ev = self.events[s_e]
            if 'status' in ev:
                if ev['status'] == 'CANCELLED':
                    # print("%s %s going away" % (ev['title'], evstrt.strftime("%Y-%m-%d %I:%M%p")))
                    event['status'] = 'CANCELLED'
                elif ev['status'] == 'MODIFIED':
                    # print("%s %s changed" % (ev['title'], evstrt.strftime("%Y-%m-%d %I:%M%p")))
                    event['status'] = 'CONFIRMED'

            evtitl = ev['title']
            if 'venue' in ev:
                venue = ev['venue']
                if venue in self.venue_addrs:
                    a1, a2 = self.venue_addrs[venue]
                    locn = "%s\n%s\n%s" % (venue, a1, a2)
                    event.add('location', locn)

            desc = []
            if 'uni' in ev:
                desc.append("UNIFORM:" + ev['uni'])
            if 'type' in ev:
                desc.append("EVENT_TYPE:" + ev['type'])

            if len(desc) > 0:
                event.add('description', "\n".join(desc))

            if evstrt.hour == 0:
                # make date objects from the datetime objects
                # so calendar treats as "all day"
                evstrt = evstrt.date()
                evend = evend.date()

            event.add('summary', evtitl)
            event.add('dtstart', evstrt)
            event.add('dtend', evend)
            event.add('dtstamp', dtstamp)
            if 'uid' in ev:
                event['uid'] = ev['uid']
                # print("old uid %s" % (event['uid']))
            else:
                event['uid'] = uidgen.uid(host_name="twotowntuners.org")
                # print("gend uid %s" % (event['uid']))

            # print(event)
            cal.add_component(event)
            nev += 1

        f = open(ofn, 'w', newline='')
        # icalendar has no way to specify linesep - always uses "\r\n".
        # RFC 2554 says always use "\r\n". importing that into Google calendar
        # says no items imported. Changing to "\n" fixes the problem. BAH!
        f.write(cal.to_ical().decode('utf-8').replace("\r\n", "\n"))
        f.close()

        return nev

    def output_events(self, ofn=None):
        if ofn is None:
            return

        (_, ext) = splitext(ofn)
        if ext == ".ics":
            nev = self.cal_events(ofn)
        elif ext == ".csv":
            nev = self.csv_events(ofn)

        print("Wrote %d events to %s" % (nev, ofn))
        
    def comp_events(self, list_changes=True):
        ''' compare evenevents '''

        for s_e in sorted(self.class1.events):
            ev = self.class1.events[s_e]

            if s_e not in self.class2.events:
                # class1 event is new
                self.add(s_e, ev)

            else:
                if ev.get('title') != self.class2.events[s_e].get('title'):
                    self.modify(s_e, ev, 'title')

                if ev.get('venue') != self.class2.events[s_e].get('venue'):
                    self.modify(s_e, ev, 'venue')

                if ev.get('uni', "") != self.class2.events[s_e].get('uni', ""):
                    self.modify(s_e, ev, 'uni')

        pfmt = "%b %d, %Y at %I:%M%p"

        for s_e in sorted(self.class2.events):
            if s_e not in self.class1.events:
                print(s_e)
                # event from class1 not in class2 - dropped (or moved?? or manually added to calendar)
                self.drop(s_e, self.class2.events[s_e])

        if list_changes:
            # list the events to be changed
            print()
            for s_e in sorted(self.events):
                (evstrt, evend) = s_e
                dt = evend - evstrt
                ev = self.events[s_e]

                if 'status' in ev:
                    st = ev['status']
                    if st == 'CANCELLED':
                        act = '-'
                    elif st == 'MODIFIED':
                        act = 'm'
                    else:
                        print("\n  >>> ev status = %s??\n" % (st))
                else:
                    act = '+'

                print("%s %s from %s to %s (%s)" % (act, self.events[s_e]['title'], evstrt.strftime(pfmt),
                    evend.strftime(pfmt), dt))

    def csv_events(self, ofn=None):
        if len(self.events) < 1:
            return 0 # if there aren't any changed events, we're done here

        self.utc_tz = pytz.UTC

        flds = ["Event name", "Date start", "Date end", "Event type", "Location name", "Street",
        "additional", "city", "Province", "country", "Postal code", "notes",
        "internal_notes"]

        fo = open(ofn, "w", newline='')

        ocs = DictWriter(fo, flds, lineterminator='\n')
        ocs.writeheader()

        nev = 0
        for s_e in sorted(self.events):
            event = {}

            (evst, evend) = s_e
            ev = self.events[s_e]
            if ev['type'] == 'absences':
                continue

            ven = ev['venue']

            if ven and ven != '':
                if self.complist[1].event_source == "none":
                    # output is to new csv - use input venues
                    a1, a2 = self.class1.venue_addrs[ven]
                else:
                    a1, a2 = self.class2.venue_addrs[ven]
            else:
                a1 = ''
                a2 = None

            if a2 is None:
                # must be open or blacked out - 
                cit = ""
                st = ""
                zipcode = ""
            else:
                cit, st, *junk = map(str.strip, a2.split(","))

                if len(junk) > 0:
                    zipcode = junk[0].strip()
                elif len(st) > 5:
                    st, zipcode = st.split(" ")
                    if st == "WA":
                        st = "Washington"
                    elif len(st) < 4:
                        print("WARNING: State abbreviations (except for WA) don't work!")
                else:
                    zipcode = ""

            utcevstart = evst.astimezone(self.utc_tz)
            utcevend = evend.astimezone(self.utc_tz)

            event['Event name'] = ev['title']
            event['Date start'] = utcevstart.strftime("%b %d %Y - %I:%M%p").replace(" 0", " ").replace("AM", "am").replace("PM", "pm")
            event['Date end'] = utcevend.strftime("%b %d %Y - %I:%M%p").replace(" 0", " ").replace("AM", "am").replace("PM", "pm")
            event['Event type'] = ev['type']
            event['Location name'] = ven
            event['Street'] = a1
            event['additional'] = ""
            event['city'] = cit
            event['Province'] = st
            event['country'] = "United States"
            event['Postal code'] = zipcode

            if not ev['uni']:
                ev['uni'] = "- none -"

            event['notes'] = "UNIFORM:" + ev['uni']
            event['internal_notes'] = ""

            # print(event)
            
            ocs.writerow(event)

            nev += 1

        return nev

    def list_events(self):
        # print("\nListing changed events")

        lastmo = -1
        for s_e in sorted(self.events):
            (evst, evend) = s_e
            if evst.month != lastmo:
                lastmo = evst.month
                print("\n{:%B %Y}".format(evst))

            ev = self.events[s_e]
            typ = ev.get('type', "")
            uni = ev.get('uni', "")

            if typ == "absences":
                # sts = evst.strftime("%m/%d/%Y")
                # ends = evend.strftime("%m/%d/%Y")
                sts = "{:%d}".format(evst)
                ends = "{:%d}".format(evend)

                print("%s"  % (ev['title']))
                print("  from %s to %s"  % (sts, ends))
            else:
                ven = ev['venue']

                if evend.day == evst.day:
                    times = "\n  {:%d (%a), %I:%M %p} - {:%I:%M %p}".format(evst, evend)
                else:
                    times = "\n  {:%d (%a) %I:%M %p} - {:%d (%a) at %I:%M %p}".format(evst, evend)

                print("  {}".format(times))

                if ev['title'] == ven:
                    evnam = ven
                elif 'Rehearsal' in ev['title'] and ven == "Lewis & Clark Evt Ctr":
                    evnam = ev['title']
                elif ev['title'] == 'Board Meeting' and ven == "Lewis & Clark Evt Ctr":
                    evnam = ev['title']
                else:
                    evnam = "{} at {}".format(ev['title'], ven)

                if uni and uni != "" and uni != "- none -":
                    if uni == "singout":
                        evnam = "{}, UNIFORM: black shirt, blue tie".format(evnam)
                    elif uni == "contest":
                        evnam = "{}, UNIFORM: black shirt, blue tie, blue vest".format(evnam)
                    else:
                        evnam = "{}, UNIFORM: {}".format(evnam, uni)

                print("    {}".format(evnam))

    def event_list_pdf(self, pdffn=None):
        def pdfbold(txt, tcolor, keep):
            keepfont = self.pdffont
            keepfontsize = self.fontsize
            self.pdffont = self.pdffont + "-Bold"
            self.fontsize = self.fontsize + 2
            self.canvas.setFont(self.pdffont, self.fontsize)

            pdfout(txt, tcolor, keep, 1)

            self.pdffont = keepfont
            self.fontsize = keepfontsize
            self.canvas.setFont(self.pdffont, self.fontsize)

        def pdfout(txt, tcolor, keep, strtcol):
            ''' write string "txt" at current pdfy, starting in column "strtcol",
                after ensuring there is room on the current page for "keep" lines
            '''
            txt = txt.rstrip()

            if (self.pdfy + keep * self.pdfdy) > (self.pageh - self.bmarg):
                # close current page, reset font for new page, set y to top line.
                self.canvas.showPage()
                self.canvas.setFont(self.pdffont, self.fontsize)
                self.pdfy = self.tmarg

            x = self.pdfx + (strtcol - 1) * self.fontsize
            y = self.pdfy

            self.canvas.setFillColor(tcolor)
            self.canvas.drawString(x, y, txt)
            self.pdfy += self.pdfdy

        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.colors import black, lightslategray, crimson, lightpink

        self.pdffn = pdffn

        # leave 1/2" top and bottom margins
        self.tmarg = inch/2
        self.bmarg = inch/2

        # leave 1/4" left and right margins
        lmarg = inch/4
        # rmarg = inch/4

        self.canvas = canvas.Canvas(self.pdffn, bottomup=0, pagesize=letter)
        (self.pagew, self.pageh) = letter
        self.canvas.setTitle = "Tuners Events"

        # ppw = (self.pagew - lmarg - rmarg)/inch
        # pph = (self.pageh - self.tmarg - self.bmarg)/inch
        # print("printable page is {} x {} inches.".format(ppw, pph))

        self.pdfx = lmarg
        self.pdfy = self.tmarg

        # set fontsize.
        self.fontsize = 8
        self.pdffont = "Helvetica"

        # dy (vertical distance between lines) can be different, but fontsize seems to make a good default.
        self.pdfdy = self.fontsize
        self.canvas.setFont(self.pdffont, self.fontsize)

        lastmo = -1
        tz = pytz.timezone("US/Pacific")
        midnite = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=tz)

        for s_e in sorted(self.events):
            (evst, evend) = s_e

            if evend < midnite:
                tcolor = lightslategray
            else:
                tcolor = black

            if evst.month != lastmo:
                lastmo = evst.month

                # leave an empty line
                self.pdfy += self.pdfdy

                txt = ("{:%B %Y}".format(evst))
                pdfbold(txt, tcolor, 5)

            ev = self.events[s_e]
            typ = ev.get('type', "")
            uni = ev.get('uni', "")

            if 'cancelled' in ev['title'].lower():
                if evend < midnite:
                    tcolor = lightpink
                else:
                    tcolor = crimson

            if typ == "absences":
                sts = "{:%d (%a)}".format(evst)
                ends = "{:%d (%a)}".format(evend)

                # leave an empty line
                self.pdfy += self.pdfdy
                pdfout("{} - {}".format(sts, ends), tcolor, 3, 3)
                pdfout("{}".format(ev['title']), tcolor, 2, 5)
            else:
                ven = ev['venue'].strip()

                self.pdfy += self.pdfdy
                if evend.day == evst.day:
                    times = "{:%d (%a), %I:%M %p} - {:%I:%M %p}".format(evst, evend)
                else:
                    times = "{:%d (%a) %I:%M %p} - {:%d (%a) at %I:%M %p}".format(evst, evend)

                pdfout("{}".format(times), tcolor, 3, 3)

                if ev['title'] == ven:
                    evnam = ven
                elif 'Rehearsal' in ev['title'] and ven == "Lewis & Clark Evt Ctr":
                    evnam = ev['title']
                elif ev['title'] == 'Board Meeting' and ven == "Lewis & Clark Evt Ctr":
                    evnam = ev['title']
                else:
                    evnam = "{} at {}".format(ev['title'], ven)

                if uni and uni != "" and uni != "- none -":
                    if uni == "singout":
                        evnam = "{}, UNIFORM: black shirt, blue tie".format(evnam)
                    elif uni == "contest":
                        evnam = "{}, UNIFORM: black shirt, blue tie, blue vest".format(evnam)
                    else:
                        evnam = "{}, UNIFORM: {}".format(evnam, uni)

                pdfout(evnam, tcolor, 2, 5)

        self.canvas.showPage()
        self.canvas.save()

        print("Created {}".format(pdffn))

