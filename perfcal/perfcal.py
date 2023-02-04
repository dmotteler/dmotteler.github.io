#!/usr/bin/env python
'''
    started with
    $Id: singouts.py,v 1.11 2022/04/04 03:31:55 dfm Exp dfm $

    remove database support and testmode

'''

import os, sys
sys.dont_write_bytecode = True # don't mess up git repo with __pycache__ files
from datetime import datetime, timedelta

import pytz

import getopt

from tuner_events import tuner_events
from event_changes import event_changes

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)

def usage(msg="", error=0):
    if msg != "":
        print("\n>>> %s\n" % (msg))

    print("""Usage: %s [-h] [-e file] [-i file] [-s cal] [-l] [-o file] [-c xy] [-m range] [-a] [-b] [-p] [-r]
   where:
      -h    show this help and exit
      -e    path to excel workbook
                default - %s
      -i    path to ical .ics file, or .zip file which contains ics files
                default - %s

      -s cal names calendar within ics zip file. may appear more than once.
             default - "tuners" and "tunersboardabs" + years implied by -m.
             (e.g. ['tuners2020', 'tunersboardabs2020'])

      -l => just list out events to screen

      -o file => list events, to pdf file

      -c xy x is one of e or i - specifies type of the "current" file (excel or ics)
            y is the type of the "old" file. If y is e or i, changes to the old e or i file
                are output to bring it into agreement with the current file.

            If y is 'v', all events from the "current" file are written to a csv file.
            If y is 'c', those events are written to an .ics file
            If y is empty, the -l option is assumed.

            Note: the listing options, -l and -o, cause other output to be suppressed,
                so the setting of y is ignored.
            
            default: ei - reads excel and ics files, and outputs the changes
                between the two as ics file

      -m range => range can be n (month n current year), or n1-n2 (months n1 thru
                n2, current year), or yyyy:n (month n, year yyyy), or yyyy:n1-n2
                (months n1 thru n2 of yyyy), or yyyy:n1-yyy2:n2 (month n1 of yyyy
                thru n2 of yyy2) 
                default is remaining months of current year.

      -a => don't do absences
      -b => don't do board mtgs
      -p => don't do performance events
      -r => don't do rehearsal events
""" % (sys.argv[0], infiles['e'], infiles['i']))

    sys.exit(error)

infiles = {}
# establish default input file
infiles['e'] = "SingoutInfo.xlsx"
infiles['i'] = "tuners2023.ics"
calnames = []

