import os
import zipfile
import re
import csv
import pandas as pd
from functools import reduce


# Helpers

def normalize_name(s: str) -> str:
    return re.sub(r'[^0-9A-Za-z]+', '', (s or '')).lower()

def clean_cell(val):
    if isinstance(val, str):
        return val.replace('\r', ' ').replace('\n', ' ').strip()
    return val

def handle_special_zip(zipc: str, inst_raw: str, inst_key: str, cands: pd.DataFrame):
    lower_names = cands['school_name'].str.lower()
    # 1) St. Edward closed permanently
    if 'stedward' in inst_key:
        return None, None
    # 2) Generic steward vs nativity conflict
    if 'steward' in inst_raw:
        return None, None
    if 'nativity' in inst_raw:
        cand = cands[lower_names.str.contains('nativity')]
        if not cand.empty:
            sel = cand.iloc[0]
            return sel['school_id'], sel['school_name']

    # ZIP-specific overrides 
    if zipc == '98006':
        mask = lower_names.str.contains('madeleine') if 'madeleine' in inst_key else lower_names.str.contains('middle')
    elif zipc == '98074':
        mask = lower_names.str.contains('middle')
    elif zipc == '98115':
        if 'our lady of the lake' in inst_raw:
            mask = lower_names.str.contains('our lady of the lake')
        elif 'catherine' in inst_raw:
            mask = lower_names.str.contains('catherine')
        else:
            mask = ~(lower_names.str.contains('our lady of the lake') | lower_names.str.contains('catherine'))
    elif zipc == '98103':
        if 'blanchet' in inst_raw or 'bishop' in inst_raw:
            mask = lower_names.str.contains('blanchet')
        elif 'benedict' in inst_raw:
            mask = lower_names.str.contains('benedict')
        elif 'john' in inst_raw:
            mask = lower_names.str.contains('john')
        else:
            mask = pd.Series(True, index=lower_names.index)
    elif zipc == '98112':
        if 'holy names' in inst_raw:
            mask = lower_names.str.contains('holy names')
        elif 'joseph' in inst_raw:
            mask = lower_names.str.contains('joseph')
        else:
            mask = pd.Series(True, index=lower_names.index)
    elif zipc == '98133':
        if 'christ the king' in inst_raw:
            mask = lower_names.str.contains('christ the king')
        elif 'luke' in inst_raw:
            mask = lower_names.str.contains('luke')
        else:
            mask = pd.Series(True, index=lower_names.index)
    elif zipc == '98208':
        if 'magdalen' in inst_raw:
            mask = lower_names.str.contains('magdalen')
        elif 'murphy' in inst_raw:
            mask = lower_names.str.contains('murphy')
        else:
            mask = pd.Series(True, index=lower_names.index)
    elif zipc == '98503':
        if 'holy family' in inst_raw:
            mask = lower_names.str.contains('holy family')
        elif 'pope john' in inst_raw:
            mask = lower_names.str.contains('pope john')
        else:
            mask = pd.Series(True, index=lower_names.index)
    else:
        return None, None

    subset = cands[mask]
    if not subset.empty:
        sel = subset.iloc[0]
        return sel['school_id'], sel['school_name']
    return None, None

def pick_school(row: pd.Series) -> pd.Series:
    zipc     = str(row.get('Institution Postal Code', '')).strip()
    inst_raw = str(row.get('Institution Name', '')).lower().strip()
    inst_key = normalize_name(inst_raw)

    # exact ZIP
    cands = school_info[school_info['zip_code'] == zipc]
    # 3-digit fallback
    if cands.empty and len(zipc) >= 3:
        cands = school_info[school_info['zip_code'].str.startswith(zipc[:3])]

    # special-case logic
    sid, sname = handle_special_zip(zipc, inst_raw, inst_key, cands)
    if sid or sname:
        return pd.Series({'school_id': sid, 'school_name_info': sname})

    # merge_key match
    match = cands[cands['merge_key'] == inst_key]
    if not match.empty:
        sel = match.iloc[0]
        return pd.Series({'school_id': sel['school_id'], 'school_name_info': sel['school_name']})

    # any remaining candidate
    if not cands.empty:
        sel = cands.iloc[0]
        return pd.Series({'school_id': sel['school_id'], 'school_name_info': sel['school_name']})

    return pd.Series({'school_id': None, 'school_name_info': None})


# 1) Unzip & Merge Yearly Excel → CSV

