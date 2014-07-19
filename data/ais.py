#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import sys
import datetime, time
import re

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

"""
.schema geog
CREATE TABLE geog (loc_id REAL, 
name TEXT, 
shape TEXT, 
loc_type TEXT, 
loc CHAR(5));
"""

def read_geog():
  c = connection.cursor()
  c.execute("SELECT name,shape,loc_type,loc FROM geog")
 
  def av_size(arr, pos):
    arr_pos=[]
    for e in arr:
      arr_pos.append(e[pos])
    return (sum(arr_pos)/len(arr_pos), (max(arr_pos)-min(arr_pos))/2)
     
  g=dict()
  for r in c.fetchall():
    loc = dict(zip(['name','shape','loc_type','loc'], r))
    #print loc
    m = re.search(r'MDSYS.SDO_ORDINATE_ARRAY\((.[^\)]*?)\)', loc['shape'])
    if m is None:
      print "NO SHAPE : ", loc
    else:
      shape_arr=m.group(1).split(',')
      #print shape_arr
    shape_py=[]
    for (lon_str,lat_str) in zip( shape_arr[0::2], shape_arr[1::2] ):
      (lat,lon) = (float(lat_str),float(lon_str))
      shape_py.append( (lat,lon) )
    loc['shape_py']=shape_py
    
    (av_lat, size_lat) = av_size(shape_py, 0)  
    (av_lon, size_lon) = av_size(shape_py, 1)  
    loc['shape_mid'] = (av_lat, av_lon)
    loc['shape_size']= (size_lat, size_lon)
  
    g[loc['loc']]=loc
    
  return g

#exit(1)
c = connection.cursor()

t_now="2014-05-15 14:00:00"
ts = datetime.datetime.strptime(t_now, "%Y-%m-%d %H:%M:%S")  # 2014-05-15 14:00:00
v = time.mktime(ts.timetuple())
#print v

if cmd=="current":
  c.execute("SELECT ts,vid,lat,lon,course,speed FROM ais WHERE ts>? AND ts<? ORDER BY vid,ts", [v-20*60, v])  # X mins

  print "["
  for r in c.fetchall():
    l = list(r)
    print(" %s," % (l,))
  print " [0,0,0,0,0,0]\n];"


#315,TANJONG PAGAR TERMINAL (PSA CORPORATION LTD) T6,
#"MDSYS.SDO_GEOMETRY(2003,8307,NULLMDSYS.SDO_ELEM_INFO_ARRAY(1,1003,1)MDSYS.SDO_ORDINATE_ARRAY(103.849260833333,1.26282716666667,103.848994166667,1.26258466666667,103.847206833333,1.2645785,103.847476,1.264823,103.849260833333,1.26282716666667))"
#,BERTH,T6,null

if cmd=="target":
  loc=(sys.argv[2] or "").upper()
  geog=read_geog()

  #shape = geog[loc]['shape_py']
  
  #target = [1.2645785,103.847206833333];
  target = geog[loc]['shape_mid']
  #pm = 0.0001
  pm = max(geog[loc]['shape_size'])
  print target, pm
  #exit(1)
  
  c.execute("SELECT ts,vid,lat,lon,course,speed FROM ais WHERE lat>? AND lat<? AND lon>? AND lon<? ORDER BY vid,ts",
    (target[0]-pm, target[0]+pm,target[1]-pm, target[1]+pm)
  )

  print "["
  for r in c.fetchall():
    l = list(r)
    print(" %s," % (l,))
  print " [0,0,0,0,0,0]\n];"

connection.close()
