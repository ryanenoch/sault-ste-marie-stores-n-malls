#Dataframe to GeoJSON converter function by Geoff Boeing
#https://geoffboeing.com/2015/10/exporting-python-data-geojson/
def df_to_geojson(df, properties, lat='lat', lon='lng'):
  geojson = {'type': 'FeatureCollection', 'features': []}
  for _, row in df.iterrows():
    feature = {
      'type': 'Feature',
      'properties': {},
      'geometry': {
        'type': 'Point',
        'coordinates': []
      }
    }
    feature['geometry']['coordinates'] = [row[lon], row[lat]]
    for prop in properties:
      feature['properties'][prop] = row[prop]
    geojson['features'].append(feature)
  return geojson