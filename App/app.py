#!/usr/bin/env python3

from constants import *
from Holders import *

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

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
wd = webdriver.Chrome(r'C:\Users\david\OneDrive\Desktop\App\chromedriver.exe', options=chrome_options)

bsc_blockchain = 'https://bsc-dataseed.binance.org/'
web3_bsc = Web3(Web3.HTTPProvider(bsc_blockchain))
web3_bsc.middleware_onion.inject(geth_poa_middleware, layer=0) # To solve "The field extraData is 97 bytes, but should be 32." error
pancake_contract = web3_bsc.eth.contract(address=pancake_factory, abi=pancake_factory_abi)

def get_pair_pool_info (Pair_address):
	
	Pair_loaded = web3_bsc.eth.contract(abi = Pair_address_abi, address=Pair_address)
	Pair_reserves = Pair_loaded.functions.getReserves().call()
	
	token0_reserves = web3_bsc.fromWei(Pair_reserves[0], 'ether') 
	token1_reserves = web3_bsc.fromWei(Pair_reserves[1], 'ether') 
	
	token0_address = Pair_loaded.functions.token0().call()
	token1_address = Pair_loaded.functions.token1().call()
	
	token0_contact = web3_bsc.eth.contract(abi = Pair_address_abi, address=token0_address)
	token1_contact = web3_bsc.eth.contract(abi = Pair_address_abi, address=token1_address)
	
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

def get_token_name (pair_info):
	if pair_info[0] == 'WBNB':
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

	token_Pair_loaded = web3_bsc.eth.contract(abi = token_Pair_address_abi, address=token_address)
	token_full_name = token_Pair_loaded.functions.name().call()
	#print('get_token_name called',WBNB_name,WBNB_address,token_name,token_address,token_full_name)
	return WBNB_name,WBNB_address,token_name,token_address,token_full_name,WBNB_reserves,token_reserves

def get_token_price():
	WBNB =   '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'
	token1 = '0xC9882dEF23bc42D53895b8361D0b1EDC7570Bc6A'
	#token1 = '0x4fd87Df4D164D11F4e7C7A490C0748b5C7a0B764'
	pancake_routerV2 = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
	pancake_routerV2_abi = json.loads(pancake_routerV2_abi_str)
	pancake_contract = web3_bsc.eth.contract(address=pancake_routerV2, abi=pancake_routerV2_abi)
	oneToken = Web3.toWei(1, 'Ether')
	#print(oneToken)
	#price = pancake_contract.functions.getAmountsOut(oneToken, [token1,WBNB]).call()
	price = pancake_contract.functions.getAmountsIn(oneToken, [token1,WBNB]).call()
	price = price[1]**2/price[0]
	price = price/oneToken
	return price
	
def honeypot(addr):
	url = "https://honeypot.is/?address=" + addr
	wd.get(url)
	Transcations = WebDriverWait(wd,30).until(EC.visibility_of_all_elements_located((By.ID,'shitcoin')))
	# print(Transcations[0].text)
	if len(Transcations) == 0:
		print("Oops! Cannot open the url")
	else:
		s = Transcations[0].text
		if "Yup, honeypot. Run the fuck away." in s:
			return True
		elif "Does not seem like a honeypot." in s:
			return False
		else:
			# Website cannot decide.
			return None

def honeypot_api(addr):
	url = 'https://aywt3wreda.execute-api.eu-west-1.amazonaws.com/default/IsHoneypot?chain=bsc2&token={}'.format(addr)

	url_json = requests.get(url).json()

	if url_json['IsHoneypot'] == True:
		return True
	elif url_json['IsHoneypot'] == False:
		return False
	else:
		# Website cannot decide.
		return None
		
def update_reserved(addr):
	Pair_loaded = web3_bsc.eth.contract(abi = Pair_address_abi, address=addr)
	Pair_reserves = Pair_loaded.functions.getReserves().call()
	
	token0_address = Pair_loaded.functions.token0().call()
	token1_address = Pair_loaded.functions.token1().call()
	
	token0_reserves = web3_bsc.fromWei(Pair_reserves[0], 'ether') 
	token1_reserves = web3_bsc.fromWei(Pair_reserves[1], 'ether')
	if WBNB_addr in token0_address:
		return token0_reserves, token1_reserves
	elif WBNB_addr in token1_address:
		# make sure WBNB is always in the front
		return token1_reserves, token0_reserves 
	else:
		return 0, 0
	
	
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
				

