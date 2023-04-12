import tweepy
import pandas as pd
from pandas import ExcelWriter
import os
import tweepy
import time
import sys
import numpy as np
import os
import xlsxwriter
from ast import literal_eval

row = 1388




df = pd.read_csv('feb_cvs.csv')

print(df)
print(df.loc[[row]])

df = df.drop(row)
df = df.reset_index(drop=True)
print(df.loc[[row]])
print("_________________________________________")
df.to_csv('feb_cvs.csv', index=False)
