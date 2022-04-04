#!/usr/bin/env python3

from constants import *
from Holders import *
from Honeypot_dect import *

import requests
from bs4 import BeautifulSoup
import selenium
import sys
#sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from eth_utils import address
import json
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput
from eth_abi.exceptions import InsufficientDataBytes
import asyncio
import time
from web3.middleware import geth_poa_middleware
from datetime import datetime, date,timedelta
import numpy as np
import pandas as pd
import requests

from playwright.sync_api import sync_playwright
from cf_clearance import sync_cf_retry, stealth_sync

from os.path import exists

cookie = "r9GTp4mUVYGCy61P.k9ilXE2eybLFeNBeTJWloJAKvQ-1644989625-0-150"
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4863.0 Safari/537.36"

avax_blockchain = 'https://api.avax.network/ext/bc/C/rpc'
web3_avax = Web3(Web3.HTTPProvider(avax_blockchain))
web3_avax.middleware_onion.inject(geth_poa_middleware, layer=0) # To solve "The field extraData is 97 bytes, but should be 32." error
Traderjoe_contract = web3_avax.eth.contract(address=avax_factory, abi=avax_factory_abi)
print(web3_avax.isConnected())


def get_pair_pool_info (Pair_address):
	
	Pair_loaded = web3_avax.eth.contract(abi = Pair_address_abi, address=Pair_address)
	Pair_reserves = Pair_loaded.functions.getReserves().call()
	
	token0_reserves = web3_avax.fromWei(Pair_reserves[0], 'ether')
	token1_reserves = web3_avax.fromWei(Pair_reserves[1], 'ether')
	
	token0_address = Pair_loaded.functions.token0().call()
	token1_address = Pair_loaded.functions.token1().call()
	
	token0_contact = web3_avax.eth.contract(abi = Pair_address_abi, address=token0_address)
	token1_contact = web3_avax.eth.contract(abi = Pair_address_abi, address=token1_address)
	
	token0_symbol = token0_contact.functions.symbol().call()
	token1_symbol = token1_contact.functions.symbol().call()
	
	print('*******************************************************************************************************')
	print('----- ',token0_symbol,' token 0 : ',token0_reserves,' in USD : ', token1_reserves*508)
	print('----- ',token1_symbol,' token 1 : ',token1_reserves,' in USD : ', token1_reserves*508)
	print(token0_symbol, ' address : ', token0_address)
	print(token1_symbol, ' address : ', token1_address)
	print('Pair address : ', Pair_address)
	print('Time : ', time.ctime())
	
	return token0_symbol,token1_symbol,token0_address,token1_address,Pair_address,time.ctime(),token0_reserves,token1_reserves

