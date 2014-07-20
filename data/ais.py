#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import sys
import datetime, time
import re
import json 

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
#CREATE INDEX ais_vid ON ais (vid);             # <4mins
#CREATE INDEX ais_latlon ON ais (lat,lon);      # ~3mins

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
print "//Special time = %d" % (v,)

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
  geog=read_geog()
  loc=(sys.argv[2] or "T6").upper()

  #target = [1.2645785,103.847206833333];  # T6
  target = geog[loc]['shape_mid']
  #pm = 0.0001
  pm = max(geog[loc]['shape_size'])
  print loc, target, pm
  #exit(1)
  
  c.execute("SELECT ts,vid,lat,lon,course,speed FROM ais WHERE lat>? AND lat<? AND lon>? AND lon<? ORDER BY vid,ts",
    (target[0]-pm, target[0]+pm,target[1]-pm, target[1]+pm)
  )
  
  r=c.fetchall()
  print json.dumps(r)    


#1.35,WEST JURONG ANCHORAGE,"MDSYS.SDO_GEOMETRY(2003,8307,NULLMDSYS.SDO_ELEM_INFO_ARRAY(1,1003,1)MDSYS.SDO_ORDINATE_ARRAY(103.62375,1.238417,103.648633,1.250033,103.652583,1.24175,103.627683,1.230117,103.62375,1.238417))",
#ANCHORAGE,AWJ,null

trails_from_markers=None
if cmd=="markers":
  geog=read_geog()
  loc=(sys.argv[2] or "AWJ").upper()
  
  target = geog[loc]['shape_mid']
  pm = max(geog[loc]['shape_size'])*2
  print loc, target, pm
  
  c.execute("SELECT ts,vid,lat,lon,course,speed FROM ais WHERE ts>? AND ts<? AND lat>? AND lat<? AND lon>? AND lon<? ORDER BY vid,ts", 
    [v-5*60, v, target[0]-pm, target[0]+pm,target[1]-pm, target[1]+pm]
  )  # X mins

  r=c.fetchall()
  
  print "// Markers in last 5 mins from %s" % (loc,)
  print "// { vid : [ [ts, lat_, lon_, course, speed, vid], ... ], ... }"
  print json.dumps(r)
  
  trails_from_markers=r
  print "\n\n"

