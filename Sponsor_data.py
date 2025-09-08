import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os
from scipy.stats import entropy
import re
import sys

# Read in old financial data
fy_df = pd.read_csv(r'Financial_Data_Combined.csv',index_col=0)

# Read in new financial data
excel_file = pd.ExcelFile(r'School_PL2.xlsx', engine='openpyxl')

# Get first sheet name
first_sheet = excel_file.sheet_names[0]

# Read the data from that sheet
skip_rows = [0,1,4,5,6,7]
df = pd.read_excel(excel_file, sheet_name=first_sheet, skiprows=skip_rows)

df.rename(columns={
    'For the Fiscal Year Ending:':'category'
}, inplace=True)

df.drop(columns=['Unnamed: 58', 'Unnamed: 1'],axis=1,inplace=True)

keep_cols=('category', 1002, 1004, 1005, 1006, 1008, 1009, 1010, 1014, 1015, 1016, 1017,
       1019, 1021, 1022, 1023, 1024, 1026, 1028, 1032, 1033, 1039, 1040,
       1043, 1044, 1045, 1046, 1049, 1051, 1060, 1061, 1062, 1066, 1068,
       1071, 1076, 1079, 1083, 1086, 1091, 1094, 1099, 1100, 1104, 1108,
       1122, 1135, 1115, 1119, 1128, 1139, 1140, 1147, 1150, 1152, 1155)

df = df.loc[:, df.columns.isin(keep_cols)]

text = df.iloc[0,0]

match = re.search(r'\b(\d{4})\b', text)
if match:
    year = match.group(1)
    if year in fy_df['year'].astype(str).values:
        raise RuntimeError(f"Year {year} found in dataframe. Stopping execution.")

# Aggregation

# Revenue
tuition_fees_finaid_scholarships=('4201.8','4202.8','4203.8','4204.8','4205.8','4206.8','4207.8','4210.8','4211.8','4212.8','4213.8',
'4214.8','4215.8','4217.8')

gift_revenue_44xx=('4401.8','4405.8','4407.8','4409.8','4430.8','4450.8','4451.8','4452.8','4453.8','4454.8','4458.8','4470.8')

parish_support_direct=('4225.8',)

bequests=('4402.8','4403.8','4404.8')

business_revenue_45xx=('4501.8','4503.8','4507.8','4510.8','4511.8','4512.8','4522.8','4524.8','4525.8','4526.8','4527.8','4535.8','4538.8',
'4550.8','4571.8','4572.8','4573.8','4579.8')

neighboring_par_support=('4230.8',)

fundraising_parents_club=('4250.8','4310.8','4311.8','4312.8','4313.8','4314.8','4315.8','4316.8','4317.8','4318.8','4319.8','4320.8',
'4321.8','4322.8','4330.8','4331.8','4332.8','4333.8','4334.8','4340.8','4341.8','4321.8','4343.8','4350.8')

all_other_revenue=('4101.8','4102.8','4103.8','4104.8','4105.8','4120.8','4121.8','4140.8','4160.8','4170.8','4199.8','4219.8','4227.8',
'4251.8','4252.8','4253.8','4254.8','4255.8','4270.8','4271.8','4272.8','4273.8','4280.8','4299.8','4601.8','4602.8','4603.8','4604.8',
'4701.8','4702.8','4703.8','4704.8','4705.8','4720.8','4721.8','4722.8','4723.8','4730.8','4735.8','4737.8','4750.8','4760.8')

# Expenses
salaries_51xx=('5101.8','5102.8','5103.8','5105.8','5110.8','5115.8','5116.8','5120.8','5121.8','5122.8','5123.8','5124.8','5125.8','5126.8',
'5127.8','5130.8','5132.8','5134.8','5136.8','5138.8','5140.8','5142.8','5150.8','5152.8','5153.8','5155.8','5160.8','5161.8','5162.8','5170.8')

benefits_52xx=('5201.8','5202.8','5207.8','5208.8','5209.8','5210.8','5220.8','5221.8','5222.8','5223.8','5224.8','5225.8','5230.8','5232.8',
'5234.8','5235.8','5236.8','5237.8','5239.8','5241.8','5242.8','5245.8','5247.8','5270.8')

depreciation_bad_debts_62xx=('6201.8','6202.8','6203.8','6204.8','6220.8')

fundraising_expense_6180=('6180.8',)

interest_expense_6106_6106=('6105.8','6106.8')

utilities=('6301.8','6302.8','6303.8','6305.8','6309.8','6310.8','6311.8','6312.8','6313.8','6315.8','6350.8')

