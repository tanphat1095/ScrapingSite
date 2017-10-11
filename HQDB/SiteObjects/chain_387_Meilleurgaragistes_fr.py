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
import requests
from time import sleep
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import time
import phonenumbers
import threading
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
    indexc_ =-1
    link_venues = []
    runningThread =[]
    listlink=[]
    phoneRemove =['08714856510','055094212','0549569']
    removeFromStreet=['-',',','.']
    regex_= ['(BP[\s][\d]{1,5})','(BP[\d]{1,5})','(BP[\s][\d]{1,5})','(B.P.[\s][\d]{1,5})','(CS[\s][\d]{1,5})','(CS[\d]{1,5})','([\d]{1,4}[\s]{1,5}[\d]{1,4})','([\d]{4,20})']
    
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
        #string =  'SILIGOM - SARL PNEU ROUTE 01  165 RADIOR'
        #print self.validateStreet2(string)
        #print self.replaceChar('-', self.replaceChar(',', string, True), True)
        self.__getListVenues()
        #self.__VenueParser('https://www.meilleur-garagiste.com/annuaire/eurotyre-bot630.460039.html')
        
    def addIndex(self):
        index = self.indexc_+1
        self.indexc_ = index
        return index
    def checkAlive(self):
        count=0
        for thread_ in self.runningThread:
            if thread_.isAlive():
                count+=1
            else:
                self.runningThread.remove(thread_)
        print str(count) +' thread is runing'
        return count
    
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
            
                for item in listPerpage:
                    link__ = self.__url__+ item.get('href')
                    self.listlink.append(link__)
                print 'Found: '+ str(len(self.listlink))
                
            else:
                print 'End'
                break
        print 'Total: '+str(len(self.listlink))+' url found'
        while len(self.listlink)>0:
            print str(len(self.listlink)) +' link exist'
            if self.checkAlive()<5:
                items=  self.listlink[-1]
                #link_ = self.__url__+ items.get('href')
                thread1 = threading.Thread(target=self.__VenueParser,args=(items,))
                self.listlink.remove(items)
                self.runningThread.append(thread1)
                thread1.start()
                time.sleep(0.3)
                #time.sleep(1)
            else:
                time.sleep(1)
            '''if len(listPerpage)>0:
                while len(listPerpage)> 0:
                    if self.checkAlive()<5:
                        try:
                            items =listPerpage[-1]
                            link_ = self.__url__+ items.get('href')
                            thread1 = threading.Thread(target=self.__VenueParser,args=(link_,))
                            self.runningThread.append(thread1)
                            listPerpage.remove(items)
                            thread1.start()
                            time.sleep(0.1)
                        except Exception,ex:
                            print ex
                            continue
                    else:
                        time.sleep(1)
                
            else:
                print 'End'
     
               break'''
    def getFromList(self,list_):
        for items in list_:
            link = self.__url__+ items.get('href')
            self.listlink.append(link)
            print link      
    def __VenueParser(self, link): 
        #link ='https://www.meilleur-garagiste.com/annuaire/garage-la-couronne.464207.html'       
        print 'Scrapping: ' + link+'\n'
        existing=[x for x in self.link_venues if link in x]
        if len(existing)>0:
            print 'Len existing : '+ str(len(existing))
            return 
        xmlBody = Util.getRequestsXML(link,'//div[@id="fiche-artisan"]')
        if xmlBody !=None and len(xmlBody)>0:
            ven = Venue()
            name_ = xmlBody.xpath('.//h1/parent::div')
            if len(name_)>0:
                if name_!=None:
                    name_h1 = name_[0].find('./h1')
                    name_h2 = name_[0].find('.//h2')
                    if name_h2!=None:
                        ven.name = name_h1.text
                    else:
                        ven.name = name_h1.text
           
            else:
                return            
            xmldiv = xmlBody.find('.//div[@class="row nomargin"]/div')
            if xmldiv ==None: 
                return 
            span_ = xmldiv.xpath('./span')
            for i_ in span_:
                if i_.get('class')== 'street-address text-hide-mobile':
                    ven.street = i_.text
                    if ven.street!=None:
                        #ven.street = self.validateStreet(ven.street).replace('43442491700012', '')
                        ven.street = self.validateStreet2(ven.street).replace('43442491700012', '')
                        #ven.street = self.replaceChar('-', self.replaceChar(',', ven.street, True), True)
                        #ven.street = self.replaceChar(',', self.replaceChar('-', ven.street, True), True)
                        ven.street = self.replaceChar('-', ven.street, False)
                        for r in self.removeFromStreet:
                            ven.street = self.replaceChar(r, ven.street, True)
                        if ven.street.strip()=='.':
                            ven.street= None
                if i_.get('class')=='postal-code':
                    ven.zipcode = i_.text
                    ven.zipcode = self.validateZipcode(ven.zipcode)
                if i_.get('class')=='locality':
                    ven.city = i_.text
            a = xmlBody.find('.//a[@class="col m12 s4 tel waves-effect waves-light btn center btn-fix bleu"]')
            if a!=None:
                phone = a.get('href').replace('tel:','').replace(' ','')
                if phone.startswith('07') | phone.startswith('06'):
                    ven.mobile_number = self.validatePhone__(phone, 'FR')
                else:
                    ven.office_number =  self.validatePhone__(phone, 'FR')
            logo =  xmlBody.find('.//div[@class="center-align"]/img')
            if logo!=None:
                ven.img_link= [self.__url__+ logo.get('src')]
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
            if ven.city!=None and ven.zipcode !=None:
                if ven.street !=None and len(ven.street)>0:
                    add_= ven.street+', '+ ven.city+', '+ ven.zipcode
                else:
                    add_ = ven.city+', '+ven.zipcode
            else:
                add_ = None      
            (ven.latitude,ven.longitude) = self.getLatlng(add_, 'FR')
            if ven.latitude == None and ven.longitude ==None:
                Util.log.coordinate_logger.error(ven.scrape_page+' : Cannot get GEO code')
            self.link_venues.append(link)
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
            ven.description =desc_.replace('|', '\n')
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
            ven.is_get_by_address = True
            ven.category='Garages/Car services'
            featureAd= xmlBody.find('.//a[@class="vert-text modal-trigger"]/strong')
            if featureAd!=None:
                text = featureAd.text.replace('é','e')
                if text =='Entreprise verifiee ':
                    ven.hqdb_featured_ad_type ='Featured'
            if ven.zipcode !=None  and len(ven.zipcode)>0 and ven.zipcode.isdigit() :
                zip_ = int(ven.zipcode)
                if zip_ <1000 :
                    Util.log.running_logger.error(link+': Oversea of Fr - Zipcode:'+ ven.zipcode)
                    return
                if zip_ >95978 :
                    Util.log.running_logger.error(link+': Oversea of Fr - Zipcode:'+ ven.zipcode)
                    return
                if len(ven.zipcode)>=4:
                    if len(ven.zipcode)==4:
                        ven.zipcode = '0'+ ven.zipcode
            index_ = self.addIndex()
            print 'Writing files: '+ str(index_)+'\n'
            ven.writeToFile(self.folder, index_, ven.name, False)
            print str(len(self.services))+ ' services\n'
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
    def validateStreet2(self, street):
        for reg in self.regex_:
            results = re.search(reg, street, flags=0)
            if results!=None:
                street = street.replace(results.group(0),'')
        return street
    def validatePhone(self,phone):
        if phone ==None:
            return None
        for re in self.phoneRemove:
            phone.replace(re,'')
        if phone.isdigit():
            if phone.startswith('0'):
                if len(phone)>=11:
                    return phone
                else:
                    return None
            else:
                if len(phone)>=10:
                    return phone
                else:
                    return None
        else:
            return None
    def validateZipcode(self,zipcode):
        if zipcode.isdigit() and len(zipcode) >=4:
            return zipcode
        else:
            None 
    def validatePhone__(self,phone,country='FR'):        
        try:
            parsed_phone = phonenumbers.parse(phone, country.upper(), _check_region=True)
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
    def replaceChar(self,char,string,isStart=True):
        string = string.strip()
        if isStart ==True:
            if string.startswith(char):
                string = string[1:len(string)]
        else:
            if string.endswith(char):
                string = string[0:len(string)-1]
        
        return string
        
        