#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Util,Validation
from lxml import etree as ET
from lxml import html
from SiteObjects.Objects_HQDB import Venue, Service
import re
import json
import urllib3
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
class Architecturalindex_gb(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = 'http://www.architecturalindex.com'
    _language = 'gb'
    _chain_ = 'chain_399_'
    __name__ = 'Architectural inex'
    _url_lstVenues = ''  
    _xpath_lstVenues = ''        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    list_url= []
    
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
        self.__getListVenues()
    
    def __getListVenues(self):
        index =0
        print "Getting list of Venues"
        xmlSub = self.getRequestXML()
        xmlSub = xmlSub[xmlSub.find('<select name="strNearRegion"'):xmlSub.find('</select>')]+'</select>'
        xmlSub = html.fromstring(xmlSub)
        options =  xmlSub.xpath('./option')
        for option in options:
            value = option.get('value')
            if value !=None and len(value.split('-')) >1:
                pages = 1
                while True:
                    
                    content__ = self.getRequest(pages, value, '//div[@class="area"]/div[@class="content_wrapper"]')
                    if content__ !=None:
                        paging = content__.find('.//div[@class="paging_statistics"]')
                        if paging !=None:
                            paging =  ''.join(paging.itertext()).replace('Page','').replace('of','-').split('-')
                            #curr = paging[0].strip()
                            #curr =  int(curr)
                            
                            total = paging[1].strip()
                            total = int(total)
                        else:
                            total = 1
                        curr = pages
                        items =  content__.xpath('//div[@class="search_result"]')
                        
                        for item in items:
                            ven = self.__VenueParser(item,index)
                            if ven!=None:
                                self.list_url.append(ven.scrape_page)
                                ven.adid = item.get('id')
                                ven.writeToFile(self.folder,index,ven.name.replace(':',''),False)
                                index+=1
                        if curr == total:
                            break
                    pages+=1
                    
    def __VenueParser(self, xmlE,index):        
        print 'Scrapping: '
        ven  = Venue()
        ven.category ='architecural technologist'
        photos = xmlE.find('./div[@class="search_result_photo"]/div[@class="photo"]/a')
        ven.venue_images = self.__url__+ photos.find('./img').get('src')
        ven.scrape_page = self.__url__+ photos.get('href')
        print str(index)+' >>'+ ven.scrape_page
        existing=[x for x in self.list_url if ven.scrape_page in x]
        if len(existing)>0:
            print 'This venues exist in list'
            return None
        
        details_ =  xmlE.find('.//div[@class="search_result_details"]')
        ven.name =  details_.find('./div[@class="title"]/h3/a').text
        contacts_ = details_.find('./div[@class="contact"]').text
        ven.description = details_.find('./div[@class="desc"]').text
        contact__ = contacts_.split(',')
        if len(contact__)>=2:
            ven.zipcode = contact__[len(contact__)-1]
            ven.city = contact__[len(contact__)-2]
            
        #scraping details ____ 
        #ven.scrape_page ='http://www.architecturalindex.com/consumers/architects/architect.asp?lngArchitectId=207922'
        xmlInfo = Util.getRequestsXML(ven.scrape_page, '//div[@class="architect_header"]/parent::div' )
        if xmlInfo!=None:
            addressInfo = xmlInfo.find('.//div[@class="architect_header"]/div[@class="architect_header_info"]')
            h2 = addressInfo.find('./h2')
            if h2!=None:
                addressInfo.remove(h2)
            address__ = ' '.join(addressInfo.itertext())
            if ven.city== None:
                __address =  address__.split(',')
                ven.city = __address[len(__address)-3]
            if len(ven.city)<2:
                __address =  address__.split(',')
                ven.city = __address[len(__address)-3]
            street = address__[0:address__.find(ven.city.strip())-1]
            if street.endswith(','):
                street  = street[0:len(street)-1]
                if street.upper().find('PO BOX')>=0:
                    street = None
                ven.street = street
            
            #ven.office_number= '08708700053'
            img= []
            img_info = xmlInfo.find('.//div[@class="architect_portfolio"]')
            photos_ = img_info.xpath('./div[@class="architect_portfolio_photo"]//img')
            for photo in photos_:
                im_ = self.__url__+ photo.get('src')
                img.append(im_)
            ven.img_link = img
            sers = []
            des = xmlInfo.find('.//div[@class="architect_info_statement"]')
            des = ' '.join(des.itertext())
            ven.description = des
            services = xmlInfo.xpath('//div[@class="architect_info"]/ul')
            desP = xmlInfo.xpath('//div[@class="architect_info"]/p')
            affi =  xmlInfo.xpath('//div[@class="architect_info"]/h3')
            isAffiliations  =''
            for aff in affi :
                if aff.text.strip() =='Affiliations':
                    isAffiliations= desP[len(desP)-1].text
                    ven.accreditations = isAffiliations
            
            
            if len(desP)>=2:
                p1 = desP[0].text
                p2 = desP[1].text
                
                #ven.description= ven.description+' '+p1+' '+p2
                if p1!=None:
                    ven.description+=' '+p1
                if p2!=None:
                    if p2!='None':
                        ven.description+=' '+p2+': '
            
            
            if len(services)>=3:
                services_ = services[1]
                listSer = services_.xpath('./li')
                
                
                listDes_2 =  services[2].xpath('./li')
                des_2 = ''
                if len(listDes_2)>0:
                    des_2 ='. Specialist Experience: '
                    for des2 in listDes_2:
                        des_2 += des2.text+', '
                
                    des_2 = des_2.strip()
                    if des_2.endswith(','):
                        des_2 = des_2[0:-1]
                
                
                listDes =  services[0].xpath('./li')
                if len(listDes)>0:
                    desSectors = ''
                    for lides in listDes:
                        desSectors+= lides.text+', '
                    desSectors = desSectors.strip()
                    if desSectors.endswith(','):
                        desSectors = desSectors[0:-1]
                    ven.description = ven.description+' '+ desSectors+'.'+des_2
                    ven.description = ven.description.replace(', ,', ', ').replace('..','.')
                for ser in listSer:
                    se = ser.text
                    serv = Service()
                    serv.service = se
                    sers.append(serv)
            ven.services = sers
            ven.pricelist_link = [ven.scrape_page]
            ven.country ='gb'
            if ven.street!=None:
                add_ = ven.street+', '+ven.city+', '+ ven.zipcode
            else:
                add_ = ven.city+', '+ ven.zipcode
            (ven.latitude,ven.longitude) = self.getLatlng(add_, 'UK')
            
            
            
        else:
            return None 
        return ven
    
    
    def getLatlng(self,address,countr):
        try:
            jsonLatlng = Util.autoChange(address, countr)
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
    def __ServicesParser(self,url,xmlServices):        
        ''
    def getRequestXML(self):
            url = "http://www.architecturalindex.com/consumers/search/search.asp?intCountryId=1&strNearRegion=100-0"
            querystring = {"Referer":"http://www.architecturalindex.com/consumers/search/search.asp?intCountryId=1&strNearRegion=0"}
            headers = {
                'cache-control': "no-cache",
                'postman-token': "6245b561-3452-d58c-315b-eeb107d67912"
                        }

            response = requests.request("GET", url, headers=headers)
            return   response.text
    def getRequest(self,pages,value,xpath_):
        url = 'http://www.architecturalindex.com/consumers/search/search.asp?strNearRegion='+str(value)+'&intPage='+str(pages)
        print '*'*25
        print 'Request: '+url
        print'*'*25
        results = Util.getRequestsXML(url,xpath_)
        return results