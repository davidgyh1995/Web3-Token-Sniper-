#!/usr/bin/env python3

import pandas as pd
#df = pd.DataFrame(columns = ["token0_symbol", "token1_symbol", "token0_address", "token1_address", "Pair_address", "time", "token0_reserves", "token1_reserves", "status"])

try:
	df = pd.read_csv("test2.csv", index_col = False)
except:
	df = pd.DataFrame(columns = ["token0_symbol"])
	
#print(df["token0_symbol"] == "APPLE")

df = df.append({"token0_symbol" : "APPLE"}, ignore_index = True)
df = df.append({"token0_symbol" : "APP"}, ignore_index = True)
#print(df)
print(sum(list(df["token0_symbol"] == "AP")))

##
##
#df.to_csv("test2.csv", index = False)
#def change(df):
#	dict1 = {"A" : 1, "B" : 2}
#	ret = df.append(dict1, ignore_index = True)
#	return ret
#	
#test_df = pd.DataFrame(columns = ["A", "B"])
#print("Before")
#print(test_df)
#test_df = change(test_df)
#print("After")
#print(test_df)