#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Util,Validation
from lxml import etree as ET
from SiteObjects.Objects_HQDB import Venue, Service
import re
import json
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

class TEMPLATE_HQDB(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = ''
    _language = ''
    _chain_ = ''
    __name__ = ''
    _url_lstVenues = ''    
    _xpath_lstVenues = ''        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
        #Set OutFile Values
        self.outFileVN = self.folder + '/' + self._chain_ + '_' + Validation.RevalidName(self.__name__) + '_Venues.csv'
        self.outFileSV = self.folder + '/' + self._chain_ + '_' + Validation.RevalidName(self.__name__) + '_Services.csv'
        self.phoneCodeList = Util.getPhoneCodeList()
        '''
        Code Here
        '''
        #Write Files
        if len(venues) > 0:
            Util.writelist2File(self.venues,self.outFileVN)
        if len(self.services) > 0:
            Util.writelist2File(self.services,self.outFileSV)

    
    def __getListVenues(self):
        print "Getting list of Venues"
        

    def __VenueParser(self):        
        print 'Scrapping: '
        ven = Venue()
        return ven

    def __ServicesParser(self,url,xmlServices):        
        ''
    