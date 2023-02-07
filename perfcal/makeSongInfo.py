#! /usr/bin/env python
'''
    initialize rehearsals and performances SongInfo sheets
    for a year. default is current year, else specify as first argument.
'''

import sys
from datetime import date, time, timedelta
from openpyxl import Workbook

# day-of-week day-of-month   day-of-month
#  for 1st     for 1st Tue    for 1st Thu
#    6 (Sun)       3              5
#    0 (Mon)       2              4
#    1 (Tue)       1              3
#    2 (Wed)       7              2
#    3 (Thu)       6              1
#    4 (Fri)       5              7
#    5 (Sat)       4              6

# figure out which year to do
if len(sys.argv) > 1:
    yr = int(sys.argv[1])
else:
    yr = date.today().year

# Tuners rehearsal start and end times
rehst = time(18, 0, 0)
rehend = time(20, 0, 0)

# build a date for Jan 1 of year
jan1 = date(yr, 1, 1)
# dow is weekday of Jan 1, 0 is Monday
dow = jan1.weekday()

# build date for 1st Tuesday in January
tuedom = 2 - dow if dow < 2 else 9 - dow
tue = date(yr, 1, tuedom)

# build date for Jan 1 of following year
nxtyr = yr + 1
nxtjan1 = date(nxtyr, 1, 1)

tuesdays = []

# until Tue is in following year, add date to list of tuesdays
while tue < nxtjan1:
    tuesdays.append(tue)
    tue += timedelta(days=7)

# create a workbook, name active (only) sheet <year> Rehearsals
wb = Workbook()
ws = wb.active
ws.title = "{} Rehearsals".format(yr)

# add the header row to the sheet
cols = ['Event', 'Venue', 'Date', 'Start Time', 'End Time', 'Uniform', 'Type']
ws.append(cols)

# then add a rehearsal row for each Tuesday
for tue in tuesdays:
    row = ['Tuners Rehearsal', 'Lewis & Clark Evt Ctr', tue, rehst, rehend, None, 'Rehearsal']
    ws.append(row)
    
# add a sheet for performances and put the header row out
ws = wb.create_sheet("{} Performances".format(yr))
ws.append(cols)


# typical performance from 6:30 to 7:15
perst = time(18, 30, 0)
perend = time(19, 15, 0)

# for each month...
for mo in range(1, 13):
    # build date for 1st of month, get its weekday
    mo1 = date(yr, mo, 1)
    dow = mo1.weekday()

    # calculate 1st Thursday of the month
    thudom = 4 - dow if dow < 4 else 11 - dow
    thu = date(yr, mo, thudom)

    # add a placeholder for the performance
    row = ['at venue', 'venue', thu, perst, perend, 'singout', 'Performance']
    ws.append(row)

    # calculate 3rd Thursday
    thu += timedelta(days=14)
    # and add a placeholder for that date
    row = ['at venue', 'venue', thu, perst, perend, 'singout', 'Performance']
    ws.append(row)

# save the workbook
wbfn = "si.xlsx"
wb.save(wbfn)

print("created {}".format(wbfn))
