#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Util,Validation
from lxml import etree as ET
from SiteObjects.Objects_HQDB import Venue, Service
import re
import json
import time
import requests.packages.urllib3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep
#from pyvirtualdisplay import Display
requests.packages.urllib3.disable_warnings()
class Unbiased_gb(BaseSite):
    """description of class"""
    phoneCodeList = None
    __url__ = 'https://www.unbiased.co.uk/'
    _language = 'gb'
    _chain_ = 'chain_374_'
    __name__ = 'Unbiased Adviser search'
    _url_lstVenues = ['https://www.unbiased.co.uk/advisers/financial-adviser?search=',
                      'https://www.unbiased.co.uk/advisers/mortgage-adviser?search=',
                      'https://www.unbiased.co.uk/advisers/solicitor?search=',
                      'https://www.unbiased.co.uk/advisers/accountant?search=']

    __url_profile =['https://www.unbiased.co.uk/profile/financial-adviser/',
                    'https://www.unbiased.co.uk/profile/mortgage-adviser/',
                    'https://www.unbiased.co.uk/profile/solicitor/',
                    'https://www.unbiased.co.uk/profile/accountant/'] # + companyslug + id + ?hash=8571913
    hash_url ='https://www.unbiased.co.uk/advisers/hash/'
    _xpath_lstVenues = ''        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    list_url =[]
    vens=[]
    serv=[]
    
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
        #Set OutFile Values
    #    self.outFileVN = self.folder + '/' + self._chain_ + '_' + Validation.RevalidName(self.__name__) + '_Venues.csv'
     #   self.outFileSV = self.folder + '/' + self._chain_ + '_' + Validation.RevalidName(self.__name__) + '_Services.csv'
        self.phoneCodeList = Util.getPhoneCodeList()
        #self.getUrlSelenium('https://www.unbiased.co.uk/advisers/mortgage-adviser?search=MK1')
        self.__getListVenues()
        '''
        Code Here
        '''       
        for items in range(0,len(self.venues)):
            ven = self.venues[items]
            if ven!=None:
                ven.writeToFile(self.folder,items,False)
                #self.vens.append(ven.toOrderDict())
            
        #Write Files
        #if len(self.venues) > 0:
        #    Util.writelist2File(self.vens,self.outFileVN)
        #if len(self.services) > 0:
        #    Util.writelist2File(self.services,self.outFileSV)
    def __getListVenues(self):
        print "Getting list of Venues"
        files_ = open('Data/EngCity.txt','r')
        postcode = files_.read().splitlines()
        print 'Total post code: '+ str(len(postcode))
        index =0
        for url_i in self._url_lstVenues:
            for post_ in postcode : 
                timeSleep =10
                url_find = url_i+ str(post_)
                
                url_hash = self.getUrlSelenium(url_find,timeSleep)
                while url_hash ==None:
                    print 'Retry get Hash...'
                    timeSleep+=1
                    url_hash = self.getUrlSelenium(url_find,timeSleep)
                    if timeSleep>=15:
                        break
                if url_hash ==None:
                    continue
                arraysHash = url_hash.split('#/')
                while len(arraysHash)<2:
                    timeSleep+=1
                    print 'retry get hash from url...'
                    url_hash = self.getUrlSelenium(url_find,timeSleep)
                    if timeSleep>=20:
                        if len(arraysHash)<2:
                            arraysHash.append('')
                        break
                hash = arraysHash[1]
                if len(hash)<=3:
                    continue
                print str(index)+' >URL: '+ url_hash.encode('utf-8').encode('string-escape')
                print self.hash_url+str(hash)
                try:
                    jsonString = self.getRequestsXML(self.hash_url+hash)
                    #jsonString = self.getRequestsXML('https://www.unbiased.co.uk/advisers/hash/8637272')
                    json_ = json.loads(jsonString)
                    brands = json_.get('data').get('branches') 
                    print 'Postcode: '+ post_+' Record:'+ str(len(brands))
                    for items in brands:
                        ven = self.__VenueParser(items,hash)
                        if ven!=None:
                            ven.writeToFile(self.folder,index,ven.name.replace('/','-').replace(':',' '),False)
                            index+=1
                            
                   
                except:
                    sleep(5)
                    continue
                #jsonString = self.getRequestsXML('https://www.unbiased.co.uk/advisers/hash/8627543')
                
                        #self.venues.append(ven.toOrderDict())
                
    def __VenueParser(self,jsonItems,hash):           
        url = self.__url__+'profile/'+jsonItems.get('serviceSlug')+'/'+ jsonItems.get('companySlug')+'-'+jsonItems.get('id')+'?hash='+hash
        url__ = self.__url__+'profile/'+jsonItems.get('serviceSlug')+'/'+ jsonItems.get('companySlug')+'-'+jsonItems.get('id')
        id_ = str(jsonItems.get('id'))
        existing=[x for x in self.list_url if url__ in x]
        if len(existing)>0:
            print 'this venues existed in list'
            return None
        if len(existing)<=0:
         print 'Scrapping: '+url    
         ven = Venue()
         services_v =[]
         ven.category =  jsonItems.get('restriction').get('name')
         ven.adid = str(jsonItems.get('id'))
         ven.name = jsonItems.get('companyName')
         ven.latitude = jsonItems.get('coordinates').get('lat')
         ven.longitude = jsonItems.get('coordinates').get('long')
         ven.venue_images = jsonItems.get('logo')
         points_ = jsonItems.get('satisfaction_rating')
         if str(points_).find('.') >=0:
             ven.hqdb_review_score = str(round(points_,1))
         else:
             ven.hqdb_review_score = str(points_)      
         #ven.img_link = [url]
         ven.description = jsonItems.get('salesPitch')
         ven.country ='gb'
         ven.scrape_page = url
         #ven.pricelist_link = [url]
         self.list_url.append(url__)
         #url ='https://www.unbiased.co.uk/profile/financial-adviser/stiles-company-financial-services-petersfield-ltd-511274'
         xmlRequest = Util.getRequestsXML(url,'//div[@class="container-fluid"]')
         if xmlRequest !=None:
            stringAddress = xmlRequest.find('.//span[@class="profile-meta__address"]').text.replace(',,',',')
            ven.formatted_address = self.removeNameFromAdd(ven.name.strip(), stringAddress)
            
            
            
            
            
            phoneLabel = xmlRequest.xpath('.//span[@class="phone-label"]/parent::a')
         
            if len(phoneLabel)>0:
                for phone_ in phoneLabel:
                    phone= phone_.get('data-phone').replace('\n','').replace(' ','')
                    if phone.find('Shownumber')<=0:
                        phone = self.validatePhone(phone)
                        if phone =='01615069963':
                            phone = None
                        if phone!=None:
                            if phone.startswith('07'):
                                ven.mobile_number = phone
                            else:
                                ven.office_number = phone
                            break
            services = xmlRequest.find('.//ul[@class="advice-area__level-one"]')
            if services!=None:
                list_ser = services.xpath('./li/span')
                for ser_name  in list_ser:
                    services_ = Service()
                    services_.service = ser_name.text
                    #services_.scrape_page = ven.scrape_page
                    services_v.append(services_)
                    #self.services.append(services_.toOrderDict())
            ven.services = services_v
            return ven
        else:
            return None
    def __ServicesParser(self,url,xmlServices):        
        ''
    def appensList(self,arrays):
        for item in arrays:
            href= item.get('href')
            existing=[x for x in self.list_url if href in x]
            if existing <=0 :
                print 'appen list url: '+ href
                self.list_url.append(href)
    def getUrlSelenium(self,url,timeSleep):
        delay= 60
        result =''
        try:
            driver = webdriver.Chrome('Data/chromedriver.exe')
            driver.start_client()
            driver.set_page_load_timeout(delay)
            driver.get(url)                     
            page_state = driver.execute_script('return document.readyState;')
            while page_state != 'complete':            
                page_state = driver.execute_script('return document.readyState;')     
            time.sleep(timeSleep)
            currentUrl= driver.current_url
            result = currentUrl
        except Exception,ex:
            result=None
        finally:
            driver.close()
            driver.quit()
        return result
    def getRequestsXML(self,url):
        headers = {
            'content-type': "application/x-www-form-urlencoded",   
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        response = requests.request("GET", url, headers=headers,timeout=(60,60),verify=False)
        return response.content
    def validatePhone(self,phone):
        if phone.isdigit():
            if phone.startswith('0800') | phone.startswith('800') :
                return None
            if phone.startswith('44') and len(phone) == 12:
                return '+'+ phone
            if phone.startswith('+44') and len(phone)==13:
                return phone
            if phone.startswith('0') and len(phone) ==11:
                return phone
            else:
                if phone.startswith('44'):
                    return None
                if phone.startswith('+44'):
                    return None
                if phone.startswith('0'):
                    return None
                else:
                    return phone
        else:
            phone = None
        return phone
    def checkPhone(self, phone):
        _phone =''
        try:
            if int(phone) > 0:
                _phone = phone
            else:
                _phone=  None
        except:
            _phone = None
        print _phone
        return _phone
    def removeNameFromAdd(self,name, address__):
        if name !=None and address__!=None:
            count =0
            nameArr = name.split()
            addressArr = address__.split(',')
            addressArr = addressArr[0].split()
            for na in nameArr:
                for ad in addressArr:
                    if na == ad:
                        count+=1
            if count >= len(nameArr)-2:
                add_ = address__.split(',')
                return ','.join(add_[1:len(add_)])
            else:
                return address__
        else:
            return address__
            
            
            
            
            
            
            
            
            