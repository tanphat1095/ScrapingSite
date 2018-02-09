#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Validation
from Common import Util
from lxml import etree as ET
from SiteObjects.Objects_HQDB import Venue, Service
import re
from lxml import html
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import phonenumbers
import threading

class Osteopathesdefrance_fr(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = 'https://osteofrance.com'
    _language = 'fr'
    _chain_ = 'chain_443_'
    __name__ = 'Ostéopathes de France'
    _url_lstVenues = 'https://osteofrance.com/rechercher/'    
    _xpath_lstVenues = '//div[@class="search_results search_results_vcards wide wide-full"]/div[@class="vcard"]'        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    urlList =[]
    runningThread= []
    count = 0
    index = -1
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    def doWork(self):
        self.phoneCodeList = Util.getPhoneCodeList()
        #print self.getRequests(75)
        self.__getbypostcode()
        
        
        # debug
        #self.__VenueParser('https://osteofrance.com/membre/berengeremichaIlesco')
        
    def manageThread(self):
        count =0
        for thread_ in self.runningThread:
            if thread_.isAlive():
                count+=1
            else:
                self.runningThread.remove(thread_)
        return count
    def __getbypostcode(self):
        
        postcode_ = []
        for i in range(1,97):
            postcode = str(i)
            if i<10 :
                postcode = '0'+str(i)
            postcode_.append(postcode)
            
        while len(postcode_)>0:
            if self.manageThread()<=6:
                #xmlDoc = self.getRequests(postcode)
                #self.__getListVenues(xmlDoc)
                post_ = postcode_[-1]
                thread__ = threading.Thread(target=self.__getListVenues,args=(self.getRequests(post_),))
                thread__.start()
                self.runningThread.append(thread__)
                postcode_.remove(post_)
            
    def __getListVenues(self,element):
        listVenues = element.xpath(self._xpath_lstVenues)
        for venue in listVenues:
            aLink = venue.find('./div[@class="fn"]/a')
            if aLink!=None:
                link =self.__url__+  aLink.get('href')
                '''if self.checkDuplicate(self.urlList, link)==False:
                    self.count+=1
                self.urlList.append(link)'''
                self.__VenueParser(link)
        #print str(self.count)

    def __VenueParser(self,url):        
        try :
            if self.checkDuplicate(self.urlList, url)==False:
                ven = Venue()
                print '[SCRAPING]:'+ url
                #ven.scrape_page= url
                
                
                
                ven.country = self._language
                self.urlList.append(url)
                xmlDoc =Util.getRequestsXML(url, '//div[@class="content"]/main')
                xmlDoc = xmlDoc.find('./main')
                name = xmlDoc.find('./h2')
                ven.name = name.text
                des = xmlDoc.find('./div[@class="clearfix"]')
                if des!=None:
                    imgs =[]
                    img = des.xpath('.//img')
                    for im in img:
                        imgs.append(self.__url__+ im.get('src'))
                        des.remove(( im.getparent()).getparent())
                    if len(imgs) >0:
                        ven.img_link = imgs
                    ven.description= ''.join(des.itertext())
                    pass
                map_and_phone_number = xmlDoc.xpath('./div/div[@class="footer row"]')
                isMulti = False
                if len(map_and_phone_number)>1:
                    isMulti = True
                countVenues_ = 0
                for clone_ in map_and_phone_number:
                    countVenues_+=1
                    self._cloneVenues(ven, clone_, countVenues_,url, isMulti)  
            else:
                print'[DUPLICATE]: '+url
        except Exception, ex:
            print '[ERROR]: ' +url
            print ex
    def processAdress(self,address):
        address_ =address.split(',')
        city=''
        zipcode =''
        street = ''
        for add in address_:
            results = re.search('\d{2}[ ]?\d{3}', add, flags=0)
            if results!=None:
                zipcode = results.group(0)
                city = add.replace(zipcode,'')
            else:
                street = add
        return (street,city,zipcode)
    def _cloneVenues(self,ven,map_and_phone_number,count,url,isMulti):
        try:
            if isMulti ==True:
                ven.scrape_page=url+'#'+str(count)
            else:
                ven.scrape_page = url
            #print ET.dump(map_and_phone_number)
            address =  map_and_phone_number.find('./div/p[@class="address"]/a')
            if address !=None:
                
                if address.text.find(' LONDON ')!=-1: # venue in UK
                    return
                
                (ven.street,ven.city,ven.zipcode) = self.processAdress(address.text)
                googleMapUrl = address.get('href')
                (ven.latitude,ven.longitude) = self.getLatLong(googleMapUrl)
            phonenumber =  map_and_phone_number.xpath('./div/p[@class="call2action"]/a')
            phoneList = []
            for phone in phonenumber:
                phoneList.append(phone.get('href').replace('tel:','').replace('.','').replace('O','0').replace('o','0'))
            phoneList = list(set(phoneList))
            (ven.office_number,ven.office_number2,ven.mobile_number,ven.mobile_number2) = self.processPhone(phoneList)
            index=self.index+1
            self.index = index
            ven.writeToFile(self.folder,index,ven.name,False)
        except Exception,ex:
            print ex
    def __ServicesParser(self,url,xmlServices):        
        ''
    def processPhone(self,listPhone):
        office1 =None
        office2 = None
        mobile1 = None
        mobile2 = None
        for phone in listPhone:
            #phone =  phone.replace('O','0').replace('o','0')
            if phone.startswith('+'):
                if phone.startswith('+33'):
                    ''
                else:
                    continue
            if phone.startswith('33'):
                phone = '+'+ phone
            if phone.startswith('00'):
                phone= '+'+ phone[2:len(phone)]
            
            
            if phone.startswith('06') or phone.startswith('07'):
                if mobile1==None:
                    mobile1 =  self.validatePhone__(phone)
                else:
                    mobile2 = self.validatePhone__(phone)
            else:
                if office1 == None:
                    office1 =  self.validatePhone__(phone)
                else:
                    office2 = self.validatePhone__(phone)
        return (office1,office2,mobile1,mobile2)
    def validatePhone__(self,phone):
        try:
            if phone.startswith('0800'):
                return None
            parsed_phone = phonenumbers.parse(phone, self._language.upper(), _check_region=True)
        except phonenumbers.phonenumberutil.NumberParseException as error: 
                print str(phone) +': can not parse'
                Util.log.running_logger.warning(str(phone)+' : cannot parse')
                return None
        if not phonenumbers.is_valid_number(parsed_phone):
            print str(phone) +': not number'
            Util.log.running_logger.warning(str(phone)+' : not number')
            return None
        else:
            return phone            
    def getLatLong(self,mapUrl):
        try:
            lat_lng = mapUrl[mapUrl.find('loc:')+len('loc:'):len(mapUrl)]
            lat_lng =  lat_lng.split('+')
            lat = str(float(lat_lng[0]))
            lng = str(float(lat_lng[1]))
            return (lat,lng)
        except Exception,ex:
            return (None,None)
    def checkDuplicate(self,list,item):
        for item_ in list:
            if item_ == item:
                return True
        return False
    def getRequests(self,postcode):
        url = "https://osteofrance.com/rechercher/"

        querystring = {"location":str(postcode),
                       "nameinc":""}
        response = requests.post(url, data=querystring)

        return html.fromstring(response.content)