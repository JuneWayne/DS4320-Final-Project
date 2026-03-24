import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.float_format', '{:.2f}'.format)

eia = pd.read_csv("data/EIA930_BALANCE_2026_Jan_Jun.csv")
dc = pd.read_csv("data/us_data_centers.csv")

print("=== EIA NUMERICAL COLUMNS ===")
numerical_cols = ['Demand Forecast (MW)', 'Demand (MW)', 'Net Generation (MW)',
                  'Total Interchange (MW)', 'Net Generation (MW) from Coal',
                  'Net Generation (MW) from Natural Gas', 'Net Generation (MW) from Nuclear',
                  'Net Generation (MW) from Solar without Integrated Battery Storage',
                  'Net Generation (MW) from Wind without Integrated Battery Storage']
print(eia[numerical_cols].describe())

print("\n=== DATA CENTERS NUMERICAL COLUMNS ===")
print(dc[['lat', 'lon']].describe())

print("\n=== NULL COUNTS EIA ===")
print(eia[numerical_cols].isnull().sum())

print("\n=== NULL COUNTS DC ===")
print(dc.isnull().sum())