def pass_test(input_df,token_info,pair_info,threshold):
	# Step 1:
	df = input_df
	## TODO: token 0 or 1 is WBNB problem; get_token_name
	row = {"token0_symbol": token_info[0], "token0_name": token_info[0], "token1_symbol": token_info[2],
		   "token1_name": token_info[4], "token0_address": token_info[1], "token1_address": token_info[3],
		   "Pair_address": pair_info[4], "time": pair_info[5], "token0_reserves": token_info[5],
		   "token1_reserves": token_info[6]}
	if sum(list(df["token1_symbol"] == token_info[2])) > 0:
		print("1. found same name, don't buy")
		# TODO: If I found same name in my database, skip
	else:
		print("1. Name test passed")
		if token_info[5] < threshold:
			# TODO: add row but set status to 'wait' (set -5)
			print("2. Pool liq less than threshold, waiting, Liq: ", token_info[5])
			row["status"] = -3
			df = df.append(row, ignore_index=True)

		else:
			print("2. Pool liq test passed", token_info[5])
			if avax_playwright_honeypot(token_info[3]) == False:
				# TODO: add row but set stutus to 'don't buy'
				print("3. it's honeypot, don't buy")
				row["status"] = 0
				df = df.append(row, ignore_index=True)

			else:
				print("3. Honeypot test passed")
				# if holders_perc(token_info[3]) == False:
				# 	print("4. Holder test doesn't passed, don't buy", token_info[3])
				# 	row["status"] = 0
				# 	df = df.append(row, ignore_index=True)
				# else:
				# TODO: buy
				print("buy!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
				row["status"] = 1
				df = df.append(row, ignore_index=True)

	print("test 5 df tail 4: ",df.tail(4))
	return df

def check_reserved(input_df, threshold):
	"""
		Input: a panda dataframe

		status convention:
		< 0 : number of left cycles
		0 : don't buy
		1 : buy

		Step 1: find all record with status 'wait'
		Step 2: pull the new liqultiy from blockchain
		Step 3: Check if liqultiy is greater than threshold liquilty
			Step 3.1 If Yes, check for honeypot
				Step 3.1.1 If honeypot: set don't buy, else buy

		Step 4: liqultiy is still smaller, wait but update the wait colume
	"""
	df = input_df
	for i in range(df.shape[0]):
		if df.iloc[i, 10] < 0: # current pair is still on waiting status
			# assume WBNB reserved stored at index 8. the reserved for the other token
			# is stored at 9.
			df.iloc[i, 8], df.iloc[i, 9] = update_reserved(df.iloc[i, 6]) # Step 2: pull the new liqultiy from blockchain; pair addr stored in 6
			if df.iloc[i, 8] >= threshold:
				if honeypot_api(df.iloc[i, 5]):
					print("3.Updated reserved but honeypot, don't buy. Name: ", df.iloc[i, 2])
					df.iloc[i, 10] = 0
				else:
					df.iloc[i, 10] = 1 # Buy
			else:
				print("3.Still no reserve, wait or don't buy till 3 tries. Name: ",df.iloc[i, 2])
				## keep waiting
				df.iloc[i, 10] += 1
	#print("check res:",df.tail(4))
	return df


def update_reserved(addr):
	Pair_loaded = web3_avax.eth.contract(abi=Pair_address_abi, address=addr)
	Pair_reserves = Pair_loaded.functions.getReserves().call()

	token0_address = Pair_loaded.functions.token0().call()
	token1_address = Pair_loaded.functions.token1().call()

	token0_reserves = web3_avax.fromWei(Pair_reserves[0], 'ether')
	token1_reserves = web3_avax.fromWei(Pair_reserves[1], 'ether')
	if WBNB_addr in token0_address:
		return token0_reserves, token1_reserves
	elif WBNB_addr in token1_address:
		# make sure WBNB is always in the front
		return token1_reserves, token0_reserves
	else:
		return 0, 0

def get_token_name (pair_info):
	if pair_info[0] == 'WAVAX':
		WBNB_name = pair_info[0]
		WBNB_address = pair_info[2]
		WBNB_reserves = pair_info[6]
		token_name = pair_info[1]
		token_address = pair_info[3]
		token_reserves = pair_info[7]
		# print('get_tokne_name',pair_info[3])
	else:
		WBNB_name = pair_info[1]
		WBNB_address = pair_info[3]
		WBNB_reserves = pair_info[7]
		token_name = pair_info[0]
		token_address = pair_info[2]
		token_reserves = pair_info[6]
		# print('get_tokne_name',pair_info[2])
	token_Pair_address_abi = json.loads(token_address_abi)

	token_Pair_loaded = web3_avax.eth.contract(abi = token_Pair_address_abi, address=token_address)
	token_full_name = token_Pair_loaded.functions.name().call()
	#print('get_token_name called',WBNB_name,WBNB_address,token_name,token_address,token_full_name)
	return WBNB_name,WBNB_address,token_name,token_address,token_full_name,WBNB_reserves,token_reserves

def main():
	#token0_symbol,token1_symbol,token0_address,token1_address,Pair_address,time.ctime(),token0_reserves,token1_reserves
	#WBNB_name,WBNB_address,token_name,token_address,token_full_name

	if exists('avax_database.csv'):
		df = pd.read_csv("avax_database.csv")
	else:
		df = pd.DataFrame(columns = ["token0_symbol", "token0_name", "token1_symbol", "token1_name", "token0_address", "token1_address", "Pair_address", "time", "token0_reserves", "token1_reserves", "status"])

	counter = 0
	counter2 = 0 # I save the database(df) every hour
	threshold = 5 # 5 avax; roughly 400 USD

	previous_block_num = web3_avax.eth.get_block_number() - 1
	previous_NewPairCreated_allentries = []
	while True:
		try:
			current_block_num = web3_avax.eth.get_block_number()
			if current_block_num - previous_block_num >= 1:
				miss_blocks = list(range(previous_block_num + 1, current_block_num + 1))
				for miss_block in miss_blocks:
					event_filter = Traderjoe_contract.events.PairCreated.createFilter(fromBlock=miss_block)
					#event_filter = Traderjoe_contract.events.PairCreated.createFilter(fromBlock=11860250)
					NewPairCreated_allentries = event_filter.get_all_entries()
					#print("listening")
					if len(NewPairCreated_allentries)>0 and NewPairCreated_allentries[0]['args']['pair'] != previous_NewPairCreated_allentries:
						print(NewPairCreated_allentries)
						previous_NewPairCreated_allentries = NewPairCreated_allentries[0]['args']['pair']
						NewPairCreated_allentries_Pair_address = NewPairCreated_allentries[0]['args']['pair']
						pair_info = get_pair_pool_info(NewPairCreated_allentries_Pair_address)
						token_info = get_token_name(pair_info)
						df = pass_test(df, token_info, pair_info, threshold)


				time.sleep(1)
				if counter == 2 * 30 * 3: # every 1 mins to re-check the reserves of tokens in pair pool
					#print("rechecked called")
					## update the status in df
					df = check_reserved(df, threshold)
					counter = 0
					if counter2 == 2 * 30 * 6: # every 5 mins to save the csv file
						## Update Database
						df.to_csv(r"C:\Users\david\OneDrive\Desktop\App\avax_database.csv", index = False)
						counter2 = 0

				else:
					counter += 2
					counter2 += 2
				previous_block_num = current_block_num
		except KeyboardInterrupt:
			print('keyboard interrupt, stop')
			# df.to_csv(r"C:\Users\david\OneDrive\Desktop\App\avax_database.csv", index = False)
			break
		except ValueError:
			print('ValueError')
			pass
		except (InsufficientDataBytes, BadFunctionCallOutput) :
		 	pass




if __name__ == "__main__":
	main()




