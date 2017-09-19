#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Util, Validation
from Objects_HQDB import Service
from Objects_HQDB import Venue
import re
import time
from selenium import webdriver

import urllib3
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
    phoneRemove= ['01717643013','32475466172','09793373930']
    listCountry =['UK','FR','BM','NE','GF','IT','SP','CZ','PL']
   
    
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
        
    
    def doWork(self):
        self.phoneCodeList = Util.getPhoneCodeList()
        self.__getListVenues()
    def __getListVenues(self):
        print "Getting list of Venues"
        file = open('Data/EngCity.txt','r')
        postcode = file.read().splitlines()
        indexUrl =0
        indexItems =0
        for countr in self.listCountry:
          print 'Country: '+ countr #range(0,10) +
          for post in  range(0,10) + [chr(x) for x in range(ord('a'), ord('z')+1)]:
               page =1
               countRequest =1
               #post ='a'
               
               url = self.url_(page,post,countRequest,countr)
               print 'Find with: '+str(post)
               stop_1 = False
               stop_2 =False
               isTable = Util.getRequestsXML(url,'//table[@class="table-responsive firm-search-results expandable-rows"]')
               while len(isTable)>0:
                   page = countRequest*4-3
                   url = self.url_(page,post,countRequest,countr)
                   #url ='http://www.accaglobal.com/ca/en/member/find-an-accountant/find-firm/results.html?isocountry=VN&location=&country=UK&firmname=a&organisationid=ACCA&hid=&pagenumber=3&resultsperpage=5&requestcount=1'
                   print 'find with url: '+url
                   isTable = Util.getRequestsXML(url,'//table[@class="table-responsive firm-search-results expandable-rows"]')
                   hides=  isTable.xpath('//tr[@class="expandable"]')
                   print 'found: '+str(len(hides))
                   indexHides =0
                   for i in range(0,len(hides)):
                       find = './/tbody/tr[@id="rowId-'+str(i+1)+'"]'
                       if i+1 ==14:
                           print ''
                       show = isTable.find(find)
                       sers =[]
                       if show==None:
                           print 'id: '+ str(i+1) +' not found'
                           break
                       hide = hides[i]
                       div = hide.find('./td/div')
                       certifi =''
                       servicesstr='' 
                       if div !=None:
                         h5 = div.xpath('./h5')
                         p = div.xpath('./p')
                         for h5_c in range(0,len(h5)):
                                  if h5[h5_c].text =='Certificates held':
                                      certifi = p[h5_c].text.replace('\n','').replace('\t','')
                                  if h5[h5_c].text =='Services offered':
                                      servicesstr = p[h5_c].text.replace('\n','').replace('\t','').replace(',,',',')
                         td = show.xpath('./td')
                         link = td[0].find('./h5/a').get('href')
                         id_ =  link[link.find('advisorid=')+len('advisorid='):+ len(link)]
                       self.listlink.append(id_)
                       
                       #servicesstr ='Business plans, Business start-up and company formation, Limited company accounts, Management advice to business, Partnership / sole trader accounts, Tax(CGT, Corporate, IHT, Personal and VAT)'
                       ven =self.__VenueParser(show,countr)
                       ven.adid = id_
                       ven.business_website = self.validateWebsite(ven.business_website)
                      
                      
                       print 'Writing index: '+str(indexItems)
                       ven.writeToFile(self.folder,indexItems,ven.name,False)
                       indexItems+=1
                   countRequest+=1
                   print str(len(self.venues_))+' venues'
                   print str(len(self.services))+' services'

    def __VenueParser(self, element,countr):        
        ven = Venue()
        ven.country ='gb'
        td = element.xpath('./td')
        locate = td[0]
        contact = td[1]
        aTag = locate.find('./h5/a')
        link =  aTag.get('href')
        
        findCity  = locate.find('./div')
        '''servicesstr ='Business plans, Business start-up and company formation, Limited company accounts, Management advice to business, Partnership / sole trader accounts, Tax(CGT, Corporate, IHT, Personal and VAT)'
        ser__ = self.__ServicesParser(servicesstr)
        for s in ser__ :
            print s.service'''
        ven.business_email=''
        ven.name = aTag.text.replace('/','-')
        ven.scrape_page =self.__url__+  link
        
        #ven.name='A R Kazi & Co'
        #ven.scrape_page ='http://www.accaglobal.com/uk/en/member/find-an-accountant/find-firm/results/details.html?isocountry=VN&location=&country=UK&firmname=a&organisationid=ACCA&hid=&pagenumber=5&resultsperpage=25&requestcount=2&advisorid=8011731'
        
        xmlVenues = Util.getRequestsXML(ven.scrape_page, '//div[@id="main"]') #//div[@class="content-section no-padding"]
        
        addressInfo = xmlVenues.xpath('//address')
        address_ = ''
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
        address = ' '.join(locate.itertext()).replace('\t','')
        address_ = address.split('\n')
        lensAdd = len(address_)
        zipcode =address_[lensAdd-1]
        info = address_[lensAdd-3].split(',')
        info = info[len(info)-1]
        info = info.split()
        if findCity!=None:
            city = findCity.text
            address2= address.replace('\n', '').replace(ven.name.strip(), '')
            street = address2[0:address2.find(city)]
            
        else:
            city = info[len(info)-1]
            street= ' '.join(info[0:len(info)-1]).replace(ven.name.strip(), '').replace('PO BOX 16988','')
        
        if street.upper().find('PO BOX')>=0:
            street = None
        city = city.upper()
        
        ven.city = city
        ven.zipcode = zipcode
        ven.street = street
        
        if street!=None and len(street)>2:
            ven.formatted_address = ', '.join([street,city,zipcode])
            
        #ven.zipcode = 'HA3 7QT'
        #ven.formatted_address ='Unit A3, Livingstone Court, 55 Peel Road, Wealdstone Harrow HA3 7QT'
        (ven.latitude,ven.longitude) = self.getLatlng(ven.formatted_address, countr)
        if ven.latitude==None and ven.longitude==None:
            (ven.latitude,ven.longitude) =  self.getLatlng(maps, countr)
            if ven.latitude==None and ven.longitude==None:
                (ven.latitude,ven.longitude) = self.getLatlng(ven.zipcode, countr)
                if ven.latitude==None and ven.longitude == None:
                    Util.log.running_logger.info(maps.replace('+',' ')+': '+ 'cannot get GEO code')
            
        li = contact.xpath('./ul/li')
        for l in li :
                href_ = l.find('./a')
                if href_!=None:
                    is_email = href_.get('href').startswith('mailto:')
                    if is_email ==True:
                        ven.business_email = href_.text
                    else:
                   
                        website = href_.text
                        if website.lower().startswith('http://') | website.lower().startswith('https://'):
                            ven.business_website = website
                        else:
                            ven.business_website = 'http://'+ website
                else: 
                    phone = l.text.replace(' ','')
               
                    
                    finds=  phone.find('/')
                    if finds >=0:
                        phone_ = phone.split('/')
                        if len(phone_) >=2:
                            phone_1 = phone_[0]
                            
                            phone_2 = phone_[1]
                            phone_2 = phone_1[0:len(phone_1)-len(phone_2)]+ phone_2
                            if phone.startswith('07') | phone.startswith('7'):
                               ven.mobile_number = self.valiDatePhone(phone_1)
                            else:
                               ven.office_number = self.valiDatePhone(phone_1)
                            if phone.startswith('07') | phone.startswith('7'):
                               ven.mobile_number2 = self.valiDatePhone(phone_2)
                            else:
                               ven.office_number2 = self.valiDatePhone(phone_1)
                    else:

                           if phone.startswith('07') | phone.startswith('7'):
                               ven.mobile_number = self.valiDatePhone(phone)
                           else:
                               ven.office_number = self.valiDatePhone(phone)
      
      
            
      
        return ven
        
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
            
            return result_
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