repairs_maintenance_58xx=('5801.8','5802.8','5804.8','5805.8','5830.8','5831.8','5832.8','5833.8','5834.8','5835.8','5836.8','5837.8','5838.8',
'5839.8','5851.8','5852.5','5853.8','5854.8','5860.8')

supplies=('5501.8','5502.8','5503.8','5504.8','5505.8','5506.8','5507.8','5508.8','5509.8','5510.8','5515.8','5516.8','5517.8',
'5519.8','5518.8','5520.8','5521.8','5522.8','5523.8','5524.8','5525.8','5526.8','5527.8','5528.8','5529.8','5530.8','5531.8',
'5540.8','5541.8','5542.8','5545.8','5550.8','5551.8','5552.8','5553.8','5560.8','5565.8','5570.8','5571.8','5572.8','5573.8','5574.8',
'5575.8','5576.8','5577.8','5578.8','5579.8','5580.8','5585.8','5586.8','5587.8','5589.8','5592.8','5595.8','5599.8')

program_expenses=('5701.8','5702.8','5703.8','5704.8','5705.8','5706.8','5726.8','5727.8','5728.8','5729.8','5740.8','5741.8','5760.8','5770.8',
'5780.8','5781.8','5782.8','5783.8','5790.8','5791.8','5792.8','5793.8')

contracted_services=('5901.8','5905.8','5906.8','5910.8','5911.8','5912.8','5913.8','5914.8','5915.8','5916.8','5918.8',
'5919.8','5920.8','5921.8','5922.8','5923.8','5940.8','5941.8','5942.8','5943.8','5945.8','4946.8','5950.8','5960.8','5961.8',
'5970.8','5971.8','5972.8','5973.8')

all_other_expenses=('6101.8','6107.8','6109.8','6120.8','6125.8','6130.8','6131.8','6132.8','6133.8','6134.8','6135.8','6136.8','6137.8',
'6138.8','6139.8','6140.8','6145.8','6160.8','6161.8','6162.8','6163.8','6164.8','6167.8','6170.8','6175.8','6181.8','6182.8',
'6183.8','6184.8','6185.8','6186.8','6187.8','6188.8','6189.8','6190.8','6191.8','6199.8','6401.8','6402.8','6403.8','6404.8','6405.8',
'6410.8','6415.8','6430.8','6450.8','6501.8','6502.8','6503.8','6504.8','6510.8','6520.8','6530.8','6531.8','6550.8','6603.8','6604.8',
'6605.6','6606.8','6660.8','6671.8','6690.8')

total_revenue_80=('TOTAL REVENUES (80)',)

total_expenses_80=('TOTAL EXPENDITURES (80)',)

net_program_80=('SURPLUS/DEFICIT (80)',)

category_groups ={
    # Revenue
    'tuition_fees_finaid_scholarships':tuition_fees_finaid_scholarships,
    'parish_support_direct':parish_support_direct,
    'neighboring_par_support':neighboring_par_support,
    'fundraising_parents_club':fundraising_parents_club,
    'bequests':bequests,
    'gift_revenue_44xx':gift_revenue_44xx,
    'business_revenue_45xx':business_revenue_45xx,
    'all_other_revenue':all_other_revenue,
    # Expenses
    'salaries_51xx':salaries_51xx,
    'benefits_52xx':benefits_52xx,
    'supplies':supplies, 
    'repairs_maintenance_58xx':repairs_maintenance_58xx,  
    'program_expenses':program_expenses,
    'contracted_services':contracted_services,
    'fundraising_expense_6180':fundraising_expense_6180,
    'interest_expense_6106_6106':interest_expense_6106_6106,
    'fundraising_expense_6180':fundraising_expense_6180,
    'utilities':utilities,
    'depreciation_bad_debts_62xx':depreciation_bad_debts_62xx,
    'all_other_expenses':all_other_expenses,
    'all_other_expenses':all_other_expenses,
     'total_expenses_80':total_expenses_80,   
    'total_revenue_80':total_revenue_80,
    'net_program_80':net_program_80
}


aggregated = pd.DataFrame()

school_cols = df.columns[df.columns != 'category']
df[school_cols] = df[school_cols].apply(pd.to_numeric, errors='coerce')
df['category'] = df['category'].astype(str)

for group_name, codes in category_groups.items():
    pattern = '|'.join(map(re.escape, codes)) 
    filtered = df[df['category'].str.contains(pattern, na=False, regex=True)]
    
    group_sum = filtered[school_cols].sum().to_frame().T
    group_sum.index = [group_name]
    
    aggregated = pd.concat([aggregated, group_sum])

aggregated = aggregated.fillna(0)

df_transposed = aggregated.T.reset_index().rename(columns={'index':'school_id'})
df_transposed['year']=year