def main():
    # for reasons I still don't understand, I get the byte string for a colon.
    # this seems to put it back to what I wanted...
    colon = b'\xef\x80\xba'
    argv = [x.replace(colon, b":").decode('utf-8') for x in list(map(os.fsencode, sys.argv))]

    try:
        opts, args = getopt.getopt(argv[1:], "c:e:hi:s:o:m:ablpr")

    except getopt.GetoptError as err:
        # will print something like "option -a not recognized"
        usage(msg=str(err), error=1)

    validcur = ['e', 'i']
    validold = ['e', 'i', 'c', 'v']
    cur, old = ['e', 'i'] # default process updates ical to match excel

    startmo = 1
    endmo = 12
    y1 = datetime.now().year
    y2 = y1
    m1 = datetime.now().month
    m2 = 12

    # absences, board mtgs, performances, and rehearsals may be individually turned off.
    dotypes = {}
    dotypes['a'] = True
    dotypes['b'] = True
    dotypes['p'] = True
    dotypes['r'] = True

    dolist = False
    
    pdffn = ""

    for o, a in opts:
        if o == "-c":
            if a.startswith("-"):
                usage("-c option with no comp order spec??", error=1)
            else:
                co = list(a)
                if len(co) == 1:
                    old = None
                    if co[0] in validcur:
                        cur = co[0]
                    else:
                        cur = None
                        usage("-c value (%s) not recognized" % (a), error=1)

                elif len(co) == 2:
                    if co[0] in validcur:
                        cur = co[0]
                    else:
                        cur = None
                    if co[1] in validold:
                        old = co[1]
                    else:
                        old = None

                    if not cur or not old:
                        usage("-c value (%s) not recognized" % (a), error=1)

        elif o == "-e":
            if a.startswith("-"):
                usage("-e option with no file name??", error=1)

            if a.endswith(".xlsx"):
                infiles['e'] = a.replace("/", "\\\\")
            else:
                usage("for now, -e files must end with .xlsx", error=1)

        elif o == "-h":
            usage()

        elif o == "-i":
            if a.startswith("-"):
                usage("-i option with no file name??", error=1)

            if a.endswith(".ics") or a.endswith(".zip"):
                infiles['i'] = a
            else:
                usage("-i file must end with .ics or .zip", error=1)

        elif o == "-o":
            if a.startswith("-"):
                usage("-o option with no file name??", error=1)

            if a.endswith(".pdf"):
                pdffn = a
            else:
                usage("-o file must end with .pdf", error=1)

        elif o == "-m":
            if a.startswith("-"):
                usage("-m option with no month argument??", error=1)

            mos = a.split("-")
            if len(mos) < 1 or len(mos) > 2:
                raise UserWarning("invalid value ({}) in date range.".format(a))

            startmo = mos[0]
            if len(mos) > 1:
                endmo = mos[1]
            else:
                endmo = startmo

            ym1 = startmo.split(":")
            if len(ym1) < 1 or len(ym1) > 2:
                raise UserWarning("invalid value ({}) in starting month.".format(startmo))

            if len(ym1) == 1:
                t = int(ym1[0])
                if t > 0 and t < 13:
                    m1 = t
                elif t > 2009 and t < 2100:
                    m1 = 1
                    m2 = 12
                    y1 = t
                else:
                    raise UserWarning("invalid value ({}) in starting month.".format(ym1[0]))

            elif len(ym1) == 2:
                # first part of range is y:m
                y1 = int(ym1[0])
                m1 = int(ym1[1])
                if m1 < 1 or m1 > 12 or y1 < 2010 or y1 > 2099:
                    raise UserWarning("invalid value ({}) in range start.".format(startmo))

            ym2 = endmo.split(":")
            if len(ym2) < 1 or len(ym2) > 2:
                raise UserWarning("invalid value ({}) in ending month.".format(endmo))

            if len(ym2) == 1:
                t = int(ym2[0])
                if t > 0 and t < 13:
                    m2 = t
                    y2 = y1
                elif t > 2009 and t < 2100:
                    m1 = 1
                    m2 = 12
                    y2 = t
                else:
                    raise UserWarning("invalid value ({}) in ending month.".format(endmo))

            elif len(ym2) == 2:
                # second part of range is y:m
                y2 = int(ym2[0])
                m2 = int(ym2[1])
                if m2 < 1 or m2 > 12 or y2 < 2010 or y2 > 2099:
                    raise UserWarning("invalid value ({}) in range start.".format(startmo))

        elif o == "-a":
            # don't do absences
            dotypes['a'] = False

        elif o == "-b":
            # don't do board meetings
            dotypes['b'] = False

        elif o == "-l":
            dolist = True

        elif o == "-p":
            # don't do performances
            dotypes['p'] = False

        elif o == "-r":
            # don't do rehearsals
            dotypes['r'] = False

        elif o == "-s":
            if a.startswith("-"):
                usage("-s option with no calendar name??", error=1)
            calnames.append(a)

        else:
            assert False, "getopt allows unhandled option %s" % (o)

    if not any(dotypes.values()):
        usage("absences, board mtgs, performances and rehearsals suppressed - we're done!", error=0)

    pst = pytz.timezone('US/Pacific')
    fromdate = datetime(y1, m1, 1, tzinfo=pst)
    todate = datetime(y2, m2, 1, tzinfo=pst)
    todate = last_day_of_month(todate)
    todate = todate.replace(hour=23, minute=59, second=59)

    print("Processing events between %s and %s\n" % (fromdate.strftime("%b %d, %Y"),
        todate.strftime("%b %d, %Y")))

    # set the extension for output file, if any
    if old in ['e', 'v']:
        ext = "csv"
    elif old in ['i', 'c']:
        ext = "ics"
    else:
        ext = None

    listonly = dolist or pdffn != ""
    if listonly:
        old = ''

    # complist has events object for current, old
    complist = [None, None]

    # if current or old is e, get events from excel
    if cur == 'e' or old == 'e':
        e_events = tuner_events(infiles['e'], dotypes, caln=None, outext=ext, fromdate=fromdate, todate=todate)
        if not listonly:
            print("%s contains %d events" % (infiles['e'], len(e_events.events)))
        if cur == 'e':
            complist[0] = e_events
        else:
            complist[1] = e_events

    # if current or old is i, get events from ics
    if cur == 'i' or old == 'i':
        i_events = tuner_events(infiles['i'], dotypes, caln=calnames, outext=ext, fromdate=fromdate, todate=todate)
        if not listonly:
            if infiles['i'].endswith(".zip"):
                print("{}:".format(infiles['i']))
                for cal in i_events.calfiles:
                    print("  {} contains {} events".format(cal, i_events.calfiles[cal][1]))
            else:
                cal = infiles['i']
                print("{} contains {} events".format(infiles['i'], i_events.calfiles[cal][1]))

        if cur == 'i':
            complist[0] = i_events
        else:
            complist[1] = i_events

    if ext is not None and not listonly:
        print("events will be written to a new .{} file".format(ext))

    if False:
        print("about to go to new events.")
        print("e_events:")
        print(e_events.events)
        for s_e in sorted(e_events.events):
            ini = s_e in i_events.events
            print("{:%Y-%m-%d@%H:%M%p} - {:%Y-%m-%d@%H:%M%p} {}".format(*s_e, ini))
            ev = e_events.events[s_e]
            for k in ev:
                print("   {}: {}".format(k, ev[k]))
            print()

        print("i_events:")
        print(i_events.events)
        for s_e in sorted(i_events.events):
            ine = s_e in e_events.events
            print("{:%Y-%m-%d@%H:%M%p} - {:%Y-%m-%d@%H:%M%p} {}".format(*s_e, ine))
            ev = i_events.events[s_e]
            for k in ev:
                print("   {}: {}".format(k, ev[k]))
            print()
        sys.exit()
        
    new_events = event_changes(complist, show_detail=not listonly)
    new_events.comp_events(list_changes=not listonly)

    # new_events.dump_events("eventdump.txt")

    if pdffn != "":
        new_events.event_list_pdf(pdffn)

    if dolist:
        new_events.list_events()

    if listonly:
        sys.exit()

    elif ext is not None:
        if startmo == 1 and endmo == 12 and y1 == y2:
            base   = "events%d" % (y1)
        elif startmo == endmo and y1 == y2:
            base   = "events%d%02d" % (y1, m1)
        elif y1 == y2:
            # start and end months given and different, years same
            base   = "events%d%02d%02d" % (y1, m1, m2)
        else:
            base   = "events%d%02d%d%02d" % (y1, m1, y2, m2)

        ofn = "%s.%s" % (base, ext)
        new_events.output_events(ofn)

if __name__ == "__main__":
    main()
