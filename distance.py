def distance(live_loc,sm_loc):
  import geopy.distance

  #print('Distance (km)')
  dist = round(geopy.distance.geodesic(live_loc, sm_loc).km, 2) #rounded to 2 decimal point

  return dist