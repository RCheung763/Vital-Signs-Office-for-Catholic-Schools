import pandas as pd

household_counts = pd.read_excel('C:/Users/cheungr/Desktop/Capstone FIles/Master Registered Households.xlsx', engine='openpyxl') 

parishIDs = pd.read_csv('C:/Users/cheungr/Desktop/Capstone FIles/Dependencies/School_Parish_ID.csv')

household_counts = household_counts.drop(household_counts.columns[2:17], axis=1)

household_counts = pd.melt(household_counts, id_vars=['PID', 'Parish'], var_name='year',value_name='count')

household_counts['year'] = household_counts['year'].str.extract(r'(\d{4})')

parish_household_counts = household_counts.merge(parishIDs, on='PID', how='left')

parish_household_counts = parish_household_counts.dropna(subset=['school_id'])

# Change Year
parish_household_counts['academic_year'] = (
    parish_household_counts['year'].astype(int).astype(str) + "-" +
    (parish_household_counts['year'].astype(int) + 1).astype(str).str[-2:]
)


del household_counts
del parishIDs

print(parish_household_counts)

