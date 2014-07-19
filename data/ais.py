#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import sys
import datetime, time

#db_file = "ports.db"
db_file = "/home/andrewsm/sketchpad/redcatlabs/ports/db/ports.db"

if len(sys.argv)<2:
  print """Usage:
python ais.py {current}
"""
  exit(1)
  
cmd = sys.argv[1].lower()

# http://www.tutorialspoint.com/sqlite/sqlite_python.htm
connection = sqlite3.connect(db_file)

#CREATE INDEX ais_ts ON ais (ts);               # ?mins
#CREATE INDEX ais_latlon ON ais (lat,lon);      # 3mins

""".schema ais
CREATE TABLE AIS (
vid INT, country CHAR(2), 
lat REAL, lon REAL, course REAL, speed REAL, 
l INT, gt INT, beam INT, 
ts INT);
"""

c = connection.cursor()

t_now="2014-05-15 14:00:00"
ts = datetime.datetime.strptime(t_now, "%Y-%m-%d %H:%M:%S")  # 2014-05-15 14:00:00
v = time.mktime(ts.timetuple())
print v

if cmd=="current":
  c.execute("SELECT ts,vid,lat,lon,course,speed FROM ais WHERE ts>? AND ts<? ORDER BY vid,ts", [v-20*60, v])  # X mins

  print "["
  for r in c.fetchall():
    l = list(r)
    print(" %s," % (l,))
  print " [0,0,0,0,0,0]\n];"

connection.close()
