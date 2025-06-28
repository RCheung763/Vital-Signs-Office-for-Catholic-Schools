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
for year in range(start_year, last_year):
    year = str(year)
    if year not in api_variables.columns:
        print(f"Skipping year {year}")
        continue
    
    # Drop if year is not in the api_variables csv
    year_vars = api_variables[year].dropna().tolist()
    dp_variables = [v for v in year_vars if v.startswith(('DP02', 'DP04', 'DP05'))]

    if not dp_variables:
        continue

    # split into batches
    variable_batches = [
        dp_variables[i:i + variable_batch_size]
        for i in range(0, len(dp_variables), variable_batch_size)
    ]

    zip_batches = [
        zips_list[i:i + zip_batch_size]
        for i in range(0, len(zips_list), zip_batch_size)
    ]

    # The api link
    url = f"https://api.census.gov/data/{year}/acs/acs5/profile"

    # Loop through variable batches
    for var_batch in variable_batches:
        # join once per batch
        var_str = ",".join(var_batch)

        # Loop through zips
        for zip_batch in zip_batches:
            zip_str = ",".join(str(z) for z in zip_batch)
            params = {
                'get': var_str,
                'for': f"zip code tabulation area:{zip_str}",
                'key': api_key
            }

            # The new years after 2020 required state parameters
            if int(year) < 2020:
                params['in'] = 'state:53'

            response = requests.get(url, params=params)

            # Raise and error if the request was not successfull
            #if response.status_code == 200:
                #print(f"Success for {year} vars {var_str} / zips {zip_str} (status {response.status_code})")

            if response.status_code != 200 or not response.text.strip():
                print(f"Failed or empty for vars {var_str} / zips {zip_str} (status {response.status_code})")
            
            data = response.json()

            # Without State parameter
            headers = data[0]
            for row in data[1:]:
                if int(year) >= 2020:
                    estimates = row[:-1]
                    ztca = row[-1]
                    for i, est in enumerate(estimates):
                        rows.append({
                            'variable': headers[i],
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
all_data_15_19 = pd.DataFrame(rows)

rows = []

# Loop through each year
for year in range(start_year_2, current_year):
    year = str(year)
    if year not in api_variables.columns:
        print(f"Skipping year {year}")
        continue
    
    # Drop if year is not in the api_variables csv
    year_vars = api_variables[year].dropna().tolist()
    dp_variables = [v for v in year_vars if v.startswith(('DP02', 'DP04', 'DP05'))]

    if not dp_variables:
        continue

    # split into batches
    variable_batches = [
        dp_variables[i:i + variable_batch_size]
        for i in range(0, len(dp_variables), variable_batch_size)
    ]

    zip_batches = [
        zips_list[i:i + zip_batch_size]
        for i in range(0, len(zips_list), zip_batch_size)
    ]

    # The api link
    url = f"https://api.census.gov/data/{year}/acs/acs5/profile"

    # Loop through variable batches
    for var_batch in variable_batches:
        # join once per batch
        var_str = ",".join(var_batch)

        # Loop through zips
        for zip_batch in zip_batches:
            zip_str = ",".join(str(z) for z in zip_batch)
            params = {
                'get': var_str,
                'for': f"zip code tabulation area:{zip_str}",
                'key': api_key
            }

            # The new years after 2020 required state parameters
            if int(year) < 2020:
                params['in'] = 'state:53'

            response = requests.get(url, params=params)

            # Raise and error if the request was not successfull
            #if response.status_code == 200:
                #print(f"Success for {year} vars {var_str} / zips {zip_str} (status {response.status_code})")

            if response.status_code != 200 or not response.text.strip():
                print(f"Failed or empty for vars {var_str} / zips {zip_str} (status {response.status_code})")
            
            data = response.json()

            # Without State parameter
            headers = data[0]
            for row in data[1:]:
                if int(year) >= 2020:
                    estimates = row[:-1]
                    ztca = row[-1]
                    for i, est in enumerate(estimates):
                        rows.append({
                            'variable': headers[i],
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
all_data_20_now = pd.DataFrame(rows)

all_data = pd.concat([all_data_15_19, all_data_20_now], ignore_index=True)

api_variables_long = pd.melt(api_variables, id_vars=['variable_name'], 
                             value_vars= api_years,
                             var_name='year',
                             value_name='variable_key'
                             )

all_data['year'] = all_data['year'].astype(str)
all_data = all_data.merge(api_variables_long, left_on=['variable', 'year'], right_on=['variable_key', 'year'], how='left')
all_data.drop(columns='variable', inplace=True)
all_data.drop(columns='variable_key', inplace=True)

# Change zip type
all_data['zip'] = all_data['zip'].astype(str)
zips_exploded['zip_codes'] = zips_exploded['zip_codes'].astype(str)

# Merge census data with zips 
merged_df = zips_exploded.merge(all_data, left_on='zip_codes', right_on='zip', how='left')

# Drop redudant columns 
merged_df.drop(columns=['zip_codes', 'census_tracts'], inplace=True)
merged_df['estimate'] = pd.to_numeric(merged_df['estimate'], errors='coerce')

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

del all_data
del all_data_15_19
del all_data_20_now
del api_variables
del api_variables_long
del merged_df
del tract_codes
del zips_exploded
del census_agg

population_data = census_agg_wide.copy()

print(population_data)