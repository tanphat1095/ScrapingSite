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
from _elementtree import dump
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import phonenumbers



class Vetlook_ch(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = 'http://www.vet-look.ch'
    _language = 'ch'
    _chain_ = 'chain_442_'
    __name__ = 'VETLOOK'
    _url_lstVenues = 'http://www.vet-look.ch/kanton.php?kanton=all'    
    _xpath_lstVenues = ' //td[@width="57%"]/table[@width="100%"]/tr/td/div[@align="right"]/parent::td/parent::tr'        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    index =-1
    urlmarks = 0
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
        self.phoneCodeList = Util.getPhoneCodeList()
        self.__getListVenues()
    def __getListVenues(self):
        xmlDoc = Util.getRequestsXML(self._url_lstVenues, self._xpath_lstVenues)
        listElement = xmlDoc.xpath('./tr')
        #print len(listElement)
        for ele in listElement:
            #print ele.xpath('./td//a/@onclick1')
            if len(ele.xpath('./td//a/@onclick'))>0:
                self.__VenueParser(ele)
            else:
                self.__VenueParser_2(ele)
        

    def __VenueParser(self,element):
        try:
            self.urlmarks+=1
            featured = 'featured'
            onclick  = element.xpath('./td//a/@onclick')[0]
            detailLink = onclick[onclick.find("MM_openBrWindow('")+ len("MM_openBrWindow('"):onclick.find("','','")]
            detailLink =  self.__url__+'/'+ detailLink
            xmlDoc = Util.getRequestsXML(detailLink, '//table[@cellspacing="3"]')
            xmlDoc = xmlDoc[0]
            ven = Venue()
            ven.country =  self._language
            ven.scrape_page =  detailLink
            detail_ = xmlDoc.xpath('./tr/td/table')
            detail_1= detail_[0]
            detail_2 = detail_[2]
            basicInfo = detail_1.find('./tr/td/table/tr/td[@class="text"]')
            email_website = basicInfo.getparent().xpath('//table//div[@align="right"]/a')
            #print ET.dump(basicInfo.getparent()) 
            for aTag in email_website:
                link__ = aTag.get('href')
                if link__.find('mailto')!=-1:
                    ven.business_email =  link__.replace('mailto:','')
                else:
                    if link__.find('http')!=-1:
                        ven.business_website =  link__
            
            
            openxml = detail_1.xpath('./tr')
            openxml = openxml[2].find('./td/table') # table openning hour 
            #openning hour raw
            rows =  openxml.xpath('./tr')
            dayofweek = {'Montag':'Lunedì','Dienstag':'Martedì','Mittwoch':'Mercoledì',
                         'Donnerstag':'Giovedì','Freitag':'Venerdì','Samstag':'Sabato','Sonntag':'Domenica'}
            for row in rows:
                tds = row.xpath('./td')
                if len(tds) >0:
                    if tds[0].text!=None:
                        if dayofweek.get(tds[0].text,"NULL")!="NULL":
                            print dayofweek.get(tds[0].text,"NULL")
            
            
            
            
            
            
            
            basicInfo_ =  ''.join(basicInfo.itertext()).split('\n')
            if basicInfo_[len(basicInfo_)-1].find('Fax')!=-1:
                basicInfo_ = basicInfo_[0:-1]
            phonenumber =  basicInfo_[-1].strip().replace('Tel.','').replace(' ','').replace('(0)','')
            zip_ci = basicInfo_[-2]
            street = basicInfo_[-3]
            contactName = basicInfo_[-4]
            name = ' '.join(basicInfo_[0:-4])
            (ven.office_number,ven.office_number2,ven.mobile_number,ven.mobile_number2) = self.processPhone([phonenumber])
            # 1000<= post_code <= 9658
            (ven.city,ven.zipcode) = self.processZipCity(zip_ci)
            ven.street =  street
            ven.name_of_contact = contactName
            ven.name = name
            services = detail_2.xpath('./tr[@valign="top"]/td')
            if len(services)>0:
                service_ = []
                services = services[0].text
                ven.services =  self.__ServicesParser(services)
                    
                    
                    
                    
                    
            self.index+=1
            ven.writeToFile(self.folder, self.index, ven.name, False)
        except Exception,ex:
            print ex
    def __VenueParser_2(self,element):
        try:
            featured = 'none'
            self.urlmarks+=1
            print str(self.urlmarks)
            pass
        except Exception, ex:
            print ex

    def __ServicesParser(self,string):
        list_services =string.split(',')
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
            
    def processZipCity(self,string):
        zipcode = '';
        string_ =  string.split()
        for str in string_:
            if str.isdigit():
                    zipcode =  str
        return (string.replace(zipcode,'').strip(),self.validateZip(zipcode))
    def validateZip(self,zipcode):
        if int(zipcode)<1000 or int(zipcode) > 9658:
            return None
        else:
            return zipcode
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
    def processPhone(self,phoneNumber):
        office1= None
        office2 =None
        mobile1 = None
        mobile2 =None
        for phone in phoneNumber:
            if phone.startswith('+417'):
                if mobile1==None:
                     mobile1 =  self.validatePhone__(phone)
                else:
                    mobile2 =self.validatePhone__(phone)    
            else:
                if office1==None:
                    office1 =self.validatePhone__(phone)
                else:
                    office2 = self.validatePhone__(phone)
        return (office1,office2,mobile1,mobile2)