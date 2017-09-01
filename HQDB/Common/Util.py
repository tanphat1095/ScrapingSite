# coding: utf-8
from __future__ import unicode_literals
import requests
import codecs
import io
from lxml import etree as ET
from lxml import html
from urllib import urlencode
from urllib import quote_plus
from HTMLParser import HTMLParser
import os
import csv
import unicodecsv
import json
import datetime
from collections import OrderedDict
from Common.Logging import Log
import csv
import urllib2
import urllib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

log = Log

#OpenHours Days Of Week
_24H_UK_DaysOfWeek = "Monday-Sunday: 00:00-24:00"
_24H_IE_DaysOfWeek = "Monday-Sunday: 00:00-24:00"

_24H_DE_DaysOfWeek = "Montag-Sonntag: 00:00-24:00"
_24H_AT_DaysOfWeek = "Montag-Sonntag: 00:00-24:00"

_24H_ES_DaysOfWeek = "Lunes-Domingo: 00:00-24:00"

_24H_PL_DaysOfWeek = "Poniedziałek-Niedziela: 00:00-24:00"
_24H_CZ_DaysOfWeek = "Pondĕlí-Nedĕle: 00:00-24:00"
#geocodeAPI_key = "AIzaSyDVUXo2fMFQzeg0OkIAXjcq5k4sy4x-yMU"
#geocodeAPI_key = "AIzaSyB4VhdBL6zvIr_o9TV9kud7dhfAfEYpi-s"
geocodeAPI_key = "AIzaSyCAfw9oD58hpN3SwG3tGannKhgIcOFnzbA"



def GetYQLResponse(select, url, xpath, spec=False):
    '''
    return a XML tree with tag = "results"
    '''
    _url_YQL = "https://query.yahooapis.com/v1/public/yql"
    _query = "select {0} from html where url='{1}' and xpath='{2}'"
    
    query = _query.format(select, url, xpath)
    params = {'q': query}
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    rq = requests.post(_url_YQL, params=urlencode(params), headers=headers)
    body = rq.text.encode('utf-8')
    if spec == True:
        return body
    xml = ET.ElementTree(ET.fromstring(body))
    return xml.getroot()[0]  

def POSTRequest(url, headers=None, params=None):
    '''
    return a string XML  
    '''
    rq = requests.post(url, data=params, headers=headers, timeout=(60,60))
    body = rq.text.encode('utf8')
    return body

def GETRequest(url, headers=None, params=None):
    '''
    return a string XML  
    '''
    rq = requests.get(url, data=params, headers=headers,timeout=(60,60))
    body = rq.text
    return body

def GetHTMLResponse(url, xpath, headers=None, params=None):
    respone = requests.get(url, data=params, headers=headers)
    content = respone.text
    htmlData = html.fromstring(content)
        
    return htmlData.xpath(xpath)

