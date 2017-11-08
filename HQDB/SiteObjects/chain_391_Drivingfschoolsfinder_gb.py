#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Util,Validation
from lxml import etree as ET
from SiteObjects.Objects_HQDB import Venue, Service
import re
import json
import time
import urllib3
import phonenumbers
from operator import div
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import threading
class Drivingfschoolsfinder_gb(BaseSite):
    phoneCodeList = None
    __url__ = 'http://www.drivingschoolsfinder.co.uk/'
    _language = 'gb'
    _chain_ = 'chain_391_'
    __name__ = 'Driving Schools Finder'
    _url_lstVenues = 'http://www.drivingschoolsfinder.co.uk/allcities.php'    
    _xpath_lstVenues = ''        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    venuesList =[]
    removeChar= ['10% Discount','Hourly lessons','90 & 120 minute','1 and 2 Hour','hour & haft and two hour lessons .','10% discount when paying for 10 lessons','1 and 2 hour','1 or 2 hour lessons','One Hour','2hrs','5 hours','1hr30 min','2hr','3 HOURS','6 hours','From','per hour','ONE HOUR','per one hour','First hour','first 5 hours','First 5 hours','(subject to terms and conditions 1x2x2 hours)','one hour','60 minute','one or two hour','1hr','1.5hr','1 hour','2 hour','/']
    regexString=['(?<!%)(?:[€$£]\s*(\d*[\,\.]?\d{1,2})|(\d*[\,\.]?\d{1,2})\s*(?:[€$£]|zł|kč|pln|złt))\s*(?<!%)(?!%)']
    regexZipcode='((?:[gG][iI][rR] {0,}0[aA]{2})|(?:(?:(?:[a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y]?[0-9][0-9]?)|(?:(?:[a-pr-uwyzA-PR-UWYZ][0-9][a-hjkstuwA-HJKSTUW])|(?:[a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y][0-9][abehmnprv-yABEHMNPRV-Y]))) {0,}[0-9][abd-hjlnp-uw-zABD-HJLNP-UW-Z]{2}))'
    __city__ = []
    
    index_ =-1
    runningThread =[]
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    def doWork(self):
        #Set OutFile Values

        #string= 'first £49.50 biginners only discounts for block bookings discounts for students and nursers pass plus refresher courses'
        #print self.validateNameServices(string)
        #print self.validateZipcode('S74OAP')
        
        
        self.phoneCodeList = Util.getPhoneCodeList()
        self.__list_city()
        print 'Total city: '+ str(len(self.__city__))
        #self.__getListVenues()
        while len(self.__city__)>0:
            if self.checkAlive()<5:
                thread_ = threading.Thread(target=self.__getListVenues,args=(self.__city__[-1],))
                self.__city__.remove(self.__city__[-1])
                self.runningThread.append(thread_)
                thread_.start()
                time.sleep(0.5)
            else:
                time.sleep(1)
                
        
    def addIndex(self):
        index = self.index_+1
        self.index_ =  index
        return index  
    def checkAlive(self):
        count =0
        for t in self.runningThread:
            if t.isAlive():
                count+=1
            else:
                self.runningThread.remove(t)
        print str(count)+' thread running'
        return count
    def __getListVenues(self,city):
        #print "Getting list of Venues"
        #lens= len(self.__city__)
        #index_ = 0
        #for city in range(0,lens):
            
            _Schools = Util.getRequestsXML(city, '//td[@class="welcome-padding"]/table')
            if _Schools == None:
                Util.log.running_logger.warning(city+' Done')
                return
            if len(_Schools)>=2:
                tds = _Schools[1].xpath('./tr/td')
                for td in tds:
                    as_ = td.xpath('./a')
                    for a in  as_ :
                        link =  a.get('href')
                        name = a.text
                        
                        ven =  self.__VenueParser(link,name)
                        if ven!=None:
                            index_ = self.addIndex()
                            print 'Writing to Index: '+ str(index_)
                            ven.writeToFile(self.folder, index_, ven.name, False)
                            #index_= self.addIndex()
                            #time.sleep(2)
                Util.log.running_logger.warning(city+' Done')
    def __VenueParser(self,url__, name__):
        print 'Scraping: '+ url__
        existing=[x for x in self.venuesList if url__ in x]
        if len(existing)>0:
            return None
        #url__ ='http://www.drivingschoolsfinder.co.uk/city-Accrington/1846198-driving-Terrys-School-of-Motoring.html'
        #name__ ='Terrys School of Motoring'
        city = url__.split('/')[3].replace('city-','').replace('-',' ')
        xmlDoc = Util.getRequestsXML(url__, '/html/body')
        if xmlDoc ==None :
            return None
        else:
            ven =  Venue()
            sers =[]
            ven.name = name__
            ven.city = city
            ven.scrape_page = url__
            td = xmlDoc.xpath('//td[@class="welcome-padding"]')
            iter__ = ''.join(td[0].itertext())
            iter__ = iter__[iter__.find('Driving School:')+len('Driving School:'):iter__.find('[Edit Text]')].replace('\n','|').replace('\t','')
            iter__ = iter__.replace('|||', ' | ')
            rep = '|'+ name__
            iter__ = iter__[0:iter__.find(rep)]
            rep = '  |  |'
            iter__ =iter__[0:iter__.find(rep)]
            ven.description = iter__
            div = td[0].xpath('./div')
            
            if len(div)<5:
                return None
            else:
                # div info = position div gray-line[0]+1
                div_info = 0
                for div_ in div:
                    if div_.find('./script')!=None:
                        div_info =3
                info  =  div[div_info]
                info_ =  ''.join(info.itertext())
                address = info_[0:info_.find('Phone')].replace(name__,'').replace(city,','+city).replace(',,',',').replace(', ,',',').split(',')
                #street = ', '.join(address[0:len(address)-2]).replace(','+city,'')
                street = ', '.join(address[0:len(address)])
                street = street[0:street.find(city)-1]
                if street.endswith(','):
                    street = street[0:len(street)-1]
                zipcode = address[len(address)-1]
                street__ = street.upper()
                if street__.find('PO BOX')==-1:
                    ven.street = street.replace('n/a', '').replace('***', '').replace('6 weldon place croy', '').replace('cumbernauld41 napier square bellshill ml4 1tb', '').replace('P.O. Box 1048', '')
                if ven.street =='-':
                    ven.street = None
                ven.zipcode=  self.validateZipcode(zipcode)
                
                phone = info_[info_.find('Phone:')+ len('Phone:'):info_.find('Fax:')].replace(' ','')
                if phone.isdigit():
                    if phone.startswith('07')| phone.startswith('7'):
                        ven.mobile_number = self.validatePhone(phone)
                        ven.mobile_number = self.validatePhone__(ven.mobile_number, 'gb')
                    else:
                        ven.office_number = self.validatePhone(phone)
                        ven.office_number = self.validatePhone__(ven.office_number, 'gb')
                services_ = info_[info_.find('Services Offered:')+len('Services Offered:'):info_.find('Areas Served:')].strip().replace(';',',')
                if services_ != 'None Listed - [Edit]':
                    services_ = services_.replace('/', ',').replace(',,', ',').split(',')
                    for s in services_:
                        name = self.validateServices(s)
                        if len(name)>=5:
                            name__ =name.split()
                            for n in name__:
                                name = self.validateNameServices(name)
                        if len(name.strip())>=5:
                            services = Service()
                            services.service = name
                            sers.append(services)
                        
                        
                        
                    
                    #ven.description = ven.description +' | ' +services_
                stringfind = 'No Website'
                if info_.find('No Website')==-1:
                    stringfind ='Website'
                area_coverd = info_[info_.find('Areas Served:')+len('Areas Served:'):info_.find(stringfind)].strip().replace(';',',')
                #area_coverd = area_coverd[0:area_coverd.find(stringfind)]
                if area_coverd!= 'None Listed - [Edit]':
                    ven.areas_covered = area_coverd
                    
                ven.services = sers
                reviewer=     len(xmlDoc.xpath('//td[@class="review-box"]'))
                if reviewer>0:
                    ven.hqdb_nr_reviews = str(reviewer)
                scoreInfo=  div[div_info+1]
                #http://www.drivingschoolsfinder.co.uk/halfstar.gif +0.5
                #http://www.drivingschoolsfinder.co.uk/fullstar.gif +1
                #http://www.drivingschoolsfinder.co.uk/emptystar.gif +0
                tr = scoreInfo.xpath('./table/tr')
                tr= tr[1]
                img_core = tr.xpath('./td')[1]
                img_core = img_core.xpath('./table/tr/td/img')
                score__=0.0
                for score in img_core:
                    score_ = score.get('src')
                    if score_ =='http://www.drivingschoolsfinder.co.uk/halfstar.gif':
                        score__+= 0.5
                    if score_ =='http://www.drivingschoolsfinder.co.uk/fullstar.gif':
                        score__ +=1
                    if score_== 'http://www.drivingschoolsfinder.co.uk/emptystar.gif':
                        score__ +=0
                if score__ >0:       
                        ven.hqdb_review_score = str(score__).replace('.0', '')
                ven.country = 'gb'
                emails_ = re.findall(r'[\w\.-]+@[\w\.-]+', info_)
                for email_ in emails_:
                    ven.business_email = email_
            #    website_ = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', info_)
            #    for web_  in website_:
                #       ven.business_website = web_ 
                if ven.business_email!=None:
                    if ven.business_email.startswith('http'):
                        ven.business_email= None
                    ven.business_email = None
                if info_.find('No Website') ==-1:
                    arrays__ =    info_.split(' ')
                    for i in range(0, len(arrays__)):
                        if arrays__[i].find('Website')>=0:
                            web_ = arrays__[i+1].replace('\t',' ').replace('\n',' ').split()[0].replace('No','')
                            ven.business_website = self.formatWeb_(web_)
                            print ven.business_website
                            break
                address_ =''           
                if ven.street ==None:
                    address_ =ven.city+', '+ ven.zipcode
                    #ven.formatted_address = ven.city+', '+ven.zipcode
                else:
                    if ven.zipcode!=None:
                        address_ = ven.street+', '+ven.city+', '+ ven.zipcode
                    else: 
                        address_ = ven.street+', '+ven.city
                ven.pricelist_link = [ven.scrape_page]
                
                
                
                ''' get lat -lng '''
                if address_!= '':
                    try:
                        (ven.latitude,ven.longitude) = self.getLatlng(address_, 'UK')
                    except Exception,ex:
                        Util.log.running_logger.error(ven.scrape_page+' : '+ex)
                        return None
            ven.is_get_by_address = True
            return ven
    def __ServicesParser(self,url,xmlServices):        
            ''
    def formatWeb_(self,link_):
        if link_.startswith('http') | link_.startswith('https'):
            ''
        else:
            link_ = 'http://'+link_
        link__ = link_.split('//')[1]
        if link__.startswith('www'):
            ''
        else:
            link__ = 'www.'+ link__
            link_ = 'http://'+ link__
        return link_
    def __list_city(self):
        xmlDoc = Util.getRequestsXML(self._url_lstVenues, '//td[@class="welcome-padding"]')
        #print ET.dump(xmlDoc)
        listCity = xmlDoc.xpath('//table/tr/td/a')
        if len(listCity)>0:
            for i in listCity:
                link = i.get('href')
                existing=[x for x in self.__city__ if link in x]
                if len(existing)<=0:
                    self.__city__.append(link)
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
    
    def validateServices(self,name__):
            for char  in self.removeChar:
                name__ =   name__.replace(char,'')
            #arr =  name__.split()
            '''for ar in range(0,len(arr)):
                if arr[ar].find('£')>=0:
                    arr[ar] ='''
            return name__
    def validateNameServices(self,name):
        for regex in self.regexString:
            result= re.search(regex, name, flags=0)
            if result!=None:
                name = name.replace(result.group(0),'')
        return name
    
    
    
    def validatePhone(self,phone):
        if phone.isdigit():
            if phone.startswith('0800') | phone.startswith('800') :
                return None
            if phone.startswith('44') and len(phone) == 12:
                return '+'+ phone
            if phone.startswith('+44') and len(phone)==13:
                return phone
            if phone.startswith('0') and len(phone) ==11:
                return phone
            else:
                if phone.startswith('44'):
                    return None
                if phone.startswith('+44'):
                    return None
                if phone.startswith('0'):
                    return None
                else:
                    return phone
        else:
            phone = None
        return phone
    def validatePhone__(self,phone,country='gb'):        
        try:
            parsed_phone = phonenumbers.parse(phone, country.upper(), _check_region=True)
        except phonenumbers.phonenumberutil.NumberParseException as error: 
                print str(phone) +' can not parse'
                if phone!=None:
                    Util.log.running_logger.warning(str(phone)+' : cannot parse')
                return None
        if not phonenumbers.is_valid_number(parsed_phone):
            print str(phone) +': not number'
            if phone!=None:
                Util.log.running_logger.warning(str(phone)+' : not number')
            return None
        else:
            return phone
    def validateZipcode(self,zipcode):
        result = re.search(self.regexZipcode, zipcode, 0)
        if result!=None:
            if result.group(0).strip()!=zipcode.strip():
                return None
            else:
                return zipcode
        else:
            return None