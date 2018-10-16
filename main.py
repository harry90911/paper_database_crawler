import requests, datetime, time, random, os, csv
from pymongo import *
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

class client():

	def __init__(self):
		
		options = webdriver.ChromeOptions()
		# options.add_argument("--headless")
		options.add_argument("user-agent={}".format(UserAgent().random))
		options.add_argument('--headless')
		options.add_argument('--no-sandbox') # required when running as root user. otherwise you would get no sandbox errors. 
		options.add_argument('window-size=1200,1100')
		self.driver = webdriver.Chrome("/Users/harry/anaconda/selenium/webdriver/chromedriver", chrome_options=options)

		mongo_client = MongoClient("mongodb://localhost:27017/")
		db = mongo_client.news_textmining
		self.news_title_collection = db.news_title_collection
		#news_number = db.news_number

	def _get_search_result(self, start_date, end_date, key_word):
		self.driver.get("https://udndata.com/library")
		time.sleep(random.randint(5,6))
		text_input = self.driver.find_element_by_id("SearchString")
		text_input.send_keys("{}".format(key_word))

		time_input1 = self.driver.find_element_by_id("datepicker-start")
		time_input1.send_keys(start_date)

		time_input2 = self.driver.find_element_by_id("datepicker-end")
		time_input2.send_keys(end_date)

		text_input.send_keys(Keys.RETURN)

		time.sleep(random.randint(5,6))
		WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[@id='mainbar']/section/div[1]/span[2]")))


	def _check_total_page(self):
		number = int(self.driver.find_elements_by_xpath("//*[@id='mainbar']/section/div[1]/span[2]")[0].text)
		print(number)
		if number < 20 & number != 0:
			pages = 1
		elif number == 0:
			pages = 0
		else:
			pages = int(number/20)+1

		return pages

	def kw_search(self, start_date, end_date, key_word):
		self._get_search_result(start_date, end_date, key_word)
		pages = self._check_total_page()
		if pages != 0:
			page = 1
			while page <= pages:
				time.sleep(random.randint(0,3))

				for i in range(1, 21):
					try:
						news_summary_dict =  {}
						title = self.driver.find_element_by_xpath("//*[@id='mainbar']/section/div[6]/ul/li[{}]/div/h2/a".format(i)).text
						summary = self.driver.find_element_by_xpath("//*[@id='mainbar']/section/div[6]/ul/li[{}]/div/span".format(i)).text

						title = self.driver.find_element_by_xpath("//*[@id='mainbar']/section/div[6]/ul/li[{}]/div/h2/a".format(i)).text
						news_summary_dict["title"] = title
	 
						summary = self.driver.find_element_by_xpath("//*[@id='mainbar']/section/div[6]/ul/li[{}]/div/span".format(i)).text
						date = summary.split("．")[0]
						news_summary_dict["date"] = date
	                     
						paper = summary.split("．")[1]
						news_summary_dict["paper"] = paper
	                     
						position_code = summary.split("．")[2]
						news_summary_dict["position_code"] = position_code

						position = summary.split("．")[3]
						news_summary_dict["position"] = position

						reporter = summary.split("．")[4]						
						news_summary_dict["reporter"] = reporter

						news_summary_dict["key_word"] = key_word

						news_summary_dict =  {
							"title" : title,
							"date" :  date,
							"paper" :  paper,
							"position_code" : position_code,
							"position" : position,
							"reporter" : reporter,
							"key_word" : key_word
						}

						#匯入資料庫
						self.news_title_collection.update(news_summary_dict, news_summary_dict, upsert=True)
					
					except Exception as e:
						print(e)
						pass

				next_page = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[@id='mainbar']/section/div[2]/a[last()-1]")))
				ActionChains(self.driver).click(next_page).perform()
				page+=1

	def to_csv(self,final_list):
		with open(os.path.expanduser("~/Desktop/news.csv"), "w", newline = "", encoding="utf8") as csvfile:
			fieldnames = ["title", "date", "paper", "key_word", "position", "position_code", "reporter"]
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()
			for i in final_list:
				print(i)
				writer.writerow(i)

	def close_connect():
		driver.quit()


if __name__ == "__main__":

	# 搭配「報導」
	noun = ["政黨", "朝野", "兩黨", "藍綠", "國會", "立委", "黨外"]
	verb = ["分裂", "惡鬥", "衝突", "對立", "空轉", "停擺", "打架", "示威"]
	specific_noun = ["學運"]
	must = ["報導"]
	
	words = []
	for i in noun:
		for ii in verb:
			print(i + " " + ii + " " + must[0])
			words.append(i + " " + ii + " " + must[0])
	print(words)

	Client = client()
	for word in words:
		print(word)
		Client.kw_search("1970-01-01", "2018-09-30", word)



"""
#建立一個日期字串list
base = datetime.datetime.today()
raw_date_list = [base - datetime.timedelta(days=x) for x in range(0, 170)]

date_list = []
for ii in raw_date_list:
	if len(str(ii.month)) == 1 and len(str(ii.day)) == 1:
		target = str(ii.year)+"-"+"0"+str(ii.month)+"-"+"0"+str(ii.day)

	elif len(str(ii.month)) == 1 and len(str(ii.day)) == 2:
		target = str(ii.year)+"-"+"0"+str(ii.month)+"-"+str(ii.day)

	elif len(str(ii.month)) == 2 and len(str(ii.day)) == 1:
		target = str(ii.year)+"-"+str(ii.month)+"-"+"0"+str(ii.day)
	
	else:
		target = str(ii.year)+"-"+str(ii.month)+"-"+str(ii.day)	
	date_list.append(target)
"""



