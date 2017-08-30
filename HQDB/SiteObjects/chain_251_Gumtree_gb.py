#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Util, Validation
from lxml import etree as ET
import SiteObjects
from SiteObjects import Objects_HQDB
from Objects_HQDB import Service
from Objects_HQDB import Venue
import re
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()

class Gumtree_gb(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    outFile = ''
    __url__ = 'https://www.gumtree.com'
    _language = 'gb'
    _chain_ = 'chain_251_'
    __name__ = 'Gumtree'
    _url_lstCountry = ['https://www.gumtree.com/business-services/england',
                        'https://www.gumtree.com/business-services/northern-ireland',
                        'https://www.gumtree.com/business-services/scotland',
                        'https://www.gumtree.com/business-services/wales']
    _xpath_lstCities = '//section[@class="space-pts space-pbm"]//div[@class="space-mlm"]//ul//li'
    listCities = []
    listLargerThan1500 = []
    _url_lstVenues = ''    
    _xpath_lstVenues = '//div[@class="grid-col-12 space-mbxs"]//ul[@data-q="featuredresults" or @data-q="naturalresults"]|//li[@class="pagination-next"]'    

    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
        self.outFile = self.folder + '/' + self._chain_ + '_' + Validation.RevalidName(self.__name__) + '_Venues.csv'
        self.phoneCodeList = Util.getPhoneCodeList()
        self.__getListCities()
        
        if len(self.listCities) > 0:
            self.listCities = list(set(self.listCities))
            self.__getListVenues()
            if len(self._lstVenues) > 0: 
                listWrite2File = []               
                for i in range(len(self._lstVenues)):
                    try:
                        ven = self.__VenueParser(self._lstVenues[i])
                        if ven != None:
                            listWrite2File.append(ven.toOrderDict(False))
                    except Exception,ex:
                        print "URL: " + self._lstVenues[i].scrape_page + ": " + ex.message
                        Util.log.error("URL: " + self._lstVenues[i].scrape_page + ": " + ex.message)                        
                
                Util.writelist2File(listWrite2File,self.outFile)
    
    def __getListVenues(self):
        limit = 1000
        print "Getting list of Venues"
        for url in self.listCities:
            print url
            xmlVenues = Util.getRequestsXML(url,self._xpath_lstVenues)            
            Featured = xmlVenues.find('./ul[@data-q="featuredresults"]')
            if Featured != None:
                Featured = Featured.xpath('./li/article')
                for li in Featured:                    
                    ven = self.__GetVenueFromLI(li)
                    ven.hqdb_featured_ad_type = ['FEATURED']
                    urgent = li.find('.//span[@data-q="urgentProduct"]')                    
                    if urgent != None:
                        ven.hqdb_featured_ad_type = ['URGENT']
                    existing = [x for x in self._lstVenues if ven.scrape_page == x.scrape_page]
                    if len(existing) <= 0:
                        self._lstVenues.append(ven)
            Natural = xmlVenues.find('./ul[@data-q="naturalresults"]')
            if Natural != None:
                Natural = Natural.xpath('./li/article')
                for li in Natural:
                    ven = self.__GetVenueFromLI(li)
                    ven.hqdb_featured_ad_type = ['NONE']
                    urgent = li.find('.//span[@data-q="urgentProduct"]')                    
                    if urgent != None:
                        ven.hqdb_featured_ad_type = ['URGENT']                                        
                    existing = [x for x in self._lstVenues if ven.scrape_page == x.scrape_page]
                    if len(existing) <= 0:
                        self._lstVenues.append(ven)
            li = xmlVenues.find('./li')
            while li != None:
                url = li.find('.//a')
                if url != None and url.get('href') != None:
                    url = self.__url__ + url.get('href')
                    print url
                    xmlVenues = Util.getRequestsXML(url,self._xpath_lstVenues)
                    Featured = xmlVenues.find('./ul[@data-q="featuredresults"]')
                    if Featured != None:
                        Featured = Featured.xpath('./li/article')
                        for li in Featured:
                            ven = self.__GetVenueFromLI(li)
                            ven.hqdb_featured_ad_type = ['FEATURED']
                            urgent = li.find('.//span[@data-q="urgentProduct"]')                    
                            if urgent != None:
                                ven.hqdb_featured_ad_type = ['URGENT']
                            existing = [x for x in self._lstVenues if ven.scrape_page == x.scrape_page]
                            if len(existing) <= 0:
                                self._lstVenues.append(ven)
                    Natural = xmlVenues.find('./ul[@data-q="naturalresults"]')
                    if Natural != None:
                        Natural = Natural.xpath('./li/article')
                        for li in Natural:
                            ven = self.__GetVenueFromLI(li)  
                            ven.hqdb_featured_ad_type = ['NONE']
                            urgent = li.find('.//span[@data-q="urgentProduct"]')                    
                            if urgent != None:
                                ven.hqdb_featured_ad_type = ['URGENT']                                              
                            existing = [x for x in self._lstVenues if ven.scrape_page == x.scrape_page]
                            if len(existing) <= 0:
                                self._lstVenues.append(ven)
                    li = xmlVenues.find('./li')
                    if len(self._lstVenues) >= limit:
                        break
            if len(self._lstVenues) >= limit:
                break

    def __getListCities(self):
        print "Getting list of Cities"
        for url in self._url_lstCountry:
            xmlCities = Util.getRequestsXML(url,self._xpath_lstCities)
            if xmlCities != None:
                for li in xmlCities:
                    a = li.find('.//a')
                    span = li.find('.//span')
                    count = 0
                    if span != None and span.text != None:
                        #print str(span.text)
                        count = int(span.text.replace('\r','').replace('\n','').strip().replace(',',''))                    
                    if a != None and a.get('href') != None:
                        url = self.__url__ + a.get('href')                        
                        print url + ': ' + str(count)
                        if count >= 1500:
                            self.listLargerThan1500.append(url)
                            self.__getListCitiesLargerThan1500()
                        else:
                            self.listCities.append(url)                                                
    def __getListCitiesLargerThan1500(self):
        while len(self.listLargerThan1500) > 0:
            url = self.listLargerThan1500[0]
            self.listLargerThan1500.remove(url)
            xmlCities = Util.getRequestsXML(url,self._xpath_lstCities)
            if xmlCities != None:
                for li in xmlCities:
                    a = li.find('.//a')
                    span = li.find('.//span')
                    count = 0
                    if span != None and span.text != None:
                        count = int(span.text.replace('\r','').replace('\n','').strip().replace(',',''))                    
                    if a != None and a.get('href') != None:
                        url = self.__url__ + a.get('href')
                        print url + ': ' + str(count)
                        if count >= 1500:
                            self.listLargerThan1500.append(url)                            
                        else:
                            self.listCities.append(url)                        
    
    def __GetVenueFromLI(self,li):
        ven = Venue()
        ven.country = self._language        
        adID = li.get('data-q')
        if adID != None:
            ven.adid = adID.replace('ad-','').strip()
        title = li.find('.//h2[@class="listing-title"]')
        if title != None:
            ven.name_of_business = "".join(title.itertext()).replace('\r','').replace('\n','').strip()
        thumbnail = li.find('.//div[@class="listing-thumbnail"]')
        if thumbnail != None:
            img = thumbnail.find('.//img')
            if img != None and img.get('src') != None and img.get('src').strip() != '':
                ven.venue_images = img.get('src')
            elif img != None and img.get('data-lazy') != None and img.get('data-lazy').strip() != '':
                ven.venue_images = img.get('data-lazy')
        link = li.find('./a')
        if link != None and link.get('href') != None:
            ven.url = self.__url__ + link.get('href')
            ven.scrape_page = self.__url__ + link.get('href')
        return ven
                                        
    def __VenueParser(self,ven):        
        url = ven.scrape_page
        print 'Scrapping: ' + url.encode('utf8').encode('string-escape')
        xpathVenue = '//header[@class="clearfix space-mbs"]|//div[@id="vip-tabs-images"]|//div[@id="vip-tabs-map"]|//section[@itemtype="http://schema.org/Person" and @data-sticky-header-target="reply.box.2"]|//p[@class="ad-description" and @itemprop="description"]|//ul[@class="inline-list-slash media-body"]|//script[contains(text(),"revealSellerTelephoneNumberToken")]'   
        xmlVenue = Util.getRequestsXML(url,xpathVenue)
        if xmlVenue != None:
            website = xmlVenue.xpath('.//a[@class="truncate-line"]')
            if len(website) > 0:
                website = website[0]
                if website.get('href') != None:
                    ven.website = website.get('href')
                elif website.text != None:
                    ven.website = website.text.replace('\r','').replace('\n','').strip()
            ul = xmlVenue.find('./ul')
            if ul != None and len(ul) > 0:
                ul = ul.xpath('.//text()')
                ul = [x.replace('\r','').replace('\n','').strip() for x in ul if x.replace('\r','').replace('\n','').strip() != '']
                ven.category = ul[-1]
            header = xmlVenue.find('./header')
            if header != None and header.find('./strong') != None:
                ven.formatted_address = "".join(header.find('./strong').itertext())
            listImage = xmlVenue.find('./div[@id="vip-tabs-images"]')
            if listImage != None:
                listImage = listImage.xpath('.//img')
                if len(listImage) > 0:
                    ven.img_link = []
                    for img in listImage:
                        if img.get('src') != None and img.get('src').strip() != '':
                            ven.img_link.append(img.get('src'))                            
                        elif img.get('src') == None and img.get('data-lazy') != None and img.get('data-lazy').strip() != '':
                            ven.img_link.append(img.get('data-lazy')) 
            map = xmlVenue.find('./div[@id="vip-tabs-map"]')   
            if map != None and map.find('./div[@class="googlemap"]') != None and map.find('./div[@class="googlemap"]').get('data-googlemap') != None:
                map = map.find('./div[@class="googlemap"]').get('data-googlemap')
                lat = map[map.find('latitude:') + len('latitude:'):map.rfind(',')]                      
                lng = map[map.rfind(':') + 1:]
                try:
                    float1 = float(lat)
                    float2 = float(lng)
                    ven.latitude = lat
                    ven.longitude = lng
                except:
                    ''
            section = xmlVenue.find('./section')
            if section != None:
                section = section.find('.//div[@class="media space-man h-underline-s"]/div[@class="media-body"]')                   
                if section != None:
                    h2 = section.find('./h2')
                    if h2 != None and h2.text != None:
                        ven.name_of_contact = Validation.ReValidString(h2.text.replace('/','-'))
                    span = section.find('./span')
                    if span != None and span.text != None:
                        ven.hqdb_ad_posted = span.text
            p = xmlVenue.find('./p')
            if p != None:
                p = p.xpath('.//text()')
                p = [x.replace('\r','').replace('\n','').strip() for x in p if x.replace('\r','').replace('\n','').strip() != '']
                ven.description = " | ".join(p)
            script = xmlVenue.find('./script')
            if script != None and script.text != None:
                script = script.text
                script = script[script.find('revealSellerTelephoneNumberToken": "') + len('revealSellerTelephoneNumberToken": "'):]
                script = script[0:script.find('"')]
                phoneJson = self.__GetPhone(ven.adid,script)
                if phoneJson != None and phoneJson.get('data') != None:
                    phone = phoneJson.get('data')
                    phone = Util.removesingleSpace(phone)                    
                    if phone.startswith('0044'):
                        phone = '+44' + phone[4:]
                    if phone.replace('+44','0').startswith('06') or phone.replace('+44','0').startswith('07'):
                        if ven.mobile_number == None:
                            ven.mobile_number = phone                            
                    else:
                        if ven.office_number == None:
                            ven.office_number = phone
                            if ven.office_number.startswith('00000'):
                                ven.office_number = ''                            
        return ven

    def __ServicesParser(self):
        print "Getting list of Services"

    def __GetPhone(self,adID,token):
        #adID get in Reveal button: data-reveal="advertId:<adID>"
        #token get in pagesource: revealSellerTelephoneNumberToken
        try:
            url = "https://www.gumtree.com/ajax/account/seller/reveal/number/{0}"
            url = url.format(adID)
            querystring = {"_":adID}
            headers = {
                    'x-gumtree-token': token,
                    'x-requested-with': "XMLHttpRequest",
                    'content-type': "application/x-www-form-urlencoded"            
                }
            response = requests.request("GET", url, headers=headers, params=querystring,timeout=(60,60),verify=False)    
            return response.json()
        except:
            return None