from __future__ import unicode_literals
import io
import json
from collections import OrderedDict
import Common.Validation as Validator
from Common import Util
import codecs
 
class Venue_Extra(object):
    
    name = None
    scrape_page = None
    street = None
    city = None
    zipcode = None
    country = None
    latitude = None
    longitude = None
    formatted_address = None
    business_email = None
    business_website = None
    office_number = None
    mobile_number = None
    office_number2 = None
    mobile_number2 = None
    unidentified_phone_numbers = None
    opening_hours_raw = None
    facebook_page = None
    yelp_page = None
    pricelist_link = None
    description = None
    specialty = None
    services = None
    
    def __init__(self):        
        ''       
    
    def __reValidInfo(self,keepPriceList=False):        
        self.name = Validator.ReValidString(self.name)
        self.scrape_page = Validator.ReValidString(self.scrape_page)
        self.street = Validator.ReValidString(self.street)
        self.city = Validator.ReValidString(self.city)
        type = 'phone'
        if self.country == 'pl':
            type = 'pl'
        self.zipcode = Validator.ReValidPhone(self.zipcode,type)
        self.country = Validator.ReValidString(self.country)
        self.getFullAddress()
        self.formatted_address = Validator.ReValidString(self.formatted_address)		
        self.latitude = Validator.ReValidString(self.latitude)
        self.longitude = Validator.ReValidString(self.longitude)
        self.business_email = Validator.ReValidString(self.business_email)
        self.business_website = Validator.ReValidString(self.business_website)
        self.office_number = Validator.ReValidPhone(self.office_number)
        self.mobile_number = Validator.ReValidPhone(self.mobile_number)
        self.office_number2 = Validator.ReValidPhone(self.office_number2)
        self.mobile_number2 = Validator.ReValidPhone(self.mobile_number2)
        if self.unidentified_phone_numbers != None and len(self.unidentified_phone_numbers) > 0:
            self.unidentified_phone_numbers = [Validator.ReValidPhone(x).strip() for x in self.unidentified_phone_numbers]
        elif self.unidentified_phone_numbers != None and len(self.unidentified_phone_numbers) == 0:
            self.unidentified_phone_numbers = None
        self.opening_hours_raw = Validator.ReValidString(self.opening_hours_raw)
        self.facebook_page = Validator.ReValidString(self.facebook_page)
        self.yelp_page = Validator.ReValidString(self.yelp_page)    
        self.description = Validator.ReValidString(self.description)
        self.specialty = Validator.ReValidString(self.specialty)
        if Validator.ValidateGeoCode(self.formatted_address,self.country,self.latitude,self.longitude) == False:            
            Util.log.invalid('GEO code',self.name + ': invalid GEO code (' + self.latitude + ',' + self.longitude + ')')
            self.latitude = None
            self.longitude = None
        if len(self.services) <= 0 and keepPriceList == False:
            self.pricelist_link = None                  
    
    
    def validate(self):
        Util.log.info("----------------------- Validating Venue: " + self.name)
        Validator.CityZipcode(self.city, self.zipcode)
        Validator.Country(self.country)
        Validator.LatitudeLongitute(self.latitude, self.longitude, self.city, self.zipcode)
        Validator.Email(self.business_email)
        Validator.Link(self.business_website)
        Validator.PhoneNumber(self.office_number, self.country)
        Validator.PhoneNumber(self.mobile_number, self.country)
        Validator.PhoneNumber(self.office_number2, self.country)
        Validator.PhoneNumber(self.office_number2, self.country)
        Validator.PhoneNumber(self.unidentified_phone_numbers, self.country)
        Validator.Link(self.facebook_page)
        Validator.Link(self.yelp_page)
        if self.pricelist_link != None:
            for link in self.pricelist_link:
                Validator.Link(link)
        
    def toJSON(self,keepPriceList=False):            
        self.__reValidInfo(keepPriceList) 
        services_tmp = None
        if self.services != None:
            services_tmp = []
        else: 
            self.services = []
        for serv in self.services:
            services_tmp.append(serv.toOrederdDict())
            
        order = OrderedDict([('name', self.name), ('scrape_page', self.scrape_page), ('street', self.street), ('city', self.city), 
                             ('zipcode', self.zipcode), ('country', self.country), ('latitude', self.latitude), ('longitude', self.longitude), 
                             ('formatted_address', self.formatted_address), ('business_email', self.business_email), ('business_website', self.business_website), 
                             ('office_number', self.office_number), ('mobile_number', self.mobile_number), ('office_number2', self.office_number2), 
                             ('mobile_number2', self.mobile_number2), ('unidentified_phone_numbers', self.unidentified_phone_numbers), ('opening_hours_raw', self.opening_hours_raw), 
                             ('facebook_page', self.facebook_page), ('yelp_page', self.yelp_page), ('pricelist_link', self.pricelist_link), 
                             ('description', self.description),('specialty',self.specialty), ('services', services_tmp)])
        
        return json.dumps(order, default=lambda o: o.__dict__, indent=4)
        
        
    def writeToFile(self, folder, index, spec=False,keepPriceList=False):
        try:
            index = '%0*d' % (5, index) 
            outputFile = folder + "/" + index + "_" + self.name + ".json"
            if spec == True:
                with codecs.open(outputFile, "w", encoding='utf-8') as f:
                    f.write(unicode(self.toJSON(keepPriceList)).encode("utf8"))
            else:
                with io.open(outputFile, 'w',encoding='utf-8') as f:
                    f.write(self.toJSON(keepPriceList).decode('unicode-escape'))
        except BaseException as ex:
            print ('Error when write json file: ', ex)
            raise

    def getFullAddress(self):            
        if self.street != None and self.street.strip() != "":
            self.formatted_address = self.street
        if self.city != None and self.city.strip() != "":
            if self.formatted_address == None:
                self.formatted_address = self.city
            else: self.formatted_address += ", " + self.city
        if self.zipcode != None and self.zipcode.strip() != "":
            if self.formatted_address == None:
                self.formatted_address = self.zipcode
            else: self.formatted_address += ", " + self.zipcode        
        if self.formatted_address != None and self.formatted_address.strip() == "":
            self.formatted_address = None            

class Service(object):
    
    service = None
    description = None
    price = None
    service_category = None
    duration = None
    
    def __init__(self):    
        ''
        
    def __reValidInfo(self):
        self.service = Validator.ReValidString(self.service)
        self.description = Validator.ReValidString(self.description)
        self.service_category = Validator.ReValidString(self.service_category)
        self.duration = Validator.ReValidString(self.duration)
        self.price = Validator.ReValidPrice(self.price)

        
    def toOrederdDict(self):
        self.__reValidInfo()
        order = OrderedDict([('service',
        self.service),('description',self.description),('price', self.price),
                            ('service_category',self.service_category),('duration',self.duration)])        
        return order 