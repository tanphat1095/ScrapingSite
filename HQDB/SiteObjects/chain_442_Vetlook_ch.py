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
    _xpath_lstVenues = '//td[@width="57%"]/table[@width="100%"]/tr/td/div[@align="right"]/parent::td/parent::tr'        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = {}
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
        self.filterVenues()
        
        listDict = list(self.venues)
        for l in listDict:
            ven = self.venues.get(l)
        
        
        #for ven in self.venues:
            self.index+=1
            ven.writeToFile(self.folder, self.index, ven.name, False)
        
        
    def __getListVenues(self):
        xmlDoc = Util.getRequestsXML(self._url_lstVenues, self._xpath_lstVenues)
        listElement = xmlDoc.xpath('./tr')
        for ele in listElement:
            if len(ele.xpath('./td//a/@onclick'))>0:
                self.__VenueParser(ele)
            else:
                self.__VenueParser_2(ele)
        

    def __VenueParser(self,element):
        try:
            self.urlmarks+=1
            print '[COUNT]: '+ str(self.urlmarks)
            featured = 'featured'
            onclick  = element.xpath('./td//a/@onclick')[0]
            detailLink = onclick[onclick.find("MM_openBrWindow('")+ len("MM_openBrWindow('"):onclick.find("','','")]
            detailLink =  self.__url__+'/'+ detailLink
            xmlDoc = Util.getRequestsXML(detailLink, '//table[@cellspacing="3"]')
            xmlDoc = xmlDoc[0]
            ven = Venue()
            ven.hqdb_featured_ad_type =  featured
            ven.country =  self._language
            ven.scrape_page =  detailLink
            detail_ = xmlDoc.xpath('./tr/td/table')
            detail_1= detail_[0]
            detail_2 = detail_[2]
            basicInfo = detail_1.find('./tr/td/table/tr/td[@class="text"]')
            email_website = basicInfo.getparent().xpath('//table//div[@align="right"]/a')
            for aTag in email_website:
                link__ = aTag.get('href')
                if link__.find('mailto')!=-1:
                    ven.business_email =  link__.replace('mailto:','')
                else:
                    if link__.find('http')!=-1:
                        ven.business_website =  link__
            openxml = detail_1.xpath('./tr')
            openxml = openxml[2].find('./td/table') # table openning hour 
            rows =  openxml.xpath('./tr')
            dayofweek = {'Montag':'Lunedì','Dienstag':'Martedì','Mittwoch':'Mercoledì',
                         'Donnerstag':'Giovedì','Freitag':'Venerdì','Samstag':'Sabato','Sonntag':'Domenica'}
            openning_hour_array =[]
            for row in rows:
                tds = row.xpath('./td')
                if len(tds) >0:
                    if tds[0].text!=None:
                        if dayofweek.get(tds[0].text,"NULL")!="NULL":
                            record =''
                            count_ = 0
                            for td in tds :
                                if dayofweek.get(td.text,"NULL")!="NULL":
                                    record+=dayofweek.get(td.text)+": "
                                else:
                                    if td.text.strip()!='-':
                                        record+= td.text.replace('.',':')+", "
                                    else:
                                        count_+=1
                            record = record.strip()
                            if record.endswith(','):
                                record = record[0:-1]
                            if count_ <3:
                                openning_hour_array.append(record)
            ven.opening_hours_raw =  ' | '.join(openning_hour_array)
            basicInfo_ =  ''.join(basicInfo.itertext()).split('\n')
            if basicInfo_[len(basicInfo_)-1].find('Fax')!=-1:
                basicInfo_ = basicInfo_[0:-1]
            phonenumber =  basicInfo_[-1].strip().replace('Tel.','').replace(' ','')
            zip_ci = basicInfo_[-2]
            street = basicInfo_[-3]
            contactName = basicInfo_[-4]
            name = ' '.join(basicInfo_[0:-4])
            (ven.office_number,ven.office_number2,ven.mobile_number,ven.mobile_number2) = self.processPhone([phonenumber])
            (ven.city,ven.zipcode) = self.processZipCity(zip_ci)
            if ven.zipcode!=None:
                if self.validateZip(ven.zipcode)==None:
                    return
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
            #print ET.dump(element)
            self.urlmarks+=1
            print '[COUNT]: ' +str(self.urlmarks)
            ven = Venue()
            ven.scrape_page = self._url_lstVenues+'#'+str(self.urlmarks)
            td = element.find('./td')
            div = td.find('./div')
            if div!=None:
                a =div.find('./a').get('href')
                ven.business_website = a
                td.remove(div)
            basicInfo = ''.join(td.itertext())
            basicInfo_ =  basicInfo.split('\n')
            if basicInfo_[len(basicInfo_)-1].find('Fax')!=-1:
                basicInfo_ = basicInfo_[0:-1]
            phoneNumber = basicInfo_[-1].strip().replace('Tel.','').replace(' ','')
            local =  basicInfo_[-2]
            street = basicInfo_[-3]
            contactName = basicInfo_[-4]
            name = ' '.join(basicInfo_[0:-4])
            
            
            #if name.strip() =='Kleintierpraxis':
            #    name = 'piccoli animal
                
                
                
            (ven.office_number,ven.office_number2,ven.mobile_number,ven.mobile_number2) = self.processPhone([phoneNumber])
            (ven.city,ven.zipcode) =  self.processZipCity(local)
            if ven.zipcode!=None:
                if self.validateZip(ven.zipcode)==None:
                    return
            ven.street = street
            ven.name_of_contact = contactName
            ven.name = name
            ven.country = self._language
            ven.hqdb_featured_ad_type = featured
            self.venues[ven.scrape_page] = ven
        except Exception, ex:
            print ex
            
            
    def filterVenues(self):
        listRemove = []
        
        list_ =  list(self.venues)
        for i in range(0,len(list_)):
            ven = self.venues.get(list_[i])
            for j in range(i+1,len(list_)):
                venn = self.venues.get(list_[j])
                count=0
                if ven.name == venn.name:
                    count+=1
                if ven.name_of_contact == venn.name_of_contact:
                    count+=1
                if ven.street ==venn.street and ven.city == venn.city and ven.zipcode == venn.zipcode:
                    #print ven.scrape_page+'\n-'+venn.scrape_page
                    count+=1
                if count>=3:
                    #listRemove.append(ven)
                    print list_[j] +': removed'
                    #self.venues.pop(list_[j])
                    if self.findList(listRemove, list_[j])==False:
                        listRemove.append(list_[j])
        for list__ in listRemove:
            self.venues.pop(list__)
    def findList(self,list,key):
        for l in list:
            if l ==key:
                return True
        return False
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
        return (string.replace(zipcode,'').strip(),zipcode)
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
            if phone.startswith('+4'):
                phone = phone.replace('(0)','')
            if phone.startswith('00'):
                phone = '+'+ phone[2:len(phone)]
            if phone.startswith('+417'):
                if mobile1==None:
                     mobile1 =  self.validatePhone__(phone)
                else:
                    mobile2 =self.validatePhone__(phone)    
            else:
                if office1==None:
                    office1 =self.validatePhone__(phone)
                    if office1.startswith('+41') or office1.startswith('(0)'):
                        pass
                    else:
                        office1 =  None
                else:
                    office2 = self.validatePhone__(phone)
                    if office2.startswith('+41') or office2.startswith('(0)'):
                        pass
                    else:
                        office2 =  None
        return (office1,office2,mobile1,mobile2)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    