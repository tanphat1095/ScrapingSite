'''
Created on 1 thg 9, 2017

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
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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
    __city__ = []
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    def doWork(self):
        #Set OutFile Values
        self.phoneCodeList = Util.getPhoneCodeList()
        self.__list_city()
        print 'Total city: '+ str(len(self.__city__))
        self.__getListVenues()
    def __getListVenues(self):
        print "Getting list of Venues"
        lens= len(self.__city__)
        index_ = 0
        for city in range(0,lens):
            _Schools = Util.getRequestsXML(self.__city__[city], '//td[@class="welcome-padding"]/table')
            if len(_Schools)>=2:
                tds = _Schools[1].xpath('./tr/td')
                for td in tds:
                    as_ = td.xpath('./a')
                    for a in  as_ :
                        link =  a.get('href')
                        name = a.text
                        
                        ven =  self.__VenueParser(link,name)
                        if ven!=None:
                            ven.writeToFile(self.folder, index_, ven.name, False)
                            index_+=1
                
           
    def __VenueParser(self,url__, name__):
        print 'Scraping: '+ url__
        city = url__.split('/')[3].replace('city-','').replace('-',' ')
        xmlDoc = Util.getRequestsXML(url__, '/html/body')
        if len(xmlDoc)<=0:
            return None
        else:
            ven =  Venue()
            sers =[]
            ven.name = name__
            ven.city = city
            ven.scrape_page = url__
            
            
            td = xmlDoc.xpath('//td[@class="welcome-padding"]')
            
            div = td[0].xpath('./div')
           
            if len(div)<5:
                return None
            else:
                info  =  div[3]
                info_ =  ''.join(info.itertext())
                address = info_[0:info_.find('Phone')].replace(name__,'').replace(city,'').split(',')
                street = address[0]
                zipcode = address[1]
                
                ven.street = street
                ven.zipcode=  zipcode
                
                phone = info_[info_.find('Phone:')+ len('Phone:'):info_.find('Fax:')].replace(' ','')
                if phone.isdigit():
                    ven.phone = phone
                services_ = info_[info_.find('Services Offered:')+len('Services Offered:'):info_.find('Areas Served:')].strip().replace(';',',')
                if services_ != 'None Listed - [Edit]':
                    services_ = services_.split(',')
                    for s in services_:
                        ser = Service()
                        ser.service = s.strip()
                        sers.append(ser)
                ven.services = sers
                reviewer=     len(xmlDoc.xpath('//td[@class="review-box"]'))
                if reviewer>0:
                    ven.hqdb_nr_reviews = str(reviewer)
                scoreInfo=  div[4]
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
                ven.hqdb_review_score = str(score__).replace('.0', '')
                if score__ >0:
                    print ''
                print ''
            
            return ven
    def __ServicesParser(self,url,xmlServices):        
            ''
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