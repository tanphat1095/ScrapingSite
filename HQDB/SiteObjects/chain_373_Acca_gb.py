#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Util, Validation
from Objects_HQDB import Service
from Objects_HQDB import Venue
import re
import time
import phonenumbers
from selenium import webdriver
import urllib3
import threading
from lxml import etree as ET
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class Acca_gb(BaseSite):
    """description of class"""
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = 'http://www.accaglobal.com'
    _language = 'gb'
    _chain_ = 'chain_373_'
    __name__ = 'ACCA'
    _url_lstVenues = ''    
    _xpath_lstVenues = ''        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    #char['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']#,'ä','ö','ü','ß','ñ']
    venues_=[]
    outFileVN = ''
    outFileSV = ''
    listlink =[]
    countryRunning=[]
    phoneRemove= ['01717643013','32475466172','09793373930','246988907791297065']
    listCountry =['UK','FR','BM','NE','GF','IT','SP','CZ','PL']
    
    '''zipcode regex'''
    ukReg = '((?:[gG][iI][rR] {0,}0[aA]{2})|(?:(?:(?:[a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y]?[0-9][0-9]?)|(?:(?:[a-pr-uwyzA-PR-UWYZ][0-9][a-hjkstuwA-HJKSTUW])|(?:[a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y][0-9][abehmnprv-yABEHMNPRV-Y]))) {0,}[0-9][abd-hjlnp-uw-zABD-HJLNP-UW-Z]{2}))'
    frReg='\d{2}[ ]?\d{3}'
    bmReg='[A-Z]{2}[ ]?[A-Z0-9]{2}'
    neReg='\d{4}'
    gfReg='9[78]3\d{2}'
    itReg='\d{5}'
    spReg=None
    czReg='\d{3}[ ]?\d{2}'
    plReg='\d{2}-\d{3}'
    regex_ = {"UK":ukReg,"FR":frReg,"BM":bmReg,"NE":neReg,"GF":gfReg,"IT":itReg,"SP":spReg,"CZ":czReg,"PL":plReg}
    index_ =-1
    threadRunning =[]
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    def doWork(self):
        
        
        
        #print self.validateZipcode('BN11ITU', 'UK')
        
        self.phoneCodeList = Util.getPhoneCodeList()
        for countr in range(0,len(self.listCountry)):
            countr_ = self.listCountry[countr]
            existing=[x for x in self.countryRunning if countr_ in x]
            if len(existing)<=0:
                self.countryRunning.append(countr_)
                thread1 = threading.Thread(target=self.__getListVenues,args=(countr_,))
                thread1.start()
                thread1.join()
                
        
    def addindex(self):
        index__ = self.index_+1
        self.index_ = index__
        return index__
    def checkAlive(self):
        count = 0
        for t in self.threadRunning:
            if t.isAlive():
                count+=1
            else:
                self.threadRunning.remove(t)
        print str(count)+' thread is running'
        return count
    def __getListVenues(self,countr):
        for post in  range(0,10) + [chr(x) for x in range(ord('a'), ord('z')+1)]:
        #for post in  [chr(x) for x in range(ord('b'), ord('z')+1)]:
                page =1
                countRequest =1
                url = self.url_(page,post,countRequest,countr)
                print 'Find with: '+str(post)
                isTable = Util.getRequestsXML(url,'//table[@class="table-responsive firm-search-results expandable-rows"]')
                if isTable == None:
                    continue
                while len(isTable)>0:
                    page = countRequest*4-3
                    url = self.url_(page,post,countRequest,countr)
                    #url ='http://www.accaglobal.com/ca/en/member/find-an-accountant/find-firm/results.html?isocountry=VN&location=&country=UK&firmname=a&organisationid=ACCA&hid=&pagenumber=3&resultsperpage=5&requestcount=1'
                    print 'find with url: '+url
                    isTable = Util.getRequestsXML(url,'//table[@class="table-responsive firm-search-results expandable-rows"]')
                    #hides=  isTable.xpath('//tr[@class="expandable"]')
                    hides =  isTable.xpath('//tr/td/h5/a')
                    print 'found: '+str(len(hides))
                    while len(hides)>0:
                        link = hides[-1].get('href')
                        if self.checkAlive()<6:
                            thread2 = threading.Thread(target=self.__VenueParser,args=(self.__url__+link,countr))
                            hides.remove(hides[-1])
                            thread2.start()
                            self.threadRunning.append(thread2)
                        else:
                            time.sleep(1)       
                    countRequest+=1
                print countr +' done'
                #Util.log.running_logger.warning(countr+' done')
    def __VenueParser(self, link,countr):  
        ven = Venue()
        #link =  'http://www.accaglobal.com/uk/en/member/find-an-accountant/find-firm/results/details.html?isocountry=VN&location=&country=CZ&firmname=a&organisationid=ACCA&hid=&pagenumber=1&resultsperpage=25&requestcount=1&advisorid=2437095'
        print 'Scraping :'+ link
        id_ =  link[link.find('advisorid=')+len('advisorid='):+ len(link)]
        existing=[x for x in self.listlink if id_ in x]
        if len(existing)>0:
            return
        self.listlink.append(id_)
        ven.adid = id_
        ven.country =countr.lower()
        if ven.country =='uk':
            ven.country ='gb'
        ven.name = ''
        ven.scrape_page = link
        xmlVenues = Util.getRequestsXML(ven.scrape_page, '//div[@id="main"]') #//div[@class="content-section no-padding"]
        if xmlVenues==None:
            return 
        addressInfo = xmlVenues.xpath('//address')
        address_ = ''
        ven.name = xmlVenues.find('.//h1').text
        if len(addressInfo)>0:
            address_ = ' '.join(addressInfo[0].itertext()).replace('\n','').replace('  ',' ').replace(ven.name.strip(),'')   
        servicesInfo =  xmlVenues.xpath('//div[@class="col-sm-7 col-md-8 firm-details-main text-section"]/div')
        maps =  xmlVenues.find('.//div[@id="map"]')
        if maps!=None:
            maps = maps.get('data-address')
        for row in servicesInfo:
            if row.find('.//h5')!=None:
                title = row.find('.//h5').text
                if title=='Certificates held':
                    certi =  row.find('./div[@class="col-md-7"]/p')
                    if certi!=None:
                        certi = certi.text.replace('\n','').replace('\t','')
                        ven.accreditations = certi
                if title =='Services offered':
                    serString = row.find('./div[@class="col-md-7"]/p')
                    if serString!=None:
                        serString = serString.text.replace('\n','').replace('\t','').replace(',,',',')
                        ven.services = self.__ServicesParser(serString)
                if title=='Sector expertise':
                    desc =row.find('./div[@class="col-md-7"]/p')
                    if desc !=None:
                        desc = desc.text
                        ven.description = 'Sector expertise: -'+ ' -'.join(self.formatDes(desc))
                        
        information =  xmlVenues.find('.//div[@class="firm-details-contact firm-details-panel"]')
        address__ = address_.split('\r')
        lensAdd = len(address__)
       
        info = address__[1].split(',')
        info = info[len(info)-1]
        info = info.split()
        #print ET.dump(addressInfo[0])
        findCity = addressInfo[0].xpath('./div')[0]
        
        #findCity = None
        if findCity!=None:
            city = findCity.text
            address2= address_.replace('\n', '').replace(ven.name.strip(), '')
            street = address2[0:address2.find(city)].replace('PO BOX 16988','')
        else:
            city = info[len(info)-1]
            street= ' '.join(info[0:len(info)-1]).replace(ven.name.strip(), '').replace('PO BOX 16988','')
        if city !=None:
            
            for ad in range(0,lensAdd):
                if address__[ad].find(city)!=-1:
                    if (lensAdd -1)-ad ==3:
                        zipcode = address__[lensAdd-1]
                        ven.zipcode = self.validateZipcode(zipcode, countr)
                        break
        #ven.zipcode='BN11ITU'
        if ven.zipcode!=None:
            if len(ven.zipcode.strip())==2:
                ven.zipcode.replace('de', '').replace('DE','')
                ven.zipcode = self.validateZipcode(ven.zipcode, countr)
        if street.upper().find('PO BOX')>=0:
            street = None
        city = city.upper()
        ven.city = city
        ven.street = self.validateStreet(street)
        
        (ven.latitude,ven.longitude) = self.getLatlng(maps, countr)
        if ven.latitude==None and ven.longitude == None:
            Util.log.running_logger.error(maps.replace('+',' ')+': '+ 'cannot get GEO code')    
        
        
        
        li = information.xpath('./ul/li')
        for l in li :
                href_ = l.find('./a')
                if href_!=None:
                    is_email = href_.get('href').startswith('mailto:')
                    if is_email ==True:
                        ven.business_email = href_.get('href').replace('mailto:','')
                    else:
                        website = href_.get('href')
                        if website.lower().startswith('http://') | website.lower().startswith('https://'):
                            ven.business_website = website
                        else:
                            ven.business_website = 'http://'+ website
                else: 
                    phone = l.text.replace(' ','')
                    if phone.strip().startswith('Tel:'):
                        phone = phone.strip().replace('Tel:','')
                        finds=  phone.find('/')
                        if finds >=0:
                            phone_ = phone.split('/')
                            if len(phone_) >=2:
                                phone_1 = phone_[0]
                                phone_2 = phone_[1]
                                phone_2 = phone_1[0:len(phone_1)-len(phone_2)]+ phone_2
                                if phone.startswith('07') | phone.startswith('7')| phone.startswith('+447')| phone.startswith('447'):
                                    ven.mobile_number = self.valiDatePhone(phone_1)
                                else:
                                    ven.office_number = self.valiDatePhone(phone_1)
                                if phone.startswith('07') | phone.startswith('7')| phone.startswith('+447')| phone.startswith('447'):
                                    ven.mobile_number2 = self.valiDatePhone(phone_2)
                                else:
                                    ven.office_number2 = self.valiDatePhone(phone_2)
                        else:
                                if phone.startswith('07') | phone.startswith('7')| phone.startswith('+447')| phone.startswith('447'):
                                    ven.mobile_number = self.valiDatePhone(phone)
                                else:
                                    ven.office_number = self.valiDatePhone(phone)   
        ven.is_get_by_address = True
        ven.business_website = self.validateWebsite(ven.business_website)
        index_ = self.addindex()
        print  'writing index:'  +str(index_)
        ven.writeToFile(self.folder,index_,ven.name,False)
        #return ven
        
    def __ServicesParser(self,stringServices):        
        
        list_services =stringServices.split(',')
        sers =[]
        ser_i=0
        for iser in range(0,len(list_services)):
            if ser_i >=len(list_services):
                break
            ser = Service()
            ser_services =''
            if list_services[ser_i].find('(')>=0: 
                for ichild in range(ser_i,len(list_services)):
                    strn=  list_services[ser_i]                
                    if list_services[ser_i].find(')')>=0:
                        ser_services =ser_services+ strn
                        ser_i +=1
                        break
                    else:
                        ser_services= ser_services+ strn+', '
                        ser_i +=1
            else :
                ser_services = list_services[ser_i]
                ser_i+=1
            ser.service = ser_services.strip()
            if len(ser.service.strip())>5:
                sers.append(ser)
        return sers
    def formatDes(self,stringServices):        
        
        list_services =stringServices.split(',')
        sers =[]
        ser_i=0
        for iser in range(0,len(list_services)):
            if ser_i >=len(list_services):
                break
            
            ser_services =''
            if list_services[ser_i].find('(')>=0: 
                for ichild in range(ser_i,len(list_services)):
                    strn=  list_services[ser_i]                
                    if list_services[ser_i].find(')')>=0:
                        ser_services =ser_services+ strn
                        ser_i +=1
                        break
                    else:
                        ser_services= ser_services+ strn+', '
                        ser_i +=1
            else :
                ser_services = list_services[ser_i]
                ser_i+=1             
            sers.append(ser_services.strip())
        return sers
    def url_(self, pagenum, name,count,country):
         url ='http://www.accaglobal.com/uk/en/member/find-an-accountant/find-firm/results.html?isocountry=VN&location=&country='+country+'&firmname='+str(name)+'&organisationid=ACCA&hid=&pagenumber='+str(pagenum)+'&resultsperpage=25&requestcount='+str(count)
         return url
    def getUrlSelenium(self,url):
        delay= 60
        driver = webdriver.Chrome('Data/chromedriver.exe')
        driver.start_client()
        driver.set_page_load_timeout(delay)
        driver.get(url)                     
        page_state = driver.execute_script('return document.readyState;')
        while page_state != 'complete':            
            page_state = driver.execute_script('return document.readyState;')
       # print page_state
        time.sleep(3)
        currentUrl= driver.current_url
        driver.close()
        return currentUrl
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
                
    def valiDatePhone(self,phone):
            result_ =''
            inList=  [x for x in self.phoneRemove if phone in x]
            if len(inList)>0:
                return None
            if len(phone)==11:
                result_ = phone
            else:
                if len(phone)==12 and phone.startswith('44'):
                    result_ = '+'+phone
                else:
                    result_ =None
            if result_ !=None:
                if result_.startswith('0800'):
                    result = None
            
            return self.validatePhone__(result_, 'gb')
    def validateWebsite(self,website_):
        if website_!=None:
            if website_.find('@') >=0:
                return None
            else:
                return website_
        else:
            return None
    def Services_(self,servicesstr):
                        list_services =   servicesstr.split(',')
                        sers =[]
                        ser_i=0
                        for iser in range(0,len(list_services)):
                            if ser_i >=len(list_services):
                                break
                            ser = Service()
                            ser_services =''
                            if list_services[ser_i].find('(')>=0: 
                                for ichild in range(ser_i,len(list_services)):
                                    strn=  list_services[ser_i]
                                    
                                    if list_services[ser_i].find(')')>=0:
                                        ser_services =ser_services+ strn
                                        ser_i +=1
                                        break
                                    else:
                                        ser_services= ser_services+ strn+', '
                                        ser_i +=1
                            else :
                                ser_services = list_services[ser_i]
                                ser_i+=1
                            ser.service = ser_services  
                            sers.append(ser) 
                        return sers
    def validateStreet(self, street):
        if street==None:
            return None
        street = street.strip()
        if street.startswith(','):
            street= street[1:len(street)]
        if len(street)<=1:
            street= None
        return street
    def duplicatePhone(self, phone_1,phone_2):
        if phone_1.strip() == phone_2.strip():
            return (self.validatePhone__(phone_1, 'gb'),None)
        return (self.validatePhone__(phone_1, 'gb'),self.validatePhone__(phone_2, 'gb'))
    def validatePhone__(self,phone,country):        
        try:
            parsed_phone = phonenumbers.parse(phone, country.upper(), _check_region=True)
        except phonenumbers.phonenumberutil.NumberParseException as error: 
                print str(phone) +' can not parse'
                return None
        if not phonenumbers.is_valid_number(parsed_phone):
            print str(phone) +': not number'
            return None
        else:
            return str(phone)
    def validateZipcode(self,zipcode,country):
        result  = re.search(self.regex_[country], zipcode, flags=0)
        if country =='SP':
            return zipcode
        if result!=None:
            if result.group(0).strip()== zipcode.strip():
                if country == 'FR':
                    zip = int(zipcode)
                    if zip<1000 or zip >97000:
                        Util.log.running_logger.error('Zipcode '+zipcode+' invalid in '+country)
                        return None
                return zipcode
            else:
                Util.log.running_logger.error('Zipcode '+zipcode+' invalid in '+country)
                return None
        else:
            Util.log.running_logger.error('Zipcode '+zipcode+' invalid in '+country)
            return None