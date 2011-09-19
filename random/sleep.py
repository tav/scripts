#! /usr/bin/env python2.5

from datetime import datetime, timedelta
from pytz import timezone, UTC

logs = []

def Log(data, year, tz):
    logs.append((data, year, tz))

# raindrop: 07 28

Log("""

U 08 23 1812
D 08 23 0605
U 08 22 0944
D 08 21 2201
U 08 20 1926
D 08 20 0802
U 08 19 0919
D 08 18 1908
U 08 17 1349
D 08 17 0656
U 08 16 1122
D 08 16 0135
U 08 15 1109
D 08 15 0252
U 08 14 1134
D 08 14 0325
U 08 13 1815
D 08 13 0852
U 08 12 1232
D 08 12 0054
U 08 10 1550
D 08 10 0617
U 08 09 0813
D 08 08 1502
U 08 07 1807
D 08 07 1104
U 08 06 1600
D 08 06 0600
U 08 05 0840
D 08 04 1755
U 08 03 1639
D 08 03 1311
U 08 03 1203
D 08 02 2352
U 08 01 1529
D 08 01 0755
U 07 31 1423
D 07 31 0530
U 07 30 0438
D 07 29 1349
U 07 28 1647
D 07 28 0714
U 07 27 1051
D 07 26 2354
U 07 26 0630
D 07 25 2311
U 07 25 0015
D 07 24 1026
U 07 23 0645
D 07 22 2037
U 07 21 2143
D 07 21 1303
U 07 20 1748
D 07 19 2213
U 07 18 1851
D 07 18 1240
U 07 17 1620
D 07 17 0831
U 07 17 0000
D 07 16 1528
U 07 15 1700
D 07 15 0213
U 07 13 1413
D 07 13 0849
U 07 12 1534
D 07 12 0523
U 07 11 1434
D 07 11 0730
U 07 10 1825
D 07 10 0458
U 07 09 0355
D 07 08 1841
U 07 07 1614
D 07 07 0321
U 07 05 1554
D 07 05 0649
U 07 04 1237
D 07 04 0304
U 07 03 2108
D 07 03 0854
U 07 01 1956
D 07 01 0621
U 06 29 2140
D 06 29 1350
U 06 28 2138
D 06 28 1032
U 06 27 1542
D 06 27 0446
U 06 26 0940
D 06 26 0336
U 06 25 1856
D 06 25 1349
U 06 24 1233
D 06 23 2139
U 06 22 2208
D 06 22 1553
U 06 21 1555
D 06 20 2328
U 06 19 1535
D 06 19 0551
U 06 18 1425
D 06 18 0635
U 06 17 1808
D 06 17 1034
U 06 16 1542
D 06 16 0258
U 06 15 0620
D 06 15 0231
U 06 14 1817
D 06 14 1153
U 06 14 1100
D 06 14 0920
U 06 13 1804
D 06 13 0020
U 06 11 1421
D 06 10 2336
U 06 09 1617
D 06 09 0811
U 06 08 1346
D 06 08 0521
U 06 07 1025
D 06 07 0105
U 06 06 1424
D 06 06 0922
U 06 05 1848
D 06 05 0646
U 06 04 1048
D 06 04 0437
U 06 03 0851
D 06 02 1750
U 06 01 1729
D 06 01 0217
U 05 30 1402
D 05 30 0420
U 05 29 1017
D 05 29 0420
U 05 28 1415
D 05 28 0547
U 05 27 1153
D 05 26 2119
U 05 25 1512
D 05 25 0521
U 05 24 1149
D 05 24 0155
U 05 22 2302
D 05 22 1259
U 05 21 2023
D 05 21 0349
U 05 20 0542
D 05 20 0122
U 05 19 2052
D 05 19 1159
U 05 18 1927
D 05 18 0947
U 05 17 1925
D 05 17 1421
U 05 16 1707
D 05 16 0858
U 05 15 1614
D 05 15 0617
U 05 14 1618
D 05 14 0933
U 05 13 1111
D 05 13 0233
U 05 12 0133
D 05 11 1210
U 05 10 1338
D 05 10 1040
U 05 09 1256
D 05 09 0211
U 05 08 0951
D 05 07 1655
U 05 07 1128
D 05 07 1040
U 05 06 1348
D 05 06 0900
U 05 05 1843
D 05 05 0920
U 05 04 1327
D 05 04 0626
U 05 03 1120
D 05 02 1910
U 05 01 2018
D 05 01 0437
U 04 29 1641
D 04 29 0711
U 04 28 0801
D 04 28 0001

""", 2010, timezone("Europe/London"))

# !! see why sleep was inevitable on: D 06 14 0920

entries = []

# Normalise the data into a sequence of (status, timestamp) entries.
for log in logs:
    data, year, tz = log
    for entry in reversed(data.strip().splitlines()):
        status, month, day, time = entry.split()
        hour, minute = time[:2], time[2:]
        timestamp = tz.localize(
            datetime(year, int(month), int(day), int(hour), int(minute), 0)
            )
        timestamp = timestamp.astimezone(UTC)
        entries.append((status, timestamp))

# Get rid of the first entry if it's a sleep entry
if entries[0][0] == 'D':
    entries = entries[1:]

awake = asleep = timedelta(0)

def conv(delta):
    seconds = delta.days * 86400 + delta.seconds
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return "%2s:%02d" % (hours, minutes)

# Obviously need at least one UP entry for this to work.
prev_status, prev_ts = entries.pop(0)

for status, ts in entries:
    diff = ts - prev_ts
    if prev_status == "U":
        print "Awake for ", conv(diff)
        awake += diff
    else:
        print "Sleep for ", conv(diff)
        asleep += diff
    prev_status, prev_ts = status, ts

diff = tz.localize(datetime.now()) - prev_ts

print

if prev_status == "U":
    print "# Currently Awake for ", conv(diff)
else:
    print "# Currently Sleep for ", conv(diff)

def to_seconds(delta):
    return float((delta.days * 86400) + delta.seconds)

print
print "Total Awake: ", awake
print "Total Asleep: ", asleep
print

awake_s = to_seconds(awake)
asleep_s = to_seconds(asleep)

ratio = awake_s / asleep_s
sleep24 = (86400. / (awake_s + asleep_s)) * asleep_s

sleep24_hours, sleep24 = divmod(sleep24, 3600)
sleep24_minutes, sleep24 = divmod(sleep24, 60)


print "Ratio: ", ratio
print "Average sleep per 24 hour day:", int(sleep24_hours), "hours and", int(sleep24_minutes), "minutes"
print
