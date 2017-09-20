#coding: utf-8
from __future__ import unicode_literals
from Common import Util
import csv
import unicodedata
from urllib import quote_plus
from urllib import urlencode
import geocoder
from validate_email import validate_email
import re
#import validators


with open('Data/Countries.csv', 'r') as f:
    reader = csv.reader(f)
    lstCountries = list(reader) 

def Country(country_id):
    if country_id == None:
        return
    is_valid = False
    country_name = ""
    for country in lstCountries:
        if country_id.lower() == country[0].strip().lower():
            is_valid = True
            country_name = country[1].strip()
            break
        
    msg = "Validate Country: \"" + country_id + "\" is INVALID"     
    Util.log.running_logger.running_logger.logResult("Country", msg, is_valid)
    return country_name


def Email(email):
    if email == None or email == "":
        return
    is_valid = validate_email(email)
    msg = "Validate Email: email \"" + email + "\" is valid"
    Util.log.running_logger.logResult("Email", msg, is_valid)
    
    
def CityZipcode(city, zipcode):
    is_valid = False
    try:
        location = city
        if zipcode != None:
            location += ", " + zipcode  
        if location == "": return
         
        url = "http://www.geonames.org/postalcode-search.html?q="
        url += quote_plus(location.encode("utf8")) + "&country="
        xpath = "//table[@class=\"restable\"]"
        xmlis_valid = Util.GetYQLResponse("*", url , xpath)
        if len(xmlis_valid) > 0:
            is_valid = True
            
        msg = "Validate City and Zipcode: \"" + location + "\" is not exist."
        Util.log.running_logger.info("City_Zipcode " + msg + ': ' + is_valid)
    except Exception, ex:
        Util.log.running_logger.info(ex.message)
    
    
def LatitudeLongitute(lat, lng, city, zipcode):
    is_valid = True
    if lat == None or lng == None: return
    try:
        location = city
        if zipcode != None:
            location += ", " + zipcode  
        if location == "": return        
        loc = geocoder.google([lat, lng], method='reverse')
        is_valid = is_valid and (city.lower() in loc.city.lower())
        if zipcode != None:
            is_valid = is_valid and (zipcode.lower() in loc.postal.lower())
         
        msg = "Validate Latitude & Longitute: \"" + location + "\" is not match with <" + lat + ", " + lng + ">." 
        Util.log.running_logger.info("Latitude_Longitute " + msg + ': ' + is_valid)
    except Exception, ex:
        Util.log.running_logger.info(ex.message)
        
    
def PhoneNumber(phone, country):
    if phone == None or phone == "":
        return
    is_valid = True
    try:
        intPhone = int(phone)
        is_valid = (len(phone) >= 9 and len(phone) < 12)
    except:
        is_valid = False
        
    msg = "Valide Phone Number: \"" + phone + "\" is not Valid"
    Util.log.running_logger.info("Phone_Number " + msg + ': ' + is_valid)
    

def ReValidPhone(phone,type='phone'):
    if phone != None:
        if phone == "":
            return None
        phone = ReValidString(phone)
        if phone != None:
            phone = Util.removeSpecialChar(phone,type).replace(' ','')
        if phone == '':
            return None
        return phone

def reFormatPhoneNumber(codeList,phone,country):
    code = [x for x in codeList if x.get('CountryCode').lower() == country.lower()]
    if len(code) > 0:
        code = code[0]
        phonecode = code.get('PhoneCode')
        phone = ReValidPhone(phone)
        if phone != None and phone.startswith(phonecode):
            phone = '+' + phone
            return phone
    return phone    

def ReValidPrice(price, pattern=None):
    if price == None: 
        return None
    price = price.strip().replace(",", ".").strip()
    price = price.replace('\r\n','').replace('\r','').replace('\n','').strip()
    if pattern != None and re.match(pattern, price) == None:
        return None
    if price.strip() == '':
        return None
    return Util.removedoubleSpace(price).strip()
  
def ReValidString(value):
    if value != None:
        value = value.replace('\r\n','').replace('\r','').replace('\n','').replace('\t','').strip()
        value = value.replace('"',"'").replace('\\','/')
        value = value.encode('utf8').encode('string-escape')   
             
        value = value.replace('\\xc2\\xa0',' ')#&nbsp <space>;
        value = value.replace('\\xe2\\x80\\x93','-')#&ndash <->;
        value = value.replace('\\xc2\\x81','')
        value = value.replace('\\xe2\\x80\\xa2','-')#replace bullet by dash

        value = value.decode('string-escape').decode('utf8')
        if value == "":
            return None
        return Util.removedoubleSpace(value).strip()
    
