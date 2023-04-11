import folium
import streamlit as st
import pandas as pd
import json
from streamlit_folium import st_folium
from folium import plugins
from distance import distance
from df_to_geojson_conv import df_to_geojson

#names of csv files (same filenames will be used later while making GeoJson Files )
file1 = 'ssmstores'
file2 = 'ssmmalls'
#name for the main GeoJson file (to be created later)
filemain = 'SSM'

#dataframes
df1 = pd.read_csv(f'{file1}.csv')
df2 = pd.read_csv(f'{file2}.csv')
frames = [df1, df2]
#concatenating dataframes using concat()
dfmain = pd.concat(frames)

#view the dataset
#print(df1.head())
#print()
#print(df2.head())
#print()
#print(dfmain)
#print()

cols = ['name', 'address']  #select columns other than lat and long
geojson1 = df_to_geojson(df1, cols)  #passing df & columns to function
geojson2 = df_to_geojson(df2, cols)
geojson_main = df_to_geojson(dfmain, cols)

#dumping GeoJSONs into separate files(optional)
output_filename = f'{file1}.js'
with open(output_filename, 'w') as output_file:
  output_file.write('var dataset = ')
  json.dump(geojson1, output_file, indent=2)

output_filename = f'{file2}.js'
with open(output_filename, 'w') as output_file:
  output_file.write('var dataset = ')
  json.dump(geojson2, output_file, indent=2)

output_filename = f'{filemain}.js'
with open(output_filename, 'w') as output_file:
  output_file.write('var dataset = ')
  json.dump(geojson_main, output_file, indent=2)

# center on SSM, add marker
center = [46.5277912, -84.3306842]
m = folium.Map(location=center, zoom_start=14)

#setting up different icons & color for stores & malls
#Link for icons - https://fontawesome.com/v4/
store_marker = folium.Marker(
  icon=folium.Icon(icon='fa-shopping-cart', prefix='fa', color='blue'))
mall_marker = folium.Marker(
  icon=folium.Icon(icon='fa-shopping-bag', prefix='fa', color='red'))

#create GeoJSON objects from each GeoJSON file
store_obj = folium.GeoJson(
  geojson1,
  name="Grocery Stores",
  marker=store_marker,
  tooltip=folium.GeoJsonTooltip(fields=["name", "address"],
                                aliases=["Name", "Address"],
                                localize=True),
).add_to(m)

mall_obj = folium.GeoJson(
  geojson2,
  name="Shopping Malls",
  marker=mall_marker,
  tooltip=folium.GeoJsonTooltip(fields=["name", "address"],
                                aliases=["Name", "Address"],
                                localize=True),
).add_to(m)

main_obj = folium.GeoJson(
  geojson_main,
  name="",
  show=False,  #to hide the markers by default
  tooltip=folium.GeoJsonTooltip(fields=["name", "address"],
                                aliases=["Name", "Address"],
                                localize=True),
).add_to(m)

#Adds option to show user location on map
userloc = plugins.LocateControl(
  auto_start=True,
  flyTo=True,
  enableHighAccuracy=True,
  drawCircle=True,
  drawMarker=True,
  strings={
    "title": "See your current location",
    "popup": "You're within {distance} {unit} from this point"
  }).add_to(m)

#print(userloc)

#User can search for malls & stores within the main GeoJSON object using Search()
main_search = plugins.Search(
  layer=main_obj,
  geom_type='Point',
  placeholder="Search for stores & malls",
  collapsed=True,
  search_label='name'  #search_label is the column you want to search for
).add_to(m)

#This enables user to hide/unhide each category
folium.LayerControl().add_to(m)

#############streamlit portion##################
st.set_page_config(layout="wide")
#col1, col2 = st.columns([3, 2], gap="small")


#with col1:
#Title
st.title('Map of SSM')  #center align?

# call to render Folium map in Streamlit
st_data = st_folium(m,width='95%')
#print('Map Data')
#print(st_data)

if 'center' in st_data:
  lat, lng = (st_data['center']['lat'], st_data['center']['lng'])
  curr_loc = "Coord: {}, {}".format(lat, lng)
  st.text(curr_loc)

  dist_list = []

  for i in range(0, len(geojson_main['features'])):
    name = geojson_main['features'][i]['properties']['name']
    smlat = geojson_main['features'][i]['geometry']['coordinates'][1]
    smlng = geojson_main['features'][i]['geometry']['coordinates'][0]

    #calling distance fn
    dist = distance((lat, lng), (smlat, smlng))

    dist_list.append({'Name': name, 'Distance (km)': dist})

  distdf = pd.DataFrame(dist_list).sort_values('Distance (km)',
                                               ignore_index=True)

  #with col2:
  #Display nearest store/mall as dataframe
  st.write('Nearest Store/Mall')
  st.write(distdf.to_html(index=False,justify='left'), unsafe_allow_html=True)
