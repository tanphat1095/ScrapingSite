#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Util,Validation
from lxml import etree as ET
from SiteObjects.Objects_HQDB import Venue, Service
import re
import json
import time
import threading
import requests
import phonenumbers
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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
    index__= -1
    
    threadAlive =[]
    listPhoneremove =['01615069963','01615069598','01615069896']
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    def doWork(self):
  
        self.phoneCodeList = Util.getPhoneCodeList()
   
        '''for i in range(10):
            thread1 = threading.Thread(target=self.print_ex,args=(i,))
            thread1.start()'''
        self.__getListVenues()    
        '''while len(self._url_lstVenues)>0:
            thread2 = threading.Thread(target=self.__getListVenues, args=(self._url_lstVenues[-1],))
            self._url_lstVenues.remove(self._url_lstVenues[-1])
            thread2.start()'''
        
       
    def addIndex(self):
        index_ = self.index__+1
        self.index__ = index_
        return index_
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
                    timeSleep+=5
                    url_hash = self.getUrlSelenium(url_find,timeSleep)
                    if timeSleep>=35:
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
                    #jsonString = self.getRequestsXML('https://www.unbiased.co.uk/advisers/hash/8775209')
                    json_ = json.loads(jsonString)
                    brands = json_.get('data').get('branches') 
                    print 'Postcode: '+ post_+' Record:'+ str(len(brands))
                    #for items in brands:
                    while len(brands)>0:   
                        #ven = self.__VenueParser(items,hash)
                        if self.checkAlive()<5:
                            items =  brands[-1]
                            thread1 = threading.Thread(target=self.__VenueParser,args=(items,hash,))
                            #print thread1.name+' starting'
                            brands.remove(items)
                            self.threadAlive.append(thread1)
                            thread1.start()
                        else:
                            time.sleep(0.1)
                except:
                    sleep(5)
                    continue
                    
    def checkAlive(self):
        count =0
        for t in self.threadAlive:
            if t.isAlive():
                count+=1
            else:
                self.threadAlive.remove(t)
        return count
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
         #ven.description = jsonItems.get('salesPitch')
         ven.country ='gb'
         ven.scrape_page = url
         #ven.pricelist_link = [url]
         self.list_url.append(url__)
         #url ='https://www.unbiased.co.uk/profile/financial-adviser/stiles-company-financial-services-petersfield-ltd-511274'
         xmlRequest = Util.getRequestsXML(url,'//div[@class="container-fluid"]')
         if xmlRequest !=None:
            stringAddress = xmlRequest.find('.//span[@class="profile-meta__address"]').text.replace(',,',',')
            
            #stringAddress ='1st and 2nd Floor Offices, 446 - 452 High street, Kingswinford, West Midlands,'
            
            ven.formatted_address = self.removeNameFromAdd(ven.name.strip(), stringAddress).replace('PO BOX','').replace('PO Box','').replace('Po Box','')
            zipArr =  stringAddress.split(',')
            ven.zipcode =  zipArr[len(zipArr)-1]
            ex_ = re.search('([Gg][Ii][Rr]0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z]))))\s?[0-9][A-Za-z]{2})',
                             stringAddress,
                             flags=0)
            
            if ex_!=None:
                zip_c = ex_.group(0)
                #ven.zipcode = zip_c
                #ven.formatted_address = ven.formatted_address.replace(ven.zipcode,'').strip()
                if ven.zipcode!= zip_c:
                    poZip_c = stringAddress.find(zip_c)
                    poZipcode = stringAddress.find(ven.zipcode)
                    if len(ven.zipcode.strip()) >1:
                        if poZip_c >poZipcode:
                            ven.zipcode = zip_c
            if ex_ ==None:
                if ven.zipcode!=None:
                    ven.zipcode = None           
            if ven.formatted_address.endswith(','):
                ven.formatted_address = ven.formatted_address[0:len(ven.formatted_address)-2]
            phoneLabel = xmlRequest.xpath('.//span[@class="phone-label"]/parent::a')
         
            if len(phoneLabel)>0:
                for phone_ in phoneLabel:
                    phone= phone_.get('data-phone').replace('\n','').replace(' ','')
                    if phone.find('Shownumber')<=0:
                        phone = self.validatePhone(phone)
                        for rePhone  in self.listPhoneremove:
                            if phone == rePhone:
                                phone = None
                        if phone!=None:
                            if phone.startswith('07'):
                                ven.mobile_number = phone
                            else:
                                ven.office_number = phone
                            break
            services = xmlRequest.find('.//ul[@class="advice-area__level-one"]')
            if services!=None:
                list_ser = services.xpath('./li')
                for ser_name  in list_ser:
                  
                    # feedback 3 : add category service
                    
                    cate = ser_name.find('./span').text.strip()
                    list_services = ser_name.xpath('./ul/li')
                    for service__ in list_services:
                        service = Service()
                        service.service_category = cate + ' advice'
                        service.service = service__.text +' advice'
                        services_v.append(service)
                    
                    
            ven.services = services_v
            
            
            
            # append accreditations feedback 3
            certi =[]
            cer =  xmlRequest.xpath('.//div[@class="profile-team__skill-item collapsed"]')
            for c in cer :
                inCerti=[x_ for x_ in certi if c.text in x_]
                if len(inCerti)<=0:
                    certi.append(c.text)
                    
            ven.accreditations = ', '.join(certi)
            
            
            
            # add follow :  fb, twi, website feedback 3
            follow = xmlRequest.xpath('//div[@class="profile__follow"]/ul/li')
            for fol in follow:
                values_fol =  fol.get('class')
                if values_fol =='icon-soc-tw':
                    ven.twitter = fol.find('./a').get('href')
                if values_fol =='icon-soc-www':
                    ven.business_website = fol.find('./a').get('href')
                if values_fol =='icon-soc-fb':
                    ven.facebook = fol.find('./a').get('href')
                
                        
            # description feedback 3
            
            des_1 = xmlRequest.find('.//div[@class="profile__text-block "]/p')
            if des_1!=None:
                ven.description= ''.join(des_1.itertext()).replace('.\n',' | ')
            des_2= xmlRequest.find('.//div[@class="profile__text-block spacing-bottom-xs-0"]/p')
            if des_2!=None:
                ven.description+=' -Our services: '+''.join(des_2.itertext()).replace('.\n',' | ')
            if ven.description!=None:
                if ven.description.endswith(' | '):
                    ven.description = ven.description[0:len(ven.description)-2]
            #return ven
            index = self.addIndex()
            
            
            ven.is_get_by_address = True
            
            ven.writeToFile(self.folder,index,ven.name.replace('/','-').replace(':',' '),False)
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
            """page_state = driver.execute_script('return document.readyState;')
            while page_state != 'complete':            
                page_state = driver.execute_script('return document.readyState;')"""  
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
            
    def validatePhone__(self,phone,country):        
        try:
            parsed_phone = phonenumbers.parse(phone, country.upper(), _check_region=True)
        except phonenumbers.phonenumberutil.NumberParseException as error: 
                print phone +' can not parse'
                return None
        if not phonenumbers.is_valid_number(parsed_phone):
            print phone +': not number'
            return None
        else:
            return phone

            
            
            
            
            
            