trails=[  # AWJ
 [1400133488, 3921, 1.239798784, 103.6278534, 123.9999924, 0.100000001],
 [1400133484, 6099, 1.224686623, 103.6480484, 0.0, 0.0],
 [1400133484, 6532, 1.226896286, 103.6449127, 167.6999969, 0.100000001],
 [1400133482, 7037, 1.223250031, 103.6392593, 0.0, 0.0],
 [1400133566, 8937, 1.26678133, 103.656723, 117.5000076, 0.200000003],
 [1400133499, 9279, 1.253167272, 103.6090012, 0.0, 0.0],
 [1400133548, 17670, 1.251086116, 103.644577, 316.8999939, 0.099999994],
 [1400133551, 19565, 1.24383986, 103.6419983, 119.4000015, 0.100000001],
 [1400133514, 23009, 1.2468009, 103.606636, 0.0, 0.0],
 [1400133516, 26759, 1.254663825, 103.6251068, 0.0, 0.0],
 [1400133538, 30322, 1.227916718, 103.6392365, 0.0, 0.0],
 [1400133535, 31228, 1.223065019, 103.6394043, 0.0, 0.0],
 [1400133572, 34395, 1.213630199, 103.6114502, 112.6040802, 7.607581615],
 [1400133519, 35148, 1.25463891, 103.6389923, 0.0, 0.0],
 [1400133562, 35325, 1.253131866, 103.6096802, 34.0, 0.100000001],
 [1400133456, 36569, 1.254270554, 103.643486, 0.0, 0.0],
 [1400133532, 37423, 1.244897842, 103.6492767, 234.5133209, 0.087694541],
 [1400133507, 37788, 1.233639121, 103.6415176, 129.0, 0.100000001],
 [1400133506, 38750, 1.229550004, 103.6427841, 0.0, 0.0],
 [1400133490, 39127, 1.215841651, 103.6430511, 190.9000092, 0.099999994],
 [1400133490, 39127, 1.216212034, 103.6430359, 0.0, 0.0],
 [1400133580, 39208, 1.239575028, 103.6420746, 0.0, 0.0],
 [1400133465, 39250, 1.225838304, 103.6269989, 0.0, 0.0],
 [1400133554, 39681, 1.217716694, 103.6179581, 0.0, 0.0],
 [1400133467, 40135, 1.212300777, 103.6496353, 101.6999969, 0.900000036],
 [1400133474, 41867, 1.216469288, 103.6322098, 94.59999847, 0.900000036],
 [1400133547, 42867, 1.235980034, 103.64431, 0.0, 0.0],
 [1400133579, 43303, 1.225516677, 103.6268997, 0.0, 0.0],
 [1400133516, 48195, 1.244184971, 103.6071396, 0.0, 0.0],
 [1400133463, 51200, 1.223218918, 103.6422882, 279.8482666, 6.677908421],
 [1400133481, 51289, 1.239254951, 103.6596375, 157.6999969, 18.20000076],
 [1400133556, 51419, 1.261556387, 103.6397171, 72.0, 0.099999994],
 [1400133483, 51634, 1.250822425, 103.644043, 32.70000076, 1.600000024],
 [1400133568, 51748, 1.223450065, 103.6354446, 0.0, 0.0],
 [1400133487, 52201, 1.218928337, 103.614418, 48.09999847, 0.100000001],
 [1400133552, 53583, 1.239250064, 103.6342621, 0.0, 0.0],
 [1400133494, 54252, 1.218501687, 103.614624, 0.0, 0.0],
 [1400133534, 54652, 1.265703917, 103.651001, 330.5, 0.100000001],
 [1400133515, 55662, 1.238609791, 103.6521988, 64.40000153, 0.300000012],
 [1400133538, 56553, 1.243939996, 103.6112976, 0.0, 0.0],
 [1400133521, 57015, 1.243739963, 103.6399155, 131.3999939, 0.100000001],
 [1400133498, 57804, 1.216145992, 103.6436768, 166.9000092, 0.100000001],
 [1400133519, 58190, 1.233358383, 103.6512451, 0.0, 0.0],
 [1400133513, 58229, 1.236874461, 103.631073, 64.79999542, 0.100000001],
 [1400133558, 58712, 1.217992783, 103.6485596, 216.9706879, 0.032073211],
 [1400133556, 60807, 1.223198056, 103.639534, 146.5999908, 0.100000001],
 [1400133533, 69775, 1.246816754, 103.6420212, 237.3089142, 3.017813921],
 [1400133552, 83320, 1.230763316, 103.6563263, 202.1957855, 0.052502107],
 [1400133554, 84291, 1.247601509, 103.6570969, 333.0011292, 8.299900055],
 [1400133477, 86043, 1.252434015, 103.6079483, 0.0, 0.0],
 [1400133460, 87477, 1.217317939, 103.6520844, 180.6999969, 0.400000006],
 [1400133561, 87903, 1.267009974, 103.652092, 0.0, 0.0],
 [1400133577, 89575, 1.244038582, 103.649971, 274.1572266, 6.306981087],
 [1400133485, 90838, 1.215658307, 103.6432114, 0.0, 0.0],
 [1400133532, 92306, 1.254893899, 103.6198502, 0.0, 0.0],
 [1400133533, 92417, 1.24250555, 103.6444702, 91.8999939, 0.100000001],
 [1400133563, 94552, 1.233896732, 103.6358795, 0.0, 0.0],
 [1400133563, 95150, 1.233720064, 103.6268997, 200.2136993, 4.606584072],
]

