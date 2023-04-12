import numpy
import pandas as pd

#dfs=pd.read_csv("jan_cvsb.csv")
df = pd.read_excel('march_master.xlsx','10_and_up', index_col=0)
df[['followers_ids', 'friends_ids']] = df[['followers_ids', 'friends_ids']].astype(object)

print(df)
print(df.dtypes)

df.to_csv("march_master_10_and_up.csv", index=False)

df1 = pd.read_csv("march_master_10_and_up.csv", dtype={'user_id': 'int64','followers_ids': 'object', 'friends_ids': 'object' })
print(df1)
"""
df1 = pd.read_csv("january/jan_master_15_and_up.csv", dtype={'user_id': 'int64','followers_ids': 'object', 'friends_ids': 'object' })
print(df1)
print(df1.dtypes)
df1.at[0, 'followers_ids'] = ['1','2','3']
print(df1.at[0, 'followers_ids'])
df1.to_csv("january/jan_master_15_and_up.csv", index=False)
print(df1)
df1 = pd.read_csv("january/jan_master_15_and_up.csv", dtype={'user_id': 'int64','followers_ids': 'object', 'friends_ids': 'object' })
print(df1)
"""
