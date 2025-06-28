import pandas as pd
import numpy as np
from census import Census
from us import states
import requests
import time
from datetime import datetime
import urllib.parse


######################
# Read in dataset with zip codes for each parish 
tract_codes = pd.read_excel(r'C:\Users\cheungr\Desktop\Capstone FIles\Dependencies\parish_tracts_zips.xlsx')
######################

# Explode to create and array of all zips
tract_codes['zip_codes'] = tract_codes['zip_codes'].astype(str).apply(lambda x: list(set(x.split(','))))

zips_exploded = tract_codes.explode('zip_codes').reset_index(drop=True)
zips_list = zips_exploded['zip_codes'].unique()

#####################
# Read in variable labels and keys for each year
api_variables = pd.read_csv(r'C:\Users\cheungr\Desktop\Capstone FIles\Dependencies\API_variables.csv')
#####################

api_variables.columns = [str(col) for col in api_variables.columns]

api_years = [str(col) for col in api_variables.columns[1:]]

# Parameters
api_key = 'b57979c3aa135040be060824bfd78feeb9502fab'
start_year = 2015
last_year = 2020
start_year_2 = 2020
current_year = (datetime.now().year) -1

# Batching the zips and variables to prevent errors
zip_batch_size = 5
variable_batch_size = 5

rows = []

# Loop through each year
for year in range(start_year, current_year):
    year = str(year)

    if year not in api_variables.columns:
        print(f"Skipping year {year}")
        continue

    year_variables = api_variables[year].dropna().tolist()

    # There is only one variable pulls
    sc_variables = [var for var in year_variables if var.startswith('S1903')]
    print(f"For {year} variables: {sc_variables} length {len(sc_variables)}")

    zip_batches = [
        zips_list[i:i + zip_batch_size]
        for i in range(0, len(zips_list), zip_batch_size)
    ]


    for zips in zip_batches:
        for zip_code in zips:
                for variable in sc_variables:
                    url = f'https://api.census.gov/data/{year}/acs/acs5/subject'
                
                    if int(year) >= 2020:
                        params = {
                            'get': variable,
                            'for': f"zip code tabulation area:{zip_code}",
                            'key': api_key
                        }
                        response = requests.get(url, params=params)
                    else:
                        params = {
                            'get': variable,
                            'for': f"zip code tabulation area:{zip_code}",
                            'in': 'state:53',
                            'key': api_key
                        }
                        response = requests.get(url, params=params)

                    if response.status_code == 200:

                        if not response.text.strip():
                            print(f"Empty for {zip_code} in {year} for variables {variable}")
                            continue

                        data = response.json()

                        headers = data[0]
                        for row in data[1:]:
                            if int(year) >= 2020:
                                est, ztca = row[:3]
                                rows.append({
                                    'variable': headers[0],
                                    'estimate': est,
                                    'zip': ztca,
                                    'year': year
                                    })
                            else:
                                estimates = row[:-2]
                                ztca = row[-1]
                                for i, est in enumerate(estimates):
                                    rows.append({
                                        'variable': headers[i],
                                        'estimate': est,
                                        'zip': ztca,
                                        'year': year
                                        })
                                    

# build DataFrame once at the end
all_inc_data = pd.DataFrame(rows)

all_inc_data['variable_name'] = 'med_inc_all_households'

all_inc_data.loc[all_inc_data['estimate'].astype(int) < 0, 'estimate'] = np.nan

# Change zip type
all_inc_data['zip'] = all_inc_data['zip'].astype(str)
zips_exploded['zip_codes'] = zips_exploded['zip_codes'].astype(str)

# Merge census data with zips 
merged_df = zips_exploded.merge(all_inc_data, left_on='zip_codes', right_on='zip', how='left')

# Drop redudant columns 
merged_df.drop(columns=['zip_codes', 'census_tracts'], inplace=True)
merged_df['estimate'] = pd.to_numeric(merged_df['estimate'], errors='coerce')

merged_df['estimate'] = merged_df['estimate'].fillna(merged_df.groupby(['parish_id', 'year'])['estimate'].transform('mean'))

# Aggregrate data
census_agg = merged_df.groupby(['parish_id', 'year', 'variable_name']).agg({
    'estimate': 'mean'
}).reset_index()

# Change Year
census_agg['academic_year'] = (
    census_agg['year'].astype(int).astype(str) + "-" +
    (census_agg['year'].astype(int) + 1).astype(str).str[-2:]
)


census_agg_wide = census_agg.pivot(index=['academic_year', 'parish_id', 'year'], 
                   columns='variable_name', 
                   values='estimate').reset_index()

del all_inc_data
del api_variables
del merged_df
del tract_codes
del zips_exploded
del census_agg

income_data = census_agg_wide.copy()

print(income_data)