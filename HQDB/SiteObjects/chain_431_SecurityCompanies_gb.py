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
import threading
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SecurityCompanies_gb(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = 'http://www.uksecurity-directory.co.uk'
    _language = 'gb'
    _chain_ = 'chain_431_'
    __name__ = 'Security Companies'
    _url_lstVenues = ''    
    _xpath_lstVenues = ''        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    index =-1
    listlink =[]
    countduplicate = 0
    ukReg = '((?:[gG][iI][rR] {0,}0[aA]{2})|(?:(?:(?:[a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y]?[0-9][0-9]?)|(?:(?:[a-pr-uwyzA-PR-UWYZ][0-9][a-hjkstuwA-HJKSTUW])|(?:[a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y][0-9][abehmnprv-yABEHMNPRV-Y]))) {0,}[0-9][abd-hjlnp-uw-zABD-HJLNP-UW-Z]{2}))'
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
        print self.validatePhone__('0207z1178621')
        self.getListcategory()
        
    def __getListVenues(self,xmlCate):
        try:
            cateName = xmlCate.text
            linkListVenues= xmlCate.get('href')
            pagesnum = 0
            while True:
                pagesnum+=1
                link__ = linkListVenues+'page/'+str(pagesnum)
                xmlDoc = Util.getRequestsXML(link__, '//div[@class="listings wpbdp-listings-list list"]/div/div[@class="listing-actions cf"]/a')
                if xmlDoc==None:
                    break
                listVenues = xmlDoc.xpath('./a')
                for venue  in listVenues:
                    linkVenue  = venue.get('href')
                    self.__VenueParser(linkVenue,cateName)
        except Exception, ex:
            print ex
    def getListcategory(self):
        xmlDoc = Util.getRequestsXML(self.__url__+'/the-directory', '//div[@id="wpbdp-categories"]/ul/li')
        if xmlDoc!=None:
            listcates = xmlDoc.xpath('./li/a')
            for cate in listcates:
                thread__ =  threading.Thread(target=self.__getListVenues,args=(cate,))
                thread__.start()
                
                #self.__getListVenues(cate) 

    def __VenueParser(self,url,cateName):
        existing=[x for x in self.listlink if url in x]
        self.listlink.append(url)
        if len(existing)>0:
            self.countduplicate +=1
            print '[INFO] Duplicate count = '+str(self.countduplicate)
            return
        try:
            print 'Scraping url: '+ url
            
            
            
            #url = 'http://www.uksecurity-directory.co.uk/the-directory/1905/ecpcco/'
                
                
            xmlDoc = Util.getRequestsXML(url, '//div[@class="gdl-page-content"]')
            xmlDoc = xmlDoc.xpath('//div[@class="gdl-page-content"]/div')[0]
            ven = Venue()
            
            imgs =[]
            
            ven.category =  cateName
            ven.scrape_page = url
            ven.country = self._language
            ven.name =  xmlDoc.find('./div/h2').text
            ven.hqdb_featured_ad_type ='none'
            isFeatured = xmlDoc.find('./div[@class="stickytag"]/img')
            if isFeatured!=None:
                if isFeatured.get('title') =='Featured Listing':
                    ven.hqdb_featured_ad_type ='featured'
            divInfo = xmlDoc.xpath('./div[@class="listing-details cf"]/div')
            town_ = ''
            area_ =''
            zipcode =''
            listPhone_ =[]
            for div__ in divInfo:
                label = div__.find('./label')
                if label!=None:
                    label_ = label.text
                    if label_ =='Business Website Address:':
                        website = div__.find('./span/a')
                        if website!=None:
                            website= website.get('href')
                            isFacebook = website.find('facebook.com')
                            isTwiter = website.find('twiter.com')
                            if isFacebook ==-1  and isTwiter==-1:
                                ven.business_website =  website
                            else:
                                if isFacebook !=-1 :
                                    ven.facebook = website
                                if ven.twitter !=-1:
                                    ven.twitter = website
                    if label_ =='Security Services:':
                        serviceStr = div__.xpath('./span/a')
                        sers = []
                        for ser in serviceStr:
                            serv =  Service()
                            serv.service = ser.text
                            sers.append(serv)
                        if len(sers)>0:
                            ven.services = sers
                            ven.pricelist_link = [ven.scrape_page]
                    if label_ =='Long Business Description:':
                        des = div__.find('./span')
                        if des !=None:
                            des = ' '.join(des.itertext())
                            ven.description = des
                    if label_ == 'Business Phone Number:':
                        phone = div__.find('./span').text
                        #phone = self.formatPhone(phone)
                        findsplistPPhone =  self.findSplitPhone(phone)
                        if findsplistPPhone ==None:
                                listPhone_ = [phone]
                            #(ven.office_number,ven.office_number2,ven.mobile_number,ven.mobile_number2) = self.processPhones([phone])
                        else:
                            
                            listPhone_ = phone.split(findsplistPPhone)
                        (ven.office_number,ven.office_number2,ven.mobile_number,ven.mobile_number2) = self.processPhones(listPhone_)
                        
                    if label_ == 'Postcode:':
                        zipcode = div__.find('./span').text
                    if label_ =='Town:':
                        town_ =  div__.find('./span').text
                    if label_ =='Area:':
                        area_ = div__.find('./span').text
                    zipcode =  self.validateZipcode(zipcode)
            if url =='http://www.uksecurity-directory.co.uk/the-directory/1981/s-comm-vehicle-surveillance-system':
                print
            if ven.office_number =='NOT_GB' or ven.office_number2=='NOT_GB' or ven.mobile_number=='NOT_GB' or ven.mobile_number2=='NOT_GB':
				return
            for p in  listPhone_ : 
                if p ==  town_:
                    town_ =  ''
                    break
                    
            ven.zipcode = zipcode
            ven.formatted_address = ', '.join([area_,town_,zipcode])
            
            ven.formatted_address = self.refixFormatAddress(ven.formatted_address.replace('0000000',''))
            extraImg = xmlDoc.xpath('./div[@class="extra-images"]//a/img')
            listingThumbnail = xmlDoc.xpath('./div[@class="listing-thumbnail"]//a/img')
            for thumb in listingThumbnail:
                imgs.append(thumb.get('src'))
            for img in  extraImg:
                imgs.append(img.get('src'))
            if len(imgs)>0:
                ven.img_link = imgs
            self.index =  self.index+1
            ven.writeToFile(self.folder,self.index , ven.name, False)
            
        except Exception, ex:
            print '[ERROR] ' + url+': '+ str(ex)
    def refixFormatAddress(self,string):
        string = string.strip()
        if string.endswith(', ,'):
            string = string[0:len(string)-2]
        if string.startswith(','):
            string = string[1:len(string)]
        if string.endswith(','):
            string = string[0:len(string)-1]
        if string.strip() ==',':
            return None
        string =  string.replace(', , ',', ')
        return string
    def validateZipcode(self,string):
        if string =='':
            return string
        results = re.search(self.ukReg, string, flags=0)
        if results !=None:
            if string.strip()== results.group(0).strip():
                return string
            else:
                return ''
        else:
            return ''
        
    def checkMobi(self,phone):
        mobiCode = ['+447','+446','06','07','6','7']
        for mobi in mobiCode:
            if phone.startswith(mobi):
                return True
        return False  
    def formatPhone(self,phone):
        phone =  phone.replace(' ','').replace('-','').replace('z','').strip()
        if phone.startswith('+44'):
            if phone.find('(0)'):
                phone=phone.replace('(0)','')
            if phone.startswith('+440'):
                phone= phone.replace('+440','+44')
        if phone.startswith('44'):
            phone = '+'+ phone
        if phone.startswith('044'):
            phone =  '+'+ phone[1:len(phone)]
        if phone.startswith('0044'):
            phone =  '+'+ phone[2:len(phone)]
        if phone.startswith('(+44)'):
            if phone.startswith('(+44)0'):
                phone = phone.replace('(+44)','')
            else:
                phone =  phone.replace('(+44)','+44')
        return phone
    def validatePhone__(self,phone): 
        try:
            if len(phone)<10:
                return None
	    if phone.startswith('+44'):
                ''
	    else:
                if phone.startswith('+4'):
                    return 'NOT_GB'
            parsed_phone = phonenumbers.parse(phone, self._language.upper(), _check_region=True)
        except phonenumbers.phonenumberutil.NumberParseException as error: 
                print str(phone) +' can not parse'
                return None
        if not phonenumbers.is_valid_number(parsed_phone):
            print str(phone) +': not number'
            return None
        else:
            return str(phone)
    def processPhones(self,listphone):
        office = None
        office2 = None
        mobile = None
        mobile2 =None
        for phone in listphone:
            phone = self.formatPhone(phone)
            if self.checkMobi(phone):
                if mobile ==None:
                    mobile =phone
                else:
                    mobile2 = phone
            else:
                if phone.startswith('+44'):
                    #phone =  None
                    ''
                else:
                    if phone.startswith('+4'):
                        phone = phone
                if phone !=None:
                    if phone.startswith('0800'):
                    #phone =  None
                        phone =  None
                if office ==None:
                    office = phone
                else:
                    office2= phone
        if office!=None:
            office = self.validatePhone__(office)
        if office2!=None:
            office2 = self.validatePhone__(office2)
        if mobile !=None:
            mobile= self.validatePhone__(mobile)
        if mobile2 !=None:
            mobile2 = self.validatePhone__(mobile2)
        return (office, office2, mobile, mobile2)
    def findSplitPhone(self,phone):
        splitPhone=[';','or','/']
        for char in splitPhone:
            if phone.find(char)!=-1:
                return char
        return None
    def __ServicesParser(self,url,xmlServices):        
        ''
    