new_df = pd.concat([fy_df, df_transposed], axis=0, ignore_index=True)

# Enter old financial data file path
new_df.to_csv(r'C:/Users/cheungr/Desktop/Capstone FIles/Financial_Data_Combined.csv')

dm_fall = pd.read_excel(r'C:/Users/cheungr/Desktop/Capstone FIles/DataMaster2.xlsx', sheet_name='Fall', engine='openpyxl')

dm_schoolcity = pd.read_excel(r'C:/Users/cheungr/Desktop/Capstone FIles/DataMaster2.xlsx', sheet_name='SchoolCity', engine='openpyxl')

# Drop if schoolID is a NaN in both files
dm_fall = dm_fall.dropna(subset='schoolID').copy()
dm_schoolcity = dm_schoolcity.dropna(subset='schoolID').copy()

# Changed school ID data type 
dm_fall['schoolID'] = dm_fall['schoolID'].astype('int').astype(str)
dm_schoolcity['schoolID'] = dm_schoolcity['schoolID'].astype('int').astype(str)

dm_fall['Year'] = dm_fall['Year'].astype('int').astype(str)

# Split the column type into three separate columns
dm_schoolcity[['type', 'level', 'name']]= dm_schoolcity['Type'].str.split(",", n = 2, expand=True)

dm_schoolcity['type'] = dm_schoolcity['type'].str.replace(r'Type:\s*', '', regex=True)

# Merge schoolcity with fall sheet
merged_data_master = dm_schoolcity.merge(dm_fall, on=['schoolID'], how='left')

# Impute missing capacity
merged_data_master['TS-Capacity'] = merged_data_master.groupby('schoolID')['TS-Capacity'].transform(
    lambda x: x.mask(x == 0, x[x!=0].mean())
)

# Check the number of pre-k in financial dataset, 57 schools
pre_ks = pd.DataFrame(fy_df['school_id'].unique(), columns=['school_id'])

types = merged_data_master[['schoolID', 'type']].rename(columns={'schoolID': 'school_id'}).drop_duplicates()

merged_types = pre_ks.merge(types, on="school_id", how="left")

print(merged_types['type'].value_counts())

prek_ids = merged_types[merged_types['type']=="Pre-K"]['school_id']

# Drop Pre-k from 
fy_df = fy_df[~fy_df['school_id'].isin(prek_ids)]

# Drop rows
cleaned_merged_data_master = merged_data_master.drop(['OSPI ID', 'District of Record', 'NameCity', 'Region', 'Leader', 'Category', 'Principal_x', 'Pemail', 'Virtual', 'Parish', 'Interparish', 
                                              'Diocesan', 'RelCon/Priv', 'Zero','SchEmail', 'G9', 'CapG9', 'G10', 'CapG10', 'G11','CapG11', 'G12', 'CapG12', 'President' , 
                                              'AsstPrincipal', 'Counselor', 'TAide', 'Librarian', 'OtherStaff', 'TS-Non-Hispanic', 'TPS-Hispanic', 'TPS-Non-Hispanic',
                                              'TPS-Race', 'Tuition-HS', 'StCertFT', 'TRetention', 'ISVisa', 'E-Rate-app', 'WaitList', 'DiversePlan', 'Board', 
                                              'ZSpace', 'S-NA-C','S-NA-NC','S-A-C','S-A-NC','S-B-C','S-B-NC','S-H-C','S-H-NC','S-W-C','S-W-NC','S-M-C','S-M-NC','S-U-C','S-U-NC','S-Hisp-C','S-Hisp-NC', 
                                              'S-NHisp-C', 'S-NHisp-NC', 'Hispanic-White', 'Principal_y', 'CTPreK', 'PreK-to-K', 'PreK2', 'PreK3', 'PreK4', 'CapPre-K', 'CapK', 'CapG1', 'CapG2', 'CapG3', 'CapG4', 'CapG5', 'CapG6', 'CapG7',
                                              'CapG8'], axis=1)

cleaned_merged_data_master = cleaned_merged_data_master.drop(columns=merged_data_master.columns[merged_data_master.columns.str.startswith("PS-")])

new_df['year']=new_df['year'].astype(str)
new_df['school_id']=new_df['school_id'].astype(str)

cleaned_merged_data_master['Year'] = cleaned_merged_data_master['Year'].astype(str)
cleaned_merged_data_master['schoolID'] = cleaned_merged_data_master['schoolID'].astype(str)

# Merge the datamaster with the financial year 
merged_fy_dm = new_df.merge(cleaned_merged_data_master, right_on=['schoolID', 'Year'], left_on=['school_id', 'year'], how='left')

# Drop St. Edward
merged_fy_dm = merged_fy_dm.dropna(subset=['schoolID'])

