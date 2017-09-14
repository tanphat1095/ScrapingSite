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
        self.phoneCodeList = Util.getPhoneCodeList()

    def __getListVenues(self):
        ''
        

    def __VenueParser(self):        
        ''

    def __ServicesParser(self,url,xmlServices):        
        ''
    