zip_path    = r'\Data\ulcrum TAP Data.zip'
extract_dir = r'\Data\Fulcrum TAP Data'
raw_dir     = r'\Data\Fulcrum Raw'

if not os.path.exists(extract_dir):
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_dir)

inner_dirs = [d for d in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, d))]
base_dir   = os.path.join(extract_dir, inner_dirs[0]) if len(inner_dirs)==1 else extract_dir
os.makedirs(raw_dir, exist_ok=True)

for year_folder in sorted(os.listdir(base_dir)):
    year_path = os.path.join(base_dir, year_folder)
    if not os.path.isdir(year_path):
        continue

    file_name = f'fulcrum_{year_folder.replace("-","_")}_merged.csv'
    out_path  = os.path.join(raw_dir, file_name)
    if os.path.exists(out_path):
        continue

    excels = [f for f in os.listdir(year_path)
              if f.lower().endswith(('.xlsx','.xls')) and not f.startswith('~$')]
    dfs = []
    for excel in excels:
        try:
            dfs.append(pd.read_excel(os.path.join(year_path, excel), engine='openpyxl', dtype=str))
        except:
            pass
    if not dfs:
        continue

    common_cols = list(reduce(lambda a, b: set(a)&set(b), [df.columns for df in dfs]))
    merged = reduce(lambda L, R: pd.merge(L, R, on=common_cols), dfs)
    if {'Institution Name','Institution Address Line 1'}.issubset(merged.columns):
        merged['year'] = year_folder.replace('-','_')
        merged.to_csv(out_path, index=False)


# 2) Load school_info & Assign IDs

school_info = pd.read_csv(
    r'C:\Users\veetr\OneDrive - Seattle University\Capstone Dashboard\Data\SchoolsAddresses.csv',
    dtype=str
)[['school_name','id','zip_code']].rename(columns={'id':'school_id'})

school_info['merge_key'] = (
    school_info['school_name']
    .str.replace('.', '', regex=False)
    .apply(normalize_name)
)

with_id_dir = r'C:\Users\veetr\OneDrive - Seattle University\Capstone Dashboard\Data\Fulcrum with School ID'
os.makedirs(with_id_dir, exist_ok=True)

for file_name in sorted(os.listdir(raw_dir)):
    if not file_name.startswith('fulcrum_') or not file_name.endswith('.csv'):
        continue

    df = pd.read_csv(os.path.join(raw_dir, file_name), dtype=str)
    df.columns = df.columns.str.strip()
    assigned = df.apply(pick_school, axis=1)
    df = pd.concat([df, assigned], axis=1)
    df.to_csv(os.path.join(with_id_dir, file_name), index=False)

# 3) Clean & Combine; strip "_merged" from year

cleaned_dir = r'\Data\Fulcrum Cleaned'
os.makedirs(cleaned_dir, exist_ok=True)

combined = []
for file_name in sorted(os.listdir(with_id_dir)):
    if not file_name.startswith('fulcrum_') or not file_name.endswith('.csv'):
        continue

    df = pd.read_csv(os.path.join(with_id_dir, file_name), dtype=str)
    df.columns = df.columns.str.strip()
    df = df.applymap(clean_cell)
    df.dropna(how='all', inplace=True)
    df = df[df.apply(lambda r: r.count() >= 3, axis=1)]
    if df.empty:
        continue

    # strip prefix & suffix to isolate year
    year_tag = file_name[len('fulcrum_') : -len('_merged.csv')]
    year_academic = year_tag.replace('_', '-') 
    df['year'] = year_academic

    cleaned_name = f'cleaned_{file_name}'
    df.to_csv(
        os.path.join(cleaned_dir, cleaned_name),
        index=False,
        quoting=csv.QUOTE_ALL,
        lineterminator='\n'
    )
    combined.append(df)

if combined:
    final_df = pd.concat(combined, ignore_index=True)
else:
    final_df = pd.DataFrame()


# Write the master CSV to Fulcrum Cleaned

if not final_df.empty:                       
    master_csv = os.path.join(
        cleaned_dir,
        'fulcrum_all_years_cleaned.csv'      
    )
    final_df.to_csv(
        master_csv,
        index=False,
        quoting=csv.QUOTE_ALL,
        lineterminator='\n'
    )
    print(f'✔ Combined file saved to: {master_csv}')
else:
    print('⚠️ No records to combine—master file not written.')


