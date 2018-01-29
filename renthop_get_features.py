import json
from collections import Counter

def read_file(filename):
    with open(filename) as f:
        raw_json = f.read()

    data = json.loads(raw_json)

    return data

data = read_file('renthop_manhattan.json')

def get_unique_features(data):
'''
Get the unique features/apartment amenities from the features column in the df
'''
	unique_features =  Counter()

	for apt in data:
		for feature, val in apt.items():
			if feature == 'features':
				for i in range(len(val)):
					stripped_val = val[i].strip()

					if stripped_val in unique_features:
						unique_features[stripped_val] += 1
					else:
						unique_features[stripped_val] = 1

	return [feature for feature, feature_count in unique_features.most_common(50)]

data = read_file('renthop_manhattan.json')
top_50_features = get_unique_features(data)
print(top_50_features)