def Navigate(url):
    '''
    return status code 
    '''
    try:
        headers = {
            'content-type': "application/x-www-form-urlencoded",   
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        response = requests.request("GET", url, headers=headers,timeout=(60,60),verify=False)        
        return response.status_code
    except:
        return 404
 
def createFolder(path, name):
    folder = path + "/" + name if path != "" else name

    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

def removedoubleSpace(s):
    while s.find('  ') >= 0:
        s = s.replace('  ',' ')
    return s

def removesingleSpace(s):
    s = s.replace(' ','')
    return s

def removeSpecialChar(s, exceptchar=''):
    if s != None:
        firstchar = s[0]
        charlst = ['*','-','/','(',')','.',',',':','+','\r\n','\r','\n']
        for char in charlst:
            if exceptchar == 'pl' and char == '-':
                continue
            if char != exceptchar:
                s = s.replace(char,'')
        if exceptchar == 'phone' and firstchar == '+':
            s = firstchar + s
        s = s.replace('#',',,')
    return s

def getCharReplace():
    try:
        with open('Data/Characters_Replacement.json') as json_data:
            d = json.load(json_data)
            return d
    except Exception,ex:
        return None

def getPhoneCodeList():
    try:
        with open('Data/CountryPhoneCode.json') as json_data:
            d = json.load(json_data)
            return d
    except Exception,ex:
        return None

def getOutSeasFrance():
    try:
        with open('Data/OutSeasFrance.json') as json_data:
            d = json.load(json_data)
            return d
    except Exception,ex:
        return None

def getYQLXML(select, url, xpath, spec=False):
    try:
        baseurl = "https://query.yahooapis.com/v1/public/yql"
        query = "select * from htmlstring where url='{0}' and xpath='{1}'"
        query = query.format(url,xpath)
        params = {
                "q":query,
                "env":"store://datatables.org/alltableswithkeys"
            }
        headers = {
                'content-type': "application/x-www-form-urlencoded",
                'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"           
            }
        response = requests.get(baseurl, headers=headers, params=urlencode(params),timeout=(60,60),verify=False)
        body = response.text.encode('utf-8')
        if spec == True:
            return body
        xml = ET.ElementTree(ET.fromstring(body))
        xml = xml.getroot()[0][0]
        if xml.text != None:
            xml = xml.text.replace('\r','').replace('\n','').strip()
            xml = '<results>' + xml + '</results>'
            xml = ET.ElementTree(ET.fromstring(xml))
            return xml.getroot()
    except:
        return None

def getYQLXML2(select, url, xpath, spec=False):
    baseurl = u"https://query.yahooapis.com/v1/public/yql?"
    yql_query = u"select {0} from htmlstring where url='{1}' and xpath='{2}'"
    yql_query = yql_query.format(select,url,xpath)
    yql_url = baseurl + urllib.urlencode({'q':yql_query}) + u"&env=store://datatables.org/alltableswithkeys"       
    result = urllib2.urlopen(yql_url).read()
    if spec == True:
        return result
    else:
        xml = ET.ElementTree(ET.fromstring(result))
        xml = xml.getroot()[0][0]
        if xml.text != None:
            xml = xml.text.replace('\r','').replace('\n','').strip()
            xml = '<results>' + xml + '</results>'
            xml = ET.ElementTree(ET.fromstring(xml))
            return xml.getroot()

    '''
    if spec=False: return a XML with xpath that response from URL input
    if spec=True: return html Document that respone from URL input
    '''
def getRequestsXML(url,xpath,spec=False,encoding=True):
    try:
        headers = {
            'content-type': "application/x-www-form-urlencoded",   
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        response = requests.request("GET", url, headers=headers,timeout=(60,60),verify=False)        
        htmlDocument = html.fromstring(response.content.decode(response.encoding))
        if encoding == False:
            htmlDocument = html.fromstring(response.content)
        if spec == True:
            return htmlDocument
        else:
            xmlTemp = htmlDocument.xpath(xpath)
            root = ET.Element('results')
            for xml in xmlTemp:
                root.append(xml)
            return root
    except Exception,ex:
        return None

def getSeleniumXML(url,xpath,xPathelemenClick=None):
    try:
        delay = 20  
        #driver = webdriver.Chrome('Data/chromedriver.exe')
        driver = webdriver.PhantomJS('Data/phantomjs.exe')
        driver.start_client()
        driver.set_page_load_timeout(delay)
        driver.get(url)                     
        page_state = driver.execute_script('return document.readyState;')
        while page_state != 'complete':            
            page_state = driver.execute_script('return document.readyState;')                        
        if xPathelemenClick != None:
            WebDriverWait(driver,delay).until(EC.visibility_of_element_located((By.XPATH,xPathelemenClick)))
            element = driver.find_element_by_xpath(xPathelemenClick)
            element.click()
        WebDriverWait(driver,delay).until(EC.visibility_of_element_located((By.XPATH,xpath)))
        responsehtml = html.fromstring(driver.page_source)
        return responsehtml.xpath(xpath)
    except Exception,ex:
        return None
        raise Exception(ex.message) 
    finally:
        driver.close()                                      

def WriteXMLToFile(folder, filename, xmlRoot):
    try:
        et = ET.ElementTree(xmlRoot)
        et.write("/".join([folder,filename]), pretty_print=True,encoding="utf-8")
        return True
    except:
        return False

def CheckExistingFile(folder, filename):
    return os.path.isfile("/".join([folder,filename]))

def ReadXMLFromFile(folder,filename):
    try:
        if CheckExistingFile(folder,filename) == True:
            xmlTemp = ET.parse("/".join([folder,filename]))
            return xmlTemp.getroot()
        return None
    except:
        return None

def getGEOCode(fulladdress,country):
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        querystring = {
                "address":fulladdress + "," + country,
                "key":geocodeAPI_key
            }
        headers = {
                'content-type': "application/x-www-form-urlencoded"
            }
        response = requests.request("GET", url, headers=headers, params=querystring,timeout=(60,60))
        #other way
        #
        json_location = response.json()
        return json_location
    except Exception,ex:
        return None

def subtractTime(t1,t2):        
        # caveat emptor - assumes t1 & t2 are python times, on the same day and
        # t2 is after t1
        h1, m1, s1 = t1.hour, t1.minute, t1.second
        h2, m2, s2 = t2.hour, t2.minute, t2.second
        t1_secs = s1 + 60 * (m1 + 60 * h1)
        t2_secs = s2 + 60 * (m2 + 60 * h2)
        return(t2_secs - t1_secs)

def convertString2Time(source):#time format is HH:MM
    try:
        return datetime.datetime.strptime(source,'%H:%M').time()
    except:
        return None

def writelist2File(listVenues,outFile):
    try:
        if isinstance(listVenues,list):              
            with io.open(outFile, "wb") as outfile:
                csvwriter = unicodecsv.writer(outfile,encoding='utf8')                
                csvwriter.writerow(listVenues[0].keys())
                for myOrderedDict in listVenues:
                    csvwriter.writerow(myOrderedDict.values())
    except Exception,ex:
        log.info(", ".join([unicode(ex.args)]))

def ExportCSV(folder,filename):    
    listFiles = []
    ordersVenues = ('adid',
                'name',
                'name_of_contact',
                'business_website',
                'areas_covered',
                'formatted_address',
                'description',
                'img_link',
                'hqdb_featured_ad_type',
                'hqdb_nr_reviews',
                'hqdb_review_score',
                'accreditations',
                'scrape_page',
                'category',
                'subcategory',
                'street',
                'city',
                'zipcode',
                'country',
                'office_number',
                'office_number2',
                'mobile_number',
                'mobile_number2',
                'unidentified_phone_numbers',
                'latitude',
                'longitude',
                'business_email',
                'yelp_page',
                'facebook',
                'twitter',
                'instagram',
                'venue_images',
                'opening_hours_raw',
                'pricelist_link')
    ordersServices = ('service_category',
                'service',
                'duration',
                'price',
                'description',)
    try:
        listVenues = []
        listServices = []
        outFileVN = folder + '/' + filename + '_Venues.csv'
        outFileSV = folder + '/' + filename + '_Services.csv'
        for file in os.listdir(folder):
            if file.endswith('.json'):
                try:
                    file = folder + '/' + file
                    print file
                    with open(file,'r') as jsonFile:
                        jText = jsonFile.read()
                        jText = jText.decode('utf8').replace('\\','/')
                        jObj = json.loads(jText,object_pairs_hook=OrderedDict)                        
                        services = jObj['services']
                        del jObj['services']
                        for key in ordersVenues:
                            if hasattr(jObj,key):
                                temp = jObj[key]
                                del jObj[key]
                                if temp != None:
                                    if isinstance(temp,list) and key == 'hqdb_featured_ad_type':                                
                                        jObj[key] = ["'" + x.encode('utf8').decode('utf8').strip('"').strip("'") + "'" for x in temp if x != None and x.strip() != '']
                                        jObj[key] = '[' + ", ".join(jObj[key]) + ']'
                                    elif isinstance(temp,list):
                                        jObj[key] = u','.join([x.encode('utf8').decode('utf8') for x in temp])
                                    else:
                                        jObj[key] = temp.encode('utf8').decode('utf8')
                                else:
                                    jObj[key] = ''
                        for sv in services:
                            for svkey in ordersServices:
                                if hasattr(sv,svkey):
                                    tempsv = sv[svkey]
                                    del sv[svkey]
                                    if tempsv != None:
                                        sv[svkey] = tempsv.encode('utf8').decode('utf8')
                                    else:
                                        sv[svkey] = ''
                                    listServices.append(sv)
                        listVenues.append(jObj)
                except Exception,ex:
                    log.invalid(None,file + ': ' + ex.message)
                    print file + ': ' + ex.message
                    continue
        if len(listVenues) > 0:
            writelist2File(listVenues,outFileVN)
        if len(listServices) > 0:
            writelist2File(listServices,outFileSV)       
    except Exception,ex:
        print ex.message
        raise

