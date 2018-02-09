#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Validation
from Common import Util
from lxml import etree as ET
from SiteObjects.Objects_HQDB import Venue, Service
import re
import json
import urllib3
import phonenumbers
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Hondentrimsalon_nl(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = 'http://www.hondentrimsalon.nl'
    _language = 'nl'
    _chain_ = 'chain_449_'
    __name__ = 'Hondentrimsalon'
    _url_lstVenues = 'http://www.hondentrimsalon.nl/index.php?zoeken='    
    _xpath_lstVenues = '//a[@id="resultaten"]/parent::div/div[@class="links"]'        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    count =0
    outFileSV = ''
    index=-1
    
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    def postcode (self):
        postList =[]
        for i in range(10,100):
            postList.append(str(i*100))
        return postList
    def doWork(self):
        
        
        #print self.check_website('https://www.2130113-C-2013')
        
        self.phoneCodeList = Util.getPhoneCodeList()
        postcode =  self.postcode()
        try:
            for post in postcode:
                print '-'*10+post+'-'*10
                self.__getListVenues(post)
            #self.__getListVenues_2()
        except Exception,ex:
            print ex
    def __getListVenues(self,postcode):
        xmlDoc = Util.getRequestsXML(self._url_lstVenues+postcode,'/html')
        listData = self.getListGeoCode(xmlDoc)
        xmlListVenues = xmlDoc.xpath(self._xpath_lstVenues)
        if len(xmlListVenues)>0:
            elements =  xmlListVenues[0].xpath('./ul/li') 
            count=0
            for ele in elements:
                count+=1
                self.__VenueParser(ele,listData,self._url_lstVenues+postcode+'#'+str(count))
    def __getListVenues_2(self):
        xmldoc = Util.getRequestsXML(self._url_lstVenues, '/html')
        listdata =  self.getListGeoCode(xmldoc)
        listvenues =  xmldoc.xpath('//div[@class="links"]/ul/li')
        count = 0
        for ven in listvenues:
            count+=1
            self.__VenueParser(ven, listdata, self._url_lstVenues+'#'+str(count))
    def getListGeoCode(self,xmlDoc):
        listGeoCode =[]
        scriptTags = xmlDoc.xpath('//head/script')
        for script in scriptTags:
            if script.text !=None and len(script.text)>0:
                if script.text.find('var arBog = new Array();')!=-1:
                    text_ =  script.text
                    stringGeo = text_[text_.find('var arBog = new Array();')+len('var arBog = new Array();'):text_.find('for(var i=0;')]
                    listGeoCode_ =  stringGeo.split(');')
                    for l in listGeoCode_:
                        l =l.strip()+');'
                        listGeoCode.append(l)
                    listGeoCode.pop()
                    break
        return listGeoCode
    def __VenueParser(self,element,listData,scrape_page):
        try:       
            classLI= element.get('class')
            featured = 'none'
            if classLI.find('TOP')!=-1:
                featured = 'featured'
            ven = Venue()
            ven.name =  element.find('./a').text.replace('&#039;','')
            ven.country = self._language
            ven.hqdb_featured_ad_type = featured
            ven.scrape_page = scrape_page
            
            
            div = element.find('./div')
            if div.find('./font')!=None:
                font = div.xpath('./font')
                #div.remove(font)
                for font_ in font:
                    div.remove(font_)
                
                
            a = div.find('./a')
            if a!=None:
                ven.business_website = self.check_website(a.get('href'))
                div.remove(a)
            content = '|'.join(div.itertext())
            content_ = content.split('|')
            phone = ''
            postion = -1
            if content_[postion].find('Telefoon:')!=-1:
                phone = content_[postion].replace('Telefoon:','').replace(' ','').replace('-','').replace('PR','')
                
                if phone.startswith('00'):
                    phone =  '+'+ phone[2:len(phone)]
                if phone.startswith('31'):
                    phone =  '+'+ phone
                if phone.startswith('+'):
                    if phone.startswith('+31'):
                        ''
                    else:
                        phone =  None
                
                if phone!=None:
                
                    if phone.startswith('06') or phone.startswith('+316'):
                        ven.mobile_number = self.validatePhone__(phone)
                    else:
                        ven.office_number =  self.validatePhone__(phone)
                postion -=1
            city_zipcode = content_[postion]
            street = ' '.join(content_[0:postion])
            (ven.zipcode,ven.city) =  self.__processAddress(city_zipcode)
            ven.street=  street
            (ven.latitude,ven.longitude) =  self.processlatlng(listData, city_zipcode)
            
            
            index = self.index+1
            self.index = index
            ven.writeToFile(self.folder, index, ven.name, False)
        except Exception, ex:
            print ex
    def processlatlng(self,list, string):
        for l in list:
            if l.find(string)!=-1:
                l= l[l.find('new Array(')+len('new Array('):l.find(');')]
                array = l.split(',')
                lat= array[0].strip()
                lat = lat[1:len(lat)-1]
                lng = array[1]
                lng = lng[1:len(lng)-1]
                return (lat,lng)
        return(None,None)
    def check_website(self,site):
        pattern = '(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'
        results =  re.search(pattern, site, flags=0)
        if results !=None:
            return results.group(0)
        else:
            return None
    def __processAddress(self,string):
        regex= '\d{4}[ ]?[A-Z]{2}'
        string_ =  string.strip().split()
        zipcode =   ''
        city = ''
        
        if len(string_)>=2:
            if re.search(regex, string_[0], flags=0)!=None:
                zipcode = re.search(regex,string_[0],flags=0).group(0)
            else:
                if re.search(regex, ' '.join(string_[0:2]), flags=0)!=None:
                    zipcode = re.search(regex, ' '.join(string_[0:2]), flags=0).group(0)
                    if zipcode.strip() != ' '.join(string_[0:2]).strip():
                        zipcode = ''
                        string =  string.replace(string_[0],'')
                else:
                    zipcode = ''
                    string = string.replace(string_[0],'')
        city = string.replace(zipcode,'')
        
        return (zipcode,city)
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
    def __ServicesParser(self,url,xmlServices):        
        ''
    