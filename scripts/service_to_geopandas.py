import requests
import urllib.parse
import json
import geopandas as gpd

# Get token for authentication (if needed)
username = ""
password = ""

tokenURL = 'https://gis.psrc.org/portal/sharing/rest/generateToken'
params = {'f': 'pjson', 'username': username, 'password': password, 'referer': 'https://machine.domain.com'}

data = urllib.parse.urlencode(query=params).encode('utf-8')
req = urllib.request.Request(tokenURL, data)
response = urllib.request.urlopen(req)
data = json.loads(response.read())
token = data['token']
#headers = {'token': data['token'], 'referer': 'https://machine.domain.com', 'expires': data['expires']}

# Service endpoint for PSRC TAZ
SERVICE_URL = ("https://gis.psrc.org/server/rest/services/ElmerGeo/taz2010/FeatureServer/0")
QUERY_URL = f"{SERVICE_URL}/query"

# Streets in the City of Boulder
where = "1=1"

# Determine the total number of records for the given where clause
count_params = {
    'where': '1=1',
    "returnCountOnly": True,
    "f": "json",
    'token': token
}
query_json = requests.get(QUERY_URL, params=count_params).json()
tot_records = query_json["count"]

# Determine the step size for pages
service_json = requests.get(SERVICE_URL, params={'f': 'json', 'token':token}).json()
step = service_json["maxRecordCount"]

# Fields we want in the output
#fields = ('OBJECTID', 'PREFIX', 'NAME', 'STREETTYPE', 'SUFFIX')

# Define query parameters
query_params = {'where': '1=1',
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

# Loop through each page of query results
gdfs = []
for offset in range(0, tot_records, step):
    query_params['resultOffset'] = offset
    offset_query = urllib.parse.urlencode(query_params)
    offset_query_url = f"{QUERY_URL}?{offset_query}"
    offset_gdf = gpd.read_file(offset_query_url)
    gdfs.append(offset_gdf)

# Concatenate the resulting dataframes
gdf = gpd.pd.concat(gdfs, ignore_index=True)

# Verify no OBJECTIDs are duplicated
dups = gdf[gdf['OBJECTID']._duplicated()]
dups.empty