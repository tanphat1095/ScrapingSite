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
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class GaragesAndRecovery_gb(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = 'http://www.garagesandrecovery.co.uk'
    
    #__url__ = 'http://www.computer-systems-uk.co.uk' # new chain
    
    _language = 'gb'
    _chain_ = 'chain_427_'
    __name__ = 'Garages And Recovery'
    _url_lstVenues = ''    
    _xpath_lstVenues = ''        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    index=-1
    ukReg = '((?:[gG][iI][rR] {0,}0[aA]{2})|(?:(?:(?:[a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y]?[0-9][0-9]?)|(?:(?:[a-pr-uwyzA-PR-UWYZ][0-9][a-hjkstuwA-HJKSTUW])|(?:[a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y][0-9][abehmnprv-yABEHMNPRV-Y]))) {0,}[0-9][abd-hjlnp-uw-zABD-HJLNP-UW-Z]{2}))'
    listLink =[]
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
        '''
        string='abc def'
        replace ='DEF'
        string_ = string.upper()
        starts =  string_.find(replace)
        replace_ = string[starts:starts+len(replace)]
        print string.replace(replace_, '')
        '''
        '''string ='www.facebook.com/faceface'
        print self.addHTTP(string)'''
        
        
        self.phoneCodeList = Util.getPhoneCodeList()
        self.getListRegion()
        print str(self.index)
    def getListRegion(self):
        xmlList = Util.getRequestsXML(self.__url__, '//div[@class="col-md-9 page-main"]/div/ul')
        if xmlList !=None:
            regions = xmlList.xpath('./ul/li/a')
            for region in regions :
                if region.text!='': # Channel Islands
                    url__ = self.__url__+ region.get('href')
                    self.__getListVenues(url__)
    def __getListVenues(self,urlRegion):
        xmlListVenues = Util.getRequestsXML(urlRegion, '//div[@class="row listing listing-horizontal-xs listing-horizontal-sm listing-horizontal-md business"]')
        if xmlListVenues!=None:
            listElements =  xmlListVenues.xpath('./div')
            for element in listElements:
                self.__VenueParser(element)
        

    def __VenueParser(self,venueElement):        
        try:
            img_link =[]
            ad_type = "none"
            if venueElement.find('.//span[@class="label label-success"]')!=None:
                ad_type ="featured"
            divs =  venueElement.xpath('./div')
            logo_ = divs[0].find('.//img')
            if logo_!=None:
                img_link.append(self.__url__+ logo_.get('src'))
            url__ = venueElement.xpath('./div[@class="col-xs-9 col-sm-9 col-md-9 listing-body"]//div[@class="h4 listing-heading"]/a')
            if url__!=None:
                url__ =url__[0].get('href')
                url__ = self.__url__+ url__
                '''
                files = open('D:\\test.txt','a')
                files.write(url__+'\r\n')
                files.close()
                '''
                existing=[x for x in self.listLink if url__ in x]
                if len(existing)<=0:
                    self.listLink.append(url__)
                    print 'Scraping'+' : '+ url__
                    
                    
                    #if url__ =='http://www.garagesandrecovery.co.uk/business/dorset-auto-repirs':
                    #    print 'Debug'
                    
                    
                    xmlDoc = Util.getRequestsXML(url__, '//body/div[@class="page-wrapper"]')
                    ven = Venue()
                    ven.name = xmlDoc.find('.//div[@class="page-heading"]//h1').text
                    content = xmlDoc.find('.//div[@class="container page-content"]')
                    if content!=None:
                        des_img = content.find('.//div[@class="article-body"]')
                        if des_img!=None:
                            div_img = des_img.xpath('.//img/parent::div')
                            if len(div_img)>0:
                                des_img.remove(div_img[0])
                            des = ' '.join(des_img.itertext())
                            ven.description = des
                        ven.country = self._language
                        ven.scrape_page = url__
                        ven.hqdb_featured_ad_type = ad_type
                        offices_ = content.xpath('.//div[@id="offices"]/parent::div/div[@class="row"]')
                        div_maps =  offices_[0].find('.//div[@class="google-map"]')
                        if div_maps!=None:
                            ven.latitude = div_maps.get('data-lat')
                            ven.longitude= div_maps.get('data-lng')
                        info_ = offices_[0].xpath('./div[@class="col-md-5 col-sm-6"]')
                        info_ = info_[0]
                        ul = info_.xpath('./ul')
                        phones = []
                        for u in ul:
                            phone_ = u.xpath('./li/a')
                            for phone in phone_:
                                if phone.get('title') =='Phone Number':
                                    phone = phone.text.replace(' ','')
                                    if phone.startswith('0800'):
                                        continue
                                    else:
                                        phones.append(phone)
                        if len(ul)>=2:
                            ul_2 =  ul[0]
                            li__ = ul_2.xpath('./li')
                            
                            
                            address =''
                            for li in li__:
                                if li.get('class')!='text-bold':
                                    address = '\n'.join(li.itertext())
                                    addressArr =  address.split('\n')
                                    if len(addressArr)>=3:
                                        ven.street = addressArr[len(addressArr)-3]
                                    ven.city = addressArr[len(addressArr)-2].split(',')[0]
                                    ven.zipcode = addressArr[len(addressArr)-1]
                                    if ven.zipcode!=None:
                                        results = re.search(self.ukReg, ven.zipcode, flags=0)
                                        if ven.zipcode == 'Rotherham, South Yorkshire':
                                            ven.zipcode =''
                                            ven.street =None
                                        if results ==None:
                                            ven.zipcode =None
                            
                        (ven.office_number,ven.office_number2,ven.mobile_number,ven.mobile_number2) = self.processPhones(phones)
                        
                        # right sidebar : //div[@class="col-md-3 page-sidebar"]/div
                        rightSidebar = xmlDoc.xpath('.//div[@class="col-md-3 page-sidebar"]/div[@class="section"]')
                        for right in rightSidebar:
                            
                            website = right.xpath('./a[contains(text(),"Visit Our Website")]')
                            if len(website)>0:
                                website = website[0].get('href')
                                if website.find('facebook.com')==-1:
                                    ven.business_website = website
                                else:
                                    ven.facebook =  website
                            reviews = right.xpath('./p/strong')
                            if len(reviews)>=3:
                                ven.hqdb_nr_reviews = reviews[2].text
                                ven.hqdb_review_score = reviews[1].text
                            follows = right.xpath('./ul/li/a')
                            for foll in follows:
                                follow_link = foll.get('href')
                                if follow_link.find('facebook.com')!=-1:
                                    if ven.facebook==None:
                                        ven.facebook =  self.addHTTP(follow_link)
                                if follow_link.find('twitter.com')!=-1:
                                    if ven.twitter ==None:
                                        ven.twitter = self.addHTTP(follow_link)
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                        img_find = xmlDoc.xpath('//div[@id="galleries"]/parent::div/div[@class="carousel slide equal-height"]//img')
                        for ig in img_find :
                            img_link.append(self.__url__+ig.get('src'))
                            
                            
                        if len(img_link)>0:
                            ven.img_link = img_link
                        self.index+=1
                        ven.writeToFile(self.folder, self.index, ven.name, False)
                        #img_link : //div[@id="galleries"]/parent::div/div[@class="carousel slide equal-height"]//img
                    
                else: 
                    print '\nduplicate'.upper()
                    print '*'* (len(url__)+4)
                    print '*'+ ' '*(len(url__)+2)+'*'
                    print '* '+ url__+' *'
                    print '*'+ ' '*(len(url__)+2)+'*'
                    print '*'*(len(url__)+4)+'\n'
                    
        except Exception, ex:
            print ex
            
            
    def addHTTP(self, string):
        if string.startswith('http'):
            ''
        else:
            string = 'https://'+ string
        return self.add3W(string)
    def add3W(self,string):
        string_ = string.split('://')
        if string_[1].upper().startswith('WWW'):
            ''
        else:
            string =  string_[0]+'://www.'+ string_[1]
        return string.replace('http:','https:')
    def processPhones(self,listphone):
        office = None
        office2 = None
        mobile = None
        mobile2 =None
        for phone in listphone:
            if phone.startswith('06') or phone.startswith('07'):
                if mobile ==None:
                    mobile =phone
                else:
                    mobile2 = phone
            else:
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
    
    def validatePhone__(self,phone):        
        try:
            parsed_phone = phonenumbers.parse(phone, self._language.upper(), _check_region=True)
        except phonenumbers.phonenumberutil.NumberParseException as error: 
                print str(phone) +' can not parse'
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
    