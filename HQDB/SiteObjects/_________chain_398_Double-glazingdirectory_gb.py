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

class Double_glazingdirectory_gb(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = 'http://www.double-glazing-directory.co.uk/'
    _language = 'gb'
    _chain_ = 'chain_398_'
    __name__ = 'Double-glazing directory'
    _url_lstVenues = ''    
    _xpath_lstVenues = '//div[@class="list"]'        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    list_url = []
    
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
        #Set OutFile Values
       
        self.phoneCodeList = Util.getPhoneCodeList()
        '''
        Code Here
        '''
        #Write Files

    
    def __getListVenues(self):
        print "Getting list of Venues"
        xmlArea = Util.getRequestsXML(self.__url__, self._xpath_lstVenues)
        if xmlArea==None | len(xmlArea)<=0:
            ''
        else:
            listArea = xmlArea.xpath('./a')
            for area in listArea:
                linkArea = area.get('href')
                xmlCity = Util.getRequestsXML(linkArea,self._xpath_lstVenues)
                if xmlCity ==None | len(xmlCity)<=0:
                    ''
                else:
                    listCity = xmlCity.xpath('./a')
                    for city in listCity:
                        linkCity = city.get('href')
                        xmlContent = Util.getRequestsXML(linkCity, '//div[@class="content_column"]')
                        if xmlContent==None | len(xmlContent)<=0:
                            ''
                        else:
                            items= xmlContent.xpath('./div[@class="listings"]/div[@class="list"]/div[@class="listing_box"]/a')
                            for item in items:
                                link_item = item.get('href')
                                self.list_url.append(link_item)
                                
         

    def __VenueParser(self):        
        print 'Scrapping: '
        ven = Venue()
        return ven

    def __ServicesParser(self,url,xmlServices):        
        ''
    