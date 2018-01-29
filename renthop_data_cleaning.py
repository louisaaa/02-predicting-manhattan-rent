import pandas as pd
import re
import numpy as np
from pandas.core.index import InvalidIndexError
import json

def read_file(filename):
    with open(filename) as f:
        raw_json = f.read()

    data = json.loads(raw_json)

    return data

def clean_data(data):
	df = pd.DataFrame(data)

	#check if rows = unique number of urls
	#if not equal, get rid of any duplicates by url bc unique apt identifier is url
	if df.shape[0] != df.url.nunique:
		df.drop_duplicates(subset='url', keep='first', inplace=True)

	#there can be 1.5 baths, so make baths a float not an int
	df['baths'] = df['baths'].map(lambda bath: float(bath.split()[0]))

	## need to take into account studio and loft (set that to = 0 beds)
	df['beds'] = df['beds'].map(lambda bed: bed.split()[0])
	df['beds'] = df.apply(lambda bed: 0 if bed['beds'] == 'Studio' or 'Loft' else int(bed['beds']), axis = 1)

	df['hop_score'] = df['hop_score'].map(lambda score: float(score.strip()))

	df['monthly_rent'] = df['monthly_rent'].map(lambda rent: int(re.sub('[$,]', '', rent).strip()))

	df['location2'] = df['location'].map(lambda location: location[0].strip().split(','))
	df['neighborhood'] = df['location2'].map(lambda location: location[0])
	df['borough'] = df['location2'].map(lambda location: location[-1].strip())

	df['sq_ft'] = df.apply(lambda x: np.nan if len(x['sq_ft']) > 13 else int(re.sub('[,]', '', x['sq_ft'].split()[0])), axis=1)

	df['features2'] = df.features.apply(lambda lst: [x.strip() for x in lst])
	
	#list of top 50 features by frequency. see renthop_get_features.py for code to get this list
	features_list = [u'Elevator', u'No Fee', u'Cats Allowed', u'Hardwood Floors', u'Dishwasher', u'Dogs Allowed', u'Doorman', u'Laundry In Building', u'Renovated', u'Light', u'High Ceilings', u'Marble Bath', u'Granite Kitchen', u'Fitness Center', u'Subway', u'Laundry In Unit', u'Pre-war', u'Common Outdoor Space', u'Garage', u'Walk In Closet', u'Valet', u'Eat In Kitchen', u'Concierge', u'Deck', u'Diplomats Ok', u'High Speed Internet', u'Floorplans Available', u'Lounge', u'Outdoor Space', u'Bicycle Room', u'Dining Room', u'City View', u'Open View', u'Laundry in Building', u'Storage', u'Swimming Pool', u'Balcony', u'Stainless Steel Appliances', u'Receiving Room', u'New Construction', u'Exclusive', u'Storage Facility', u'One Month Free', u'Terrace', u'Brownstone', u'Business Center', u'Laundry in Unit', u'Microwave', u'Loft', u'Garden/patio']

	df[features_list] = pd.DataFrame(list(df.features2.apply(lambda x: [1 if f in x else 0 for f in features_list])), index=df.index)
	
	df['closest_subway_distance'] = df.apply(lambda x: np.nan if len(x['subway_station_distances']) == 0 else float(x['subway_station_distances'][0].split()[0]), axis=1)

	#noticed neighborhood = Manhattan for 6 apartments, filled in the correct neighborhood for those listings
	df.iloc[355, 11] = 'Financial District'
	df.iloc[3215, 11] = 'Greenwich Village'
	df.iloc[5427, 11] = 'Financial District'
	df.iloc[5696, 11] = "Hell's Kitchen"
	df.iloc[13041, 11] = 'Kips Bay'
	df.iloc[24767, 11] = 'Financial District'

	neighborhood_mapping = {
		'East Village': 'Downtown',
		"Hell's Kitchen": 'Midtown',
		'Kips Bay': 'Mid-Downtown',
		'Hamilton Heights': 'Uptown',
		'Rose Hill': 'Mid-Downtown',
		'Lincoln Square': 'Uptown',
		'Lower East Side': 'Downtown', 
		'Chelsea': 'Mid-Downtown',
	    'Upper East Side': 'Uptown',
	    'Yorkville': 'Uptown',
	    'Theater District': 'Midtown',
	    'Battery Park City': 'Downtown',
	    'Gramercy Park': 'Mid-Downtown',
	    'East Harlem': 'Uptown',
	    'Financial District': 'Downtown',
	    'Garment District': 'Midtown',
	    'Morningside Heights': 'Uptown',
	    'Flatiron District': 'Mid-Downtown',
	    'Murray Hill': 'Midtown',
	    'Bowery': 'Downtown',
	    'Upper West Side': 'Uptown',
	    'Washington Heights': 'Uptown',
	    'Koreatown': 'Midtown',
	    'Sutton Place': 'Uptown',
	    'Turtle Bay': 'Midtown',
	    'Greenwich Village': 'Downtown',
	    'Inwood': 'Uptown',
	    'Civic Center': 'Downtown',
	    'SoHo':'Downtown',
	    'Alphabet City':'Downtown',
	    'Manhattan Valley':'Uptown',
	    'Tribeca':'Downtown',
	    'Central Harlem':'Uptown',
	    'West Village':'Downtown',
	    'Roosevelt Island': 'Midtown',
	    'NoMad': 'Mid-Downtown',
	    'NoLita': 'Downtown',
	    'Lenox Hill': 'Uptown',
	    'Carnegie Hill': 'Uptown',
	    'NoHo':'Downtown',
	    'Midtown East':'Midtown',
	    'Manhattanville':'Uptown',
	    'Hudson Square':'Downtown',
	    'Chinatown':'Downtown',
	    'Hudson Heights':'Uptown',
	    'Tudor City':'Midtown',
	    'Fort George':'Uptown',
	    'Manhattan': 'No neighborhood',
	    'Central Park': 'Midtown',
	    'Little Italy':'Downtown',
	    'Two Bridges':'Downtown',
	    'Little Senegal':'Uptown',
	    'Hunters Point': np.nan, #not in Manhattan
	    'Cooperative Village': 'Downtown',
	    'Governors Island': 'Downtown',
	    'Cobble Hill' : np.nan, #not in Manhattan
	    'USA': np.nan #these apartments did not have any info
 	}

 	df['area'] = df['neighborhood'].map(neighborhood_mapping)
 	df_area = pd.get_dummies(df['area'])
 	df = df.join(df_area)

 	df.drop(['location', 
         'features', 
         'name',  
         'subway_station_distances', 
         'url', 
         'location2', 
         'neighborhood',
         'borough',
         'features2',
         'area',
         'Mid-Downtown' #drop Mid-Downtown so we do not fall into the dummy variable trap (can calulate whether apartment is in Mid-Downtown if not in the other 3 areas)
        ], axis=1, inplace = True)

	df.dropna()

	df.to_csv('clean_data.csv')

data = read_file('renthop_manhattan.json')
clean_data(data)