final_df = merged_fy_dm.copy()

# Change variable type 
final_df['Year'] = final_df['Year'].astype(int)
final_df['Year']

# Impute Capacity using interpolation
final_df['TS-Capacity'] = final_df['TS-Capacity'].replace(0, np.nan)

final_df['TS-Capacity'] = final_df.groupby('school_id')['TS-Capacity'].transform(lambda group: group.interpolate())

# Impute Tuition using interpolation
final_df['T-Parish'] = final_df['T-Parish'].replace(0, np.nan)

final_df['T-Parish'] = final_df.groupby('school_id')['T-Parish'].transform(lambda group: group.interpolate())

# Calculate Entropy 
rev_cols = ['parish_support_direct', 'neighboring_par_support',
       'fundraising_parents_club', 'bequests', 'gift_revenue_44xx',
       'business_revenue_45xx', 'all_other_revenue']

# Calculate Entropy 
rev_cols = ['parish_support_direct', 'neighboring_par_support',
       'fundraising_parents_club', 'bequests', 'gift_revenue_44xx',
       'business_revenue_45xx', 'all_other_revenue']

# Normalize
row_probs = final_df[rev_cols].div(final_df[rev_cols].sum(axis=1), axis=0)

# Replace Nas
row_probs = row_probs.fillna(0)

# Replace 0 with a very small number to avoid log(0)
row_probs_clipped = row_probs.clip(lower=1e-12)

# Compute
final_df['rev_entropy'] = row_probs_clipped.apply(lambda row: entropy(row, base=2), axis=1)

# # Percentage change of repairs
final_df = final_df.sort_values(by=['school_id', 'Year'])

# % change
final_df['pct_change_repairs'] = final_df.groupby('school_id')['repairs_maintenance_58xx'].pct_change()

# Extract region 
final_df['Region'] = final_df['name'].str.split(',').str[0].str.replace('Region', '', regex=False).str.strip()

# Normalizing by enrollment and totals
financial_categories = [
    # Revenue components
    'tuition_fees_finaid_scholarships', 'parish_support_direct', 'neighboring_par_support',
    'fundraising_parents_club', 'bequests', 'gift_revenue_44xx', 'business_revenue_45xx',
    'all_other_revenue', 'total_revenue_80',
    
    # Expense components
    'salaries_51xx', 'benefits_52xx', 'supplies', 'repairs_maintenance_58xx',
    'program_expenses', 'contracted_services', 'interest_expense_6106_6106',
    'fundraising_expense_6180', 'utilities', 'depreciation_bad_debts_62xx',
    'all_other_expenses', 'total_expenses_80',

]

# All financial categories are normalized by enrollment to account for different sizes of schools, retains interpretability as opposed to scaling using z-score
for var in financial_categories:
    final_df[f'{var}_per_student']  = final_df[var]/final_df['TS-Enrollment']

grade_categories = [

    # Grades
    'Pre-K','GK','G1','G2','G3','G4','G5','G6','G7','G8'
]
for var in grade_categories:
    final_df[f'{var}_per_grade']  = final_df[var]/final_df['TS-Grade']

race_categories = [

    # Student races
    'S-NA','S-A','S-B','S-H','S-W','S-M','S-U'
]
for var in race_categories:
    final_df[f'{var}_per_race']  = final_df[var]/final_df['TS-Race']

# Catholic percentage
final_df['TPS-Catholic_percentage'] = final_df['TPS-Catholic']/(final_df['TPS-Catholic']+final_df['TPS-Non-Catholic'])
final_df['TPS-Non-Catholic_percentage'] = final_df['TPS-Non-Catholic']/(final_df['TPS-Catholic']+final_df['TPS-Non-Catholic'])

# Percentage of full/part-time 
final_df['TPS-FullTime_percentage'] = final_df['TPS-FullTime']/(final_df['TPS-Employment'])
# Percentage of full/part-time 
final_df['TPS-PartTime_percentage'] = final_df['TPS-PartTime']/(final_df['TPS-Employment'])

# Percentage Capacity
final_df['perc_capacity'] = final_df['TS-Enrollment']/final_df['TS-Capacity']

# Staff to Student ratio
final_df['staff_student_ratio'] = final_df['TPS-Employment']/final_df['TS-Enrollment']

del aggregated
del cleaned_merged_data_master
del df
del df_transposed
del dm_fall 
del dm_schoolcity
del filtered
del fy_df
del group_sum
del merged_data_master
del merged_fy_dm
del merged_types
del new_df
del pre_ks
del row_probs
del row_probs_clipped
del types

dataset = final_df.copy()

del final_df  
print(dataset)