def main():
	#token0_symbol,token1_symbol,token0_address,token1_address,Pair_address,time.ctime(),token0_reserves,token1_reserves
	#WBNB_name,WBNB_address,token_name,token_address,token_full_name
	
#	df = pd.read_csv("database.csv")
	try: 
		df = pd.read_csv("database.csv")
	except:
		df = pd.DataFrame(columns = ["token0_symbol", "token0_name", "token1_symbol", "token1_name", "token0_address", "token1_address", "Pair_address", "time", "token0_reserves", "token1_reserves", "status"])
	
	counter = 0
	counter2 = 0 # I save the database(df) every hour
	threshold = 10 # 10 wbnb; roughly 4000 USD
	while True:
		try:
			event_filter = pancake_contract.events.PairCreated.createFilter(fromBlock='latest')
			NewPairCreated_allentries = event_filter.get_all_entries()
			#print(NewPairCreated_allentries)
			print("listening")
			if len(NewPairCreated_allentries)>0 :
				NewPairCreated_allentries_Pair_address = NewPairCreated_allentries[0]['args']['pair']
				pair_info = get_pair_pool_info(NewPairCreated_allentries_Pair_address)
				token_info = get_token_name(pair_info)
				# Step 1:
				## TODO: token 0 or 1 is WBNB problem; get_token_name
				row = {"token0_symbol" : token_info[0], "token0_name" : token_info[0], "token1_symbol" : token_info[2], "token1_name" : token_info[4], "token0_address" : token_info[1], "token1_address" : token_info[3], "Pair_address" : pair_info[4], "time" : pair_info[5], "token0_reserves" : token_info[5], "token1_reserves" : token_info[6]}
				if sum(list(df["token1_symbol"] == token_info[2])) > 0:
					print("1. found same name, don't buy")
					# TODO: If I found same name in my database, skip
					pass
				else:
					print("1. Name test passed")
					if token_info[5] < threshold:
						# TODO: add row but set status to 'wait' (set -5)
						print("2. Pool liq less than threshold, waiting, Liq: ",token_info[5])
						row["status"] = -3
						df = df.append(row, ignore_index = True)

					else:
						print("2. Pool liq test passed",token_info[5])
						if honeypot_api(token_info[1]):
							# TODO: add row but set stutus to 'don't buy'
							print("3. it's honeypot, don't buy")
							row["status"] = 0
							df = df.append(row, ignore_index = True)

						else:
							print("3. Honeypot test passed")
							if holders_perc(token_info[3]) == False:
								print("4. Holder test doesn't passed, don't buy", token_info[3])
								row["status"] = 0
								df = df.append(row, ignore_index=True)
							else:
								# TODO: buy
								print("buy!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
								row["status"] = 1
								df = df.append(row, ignore_index = True)

					print(df.tail(4))
				#When seeing new pair, I add a new row to df.
							
							
				# if search("\"{}\"".format(token_name)) >= 3: # to have exact search
				#   print('buy')
				# else:
				#   print('pass')
			time.sleep(2)
			if counter == 2 * 30 * 1: # every 1 mins to re-check the reserves of tokens in pair pool
				#print("rechecked called")
				## update the status in df
				df = check_reserved(df, threshold)
				counter = 0
				if counter2 == 2 * 30 * 5: # every 5 mins to save the csv file
					## Update Database
					df.to_csv(r"C:\Users\david\OneDrive\Desktop\App\database.csv", index = False)
					counter2 = 0
	
			else:
				counter += 2
				counter2 += 2
				
		except KeyboardInterrupt:
			print('keyboard interrupt, stop')
			df.to_csv(r"C:\Users\david\OneDrive\Desktop\App\database.csv", index = False)
			break
		except (InsufficientDataBytes, BadFunctionCallOutput) :
		 	pass



			
if __name__ == "__main__":
	# df = pd.read_csv(r"C:\Users\david\OneDrive\Desktop\App\database.csv", index_col=False)
	# df1 = check_reserved(df, 10)
	# print(df1.tail(4))
	#main()
	# if holders_perc('0x1ED427b220eeEb5735f735F27A8Ed48c5b3Ad777') == False:
	# 	print('dont buy')
	# else:
	# 	print("buy")

