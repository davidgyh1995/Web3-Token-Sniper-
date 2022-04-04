import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from fp.fp import FreeProxy
from selenium.common.exceptions import WebDriverException,NoSuchElementException
import time
import timeit
import pandas as pd
import random

#### Bsc token scrape holders, need to swith to iframe first
#addr = '0xbA2aE424d960c26247Dd6c32edC70B295c744C43'

def chrome_setup(ip_renew):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    if ip_renew == True:
        proxy = FreeProxy(country_id=['US']).get()
        chrome_options.add_argument('--proxy-server=%s' % proxy)
        print("New proxy: ",proxy)
    wd = webdriver.Chrome(r'C:\Users\david\OneDrive\Desktop\App\chromedriver.exe', options=chrome_options)
    return wd



def holders_perc(addr):
    wd = chrome_setup(False)
    while True:
        try:
            url = 'https://bscscan.com/token/{}#balances'.format(addr)
            wd.get(url)
            wd.switch_to.frame("tokeholdersiframe")
            perc_table = WebDriverWait(wd, 30).until(EC.visibility_of_all_elements_located((By.ID, 'body')))
            #print(perc_table[0].text)

            Store = perc_table[0].text.split("\n")  # split string for every new lines
            Count = False
            linesitem = []
            for i in range(len(Store)):
                if Store[i][0] == "1":
                    Count = True
                if Count == True and Store[i][0] == "F":
                    Count = False
                if Count == True:
                    linesitem += [Store[i].split()]
            #print(linesitem)
            df_holders = pd.DataFrame()
            addr_list = []
            conv_num = []
            conv_perc = []
            for i in range(len(linesitem)):
                if (len(linesitem[i])) < 4 : # This is due to some pages have addr,quantity,perc,value columns, while others only has the first three
                    pass
                else:
                    addr_list += [linesitem[i][1:-2]]
                    conv_num += [float(linesitem[i][-2].replace(',', ''))]
                    conv_perc += [float(linesitem[i][-1].strip('%')) / 100]

            df_holders['addr'] = addr_list
            df_holders['quantity'] = conv_num
            df_holders['perc'] = conv_perc
            print(df_holders)
            for i in range(len(df_holders['addr'])):
                if df_holders['addr'][i][0][0] == '0':
                    if (df_holders['perc'][i]) < 0.5:
                        print('holder test perc',df_holders['perc'][i])
                        return True   # True means passes the test, can buy
                    else:
                        return False    # false means can't buy
                else:
                    return False

            wd.close()
            break
        except (WebDriverException, NoSuchElementException) as e:
            print('Error raised, try switching to a new ip address')
            wd = chrome_setup(True)
            time.sleep(random.randint(2, 3))

#df_holders = holders_perc(addr)
#print(df_holders)
# from timeit import Timer
# t = Timer(lambda: holders_perc(addr))
# print(t.timeit(number=1))

