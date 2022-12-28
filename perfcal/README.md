Created the tuner2023 by updating my SingoutInfo.xlsx, then running
 ./perfcal.py -a -b -m 2023 -c ec

Usage: ./perfcal.py [-e file] [-i file] [-s cal] [-o file] [-c xy] [-m range] [-a] [-b] [-l] [-p] [-r]
   where:
      -e    path to excel workbook
                default - /mnt/c/Users/dmott/Documents/SingoutInfo.xlsx
      -i    path to ical .ics file, or .zip file which contains ics files
                default - /mnt/c/Users/dmott/Downloads/del.motteler@gmail.com.ical.zip

      -s cal names calendar within ics zip file. may appear more than once.
             default - "tuners" and "tunersboardabs" + years implied by -m.
             (e.g. ['tuners2020', 'tunersboardabs2020'])

      -o file => list events, to file

      -c xy x is one of e or i - specifies type of the "current" file
            y is the type of the "old" file. If y is one of e or i,
            output is changes to the old file to bring it into
            agreement with the current file. If y is 'v', all events from
            the "current" file are written to a csv file.  If y is "c", those
            events are written to an .ics file

            default: ei - reads excel and ics files, and outputs the changes
                between the two as ics file

      -m range => range can be n (month n current year), or n1-n2 (months n1 thru
                n2, current year), or yyyy:n (month n, year yyyy), or yyyy:n1-n2
                (months n1 thru n2 of yyyy), or yyyy:n1-yyy2:n2 (month n1 of yyyy
                thru n2 of yyy2)
                default is remaining months of current year.

      -a => don't do absences
      -b => don't do board mtgs
      -l => just list out events to screen
      -p => don't do performance events
      -r => don't do rehearsal events