def ValidateGeoCode(fulladdress,country,lat,lng,scrape_page=None):
    if fulladdress != None and country != None and lat != None and lng != None:
        GermanyChar = [['ä','ae'],['ö','oe'],['ü','ue'],['Ä','Ae'],['Ö','Oe'],['Ü','Ue'],['ß','ss']]
        if country == 'de' or country == 'at':
            for x in GermanyChar:
                fulladdress = fulladdress.replace(x[0],x[1])
        fulladdress = Util.removedoubleSpace(fulladdress)
        jsonLocation = Util.getGEOCode(fulladdress,country)
        if jsonLocation != None and jsonLocation.get('status').upper() == 'OK':
            latLo = str(jsonLocation.get('results')[0].get('geometry').get('location').get('lat'))
            lngLo = str(jsonLocation.get('results')[0].get('geometry').get('location').get('lng'))
            dotIndex = latLo.find('.') + 3
            for c in range(min(dotIndex,len(lat))):
                if lat[c] != latLo[c]:
                    Util.log.coordinate_logger.warning(scrape_page + ': invalid GEO code (' + lat + ',' + lng + ')')
                    return False            
            dotIndex = lngLo.find('.') + 3
            for c in range(min(dotIndex,len(lng))):
                if lng[c] != lngLo[c]:
                    Util.log.coordinate_logger.warning(scrape_page + ': invalid GEO code (' + lat + ',' + lng + ')')
                    return False
        else:
            Util.log.coordinate_logger.warning(fulladdress + ',' + country + ': cannot get GEO code')            
    return True

def CheckURL(url):
    if url == None or url == '':
        return ''
    elif Util.Navigate(url) != 404 :
        return url
    return ''

def is_valid_url(url):
    regex = re.compile(r'^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/|www\.)[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:%/?#[\]@!\$&\(\)\*\+,;=.]+$', re.IGNORECASE)
    return url is not None and regex.search(url)

def RevalidURL(url):
    if url != None:        
        if url == None:
            return None
        if isinstance(url,list):
            url = [x.replace(' ','%20') for x in url if is_valid_url(x) != None]
        elif is_valid_url(url) != None:
            return url
        else:
            return None
    return url

def RevalidName(name,isGermany=False):
    invalidchar = ['\\','/','*','?','"','<','>','|',':']
    GermanyChar = [['ä','ae'],['ö','oe'],['ü','ue'],['Ä','Ae'],['Ö','Oe'],['Ü','Ue'],['ß','ss']]
    OtherChar = [['À','A'],['Á','A'],['Â','A'],['Ã','A'],['Ä','A'],['Ç','C'],['È','E'],['É','E'],['Ê','E'],['Ë','E'],['Ì','I'],['Í','I'],['Î','I'],['Ï','I'],['Ñ','N'],['Ò','O'],['Ó','O'],['Ô','O'],['Õ','O'],['Ö','O'],['Š','S'],['Ú','U'],['Û','U'],['Ü','U'],['Ù','U'],['Ý','Y'],['Ÿ','Y'],['Ž','Z'],['à','a'],['á','a'],['â','a'],['ã','a'],['ä','a'],['ç','c'],['è','e'],['é','e'],['ê','e'],['ë','e'],['ì','i'],['í','i'],['î','i'],['ï','i'],['ñ','n'],['ò','o'],['ó','o'],['ô','o'],['õ','o'],['ö','o'],['š','s'],['ù','u'],['ú','u'],['û','u'],['ü','u'],['ý','y'],['ÿ','y'],['ž','z']]
    if name != None:
        name = ReValidString(name)
        if name != None:        
            for char in invalidchar:
                name = name.replace(char,'-')
            if isGermany:
                for x in GermanyChar:
                    name = name.replace(x[0],x[1])
            else:
                for x in OtherChar:
                    name = name.replace(x[0],x[1])
        else:
            return "Invalid Name"
    return unicodedata.normalize('NFKD',name).encode('ascii','ignore')

def is_valid_email(email):
    return bool(re.search(r'[\w.-]+@[\w.-]+\.[a-z]{2,3}', email))

def RevalidEmail(email):
    try:
        if email == None or email == '':
            return None
        is_valid = is_valid_email(email)#validate_email(email,check_mx=True,smtp_timeout=20)
        if is_valid == False:
            Util.log.running_logger.warning(email + " invalid email")
            return None
        else:
            return email
    except:
        Util.log.running_logger.info(email + ': cannot Validate')
        return email
    
    
