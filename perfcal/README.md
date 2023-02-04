perfcal does calendar maintenance for the Tuners schedule.

It has two basic modes: creating lists of events, and comparing two lists to create an update file.

By default:
    The list of events in SingoutInfo.xlsx is compared to that in tuners2023.ics,
    and the update file created contains ics entries to bring the Google calendar up to date.

    The events listed are those for the duration of the current year. The start and end dates
    may be specified.

    All rehearsals, performances, absences, and board meetings are listed, from individual sheets
    in the excel file. Any or all may be suppressed.

    The events selected may be listed, either to the terminal or a pdf file.

Sample uses:

    1. make pdf with rehearsals and performances from current month to end of year, from the spreadsheet
        ./perfcal.py -o allyear.pdf -c e -a -b

    2. another pdf, performances only, July - December
         ./perfcal.py -o h2.pdf -c e -a -b -r -m 4-6

    3. same as 2, but list to terminal
         ./perfcal.py -l -c e -a -b -r -m 4-6
         
    4. export July - December events to a .csv file
        ./perfcal.py -c ev -m 7-12

    5. to update Google calendar, after updating spreadsheet
        a. export current calendar, rename to tuners2023.ics
        b. ./perfcal.py 
        c. import .ics file from b into Google calendar
        d. remove any "temporary" files from perfcal folder, 
             then do git push
