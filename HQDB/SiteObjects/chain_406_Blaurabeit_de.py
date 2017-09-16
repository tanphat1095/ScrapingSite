#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Util,Validation
from lxml import etree as ET
from SiteObjects.Objects_HQDB import Venue, Service
import re
import json
import urllib3
import requests
import time
from lxml import html
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Blaurabeit_de(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = 'https://www.blauarbeit.de'
    _language = 'de'
    _chain_ = 'chain_406_'
    __name__ = 'Blaurabeit'
    _url_lstVenues = ''    
    _xpath_lstVenues = ''        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFileVN = ''
    outFileSV = ''
    removeName =[':)',':','=))','=']
    removeDes= ['Mobil','Email','Tel:']
    bpfArray =['//div[@class="row row_b row_container clearfix"]',
               '//div[@class="row row_f row_container clearfix"]',
               '//div[@class="row row_p row_container clearfix"]',
               '//div[@class="row row_a row_container clearfix"]']
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
        self.phoneCodeList = Util.getPhoneCodeList()
        self.__getListVenues()
    def __getListVenues(self):
            with open('Data/Category_chain_406.txt') as f:
                line_ = f.read().splitlines()
            index =0
            for line in line_:
                cateArr = line.split('\t')
                cate = cateArr[0]
                cateLink = cateArr[1]
                subcateXml = Util.getRequestsXML(cateLink,'//div[@class="box_w box_r"]/ul/li/ul')
                if subcateXml!=None:
                    subcates =  subcateXml.xpath('./ul/li/a')
                    for subcate in subcates:
                        catename =  ''.join(subcate.itertext()).strip()
                        urlcate = subcate.get('href')
                        if urlcate.startswith('/'):
                            urlcate =  self.__url__+ urlcate
                        pages = 0
                        while True :
                            param= '?radius=21&view=list&interval='+str(pages)
                            xmlDoc = Util.getRequestsXML(urlcate+param,'//div[@class="br_results br_results_dir"]')
                            if len(xmlDoc.xpath('./div[@class="br_results br_results_dir"]'))<=0:
                                break
                            for xpath_ in self.bpfArray:
                                elementIems = xmlDoc.xpath(xpath_)
                                for ele in elementIems:
                                    type_hqdb = ele.find('.//div[@class="col-inner"]/div')
                                    if xpath_ =='//div[@class="row row_b row_container clearfix"]':
                                        hqdb_type =None
                                    else:
                                        hqdb_type =  ''.join(type_hqdb.itertext()).strip()
                                    linkItems = ele.find('.//div[@class="name"]//a').get('href')
                                    if linkItems.startswith('/'):
                                        linkItems= self.__url__+linkItems
                                        print 'Scrapping: '+ linkItems
                                        ven =    self.__VenueParser(hqdb_type, linkItems,catename,cate)
                                        if ven!=None:
                                            print 'Writing index: '+str(index)
                                            ven.writeToFile(self.folder, index, self.validateFilename(ven.name), False)
                                            index+=1
                                            
                                
                            pages+=1
    def __VenueParser(self,hqdb_type, linkItems,subcate,cate):    
            #linkItems ='https://www.blauarbeit.de/p/babysitter-berlin/belumah/207707.htm'    
            xmlPages = self.getRequest(linkItems)
            #print ET.dump(xmlPages)
            #time.sleep(1)
            xmlVen = xmlPages.xpath('//div[@class="page_move"]')
            if len(xmlVen)==0:
                return None
            name = xmlVen[0].find('.//h2')
            if name ==None:
                return None
            name = name.text.strip()
            noneValues ={'ZERO','NULL'}
            if name.upper() in noneValues:
                return None
            ven = Venue()
            nameFromUrl = self.getNamefromUrl(linkItems)
            ven.hqdb_featured_ad_type = hqdb_type
            ven.name =name
            ven.scrape_page = linkItems
            ven.subcategory = subcate
            ven.category= cate
            address_= ''
            img_link= []
            divInfo = xmlVen[0].find('.//div[@class="content_wrapper content_wrapper_main clearfix"]/div')
            if divInfo!=None:
                mainInfo =  divInfo.xpath('./section')    
                if len(mainInfo)>=2:
                    leftInfo =  mainInfo[0]
                    rightInfo = mainInfo[1]
                    tableInfo = leftInfo.find('./div/div[@class="profile_top_left"]/table')
                    trinfo = tableInfo.xpath('./tr')
                    for tr_ in trinfo:
                        td =tr_.xpath('./td')
                        if len(td)<2:
                            continue
                        key_ = ''.join(td[0].itertext()).strip()
                        values_ = ''.join(td[1].itertext()).strip().replace('keine Angabe','')
                        if key_ =='Ansprechpartner:':
                            if values_!=None and len(values_)>2:
                                #values_ =''
                                ven.name_of_contact = nameFromUrl +' '+ values_
                            
                        if key_ =='Addresse:':
                            address_ =  values_
                            (ven.street,ven.city,ven.zipcode) = self.processAddress(address_)
                            
                        if key_ =='Homepage:':
                            a_ = td[1].find('./a')
                            if a_ !=None:
                                ven.business_website = a_.get('href')
                        if key_ =='Tel:':
                            ven.office_number = values_.replace('/', '').replace(' ', '')
                    img_ = leftInfo.find('./div/div[@class="profile_top_right"]/img')
                    if img_!=None:
                        img_ =img_.get('src')
                        img_link.append(img_)
                    rating = leftInfo.xpath('.//section[@id="ratings"]/div')
                    if len(rating)>=2:
                        rating1 = ''.join(rating[0].itertext()).strip().split()[1]
                        rating2 = ''.join(rating[1].itertext()).strip().split()[0]
                        rating2 =  rating2.split('/')[0].replace(',','.')
                        try:
                            float(rating2)
                        except Exception,ex:
                            rating2=None
                        ven.hqdb_nr_reviews = rating1
                        ven.hqdb_review_score = rating2
                    script_ = xmlPages.xpath('./head/script')
                    
                    city_ =''
                    zipcode_=''
                    street_= ''
                    if ven.city!=None and len(ven.city)>=3:
                        city_ =ven.city
                    if ven.zipcode !=None and len(ven.zipcode)>=5:
                        zipcode_ = ven.zipcode
                    if ven.street !=None and len(ven.street)>=3:
                        street_ = ven.street
                    
                        
                    add__ = (street_+', '+city_+', '+zipcode_).replace(', ,', '')
                    
                    
                    if ven.zipcode ==None and ven.street == None:
                        add__ =  ven.city
                        ven.formatted_address = ven.city
                        ven.city = None
                    
                    (ven.latitude,ven.longitude)  = self.getLatlng(add__,'DE') #script_
                    redirecPhotos= rightInfo.find('./nav/div/ul/li[@class="tabOff tab_foto"]/a')
                    if redirecPhotos!=None:
                        linkPhotos =  redirecPhotos.get('href')
                        if linkPhotos.startswith('/'):
                            linkPhotos = self.__url__+ linkPhotos
                        xpathPhotos =  Util.getRequestsXML(linkPhotos, '//div[@class="portfolio thumbs"]/a')
                        listImg = xpathPhotos.xpath('./a')
                        for __img in listImg:
                            img_link.append(__img.get('data-thumb'))
                    
                    
                    desElement= rightInfo.find('./div/div[@id="cont_about"]')
                    pTag = desElement.xpath('//div[@class="overview"]/p')
                    des = ''
                    for desE in pTag :
                        des+=''.join(desE.itertext())
                    ven.description = self.validateDes(des)
                    certi = rightInfo.find('.//div/div[@id="cont_certs"]')
                    tablecerti =  certi.find('./table')
                    if tablecerti!=None:
                        certi_ = ''.join(tablecerti.itertext()).replace('Geprüfte Zertifikate:','')
                        ven.accreditations = certi_
                    ven.img_link = img_link
                    ven.country ='de'
                    return ven
            else:
                return None
                    
    def getNamefromUrl(self,url):
        arr_ =url.split('/')
        #for i in range(0, len(arr_)):
            #if arr_[i]=='p':
                #return arr_[i+1].replace('-',' ').replace('_',' ').strip()
        return arr_[4].replace('-',' ').replace('_',' ').strip()
    
    def __ServicesParser(self,url,xmlServices):        
        ''
    def getRequest(self,url):
        try:
            headers = {
            'content-type': "application/x-www-form-urlencoded",   
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
                }
            response = requests.request("GET", url, headers=headers,timeout=(60,60),verify=False)        
            htmlDocument = html.fromstring(response.content.decode(response.encoding))
            return htmlDocument
        except Exception,ex:
            return None
    def getLatLng(self,listScript):
        for script in listScript:
            text = script.text
            if text ==None:
                continue
            if text.find('new google.maps.LatLng')>=0:
                stringLatLng = text[text.find('new google.maps.LatLng(')+len('new google.maps.LatLng('):text.find(');')]
                arrLatLng = stringLatLng.split(',')
                return(arrLatLng[0].replace("'",""),arrLatLng[1].replace("'",""))
        return(None,None)
    def processAddress(self, address):
        if address==None:
            return (None,None,None)
        address = address.split()
        for i in range(0,len(address)):
            if address[i].isdigit() and len(address[i])>=4:
                zipcode = address[i]
                city = ' '.join(address[i+1:len(address)])
                street = ' '.join(address[0:i])
                return (street,city,zipcode)
        return (None, ''.join(address), None)
    def validateDes(self,des):
        for char in self.removeDes:
            if des.find(char)>=0:
                des = des[0:des.find(char)]
        return des
    def getLatlng(self,address,countr):
        if address.strip()=='':
            return (None,None)
        try:
            jsonLatlng = Util.autoChange(address, countr)
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
    def validateFilename(self,name):
        if name!=None:
            for char in self.removeName:
                name= name.replace(char,'')
        return name