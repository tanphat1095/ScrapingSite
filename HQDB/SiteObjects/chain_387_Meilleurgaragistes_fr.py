'''
Created on 28 thg 8, 2017

@author: phat.le
'''
#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Util,Validation
from lxml import etree as ET
from SiteObjects.Objects_HQDB import Venue, Service
import re
import json
from array import array
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Meilleurgaragistes_fr(BaseSite):
    phoneCodeList = None
    __url__ = 'https://www.meilleur-garagiste.com'
    _language = ''
    _chain_ = 'chain_387_'
    __name__ = 'Meilleure Garagistes'
    _url_lstVenues = 'https://www.meilleur-garagiste.com/france/'    
    _xpath_lstVenues = ''        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
     
        '''
        Code Here
        '''
        #Write Files
        self.phoneCodeList = Util.getPhoneCodeList()
        self.__getListVenues()
        
    
    def __getListVenues(self):
        print "Getting list of Venues"
        index = 1
        index_ =0
        while True :
            print 'pages: '+ str(index)
            xmlDoc = self.getXML('//div[@class="liste-entreprise"]', index) #
            #print ET.dump(xmlDoc)
            index+=1
            listPerpage = xmlDoc.xpath('//a/h2/parent::a')
            if len(listPerpage)>0:
                for items in listPerpage:
                    link_ = self.__url__+ items.get('href')
                    ven = self.__VenueParser(link_)
                    if ven!=None:
                        print 'Writing files: '+ str(index_)
                        ven.writeToFile(self.folder, index_, ven.name, False)
                        print str(len(self.services))+ ' services'
                        index_+=1
                    
            else:
                break
            
        

    def __VenueParser(self, link):        
        print 'Scrapping: ' + link
        xmlBody = Util.getRequestsXML(link,'//div[@id="fiche-artisan"]')
        if xmlBody !=None and len(xmlBody)>0:
            ven = Venue()
            name_ = xmlBody.find('.//h1')
            if name_ !=None :
                name_ = name_.text
                ven.name = name_
            xmldiv = xmlBody.find('.//div[@class="row nomargin valign-wrapper"]/div')
            if xmldiv ==None: 
                return None
            span_ = xmldiv.xpath('./span')
            for i_ in span_:
                if i_.get('class')== 'street-address text-hide-mobile':
                    ven.street = i_.text
                    if ven.street!=None:
                        ven.street = self.validateStreet(ven.street).replace('43442491700012', '')
                        if ven.street.strip()=='.':
                            ven.street= None
                if i_.get('class')=='postal-code':
                    ven.zipcode = i_.text
                    if ven.zipcode !=None  and len(ven.zipcode)>0 and ven.zipcode.isdigit() :
                        zip_ = int(ven.zipcode)
                        if zip_ <1000 | zip_>95978:
                            return None
                if i_.get('class')=='locality':
                    ven.city = i_.text
            a = xmlBody.find('.//a[@class="col m12 s4 tel waves-effect waves-light btn center btn-fix bleu"]')
            if a!=None:
                phone = a.get('href').replace('tel:','').replace(' ','')
                if phone.startswith('07') | phone.startswith('06'):
                    ven.mobile_number = phone
                else:
                    ven.office_number =  phone
            logo =  xmlBody.find('.//div[@class="center-align"]/img')
            if logo!=None:
                ven.venue_images = self.__url__+ logo.get('src')
            ven.scrape_page = link
            ven.pricelist_link = [link]
            listServices = xmlBody.xpath('//li/div[@class="collapsible-body"]/div/a')
            sers =[]
            for ser in listServices :
                servic = Service()
                servic.service = ser.text
                sers.append(servic)
                self.services.append(servic)
            ven.services = sers
            if ven.street !=None and len(ven.street)>0:
                add_= ven.street+', '+ ven.city+', '+ ven.zipcode
            else:
                add_ = ven.city+', '+ven.zipcode
                    
            (ven.latitude,ven.longitude) = self.getLatlng(add_, 'FR')
            
            
            ven.country='fr'
            desc = xmlBody.find('.//p[@id="description"]')
            desc_ =''
            if desc!=None:
                
                desc_ = ''.join(desc.itertext()).strip().replace('\n','|').replace('\t','')
            
            title = xmlBody.find('.//div[@class="container"]//h2')
            if title !=None and desc !=None:
                desc_  = title.text+ ' | '+ desc_
            img_link_arr = []
            desc_ = self.replace__(desc_)
            desc_ = self.replaceSame(desc_, '||', '|').replace('|',' | ')
            ven.description =desc_
            
            img_link = xmlBody.find('.//div[@class="realisations"]/img')
            if img_link!=None:
                temp_img  =   ven.img_link = self.__url__+ img_link.get('src')
                img_link_arr.append(temp_img)
            multi_img =  xmlBody.xpath('//div[@class="3photo realisations"]/div/img')
            for it in multi_img:
                temp_ml = self.__url__+ it.get('src')
                img_link_arr.append(temp_ml)
                
            if len(img_link_arr)>0:
                ven.img_link = img_link_arr
            nr_reviewer = xmlBody.xpath('//div[@class="avisoperation row"]')
            if len(nr_reviewer)>0:
                ven.hqdb_nr_reviews = str(len(nr_reviewer))
            return ven

    def __ServicesParser(self,url,xmlServices):     
            ''
    def getXML(self,xpath_,param_):
        xml= Util.getRequestsXML(self._url_lstVenues+'.'+str(param_)+'.html', xpath_)
        return xml
    def getLatlng(self,address,countr):
        try:
            jsonLatlng = Util.getGEOCode(address, countr)
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
    def replaceSame(self, string, old_,new_):
        for i in range(0, 5):
            string = string.replace(old_,new_)
        return string
    def replace__(self,string):
        arrays= string.split('|')
        if len(arrays)>0:
            for i in range(0,len(arrays)):
                arrays[i] = arrays[i].strip()
        return '|'.join(arrays)
    def validateStreet(self,String_):
        #String_ = '3029 LA LAURAGAISE ROUTE DE BAZIEGE BP 78178'
        array_ = String_.split()
        if len(array_)>1:
            if array_[len(array_)-1].isdigit() and array_[len(array_)-2] =='BP':
                return ' '.join(array_[0:len(array_)-2])
            if  array_[len(array_)-1].isdigit() and array_[len(array_)-2] =='PB':
                return ' '.join(array_[0:len(array_)-2])
            else:
                return String_
        else:
            return String_