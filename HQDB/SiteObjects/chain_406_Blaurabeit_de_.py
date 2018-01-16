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
import requests
import time
import phonenumbers
from lxml import html
from audioop import add
from Common.Validation import CityZipcode
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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
    linkIn=[]
    removeName =[':)',':','=))','=']
    removeDes= ['Mobil','Email','Tel:','Kontaktdaten:','Adresse:','E-Mail:','Email Adresse:']
    bpfArray =['//div[@class="row row_b row_container clearfix"]',
               '//div[@class="row row_f row_container clearfix"]',
               '//div[@class="row row_p row_container clearfix"]',
               '//div[@class="row row_a row_container clearfix"]']
    regex_= ['(BP[\s][\d]{1,5})','(BP[\d]{1,5})','(BP[\s][\d]{1,5})','(B.P.[\s][\d]{1,5})','(CS[\s][\d]{1,5})','(CS[\d]{1,5})','([\d]{4,20})']
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
        self.phoneCodeList = Util.getPhoneCodeList()
      
        self.__getListVenues()
    def getCategory(self):
        listCate=[]
        xmlDoc = Util.getRequestsXML('https://www.blauarbeit.de/branchenbuch/index.html', '//div[@class="box_w box_r"]/ul/li/a')
        if xmlDoc!=None:
            a   =  xmlDoc.xpath('./a')
        for a_ in a :
            listCate.append(a_.text+'\t'+self.__url__+a_.get('href'))
        return listCate 
    def __getListVenues(self):
            
            
            setvenuesperCate= 50000 #834
            listLink = self.getCategory()
            
            '''with open('Data/Category_chain_406.txt') as f:
                line_ = f.read().splitlines()'''
            index =0
            for line in listLink:
                countPerCate =0 
                
                cateArr = line.split('\t')
                cate = cateArr[0]
                cateLink = cateArr[1]
                subcateXml = Util.getRequestsXML(cateLink,'//div[@class="box_w box_r"]/ul/li/ul')
                if subcateXml!=None:

                    subcates =  subcateXml.xpath('./ul/li/a')
                    for subcate in subcates:
                        
                        
                        try:
                        
                            if countPerCate >= setvenuesperCate:
                                break
                        
                        
                            catename =  ''.join(subcate.itertext()).strip()
                            urlcate = subcate.get('href')
                            if urlcate.startswith('/'):
                                urlcate =  self.__url__+ urlcate
                            pages = 0
                            while True :
                            
                            
                                if countPerCate >= setvenuesperCate:
                                    break
                            
                                param= '?radius=21&view=list&interval='+str(pages)
                                xmlDoc = Util.getRequestsXML(urlcate+param,'//div[@class="br_results br_results_dir"]')
                                countWhile = 0
                                while xmlDoc ==None:
                                    time.sleep(300)
                                    print 'while sleeping...'
                                    xmlDoc = Util.getRequestsXML(urlcate+param,'//div[@class="br_results br_results_dir"]')
                                    countWhile +=1
                                    if  countWhile >=3:
                                        break
                                if len(xmlDoc.xpath('./div[@class="br_results br_results_dir"]'))<=0:
                                    break
                                for xpath_ in self.bpfArray:
                                
                                
                                    if countPerCate >= setvenuesperCate :
                                        break
                                
                                    elementIems = xmlDoc.xpath(xpath_)
                                    for ele in elementIems:
                                    
                                    
                                        if countPerCate >= setvenuesperCate:
                                            break
                                    
                                        #type_hqdb = ele.find('.//div[@class="col-inner"]/div')
                                        if xpath_ =='//div[@class="row row_p row_container clearfix"]':
                                            hqdb_type ="featured"
                                        else:
                                            #hqdb_type =  ''.join(type_hqdb.itertext()).strip()
                                            hqdb_type ='none'
                                        linkItems = ele.find('.//div[@class="name"]//a').get('href')
                                        if linkItems.startswith('/'):
                                            linkItems= self.__url__+linkItems
                                            print 'Scrapping: '+ linkItems
                                            #time.sleep(1)
                                            #linkItems = 'https://www.blauarbeit.de/p/berlin/sabine_amm/194277.htm'
                                            ven =    self.__VenueParser(hqdb_type, linkItems,catename,cate)
                                            if ven!=None:
                                                print 'Writing index: '+str(index)
                                                ven.writeToFile(self.folder, index, self.validateFilename(ven.name), False)
                                                index+=1
                                                countPerCate+=1       
                                pages+=1
                        except Exception,ex:
                            print ex
                          
                            
    def __VenueParser(self,hqdb_type, linkItems,subcate,cate):    
            #linkItems ='https://www.blauarbeit.de/p/modernisierung/_sanierung/berlin/daniel_kutscher/576667.htm'
            existing=[x for x in self.linkIn if linkItems in x]
            if len(existing)>0:
                print 'This venue exist in list'
                return None
            self.linkIn.append(linkItems)
            
            
            
            xmlPages = self.getRequest(linkItems)
            if xmlPages==None:
                return None
          
        
            xmlVen = xmlPages.xpath('//div[@class="page_move"]')
            cate__ = xmlPages.find('.//meta[@name="Description"]')
            
            if len(xmlVen)==0:
                return None
        
            name = xmlVen[0].xpath('.//h2')
            if len(name) <=0:
                name =''
            else:
                name = name[0].text.strip()
            noneValues ={'ZERO','NULL'}
            if name.upper() in noneValues:
                return None
            ven = Venue()
            
            if cate__!=None:
                ven.category = cate__.get('content').split(',')[0]
                
                
            nameFromUrl = self.getNamefromUrl(linkItems)
            ven.name =  nameFromUrl
            ven.hqdb_featured_ad_type = hqdb_type
            #ven.name =name
            ven.scrape_page = linkItems
            #ven.subcategory = subcate
            #ven.category= cate
            address_= ''
            #ven.formatted_address=''
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
                        values_ = ' '.join(td[1].itertext()).strip().replace('keine Angabe','').replace('NULL','').replace('null','')
                        if key_ =='Ansprechpartner:':
                            if values_!=None and len(values_)>2:
                                #values_ =''
                                ven.name_of_contact = values_
                                ven.name +=', '+ ven.name_of_contact
                            
                        if key_ =='Addresse:':
                            
                            address_ =  values_
                            ven.formatted_address = self.validateFormat(address_)
                            
                            
                            
                            
                            
                            '''(ven.street,ven.city,ven.zipcode) = self.processAddress(address_)
                            if ven.street!=None:
                                ven.street = self.validateStreet2(ven.street)
                            #ven.formatted_address = address_
                            if ven.city!=None:
                                checkCity = ven.city.split() 
                                if len(checkCity)>0:
                                    if checkCity[0].isdigit():
                                        if len(checkCity[0])==5:
                                            if ven.street!=None:
                                                ven.street+=' '+ ven.zipcode
                                            ven.zipcode = checkCity[0]
                                            ven.city = ven.city.replace(ven.zipcode,'')
                                        else:
                                            ven.city = None
                                            ven.street = None
                                            ven.zipcode= None
                                            ven.formatted_address = ' '.join(checkCity)
                                
                                
                                
                            if ven.zipcode!=None:
                                if len(ven.zipcode)==5:
                                    ven.zipcode = ven.zipcode
                                else:
                                    ven.zipcode = None'''
                            
                            
                            
                        if key_ =='Homepage:':
                            a_ = td[1].find('./a')
                            if a_ !=None:
                                ven.business_website = a_.get('href')
                        mobileCode =['015','016','017','+4915','+4916','+4917']
                        if key_ =='Tel:':
                            values_ = values_.replace('/', '').replace(' ', '').replace('Tel', '')
                            
                            #values_ ='01735465435'
                            
                            
                            for mCode in mobileCode:
                                if values_.startswith(mCode):
                                    ven.mobile_number = self.validatePhone__(self.validatePhone(values_), 'de')
                                    break
                            if ven.mobile_number==None:
                                ven.office_number = self.validatePhone__(self.validatePhone(values_), 'de')
                            
                            '''if values_.startswith('01')| values_.startswith('+0041')| values_.startswith('0041'):
                                ven.mobile_number = self.validatePhone__(self.validatePhone(values_), 'de')
                            else:
                                ven.office_number = self.validatePhone__(self.validatePhone(values_), 'de')'''
                            
                    img_ = leftInfo.find('./div/div[@class="profile_top_right"]/img')
                    if img_!=None:
                        img_ =img_.get('src')
                        img_link.append(img_)
                    rating = leftInfo.xpath('.//section[@id="ratings"]/div')
                    if len(rating)>=2:
                        rating1 = ''.join(rating[0].itertext()).strip().split()[1]
                        rating2 = ''.join(rating[1].itertext()).strip()
                        if len(rating2)>0:
                            rating2 = rating2.split()[0]
                            if rating2.find('/')!=-1:
                                rating2 =  rating2.split('/')[0].replace(',','.')
                        try:
                            float(rating2)
                        except Exception,ex:
                            rating2=None
                        ven.hqdb_nr_reviews = rating1
                        ven.hqdb_review_score = rating2
                    
                    
                    if ven.hqdb_review_score==None:
                        scoreIn = xmlVen[0].xpath('//div[@class="float_box"]//span[@class="txtLight"]/parent::div')
                        if len(scoreIn)>0:
                            core_ = scoreIn[0].text.replace(',','.')
                            try:
                                float(core_)
                            except Exception,ex:
                                core_ =None
                            ven.hqdb_review_score = core_
                    script_ = xmlPages.xpath('./head/script')
                    if ven.formatted_address.strip()=='' and ven.office_number==None and ven.office_number2 ==None and ven.mobile_number ==None and ven.mobile_number2 ==None:
                        return None
                    
                    '''streetTemp = ven.street
                    cityTemp =ven.city
                    zipcodeTemp =ven.zipcode
                    
                    if streetTemp ==None:
                        streetTemp =''
                    if ven.city ==None:
                        cityTemp = ''
                    if ven.zipcode ==None:
                        zipcodeTemp =''
                    address_ = streetTemp+', '+cityTemp+', '+zipcodeTemp
                    address_ = address_.strip().replace(', ,', ',').replace(',,', ',')
                    if address_.startswith(','):
                        address_ =address_[1:len(address_)]
                    if address_.endswith(','):
                        address_ = address_[0:len(address_)-1]
                        
                    if ven.formatted_address!=None:
                        address_ = ven.formatted_address'''
                    
                    #if len(address_.strip())>5:
                    #    (ven.latitude,ven.longitude)  = self.getLatlng(address_,'DE') #script_
                    zipFrom = self.findZipcode(ven.formatted_address)
                    if zipFrom!=None:
                        (ven.latitude,ven.longitude) = self.getLatlng(zipFrom, 'DE')
                        if ven.latitude ==None and ven.longitude==None:
                            Util.log.running_logger.info(ven.formatted_address+' : cannot get GEO code')
                    redirecPhotos= rightInfo.find('./nav/div/ul/li[@class="tabOff tab_foto"]/a')
                    if redirecPhotos!=None:
                        linkPhotos =  redirecPhotos.get('href')
                        if linkPhotos.startswith('/'):
                            linkPhotos = self.__url__+ linkPhotos
                        #time.sleep(1)
                        xpathPhotos =  Util.getRequestsXML(linkPhotos, '//div[@class="portfolio thumbs"]/a')
                        if xpathPhotos!=None:
                            listImg = xpathPhotos.xpath('./a')
                            for __img in listImg:
                                img_link.append(__img.get('data-thumb'))
                    
                    
                    desElement= rightInfo.find('./div/div[@id="cont_about"]')
                    
                    
                    '''
                    pTag = desElement.xpath('//div[@class="overview"]/p')
                    des = ''
                    for desE in pTag :
                        if ''.join(desE.itertext()).find('<xml>')>=0:
                            continue
                        des+=''.join(desE.itertext())
                    h5Tag = desElement.xpath('//div[@class="overview"]/h5')
                    for desE_ in h5Tag:
                        if ''.join(desE_.itertext()).find('<xml>')>=0:
                            continue
                        des += ''.join(desE_.itertext())
                    divTag =desElement.xpath('//div[@class="overview"]/h5')
                    for div_ in divTag:
                        if ''.join(div_.itertext()).find('<xml>')>=0:
                            continue
                        des+= ''.join(div_.itertext())
                    if len(pTag)==0 and len(h5Tag) ==0:
                        if desElement.find('.//div[@class="overview"]')!=None:
                            des =  desElement.find('.//div[@class="overview"]').text
                    ven.description = self.validateDes(des)
                    '''
                    des =''
                    divTag = desElement.xpath('//div[@class="overview"]')
                    for divDes in divTag:
                        des+= ' '.join(divDes.itertext())
                    ven.description =  self.validateDes(des)
                    
                    
             
                    
                    
                    certi = rightInfo.find('.//div/div[@id="cont_certs"]')
                    tablecerti =  certi.find('./table')
                    if tablecerti!=None:
                        certi_ = ''.join(tablecerti.itertext()).replace('Geprüfte Zertifikate:','')
                        ven.accreditations = certi_
                    ven.img_link = img_link
                    ven.country ='de'
                    ven.is_get_by_address = True
                    return ven
            else:
                return None
                    
    def getNamefromUrl(self,url):
        arr_ =url.split('/')
        #for i in range(0, len(arr_)):
            #if arr_[i]=='p':
                #return arr_[i+1].replace('-',' ').replace('_',' ').strip()
        return arr_[4].replace('-',' ').replace('_',' ').strip()+''
    
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
        address = address.replace('>','').split()
        for i in range(0,len(address)):
            if address[i].isdigit() and len(address[i])>=4:
                zipcode = address[i]
                #if len(zipcode)==5:
                #    zipcode =zipcode
                #else:
                #    zipcode =None
                city = ' '.join(address[i+1:len(address)])
                if city!=None:
                    if city.find(',')>=0:
                        city =city.split(',')
                        city = city[len(city)-1]
                    if city.find('+')>=0:
                        city = city.split('+')[0]
                street = ' '.join(address[0:i])
                if street!=None:
                    if street.find(':')>=0:
                        street = street[street.find(':')+1:len(street)-1]
                        if street.find('@')>=0:
                            street=None
                return (street,self.getCity(city),zipcode)
        return (None, self.getCity(''.join(address)), None)
    def validateFormat(self,format_ ):
        reg = ['(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)','([\d]{3,4}[/][\d]{6,20})','([\d]{2,4}-[\d]{6,10})','([\d]{6,20})','([+][\d]{1,20})']
        for r in reg :
            result = re.search(r, format_, flags=0)
            if result !=None:
                format_ = format_.replace(result.group(0),'')
        format_ = format_.replace('>','').replace('....','').replace('...','').replace('http://h-s-s-24.de.to ','').replace('00688','').replace('00000','')
        if format_.find(':')!=-1:
            format_ = format_[format_.find(':')+1:len(format_)-1]
   
        return format_
    def processAddress_(self,address):
        if address==None:
            return (None,None,None)
        address= address.split()
        index =0
        index_ =0
        for i in range(0,len(address)):
            tempZip = address[i]
            if tempZip.isdigit() and len(tempZip)>=4:
                if len(tempZip) ==5:
                    zipcode =tempZip
                    index= i
                else:
                    index_=i
                    for k in range(i+1,len(address)):
                        if address[k].isdigit() and len(address[k])==5:
                            zipcode = address[k]
                            index = k
        if index==0 and index_ ==0:
            return (None,' '.join(address),None)
        else:
            if index==0 and  index_>0:
                city = ' '.join(address[index_+1:len(address)])
                zipcode =None
                street = ' '.join(address[0:index_+1])
            else:
                if index >0:
                    zipcode = address[index]
                    city = ' '.join(address[index+1:len(address)])
                    street = ' '.join(address[0:index])
                    
            if city!=None:
                if city.find(',')>=0:
                    city = city.split(',')
                    city = city[len(city)-1]
                if city.find('+')>=0:
                    city = city.split('+')[0]
                if street!=None:
                    if street.find(':')>=0:
                        street = street[street.find(':')+1:len(street)-1]
                    if street.find('@')>=0:
                        street = None
            return (street,city,zipcode)
    
    
    
    
    def validateDes(self,des):
        for char in self.removeDes:
            if des.find(char)>=0:
                des = des[0:des.find(char)]
        try:        
            findchar = self.findAllPositionCharinString('[if', des)
        except Exception,ex:
            print ex
        for i in range(0,len(findchar)):
            if des.find('[if')>=0:
                remove_ = des[des.find('[if'):des.find('endif]')+len('endif]')]
                des = des.replace(remove_,'')          
        findStart = self.findAllPositionCharinString('/* Font Definitions */', des)
        while len(findStart)>1:
            findStart = self.findAllPositionCharinString('/* Font Definitions */', des)
            endchar = 'ul \t{margin-bottom:0cm;}'
            findend= self.findAllPositionCharinString(endchar, des)
            if len(findend)==0:
                endchar='page:Section1;}'
                findend= self.findAllPositionCharinString(endchar, des)
            if len(findend)==0:
                    print 'can found end point'
                    break
            remove_2 = des[findStart[0]:findend[0]+len(endchar)]
            des =  des.replace(remove_2,'')
        return des.replace('�','').replace('-',' ').replace('..',' ').replace('__','')
    def getLatlng(self,address,countr):
        if address.strip()=='':
            #return (None,None)
            address = 'null'
            return (None,None)
        try:
            jsonLatlng = UtiUtil_backuptGEOCode(address, countr)
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
    def findZipcode(self,address):
        if address!=None:
            address_ =  address.split()
            for add in address_:
                if len(add)==5 and add.isdigit():
                    return add
        return None
    def findAllPositionCharinString(self,char,String):
        return [i for i in range(len(String)) if String.startswith(char, i)]
    def validatePhone(self,phone):
        if phone ==None:
            return None
        else:
            if phone.startswith('+004')| phone.startswith('004'):
                if len(phone)<17 and len(phone)>12:
                    if phone.startswith('+'):
                        return '+'+phone[3:len(phone)]
                    else:
                        return '+'+ phone[2:len(phone)]
                else:
                    return None
        
            else:
                
                if len(phone)>=10 and len(phone)<13:
                    return phone
                else:
                    return None
    
    def getCity(self,city):
        if city!=None:
            if city.find(',')>=0:
                city =city.split(',')
                city = city[len(city)-1]
            if city.find('+')>=0:
                city = city.split('+')[0]
            if city.find('/')>=0:
                city = city.split('/')
                city =city[len(city)-1]
            return city
        else:
            return None
        
    def validatePhone__(self,phone,country='FR'):        
        try:
            parsed_phone = phonenumbers.parse(phone, country.upper(), _check_region=True)
        except phonenumbers.phonenumberutil.NumberParseException as error: 
                print str(phone) +' can not parse'
                UtiUtil_backupg.running_logger.warning(str(phone)+' : cannot parse')
                return None
        if not phonenumbers.is_valid_number(parsed_phone):
            print str(phone) +': not number'
            UtiUtil_backupg.running_logger.warning(str(phone)+' : not number')
            return None
        else:
            return self.validatePhonecode(phone)     
    def validatePhonecode(self,phone):
        if phone.startswith('4') or phone.startswith('+4'):
            if phone.replace('+','').startswith('49'):
                if phone.startswith('+'):
                    return phone
                else:
                    return '+'+phone
            else:
                return None
        else:
            if phone.startswith('o'):
                return '0'+ phone[1:len(phone)]
            return phone
    def validateStreet2(self, street):
        for reg in self.regex_:
            results = re.search(reg, street, flags=0)
            if results!=None:
                street = street.replace(results.group(0),'')
        return street
