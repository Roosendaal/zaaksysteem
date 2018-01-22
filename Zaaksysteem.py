'''
Zaaksysteem API Helper Class
Purpose: Extract cases from https://zaaksysteem.nl/ and
		write data as JSON files in a cache folder

Version: 1.0
Date: 20-1-2018
Last author: Antoon Uijtdehaag, gemeente Roosendaal

Requirements:
	Python 3.6
	requests library: PIP install requests
	config.py contains the customer specific Zaaksysteem API key
'''
import requests
import sys
import json
import os
import time
import datetime
import config as cnf

class Zaaksysteem(object):
	"""
	MANUAL https://mijn.roosendaal.nl/man/Zaaksysteem::Manual::API::V1
	"""
	def __init__(self, url, API_Interface_Id, API_Key):
		self.url = url

		self.headers = {'API-Interface-Id': API_Interface_Id, 'API-Key': API_Key, 'Content-Type': 'application/json'}

		self.setPages (None)
		self.contentList = []

		self.cachePath = 'output'


	@property
	def total_rows(self):
		return self._total_rows

	@total_rows.setter
	def total_rows(self, value):
		self._total_rows= value

	@property
	def cachePath(self):
		return self._cachePath

	@cachePath.setter
	def cachePath(self, value):
		self._cachePath= value
		if not os.path.exists(self._cachePath):
			os.makedirs(self._cachePath)


	@property
	def total_rows(self):
		return self._total_rows

	@total_rows.setter
	def total_rows(self, value):
		self._total_rows= value

	@property
	def rows(self):
		return self._rows

	@rows.setter
	def rows(self, value):
		self._rows= value

	@property
	def page(self):
		return self._page

	@page.setter
	def page(self, value):
		self._page= value

	@property
	def pages(self):
		return self._pages

	@pages.setter
	def pages(self, value):
		self._pages= value

	@property
	def status_code(self):
		return self._status_code

	@status_code.setter
	def status_code(self, value):
		self._status_code= value

	@property
	def contentList(self):
		return self._contentList

	@contentList.setter
	def contentList(self, value):
		self._contentList= value

	def setPages(self, results):
		self.total_rows = 0
		self.rows = 0
		self.page = 0
		self.pages = 0

		if (results is None):
			return

		if 'pager' in results:
			pager = results["pager"]

			if (pager):
				self.total_rows = pager["total_rows"]
				self.rows = pager["rows"]
				self.page = pager["page"]
				self.pages = pager["pages"]



	def sendRequest (self, params):

		self.contentList.clear()
		self.status_code = 0
		self.setPages(None)

		try:
			print ('{} {}'.format(self.url, params))
			r = requests.get(self.url, params=params,headers=self.headers)
			response = json.loads(r.text)

			if 'status_code' in response:
				self.status_code = response["status_code"]
			else:
				self.status_code = 0

			if (self.status_code == 200):

				results = response["result"]["instance"]

				self.setPages(results)

				if 'rows' in results:
					rows = results["rows"]
					for row in rows:
						self.contentList.append(row)


				del rows
				del results

			self.exportToJSON()

			## 500
			## Internal Server Error - There is an error. Error can be found in JSON message (or no message at all if things got really broken)
			if (self.status_code == 500):
				print (response)

			if (self.status_code == 400):
				print ("Bad Request - We do not know what you are talking about")
			if (self.status_code == 401):
				print ("Unauthorized - You are not logged in.")
			if (self.status_code == 403):
				print ("Forbidden - You do not have the proper permissions")
			if (self.status_code == 404):
				print ("Not Found - The API call you requested could not be found")
			if (self.status_code == 405):
				print ("Method Not Allowed - Use of wrong request method for this URL")
		except:
			print("Unexpected error:", sys.exc_info()[0])
##			raise

		return self.status_code

	# Build https request parameters
	def paramBuilder(self, match, rows_per_page = 10, page=1, startdate = None, enddate = None):
		params = 'rows_per_page={}'.format(rows_per_page)
		params += '&page={}'.format(page)
		params += '&es_query=1&query:bool:must:match:_all={}'.format(match)

		if ((startdate != None) and (enddate != None)):
			params += '&query:bool:must:range:date_of_registration:gte={}&query:bool:must:range:date_of_registration:lte={}'.format(startdate, enddate)

		return params

	# query zaaksysteem and store data as json files into cacheFolder
	def query(self, match, rows_per_page = 100, page=1, startdate = None, enddate = None):

		params = self.paramBuilder(match, rows_per_page,page,startdate,enddate)

		self.sendRequest(params)

		return self.status_code

	# query all zaaksysteem cases and store data as json files into cacheFolder
	def queryAll(self, match, rows_per_page = 100, startdate = None, enddate = None):

		#request first
		self.query(match,rows_per_page=rows_per_page, startdate=startdate,enddate=enddate)

		if (self.pages > 1):
			for pageCnt in range(2,self.pages+1):
				params = self.paramBuilder(match, rows_per_page,pageCnt)

				self.sendRequest(params)

				if ((self.status_code == 500) and(rows_per_page > 1)):
					#Retry query for every single page
 					for subPageCnt in range(pageCnt*rows_per_page,((pageCnt+1)*rows_per_page)):
					 	self.query(match, rows_per_page = 1,page = subPageCnt)
			 			self.exportToJSON()

	# save retrieved json from contentList to disk
	def exportToJSON(self):

		for item in self.contentList:
			reference = item["reference"]

			csvFilename = r"{}/{}.json".format(self.cachePath,reference)
			with open(csvFilename, 'w',encoding='utf8') as f:
				f.write(json.dumps(item))
			f.close()

			#timestamp filename 2017-04-02T00:25:48Z
			dateString = item["instance"]["date_created"]
			year = int(dateString[:4])
			month = int(dateString[5:7])
			day = int(dateString[8:10])
			hour  = int(dateString[11:13])
			minute  = int(dateString[14:16])
			sec  = int(dateString[17:19])

			#new_time = datetime.date(year, month, day);
			new_time = datetime.datetime(year, month, day, hour, minute, sec);
			os.utime(csvFilename, (time.mktime(new_time.timetuple()),time.mktime(new_time.timetuple())))


##
## Class tester when run standalone
##
if __name__ == '__main__':

	Zs = Zaaksysteem (cnf.URL, cnf.API_Interface_Id, cnf.API_Key)

  	# define start and enddate
	# these parameters are optional
	startdate = '"2018-01-01"'
	enddate =  '"2018-01-31"'

	Zs.queryAll('Melding woon of leefomgeving',100,startdate,enddate)


