import pandas as pd 
import numpy as np
import requests

public_schools = pd.read_csv(r'C:\Users\cheungr\Desktop\Capstone FIles\Dependencies\public_school_ids.csv', index_col=0)

public_schools.dropna(subset=['PublicSchoolID'],inplace=True)

public_schools['PublicSchoolID'] = public_schools['PublicSchoolID'].astype(int).astype(str)
public_schools['parish_id'] = public_schools['parish_id'].astype(int).astype(str)

# Base URL with filter
base_url = "https://data.wa.gov/resource/rxjk-6ieq.json"
where_clause = (
    "organizationlevel='School' AND county IN "
    "('Whatcom','Skagit','San Juan Island','Snohomish','King','Pierce','Thurston',"
    "'Lewis','Pacific Wahkiakum','Mason','Grays Harbor','Jefferson','Clallam','Cowlitz','Clark')"
)
limit = 1000
offset = 0
all_data = []

while True:
    params = {
        "$where": where_clause,
        "$limit": limit,
        "$offset": offset
    }
    response = requests.get(base_url,params=params)
    data = response.json()
    if not data:
        break
    all_data.extend(data)
    offset += limit
    
df = pd.DataFrame(all_data)

cols_to_drop = ['organizationlevel','county','esdname','esdorganizationid','districtcode','districtname','districtorganizationid',
'schoolname','schoolorganizationid','currentschooltype','dataasof','dat']

df.drop(columns=(cols_to_drop),axis=1,inplace=True)

merged_df = df.merge(public_schools, left_on='schoolcode', right_on='PublicSchoolID',how='left',indicator=True)
merged_df.dropna(subset=['_merge','PublicSchoolID'],inplace=True)

merged_df = merged_df[merged_df['gradelevel']=='All Grades']
merged_df = merged_df.copy()
merged_df['school_id'] = merged_df['school_id'].astype(int).astype(str)

merged_df.drop(columns=['schoolcode', 'gradelevel', '_merge', 'PublicSchoolID'],inplace=True)
merged_df['count'] = 1

cols_to_convert = [col for col in merged_df.columns if col not in ['school_id', 'schoolyear', 'parish_id']]
merged_df[cols_to_convert] = merged_df[cols_to_convert].apply(pd.to_numeric, errors='coerce')


grouped_df = merged_df.groupby(['schoolyear', 'school_id', 'parish_id']).sum(numeric_only=True).reset_index()

public_schools = grouped_df.copy()

public_schools['year'] = public_schools['schoolyear'].str[:4].astype(int)


del df
del merged_df

print(public_schools)