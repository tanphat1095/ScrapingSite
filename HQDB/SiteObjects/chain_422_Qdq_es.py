#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Util,Validation
from lxml import etree as ET
from SiteObjects.Objects_HQDB import Venue, Service
import re
import json
import threading
import urllib3
import phonenumbers
from time import sleep
import Common.Validation as Validator
import time
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
class Qdq_es(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = 'http://es.qdq.com'
    _language = 'es'
    _chain_ = 'chain_422_'
    __name__ = 'QDQ'
    _url_lstVenues = ''    
    _xpath_lstVenues = ''        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    index =-1
    countingVenues = 0
    listLink =[]
    threadRunning =[]
    def addIndex(self):
        index = self.index
        index+=1
        self.index =  index
        print 'Getting index: '+str(index)
        return index
    
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
        self.phoneCodeList = Util.getPhoneCodeList()
        try:
            self.__getListVenues()
        except Exception,ex:
            print ex
    def checkAlive(self):
        count =0
        for t in self.threadRunning:
            if t.isAlive():
                count+=1
            else:
                self.threadRunning.remove(t)
        return count
    def __getListVenues(self):
        counting =0
        categoryHome =  Util.getRequestsXML(self.__url__, '//ul[@class="categoriasHome"]')
        if categoryHome !=None:
            listcate_sub = categoryHome.xpath('./ul[@class="categoriasHome"]/li')
            for li in listcate_sub:
                subcate = li.text.replace(':','').strip()
                moreInfo = li.xpath('./ul/li/a/strong/parent::a')
                if len(moreInfo)>0:
                    listCate = Util.getRequestsXML(moreInfo[0].get('href'), '//div[@class="dosCol"]/ul/li/a')
                    listCate = listCate.xpath('./a')
                    counting += len(listCate)
                    for cate in listCate:
                        self.getListVenues(cate,cate.text)
                else:
                    listCate_2 = li.xpath('./ul/li/a')
                    counting+= len(listCate_2)
                    for cate_2 in listCate_2:
                        self.getListVenues(cate_2,cate_2.text)
        print 'Total: '+ str(counting)
    
    def getListVenues(self,xmlElement,cate):
        pages =-99
        while True:
            pages+=100
            numbers= 0
            try:
                link___ = xmlElement.get('href')+'/pag-'+str(pages)+'/rows-99/s:/'
                listVenues__ = Util.getRequestsXML(link___, '//div[@id="listadoResultados"]')
                listVenues = listVenues__.xpath('//li[@class="estirar gratuito"]')
                listVenues_2 = listVenues__.xpath('//li[@class="estirar "]')
                #print ET.dump(listVenues__)
                lenght_2 =  len(listVenues_2)
                lenght=    len(listVenues)
                self.countingVenues+=lenght
                self.countingVenues+=lenght_2
                if len(listVenues)<=0:
                    break
                while len(listVenues) > 0 :
                    if self.checkAlive()<10:
                        numbers+=1
                        scrappages = link___+'#'+str(numbers)
                        thread1 = threading.Thread(target=self.__VenueParser,args=(listVenues[-1],cate,scrappages))
                        self.threadRunning.append(thread1)
                        thread1.start()
                        listVenues.pop()
                    else:
                        time.sleep(0.1)
                while len(listVenues_2) >0:
                    if self.checkAlive()<10:
                        numbers+=1
                        scrape_pages =  link___+ '#'+str(numbers)
                        '''thread2 = threading.Thread(target=self.__VenueParser_2,args=(listVenues_2[-1],subcate,cate,scrape_pages))
                        self.threadRunning.append(thread2)
                        thread2.start()'''
                        self.__VenueParser_2(listVenues_2[-1], cate, scrape_pages)
                        listVenues_2.pop()
                    else:
                        time.sleep(0.1)
                
                
            except Exception,ex:
                print ex
                continue
        print str(self.countingVenues)
        
        
        
    def __VenueParser_2(self,element,cate,scrape_pages):
        subB = element.find('./div/a')
        link = subB.get('href')
         
        try:
            existing=[x for x in self.listLink if link in x]
            if len(existing)<=0:
                print 'Scraping Feature : '+ link
                if link =='http://www.qdqplus.es/u4cwxsxmf/':
                    print
                self.listLink.append(link)
                ven  = Venue()
                ven.country =self._language
                ven.hqdb_featured_ad_type ='featured'
                ven.category = cate
                #ven.subcategory = cate
                ven.scrape_page = scrape_pages
                subDiv = element.find('./div[@class="resultado nada"]')
                div = subDiv.find('./a/div')
                ven.name = div.find('./h2').text
                ven.name = Validator.RevalidName(ven.name)
                address =  div.xpath('./p[@itemprop="address"]/span')
                if address!=None:
                    for span in address:
                        itemprop = span.get('itemprop')
                        if itemprop =='street-address':
                            ven.street = span.text
                        if itemprop =='postal-code':
                            ven.zipcode =span.text
                        if itemprop == 'locality':
                            ven.city = span.text #.split(',')[0]
                            if ven.city=='' or ven.city ==None:
                                continue
                            find_slash = ven.city.find('/')
                            find_comma = ven.city.find(',')
                            if find_slash!=-1 and find_comma!=-1:
                                ven.city = ven.city.split('/')[0]
                                if ven.city.find(',')!=-1:
                                    ven.city = ven.city.split(',')[1]
                            ven.city = ven.city.split(',')[0]
                            ven.city = ven.city.split('/')[0]
                description = div.find('./p[@class="descripcion"]').text
                if description!=None:
                    ven.description = description
                imgs = subDiv.xpath('./a/figure/img')
                if len(imgs)>0:
                    imgs_ = []
                    for im in imgs:
                        imgs_.append(im.get('src'))
                    ven.img_link = imgs_
                footer = subDiv.xpath('./div[@class="iconos"]/ul/li')
                for fo in footer:
                    text__ = fo.find('./a').text
                    if text__ =='Mandar mail':
                        ven.business_website = fo.find('./a').get('href')
                    if text__ =='Ver telÃ©fono':
                        phone = fo.find('./span[@class="telefono"]').text
                        if phone.startswith('+346') or phone.startswith('+347') or phone.startswith('7') or phone.startswith('6'):
                            ven.mobile_number = self.validatePhone__(phone)
                        else:
                            ven.office_number = self.validatePhone__(phone)
                #ven.is_get_by_address =True
                ven.writeToFile(self.folder, self.addIndex(), ven.name, False)   
            else:
                print'Duplicate link'
        except Exception, ex:
            print ex
            print 'Error link: '+ scrape_pages
    def __VenueParser(self,element, cate,scrappages):  
        subA = element.find('./div/a')
        link = subA.get('href')      
        try:
            
            #if link =='http://es.qdq.com/f:1-GV9-6082/':
            #    print
            existing=[x for x in self.listLink if link in x]
            print 'Scraping : '+ link
            if len(existing)<=0:
                
                self.listLink.append(link)
                
                ven = Venue()
                #ven.name = subA.find('./div/h2').text
                ven.scrape_page = scrappages
                #ven.subcategory = cate
                ven.category = cate
                ven.country = self._language
                ven.hqdb_featured_ad_type="none"
                address = subA.xpath('./div/p/span')
                for span in address:
                    itemprop = span.get('itemprop')
                    if itemprop =='street-address':
                        ven.street = span.text
                    if itemprop =='postal-code':
                        ven.zipcode =span.text
                    if itemprop == 'locality':
                        
                        
                        
                        # before the first "," and before the "/"
                        
                        ven.city = span.text #.split(',')[0]
                        if ven.city =='' or ven.city ==None:
                            continue
                        
                        find_slash = ven.city.find('/')
                        find_comma = ven.city.find(',')
                        if find_slash!=-1 and find_comma!=-1:
                            ven.city = ven.city.split('/')[0]
                            if ven.city.find(',')!=-1:
                                ven.city = ven.city.split(',')[1]
                        ven.city = ven.city.split(',')[0]
                        ven.city = ven.city.split('/')[0]
            
                detail = Util.getRequestsXML(link, '//div[@id="contenido"]')
                ven.name = detail.find('.//h1').text
                ven.name = Validator.RevalidName(ven.name)
                phone = detail.find('.//span[@class="telefonoCliente"]')
                if phone!=None:
                    phone = phone.text
                    if phone.startswith('6') or phone.startswith('7'):
                        ven.mobile_number = ''+ phone
                        ven.mobile_number = self.validatePhone__(ven.mobile_number)
                    else:
                        ven.office_number =''+phone
                        ven.office_number = self.validatePhone__(ven.office_number)
                maps = detail.find('.//div[@id="mymap"]/img')
                if maps!=None:
                    maps = maps.get('src')
                    (ven.latitude,ven.longitude) = self.getLatlng(maps)
                #ven.is_get_by_address =True
                ven.writeToFile(self.folder, self.addIndex(), ven.name, False)
            else:
                print 'Duplicate link'
        except Exception, ex:
            print ex
            print 'Error Link:'+ link
    
    
    def getLatlng(self,stringSrc):
        arrays =stringSrc.split('&')
        for arr in arrays:
            if arr.startswith('markers'):
                latlng = arr.split('=')[1]
                lat =latlng.split(',')[0]
                lng = latlng.split(',')[1]
                return (lat,lng)
        return None
    
    
    def __ServicesParser(self,url,xmlServices):        
        ''
    def validatePhone__(self,phone):        
        try:
            parsed_phone = phonenumbers.parse(phone, self._language.upper(), _check_region=True)
        except phonenumbers.phonenumberutil.NumberParseException as error: 
                print str(phone) +' can not parse'
                Util.log.running_logger.error(phone+' can not parse')
                return None
        if not phonenumbers.is_valid_number(parsed_phone):
            Util.log.running_logger.error(phone+' not number')
            print str(phone) +': not number'
            return None
        else:
            return phone
    