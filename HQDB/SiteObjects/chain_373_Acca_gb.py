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
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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
    listCountry =['UK','FR','BM','NE','GF','IT','SP','CZ','PL']
   
    
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
        
    
    def doWork(self):
        #Set OutFile Values
      #  self.outFileVN = self.folder + '/' + self._chain_ + '_' + Validation.RevalidName(self.__name__) + '_Venues.csv'
       # self.outFileSV = self.folder + '/' + self._chain_ + '_' + Validation.RevalidName(self.__name__) + '_Services.csv'
        self.phoneCodeList = Util.getPhoneCodeList()
        self.__getListVenues()
        '''
        Code Here
        '''
        #Write Files
        #for items in range(0, len(self.venues)):
        #    ven = self.venues[items]
        #    print 'Writing items: '+ str(items)
        #    ven.writeToFile(self.folder,items,ven.name,False)
        #    self.venues_.append(ven.toOrderDict())

        #if len(self.venues_) > 0:
        #    Util.writelist2File(self.venues_,self.outFileVN)
        #if len(self.services) > 0:
        #    Util.writelist2File(self.services,self.outFileSV)

    
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
                   #if page%4>0:
                   #  countRequest =page/4+1
                   #else:
                   #  countRequest= page/4
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
                           #       print h5[h5_c].text
                                  if h5[h5_c].text =='Certificates held':
                                      certifi = p[h5_c].text.replace('\n','').replace('\t','')
                                  if h5[h5_c].text =='Services offered':
                                      servicesstr = p[h5_c].text.replace('\n','').replace('\t','').replace(',,',',')
                         td = show.xpath('./td')
                         link = td[0].find('./h5/a').get('href')
                         id_ =  link[link.find('advisorid=')+len('advisorid='):+ len(link)]
                          
                      # existing=[x for x in self.listlink if link in x]
                       #if len(existing)>0:
                        #   print 'venues exist in list'
                       #if len(existing)<=0:
                          # print 'appen'
                       self.listlink.append(id_)
                       #servicesstr ='Business plans, Business start-up and company formation, Limited company accounts, Management advice to business, Partnership / sole trader accounts, Tax(CGT, Corporate, IHT, Personal and VAT)'
                       ven =self.__VenueParser(show)
                       if ven==None: 
                           print 'ven none '
                       if ven!=None:
                        if len(servicesstr) >3:
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
                            # 
                            
                            
                            
                            
                            #sers.append(ser)
                            
                            
                            
                            
                            
                        ven.accreditations = certifi.replace('\n','').replace('\t','')
                        ven.business_website = self.validateWebsite(ven.business_website)
                        (ven.latitude,ven.longitude) = self.getLatlng(ven.formatted_address, countr)
                        ven.services = sers
                        print 'Writing index: '+str(indexItems)
                        ven.writeToFile(self.folder,indexItems,ven.name,False)
                        indexItems+=1
                   countRequest+=1
                   print str(len(self.venues_))+' venues'
                   print str(len(self.services))+' services'

    def __VenueParser(self, element):        
        #print 'Scrapping: '
        ven = Venue()
        ven.country ='gb'
        td = element.xpath('./td')
        locate = td[0]
        contact = td[1]
        aTag = locate.find('./h5/a')
        link =  aTag.get('href')
        
       
        ven.business_email=''
       
        ven.name = aTag.text.replace('/','-')
        ven.scrape_page =self.__url__+  link
        ven.pricelist_link = [self.__url__+link]
        address = ' '.join(locate.itertext()).replace('\t','')
        address_ = address.split('\n')
        lensAdd = len(address_)
        zipcode =address_[lensAdd-1]
        info = address_[lensAdd-3].split(',')
        info = info[len(info)-1]
        info = info.split()
        city = info[len(info)-1]
        street= ' '.join(info[0:len(info)-1]).replace('PO BOX 16988','')
        if ven.scrape_page=='http://www.accaglobal.com/uk/en/member/find-an-accountant/find-firm/results/details.html?isocountry=VN&location=&country=UK&firmname=a&organisationid=ACCA&hid=&pagenumber=5&resultsperpage=25&requestcount=2&advisorid=3446358':
            print ''
        city = city.upper()
        
        ven.city = city
        ven.zipcode = zipcode
        ven.street = street
        
        if street!=None and len(street)>2:
            ven.formatted_address = ', '.join([street,city,zipcode])

        '''
        format_ = ','.join(address_[2:len(address_)-2])
        lens = len(address_)
        zipcode = address_[lens-1]
        country = address_[lens-2]
        re_ = address_[lens-3]
        re_ = re_[0].upper()+ re_[1:len(re_)]
        address_[lens -3] = re_
        street_ = address_[lens-3].split(',')
        
        if len(street_)>=2:
            street = street_[len(street_)-1]
        else:
            street = ' '.join(street_)
        ven.street = street.replace('PO BOX 16988','')
        ven.areas_covered = re_
        #ven.formatted_address =ven.areas_covered+','+ zipcode
        #ven.formatted_address = format_
        if street !=None and len(street)>1:
            ven.formatted_address = street+', ' +re_ +', '+ zipcode
        else:
            ven.formatted_address = re_ +', '+zipcode
            #ven.formatted_address = format_
        ven.zipcode = zipcode
        ven.city = re_
        '''
        #ven.formatted_address = ' '.join(address_[2:lens-1]).replace('United Kingdom',',')
        li = contact.xpath('./ul/li')
        for l in li :
                href_ = l.find('./a')
                if href_!=None:
                    is_email = href_.get('href').startswith('mailto:')
                    if is_email ==True:
                        ven.business_email = href_.text
                    else:
                        #ven.business_website = href_.text
                        website = href_.text
                        if website.lower().startswith('http://') | website.lower().startswith('https://'):
                            ven.business_website = website
                        else:
                            ven.business_website = 'http://'+ website
                else: 
                    phone = l.text.replace(' ','')
                    # phone contains '/' split to 2 number
                    
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
        
    def __ServicesParser(self,url,xmlServices):        
        ''
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
        
        