if cmd=="trails" or (trails_from_markers is not None):
  if trails_from_markers is not None:
    trails=trails_from_markers
    
  import math
  res={}
  for r in trails:
    (ts, vid, lat, lon, course, speed)=r
    
    arr=[]
    n = 1
    if speed>1:
      n=10
      
    for t in range(0,n):
      scale = 0.0003   # 5 min intervals?
      lat_ = lat + t*scale*speed * math.cos(math.radians(course))
      lon_ = lon + t*scale*speed * math.sin(math.radians(course))
      
      arr.append([ts + t*5*60, lat_, lon_, course, speed, vid]) # This is what it should be...
      
    res[vid]=arr
  print "// Future Trails"
  print "// { vid : [ [ts, lat_, lon_, course, speed, vid], ... ], ... }"
  print json.dumps(res)    
  print "\n\n"
  

if cmd=="entry": # or (trails_from_markers is not None):
  if trails_from_markers is not None:
    trails=trails_from_markers

  import math
  res={}
  for r in trails:  # This is the entry version
    (ts, vid, lat, lon, course, speed)=r
    
    c.execute("SELECT ts,vid,lat,lon,course,speed FROM ais WHERE ts>? AND ts<? AND vid=? ORDER BY vid,ts", 
      [v - 24 *60 *60, v, vid]
    )  # X mins

    arr=[]
    #for t in range(0,n):
    for t in c.fetchall():
      (ts_, vid_, lat_, lon_, course_, speed_)=t
      arr.append([ts_, lat_, lon_, course_, speed_, vid_]) # This is what it should be...
      
    res[vid]=arr
    
  print "// Historical Trails"
  print "// { vid : [ [ts, lat_, lon_, course, speed, vid], ... ], ... }"
  print json.dumps(res)    

"""
.schema mv
CREATE TABLE mv (vid INT, 
mvid INT, mvnum INT, 
advice_source CHAR(1), 
advice_ts INT,  start_ts INT, end_ts INT, 
status CHAR(1), 
mv_type CHAR(1), 
mv_open CHAR(1), 
resp_from CHAR(1), resp_to CHAR(1), 
loc_from CHAR(5),  loc_to CHAR(5), 
draft INT, 
ts INT);
"""

# SELECT advice_ts, start_ts, end_ts, loc_from, loc_to FROM mv WHERE ts<1400133600 AND vid=84291;
# SELECT ts,advice_ts, start_ts, end_ts, loc_from, loc_to FROM mv WHERE vid=84291 ORDER BY advice_ts;
# SELECT * FROM ais WHERE vid=84291 ORDER BY ts DESC;  # This one goes everywhere...

# More interesting, 2 trips into SG :
#SELECT ts,advice_ts, start_ts, end_ts, loc_from, loc_to FROM mv WHERE vid=89575 AND advice_ts<1400133600 ORDER BY start_ts DESC;

"""
SELECT ts,advice_ts, start_ts, end_ts, loc_from, loc_to FROM mv WHERE vid=83123 ORDER BY advice_ts;
1393232700|1393189500|1393189440|1393235220|SEAE|SEATP
1393271160|1393271160|1393271160|1393285800|SEATP|SEAW
1398262800|1398200220|1398200220|1398264540|SEAW|SEATP
1398287580|1398287580|1398269580|1398287580|SEATP|SEAE
1399921800|1399784580|1400011200||SEAW|PWBGA

1399951080|1399934100|1399921860|1399952280|SEAE|SEATP

1400054520|1400046720|1400053800|1400053800|SEAW|PWBGA
1400065920|1400065380|1400053800|1400065500|PWBGA|P08
1400116380|1400115900|1400108700|1400115900|P08|SEAW
1403132220|1402629420|1403136000||SEAW|OTHER

1403136360|1403132280|1403136000|1403136000|SEAW|PWBGA
1403144880|1403144460|1403136000|1403144400|PWBGA|P31
1403197920|1403197440|1403193900|1403197500|P31|SEAE
"""



connection.close()
