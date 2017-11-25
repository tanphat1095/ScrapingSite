#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Util,Validation
from lxml import etree as ET
from SiteObjects.Objects_HQDB import Venue, Service
import re
import json
import urllib3
import threading
import time
import requests
import phonenumbers
from sqlalchemy.dialects.firebird.base import CHAR
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
class Yoganearby_gb(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = 'https://yoganearby.com'
    _language = 'gb'
    _chain_ = 'chain_417_'
    __name__ = 'YogaNearby'
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    listLink =[]
    '&page=101'
    index =-1
    runningThread =[]
    category ='Yoga classes'
    total =0
    
    
    
    
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
        self.phoneCodeList = Util.getPhoneCodeList()
        with open('Data/chain_417_city.txt') as f:
            line_ = f.read().splitlines()
        #print self.validateAddress('07469673811 For Address,Braintree,England,CM7')
        #print self.validatePhone__('+4407402131355', 'gb')
        #self.__VenueParser('https://yoganearby.com/events/class/pregnancy-yoga/818/','')
        while len(line_)>0:
            if self.checkAlive()<6:
                items = line_[-1].split('\t')
                thread_ = threading.Thread(target=self.__getListVenues,args=(items[1],items[0]))
                self.runningThread.append(thread_)
                line_.remove(line_[-1])
                Util.log.running_logger.info(items[0]+' : Running')
                thread_.start()
                time.sleep(1)
            else:
                time.sleep(1)      
        
    def checkAlive(self):
        count =0
        for t in self.runningThread:
            if t.isAlive():
                count+=1
            else:
                self.runningThread.remove(t)
        print str(count) +' is running'
        return count
    def addIndex(self):
        index = self.index+1
        self.index = index
        return index
    def __getListVenues(self,link,city):
        xmlDoc = Util.getRequestsXML(link, '//body/div[@class="container"]/div[@class="container"]')
        itemsXpath=['//div[@class="row top-buffer"]/a','//div[@class="row top-buffer border-row"]/a']
        if xmlDoc!=None:
            pages_ = xmlDoc.find('.//div[@class="row centered-text"]/p')
            if pages_!=None:
                totalPages = pages_.text
                try:
                    currentPages =0
                    totalPages = int(totalPages.split('of')[1])
                    '''self.total+= (totalPages*20)
                    print str(self.total)'''
                    while currentPages< totalPages:
                        currentPages+=1
                        url = link+'&page='+str(currentPages)
                        xmlContent = Util.getRequestsXML(url, '//body/div[@class="container"]/div[@class="container"]')
                        for path in itemsXpath:  
                            items = xmlContent.xpath(path)
                            for item in items:          
                                self.__VenueParser(self.__url__+item.get('href'),city)
                    Util.log.running_logger.info(city+' Done')     
                except Exception, ex:
                    print ex

    def __VenueParser(self,item,city):
        existing=[x for x in self.listLink if item in x]
        self.listLink.append(item)
        if len(existing)<=0: 
            try:
                xmlDoc = Util.getRequestsXML(item, '/html')
                ven = Venue()
                ven.scrape_page = item
                #ven.city = city
                ven.name= xmlDoc.xpath('//div[@class="row top-buffer"]/h3')[0].text
                (ven.latitude,ven.longitude) = self.getLatlng(xmlDoc)
                xmlcontent = xmlDoc.find('.//div[@class="tab-content"]')
                services_schedule_info = xmlcontent.xpath('./div/div[@class="row top-buffer"]/h4/parent::div')[0]
                if services_schedule_info !=None:
                    services_schedule_info = ''.join(services_schedule_info.itertext()).split('\n')
                    for it in services_schedule_info:
                        if it.find('Style:')!=-1:
                            it = it[0:it.find('Schedule')]
                            it = it.strip()
                            ser_name = it[it.find('Style:')+len('Style:'):it.find('Ability level')]
                            cost = len(it)
                            cost_ = ['Cost:','Concession cost:']
                            char_cost =''
                            for c in cost_:
                                if it.find(c)!=-1:
                                    cost = it.find(c)
                                    char_cost =c
                                    break
                            #cost = it.find('Cost:')
                            if cost ==-1:
                                cost = len(it)
                                
                                
                                
                                
                                
                            ser_des = it[it.find('Ability level:')+ len('Ability level:'):cost]
                            ser_price = it[cost+len(char_cost):it.find('GBP')+len('GBP')]
                            ser = Service()
                            ser.service = ser_name
                            ser.description = ser_des
                            ser.price = ser_price.replace('-','')
                            ven.services=[ser]
                        if it.find('a.m.')!=-1 or it.find('p.m.')!=-1:
                            ven.opening_hours_raw = it.strip().replace('.Monday',' | Monday').replace('.Tuesday',' | Tuesday').replace('.Wednesday',' | Wednesday').replace('.Thursday',' | Thursday').replace('.Friday',' | Friday').replace('.Saturday',' | Saturday').replace('.Sunday',' | Sunday')
                            ven.opening_hours_raw = self.formatOpenhour(ven.opening_hours_raw)
                address = xmlcontent.find('.//address')
                if address!=None:
                    
                    
                    
                    
                    #print ET.dump(address)
                    address = ''.join(address.itertext()).replace('United Kingdom','').strip()
                    address = self.validateAddress(address)
                    
                    #address ='Ward Park Arras Pavilion,Gransha Road,Bangor,Northern Ireland,BT20 4TN'
                    ven.country ='gb'
                    if address.upper().find('Ireland'.upper())!=-1:
                        if address.upper().find('Northern Ireland'.upper())!=-1:
                            ven.country ='ie'
                    if address.endswith(','):
                        address = address[0:-1]
                    ven.formatted_address = address
                posted = xmlcontent.find('./div/div[@class="row"]/p')
                imgs= xmlcontent.xpath('.//a/img')
                img_ =[]
                for img in imgs:
                    img_.append(img.get('src'))
                
                ven.img_link = img_
                if posted !=None:
                    ven.hqdb_ad_posted = posted.text.replace('Last updated','')
                    split_posted = ven.hqdb_ad_posted.split(',')
                    if len(split_posted)>=3:
                        ven.hqdb_ad_posted =', '.join(split_posted[0:len(split_posted)-1])
                ven.category = self.category
                #ven.country ='gb'
                des_info = xmlcontent.xpath('//div[@class="row top-buffer"]/h3')[1]
                #print des_info.text
                des_info = des_info.getparent()
                des__ = des_info.xpath('./p')
                
                ven.pricelist_link=  [ven.scrape_page]
                ven.hqdb_featured_ad_type ='none'
                
                
                ven.description =''
                for des in des__:
                    ven.description+= ''.join(des.itertext())+' '
                    des_info.remove(des)
                info = '____'.join(des_info.itertext())    
                a = des_info.find('./a')
                if a!=None:
                    a = a.get('href')
                    if a.find('facebook.com')==-1:
                        ven.business_website =a
                    else:
                        if a.startswith('http:'):
                            a = a.replace('http:','https:')
                        ven.facebook = a
                        
                info =  info.split('__')
                
                for inf in range(0,len(info)) :
                    if info[inf] =='Qualifications:':
                        ven.accreditations = info[inf+2]
                    if info[inf] =='Phone:':
                        
                        phone = info[inf+2].strip()
                        
                        pattren ='(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
                        '''isEmail  = re.search(pattren, phone, flags=0)
                        if isEmail!=None:
                            ven.business_email = isEmail.group(0)
                            continue'''
                        find_charSplit = self.findSplitPhone(phone)
                        if find_charSplit==None:
                            
                            issMail = re.search(pattren, phone, flags=0)
                            if issMail!=None:
                                ven.business_email = issMail.group(0)
                                continue
                            phone = phone.replace('Mobile:','').replace('ext.225','').replace('O7', '07').replace(' ', '')
                            if phone.startswith('07') or phone.startswith('447') or phone.startswith('+447') or phone.startswith('00447') or phone.startswith('+44(0)7') or phone.startswith('44(0)7') or phone.startswith('004407'):
                                ven.mobile_number = self.validatePhone__(phone, ven.country)
                            else:
                                ven.office_number = self.validatePhone__(phone, ven.country)
                        else:
                            phone = phone.split(find_charSplit)
                            for p in phone:
                                issMail = re.search(pattren, p, flags=0)
                                if issMail!=None:
                                    ven.business_email = issMail.group(0)
                                    continue
                                p = p.replace('Mobile','').replace('ext225','').replace('O7','07').replace(' ','')
                                if p.startswith('07') or p.startswith('447') or p.startswith('+447') or p.startswith('00447') or p.startswith('+44(0)7') or p.startswith('44(0)7') or p.startswith('004407') :
                                    if ven.mobile_number!=None:
                                        ven.mobile_number2 = self.validatePhone__(p, ven.country)
                                    else:
                                        ven.mobile_number = self.validatePhone__(p, ven.country)
                                else:
                                    if ven.office_number!=None:
                                        ven.office_number2 = self.validatePhone__(p, ven.country)
                                    else:
                                        ven.office_number = self.validatePhone__(p, ven.country)
                isPhoneOverSea =  self.checkPhoneOverSea([ven.office_number,ven.office_number2,ven.mobile_number,ven.mobile_number2])
                if isPhoneOverSea ==False:
                    index = self.addIndex()
                    print str(index)+' Scapping: '+ city+'---'+ven.scrape_page
                    #ven.is_get_by_address =True
                    ven.writeToFile(self.folder, index, ven.name, False)
            except Exception, ex:
                print ex
                return
    def __ServicesParser(self,url,xmlServices):        
        ''
    def checkPhoneOverSea(self,listPhone):
        start =['+35','+33']
        for phone in listPhone:
            for st in start:
                if phone!=None:
                    if phone.startswith(st):
                        return True
        return False
    
    
    def validateAddress(self,string):
        regex_= ['(BP[\s][\d]{1,5})','(BP[\d]{1,5})','(BP[\s][\d]{1,5})','(B.P.[\s][\d]{1,5})','(CS[\s][\d]{1,5})','(CS[\d]{1,5})','([\d]{1,4}[\s]{1,5}[\d]{1,4})','([\d]{4,20})']
        for reg in regex_:
            result = re.search(reg, string, flags=0)
            if result!=None:
                string = string.replace(result.group(0),'')
        if string.strip().startswith('For Address,'):
            string = string.strip()[len('For Address,'):len(string)]
        return string
    
    def getLatlng(self,xml):
        try:
            script =  xml.xpath('//script')
            for i in script :
                content = i.text
                if content!=None:
                    if content.find('google.maps.LatLng(')!=-1:
                        stringlatlng = content[content.find('google.maps.LatLng(')+len('google.maps.LatLng('):len(content)]
                        stringlatlng = stringlatlng[0:stringlatlng.find('),zoom')]
                        stringlatlng = stringlatlng.split(',')
                        lat = float(stringlatlng[0])
                        lng = float(stringlatlng[1])
                        return (stringlatlng[0],stringlatlng[1])
            return (None,None)
        except Exception,ex:
            return (None,None)
    def validatePhone__(self,phone,country):       
        try:
            if phone.startswith('00'):
                phone = '+'+ phone[2:len(phone)]
            if phone.startswith('44'):
                phone= '+'+phone
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
            if phone.startswith('+44(0)') or phone.startswith('44(0)'):
                #phone ='+44'+ phone[4:len(phone)]
                phone = phone.replace('(0)','')
            if phone.startswith('+440'):
                phone = '+44'+ phone[len('+440'):len(phone)]
            if phone.startswith('+61'):
                return None
            return phone.replace('+35340440000','')
    def findSplitPhone(self,phone):
        splitPhone=[' I ',',','|',' or ','/',' and ',' - ']
        for char in splitPhone:
            if phone.find(char)!=-1:
                return char
        return None 
    def formatOpenhour(self,open):
        chars =['a.m.','a.m','p.m.','p.m',
                'noonMonday','noonTuesday',
                'noonWednesday','noonThursday',
                'noonFriday','noonSaturday',
                'noonSunday']
        hashChar = {"a.m.":"AM","a.m":"AM","p.m.":"PM","p.m":"PM",
                    "noonMonday":"noon | Monday",
                    "noonTuesday":"noon | Tuesday",
                    "noonWednesday":"noon | Wednesday",
                    "noonThursday":"noon | Thursday",
                    "noonFriday":"noon | Friday",
                    "noonSaturday":"noon | Saturday",
                    "noonSunday":"noon | Sunday"}
        for char in chars:
            open = open.replace(char,hashChar[char])
        open = open.replace('noon','12 PM')
        return open