from playwright.sync_api import sync_playwright
from cf_clearance import sync_cf_retry, stealth_sync
import time

cookie = "r9GTp4mUVYGCy61P.k9ilXE2eybLFeNBeTJWloJAKvQ-1644989625-0-150"
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4863.0 Safari/537.36"

def avax_playwright_honeypot(address):
	with sync_playwright() as p:
		browser = p.chromium.launch(headless=False)
		page = browser.new_page()
		stealth_sync(page)
		page.goto('http://detecthoneypot.com/scan?chain=avax&address={}'.format(address))
		res = sync_cf_retry(page)
		if res:
			cppkies = page.context.cookies()
			for cookie in cppkies:
				if cookie.get('name') == 'cf_clearance':
					#print(cookie.get('value'))
					print(cookie.get('name'))
					#print("type cookie: ", type(cookie.get('value')))
			ua = page.evaluate('() => {return navigator.userAgent}')
			#print(ua)
			#print("type ua: ", type(ua))
			# print(page.content())
			time.sleep(5)
			rows = page.locator('css=[class="alert-body"]')
			texts = rows.all_text_contents()
			if 'Honeypot!' in texts[0]:
				print('Not Passed. Honeypot! ',address)
				return False
			# print(texts[0].replace(' ',''))
			elif 'high trading fee' in texts[0]:
				print('Not Passed. High trading fees ',address)
				return False
			# print(texts[0].replace(' ', ''))
			elif 'Honeypot tests passed' in texts[0]:
				print('Passed! ',address)
				return True
			elif 'IDENTICAL_ADDRESSES' in texts[0]:
				print('Not Passed. IDENTICAL_ADDRESSES ',address)
				return False
			else:
				print('Something wrong?  ', address, texts[0])
				return False
		# print(texts[0].replace(' \n', ''))
		else:
			print('Dect fail ',address)
			return False
		time.sleep(30)
		browser.close()


#avax_playwright_honeypot('0xf867555f727d26E4128ACc13d54aAE2688018cd1')

#avax_playwright_honeypot('0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7')