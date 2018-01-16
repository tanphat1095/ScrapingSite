#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Validation
from Common import Util
from lxml import etree as ET
from SiteObjects.Objects_HQDB import Venue, Service
import re
import json
import phonenumbers
import threading
import urllib3
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Serrurier_a_paris_in_fr(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = 'http://www.serrurier-a-paris.info'
    _language = 'fr'
    _chain_ = 'chain_440_'
    __name__ = 'Serrurier-a-paris in_fr'
    _url_lstVenues = 'http://www.serrurier-a-paris.info/adresses'    
    _xpath_lstVenues = ''        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    runningThread = []
    index =-1
    openFormat= ['Ouvert tous les jours 24h/24',
                 '24h/24 7j/7',
                 '24h/24 et 7j/7',
                 'Lundi 24h/24 Mardi 24h/24 Mercredi 24h/24 Jeudi 24h/24 Vendredi 24h/24 Samedi 24h/24 Dimanche 24h/24']
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
        self.phoneCodeList = Util.getPhoneCodeList()
        self.getRegions()
    def countThread(self):
        count=0
        for thread_ in self.runningThread:
            if thread_.isAlive():
                count+=1
            else:
                self.runningThread.remove(thread_)
        return count
    def getRegions(self):
        xmlDoc =  Util.getRequestsXML(self._url_lstVenues, '//ul[@id="menu-menu-adresses"]/li/a')
        if xmlDoc!=None:
            listhref = xmlDoc.xpath('./a')
            while len(listhref) >0:
                if self.countThread()<6:
                    href = listhref[-1]
                    thread_ =  threading.Thread(target=self.__getListVenues,args=(href.get('href'),))
                    thread_.start()
                    self.runningThread.append(thread_)
                    listhref.remove(href)
    def __getListVenues(self,url):
        xmlDoc =  Util.getRequestsXML(url, '//div[@class="property"]/div/h2/a')
        if xmlDoc!=None:
            listVenues=  xmlDoc.xpath('./a')
            for venue in listVenues :
                self.__VenueParser(venue.get('href'))
    def __VenueParser(self,url):
        try:
            print 'Scraping: '+ url
            xmlDoc = Util.getRequestsXML(url, '//div[@id="main"]')
            if xmlDoc!=None:
                ven = Venue()
                ven.scrape_page = url
                ven.country = self._language
                ven.name= xmlDoc.find('.//h1').text
                overview=  xmlDoc.find('.//div[@class="overview"]')
                option = overview.xpath('./div[@class="options row"]/div')
                for opt in option:
                    div_ = opt.xpath('./div')
                    for div__  in div_:
                        strong =  div__.find('./strong')
                        if strong!=None:
                            if strong.text =='Adresse:':
                                street =  div__.find('./span[@itemprop="streetAddress"]')
                                if street!=None:
                                    ven.street = street.text
                                zipcode =  div__.find('./span[@itemprop="postalCode"]')
                                if zipcode!=None:
                                    ven.zipcode =  zipcode.text
                                city = div__.find('./span[@itemprop="addressLocality"]')
                                if city!=None:
                                    ven.city= city.text
                            if strong.text=='Téléphone:':
                                phone =  ''.join(div__.itertext()).replace(' ','').replace('.','').replace('Téléphone:','')
                                if phone.startswith('06') or phone.startswith('07') or phone.startswith('7') or phone.startswith('6'):
                                    ven.mobile_number = self.validatePhone__(phone)
                                else:
                                    ven.office_number =  self.validatePhone__(phone)
                                
                            if strong.text =='Site Web:':
                                website = ''.join(div__.itertext()).replace('Site Web:','')
                                if website.find('facebook.com')!=-1:
                                    ven.facebook = self.addHTTP(website)
                                    continue
                                if website.find('twitter.com')!=-1:
                                    ven.twitter = self.addHTTP(website)
                                    continue
                                ven.business_website = self.addHTTP(website)
                            if strong.text =='Horaires:':
                                openning = ''.join(div__.itertext()).replace('Horaires:','')
                                for format in self.openFormat:
                                    if openning.strip() == format:
                                        ven.opening_hours_raw = 'Lundi au Dimanche: 0h00 - 24h00'
                                if ven.opening_hours_raw ==None:
                                    ven.opening_hours_raw = openning
                            if strong.text =='Votez pour ce serrurier:':
                                score = div__.find('./span[@class="thevotescount"]/span[@itemprop="ratingValue"]')
                                if score!=None:
                                    ven.hqdb_review_score =  score.text
                descElement = overview.find('./div[@class="contenu"]')
                if descElement!=None:
                    ven.description  = ' | '.join(descElement.itertext())
                    if ven.description!=None:
                        ven.description = ven.description.strip()
                        if ven.description.startswith('|'):
                            ven.description =  ven.description[1:len(ven.description)]
                        if ven.description.endswith("|"):
                            ven.description =  ven.description[0:len(ven.description)-1]
                        ven.description = ven.description.replace('| \n |', '|')
                        if len(ven.description.split())<3:
                            ven.description =None
                address= []
                if ven.street!=None and len(ven.street.strip())>0:
                    address.append(ven.street)
                if ven.city!=None and len(ven.city.strip())>0:
                    address.append(ven.city)
                if ven.zipcode !=None and len(ven.zipcode.strip())>0:
                    address.append(ven.zipcode)
                address_ =  ', '.join(address)        
                (ven.latitude, ven.longitude) = self.getLatlng(address_)            
                ven.is_get_by_address = True
                self.index+=1
                ven.writeToFile(self.folder, self.index, ven.name, False)
        except Exception, ex:
            print '[ERROR] '+ url
            print ex 
    
    def validateZipcode(self,zipcode):
        try:
            zipcode = int(zipcode)
            if zipcode <1000 or zipcode > 95978:
                return None
            return str(zipcode)
        except Exception, ex:
            return None
    def __ServicesParser(self,url,xmlServices):        
        ''
    def addHTTP(self, string):
        string = string.strip()
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
        
        if string.find('facebook.com')!=-1 or string.find('twitter.com')!=-1:
            return string.replace('http:','https:')
        else:
            return string
    def validatePhone__(self,phone):
        try:
            if phone.startswith('0800'):
                return None
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

    def getLatlng(self,address):
        if address.strip()=='':
            address = 'null'
            return (None,None)
        try:
            jsonLatlng = Util.getGEOCode(address, self._language.upper())
            if jsonLatlng !=None:
                if jsonLatlng.get('status') =='OK':
                    result =  jsonLatlng.get('results')
                    for re in result:
                        if re.get('geometry')!=None:
                            geometry = re.get('geometry')
                            location = geometry.get('location')
                            lat = location.get('lat')
                            lng = location.get('lng')
                            return(str(lat),str(lng))
                else:
                    return (None,None)
            else:
                return (None,None)
        except Exception,ex:
            return (None,None)