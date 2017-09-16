#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Util,Validation
from lxml import etree as ET
from lxml import  html
from SiteObjects.Objects_HQDB import Venue, Service
import re
import json
import urllib3
import requests
from openpyxl.workbook import child
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

class Homewise_gb(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = 'http://www.homewise.ie'
    _language = 'gb'
    _chain_ = 'chain_403_'
    __name__ = 'Home Wise'
    _url_lstVenues = ''    
    _xpath_lstVenues = '//span[@class="searchNavBottomText"]/div/a'        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    list_xpath=['//td[@class="tier0Top"]/a','//td[@class="tier1Top"]/a','//td[@class="tier2Top"]/a','//td[@class="tier3Top"]/a']
    venuesLinks= []
    
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
        #Set OutFile Values
       
        self.phoneCodeList = Util.getPhoneCodeList()
        '''
        Code Here
        '''
        #Write Files
        
        self.__getListVenues()
        #print '*'*25
        #print 'Total:'+ str(len(self.venuesLinks)) +' Venues'
        
        with open('Data/listVenues_403.txt') as f:
            links = f.read().splitlines()
        for link in links:
            #print link
            ven =self.__VenueParser(link)
        
        
    def __getListVenues(self):
        print '*'* 25
        print 'Collecting list venues....'
        print '*'*25
        areas_ = Util.getRequestsXML(self.__url__, self._xpath_lstVenues)
        for area in areas_ :
            link_ = area.get('href')
            cate = area.text
            #xmlDoc =    Util.getRequestsXML(link_, '//div[@align="right"]')
            #if xmlDoc!=None: 
                #print ET.dump(xmlDoc)
            driver = webdriver.Chrome('Data/chromedriver.exe')
            driver.start_client()
            driver.set_page_load_timeout(60)                      
            driver.get(link_)       
            #output = driver.page_source
            #output = html.fromstring(output)
            xmlDoc = driver.find_element_by_xpath('//div[@align="right"]')
            if xmlDoc!=None:   
                pages = 1
                totalPages =xmlDoc.text
                totalPages = totalPages[totalPages.find('of')+ 2:totalPages.find('[')].strip()
                if totalPages.isdigit():
                    totalPages = int(totalPages)
                    while pages <=totalPages:
                        files = open('D:\\listVenues_403.txt','a')
                        url_listItem = self.__url__+'/search.php?PageNO='+ str(pages)
                        time.sleep(2)
                        print url_listItem
                        driver.get(url_listItem)
                        output_2 = driver.page_source
                        output_2 = html.fromstring(output_2)
                        xmlList = output_2.xpath('//div[@id="container"]')
                        if xmlList!=None:
                            for xpath_ in self.list_xpath:
                                links= xmlList[0].xpath(xpath_)
                                for linkin in  links:
                                    itemLink = linkin.get('href')
                                    #print 'URL Found: '+ itemLink
                                    
                                    future_ad_type =''
                                    childTd = linkin.xpath('./parent::td/parent::tr/parent::tbody/parent::table/parent::td')
                                    if len(childTd) >=1:
                                        childTables = childTd[0].xpath('./table')
                                        if len(childTables)==3:
                                            #print ET.dump(childTables[1])
                                            td_ = childTables[1].xpath('./tbody/tr/td')
                                            if len(td_)==3:
                                                stringTd = ''.join(td_[1].itertext())
                                                stringTd = stringTd.split('\n')
                                                if xpath_ != '//td[@class="tier0Top"]/a':
                                                    if len(td_[1].xpath('./table'))<=0:
                                                        future_ad_type = stringTd[2].strip()
                                                        print '***'.join(stringTd)
                                                    else:
                                                        for string_ in stringTd:
                                                            string_ = string_.strip()
                                                            
                                    
                                    if itemLink!=None:
                                        self.venuesLinks.append(itemLink+'/#/'+cate+'/#/'+future_ad_type)
                                        files.write(itemLink+'/#/'+cate+'/#/'+future_ad_type.strip()+'\r\n')  
                        files.close()         
                        pages+=1
            driver.close()
            driver.quit()           
        

    def __VenueParser(self, urlVenues):        
        print 'Scrapping: ' + urlVenues
        urlVenues = urlVenues.split('/#/')
        if len(urlVenues)==2:
            ven = Venue()
            ven.category = urlVenues[1]
            xmlDoc =Util.getRequestsXML(urlVenues[0], '//div[@id="container"]')
            subTable = xmlDoc.xpath('./div/table')
            if len(subTable) ==3:
                subTable = subTable[1]
                subtd  = subTable.xpath('./tr/td/table/tr/td')
                if len(subtd)==2:
                    subtd = subtd[1]
            return ven
        else:
            return None

    def __getRequestUrl(self, pages,referer):
            url = "http://www.homewise.ie/search.php?PageNO="+str(pages)

            querystring = {
                           "Referer":referer
                           }

            headers = {
                    'cache-control': "no-cache",
                    'postman-token': "411dcf46-f5d7-156f-3e08-0e49f6385fbd"
                        }

            response = requests.request("POST", url, headers=headers, params=querystring)
            
            print(response.text)
            file =open('d:\\files.html','w')
            file.write(response.text)
            file.close()
                   
            
    
    def __ServicesParser(self,url,xmlServices):        
        ''
    