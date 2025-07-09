import geopandas as gpd
import urllib
import json
import requests
import urllib.parse


username = "arcpro_advanced1"
password = ""

tokenURL = 'https://gis.psrc.org/portal/sharing/rest/generateToken'
params = {'f': 'pjson', 'username': username, 'password': password, 'referer': 'https://machine.domain.com'}

data = urllib.parse.urlencode(query=params).encode('utf-8')
req = urllib.request.Request(tokenURL, data)
response = urllib.request.urlopen(req)

data = json.loads(response.read())
#headers = {'token': data['token'], 'referer': 'https://machine.domain.com', 'expires': data['expires']}
#gdf = gpd.read_file("https://gis.psrc.org/server/rest/services/ElmerGeo/taz2010/FeatureServer/0/query?where=1%3D1&f=geojson", headers=headers, driver='GeoJSON')

token = data['token']

#headers = {'token': token}
params = {'where': '1=1',
		   'geometryType': 'esriGeometryEnvelope',
		   'spatialRel': 'esriSpatialRelIntersects',
		   'relationParam': '',
		   'outFields': '*',
		   'returnGeometry': 'true',
		   'geometryPrecision':'',
		   'outSR': '',
		   'returnIdsOnly': 'false',
		   'returnCountOnly': 'false',
		   'orderByFields': '',
		   'groupByFieldsForStatistics': '',
		   'returnZ': 'false',
		   'returnM': 'false',
		   'returnDistinctValues': 'false',
		   'f': 'geojson',
           'token': token
		   }
params 
encode_params = urllib.parse.urlencode(params).encode("utf-8")
url = "https://gis.psrc.org/server/rest/services/ElmerGeo/taz2010/FeatureServer/0/query?"
response = urllib.request.urlopen(url, encode_params)
json = response.read()
gdf = gpd.read_file(json)








#**********************
username = "arcpro_advanced1"
password = ""

tokenURL = 'https://gis.psrc.org/portal/sharing/rest/generateToken'
params = {'f': 'pjson', 'username': username, 'password': password, 'referer': 'https://machine.domain.com'}

data = urllib.parse.urlencode(query=params).encode('utf-8')
req = urllib.request.Request(tokenURL, data)
response = urllib.request.urlopen(req)

data = json.loads(response.read())
headers = {'token': data['token'], 'referer': 'https://machine.domain.com', 'expires': data['expires']}
url = "https://gis.psrc.org/server/rest/services/ElmerGeo/taz2010/FeatureServer/0/query?where=1%3D1&outFields=*&where=1%3D1&f=geojson"
response = requests.get(url, headers)
gdf = gpd.read_file(response.text, driver='GeoJSON')











url_base = r'https://gis.psrc.org/server/rest/services/ElmerGeo/taz2010/FeatureServer/0/query?'
params = {
    'f': 'geojson',
}
url_final = url_base + urllib.parse.urlencode(params)
response = requests.get(url_final)











headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} # This is chrome, you can set whatever browser you like

QUERY_URL = ("https://gis.psrc.org/server/rest/services/ElmerGeo/taz2010/FeatureServer/0/query?where=1%3D1&outFields=*&where=1%3D1&f=geojson")

gdf = gpd.read_file(QUERY_URL)

url = r'https://gis.psrc.org/server/rest/services/ElmerGeo/waterbodies/FeatureServer/0'










response = urllib.request.urlopen(url, encode_params)
json = response.read()

jsonIO = BytesIO(json)

zones = geopandas.read_file(jsonIO, driver = 'GeoJSON')
print(type(zones))