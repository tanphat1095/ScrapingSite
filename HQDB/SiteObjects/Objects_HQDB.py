# coding: utf-8
from __future__ import unicode_literals
import io
import json
from collections import OrderedDict
import Common.Validation as Validator
from Common import Util
import codecs
 
class Venue(object):    
    adid = None
    name = None
    name_of_contact = None    
    business_website = None
    areas_covered = None
    formatted_address = None
    description = None
    img_link = None
    hqdb_featured_ad_type = None
    hqdb_nr_reviews = None
    hqdb_review_score = None    
    accreditations = None
    scrape_page = None
    category = None
    subcategory = None
    street = None
    city = None
    zipcode = None
    country = None
    office_number = None
    office_number2 = None
    mobile_number = None
    mobile_number2 = None
    unidentified_phone_numbers = None
    latitude = None
    longitude = None
    business_email = None
    yelp_page = None
    facebook = None
    twitter = None
    instagram = None
    venue_images = None
    opening_hours_raw = None
    pricelist_link = None
    services = None
    
    def __init__(self):        
        ''       
    
    def __reValidInfo(self):               
        self.adid = Validator.ReValidString(self.adid)
        self.name = Validator.ReValidString(self.name)
        self.name_of_contact = Validator.ReValidString(self.name_of_contact)        
        self.business_website = Validator.RevalidURL(self.business_website)
        self.areas_covered = Validator.ReValidString(self.areas_covered)
        self.formatted_address = Validator.ReValidString(self.formatted_address)
        self.description = Validator.ReValidString(self.description)
        if self.img_link != None and len(self.img_link) > 0:
            self.img_link = [Validator.RevalidURL(x) for x in self.img_link]
            self.img_link = '[' + ', '.join(self.img_link) + ']'
        if self.img_link != None and len(self.img_link) == 0:
            self.img_link = None
        if self.hqdb_featured_ad_type != None and len(self.hqdb_featured_ad_type) > 0:
            self.hqdb_featured_ad_type = ['"' + Validator.ReValidString(x.lower()) + '"' for x in self.hqdb_featured_ad_type]
            self.hqdb_featured_ad_type = '[' + ', '.join(self.hqdb_featured_ad_type) + ']'
        elif self.hqdb_featured_ad_type != None and len(self.hqdb_featured_ad_type) == 0:
            self.hqdb_featured_ad_type = None
        self.hqdb_nr_reviews = Validator.ReValidString(self.hqdb_nr_reviews)
        self.hqdb_review_score = Validator.ReValidString(self.hqdb_review_score)
        self.accreditations = Validator.ReValidString(self.accreditations)
        self.scrape_page = Validator.RevalidURL(self.scrape_page)
        self.category = Validator.ReValidString(self.category)
        self.subcategory = Validator.ReValidString(self.subcategory)
        self.street = Validator.ReValidString(self.street)
        self.city = Validator.ReValidString(self.city)
        type = 'phone'
        if self.country == 'pl':
            type = 'pl'
        self.zipcode = Validator.ReValidPhone(self.zipcode,type)        
        self.country = Validator.ReValidString(self.country)
        self.office_number = Validator.ReValidPhone(self.office_number)
        self.mobile_number = Validator.ReValidPhone(self.mobile_number)
        self.office_number2 = Validator.ReValidPhone(self.office_number2)
        self.mobile_number2 = Validator.ReValidPhone(self.mobile_number2)          
        if self.unidentified_phone_numbers != None and len(self.unidentified_phone_numbers) > 0:
            self.unidentified_phone_numbers = [Validator.ReValidPhone(x).strip() for x in self.unidentified_phone_numbers]
            self.unidentified_phone_numbers = '[' + ", ".join(self.unidentified_phone_numbers) + ']'
        elif self.unidentified_phone_numbers != None and len(self.unidentified_phone_numbers) == 0:
            self.unidentified_phone_numbers = None
        self.latitude = Validator.ReValidString(self.latitude)
        self.longitude = Validator.ReValidString(self.longitude)
        self.business_email = Validator.RevalidEmail(Validator.ReValidString(self.business_email))
        self.yelp_page = Validator.RevalidURL(self.yelp_page)
        self.facebook = Validator.RevalidURL(self.facebook)
        self.twitter = Validator.RevalidURL(self.twitter)
        self.instagram = Validator.RevalidURL(self.instagram)
        self.venue_images = Validator.ReValidString(self.venue_images)        
        if Validator.ValidateGeoCode(self.formatted_address,self.country,self.latitude,self.longitude) == False:            
            Util.log.invalid('GEO code',self.scrape_page + ': invalid GEO code (' + self.latitude + ',' + self.longitude + ')')
            self.latitude = None
            self.longitude = None
        self.opening_hours_raw = Validator.ReValidString(self.opening_hours_raw)
    
    def getFullAddress(self):            
        if self.street != None and self.street.strip() != "":            
            self.formatted_address = self.street
        if self.city != None and self.city.strip() != "":
            if self.formatted_address == None:
                self.formatted_address = self.city
            else: 
                self.formatted_address = self.formatted_address.strip()
                self.formatted_address += ", " + self.city
        if self.zipcode != None and self.zipcode.strip() != "":
            if self.formatted_address == None:
                self.formatted_address = self.zipcode
            else: 
                self.formatted_address = self.formatted_address.strip()
                self.formatted_address += ", " + self.zipcode
        if self.formatted_address != None and self.formatted_address.strip() == "":
            self.formatted_address = None                    

                          
    def __reValidInfoJSON(self):
        self.adid = Validator.ReValidString(self.adid)
        self.name = Validator.ReValidString(self.name)
        self.name_of_contact = Validator.ReValidString(self.name_of_contact)        
        self.business_website = Validator.RevalidURL(self.business_website)
        self.areas_covered = Validator.ReValidString(self.areas_covered)
        self.formatted_address = Validator.ReValidString(self.formatted_address)
        self.description = Validator.ReValidString(self.description)
        if self.img_link != None and len(self.img_link) == 0:
            self.img_link = None
        self.hqdb_featured_ad_type = Validator.ReValidString(self.hqdb_featured_ad_type)
        self.hqdb_nr_reviews = Validator.ReValidString(self.hqdb_nr_reviews)
        self.hqdb_review_score = Validator.ReValidString(self.hqdb_review_score)        
        self.accreditations = Validator.ReValidString(self.accreditations)        
        self.category = Validator.ReValidString(self.category)
        self.subcategory = Validator.ReValidString(self.subcategory)
        self.street = Validator.ReValidString(self.street)
        self.city = Validator.ReValidString(self.city)
        type = 'phone'
        if self.country == 'pl':
            type = 'pl'
        self.zipcode = Validator.ReValidPhone(self.zipcode,type)       
        self.country = Validator.ReValidString(self.country)
        self.getFullAddress()
        self.formatted_address = Validator.ReValidString(self.formatted_address)	
        if self.formatted_address != None:
            self.formatted_address = self.formatted_address.replace(',,',',')
        self.office_number = Validator.ReValidPhone(self.office_number)
        self.mobile_number = Validator.ReValidPhone(self.mobile_number)
        self.office_number2 = Validator.ReValidPhone(self.office_number2)
        self.mobile_number2 = Validator.ReValidPhone(self.mobile_number2)          
        if self.unidentified_phone_numbers != None and len(self.unidentified_phone_numbers) > 0:
            self.unidentified_phone_numbers = [Validator.ReValidPhone(x).strip() for x in self.unidentified_phone_numbers]
        elif self.unidentified_phone_numbers != None and len(self.unidentified_phone_numbers) == 0:
            self.unidentified_phone_numbers = None
        self.latitude = Validator.ReValidString(self.latitude)
        self.longitude = Validator.ReValidString(self.longitude)
        self.business_email = Validator.RevalidEmail(Validator.ReValidString(self.business_email))
        self.yelp_page = Validator.RevalidURL(self.yelp_page)
        self.facebook = Validator.RevalidURL(self.facebook)
        self.twitter = Validator.RevalidURL(self.twitter)
        self.instagram = Validator.RevalidURL(self.instagram)
        self.venue_images = Validator.ReValidString(self.venue_images)        
        if Validator.ValidateGeoCode(self.formatted_address,self.country,self.latitude,self.longitude) == False:            
            Util.log.invalid('GEO code',self.scrape_page + ': invalid GEO code (' + self.latitude + ',' + self.longitude + ')')
            self.latitude = None
            self.longitude = None
        self.opening_hours_raw = Validator.ReValidString(self.opening_hours_raw)

    
    def validate(self):
        Util.log.info("----------------------- Validating Venue: " + self.name)
        Validator.CityZipcode(self.city, self.zipcode)
        Validator.Country(self.country)
        Validator.LatitudeLongitute(self.latitude, self.longitude, self.city, self.zipcode)
        Validator.Email(self.business_email)
        Validator.Link(self.business_business_website)
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
        
    def toOrderDict(self):            
        self.__reValidInfo()             
        order = OrderedDict([('adid',self.adid),
                             ('name',self.name),
                             ('name_of_contact',self.name_of_contact),                             
                             ('business_website',self.business_website),
                             ('areas_covered',self.areas_covered),
                             ('formatted_address',self.formatted_address),
                             ('description',self.description),
                             ('img_link',self.img_link),
                             ('hqdb_featured_ad_type',self.hqdb_featured_ad_type),
                             ('hqdb_nr_reviews',self.hqdb_nr_reviews),
                             ('hqdb_review_score',self.hqdb_review_score),                             
                             ('accreditations',self.accreditations),
                             ('scrape_page',self.scrape_page),
                             ('category',self.category),
                             ('subcategory',self.subcategory),
                             ('street',self.street),
                             ('city',self.city),
                             ('zipcode',self.zipcode),
                             ('country',self.country),
                             ('office_number',self.office_number),
                             ('office_number2', self.office_number2), 
                             ('mobile_number',self.mobile_number),                             
                             ('mobile_number2', self.mobile_number2),
                             ('unidentified_phone_numbers', self.unidentified_phone_numbers),
                             ('latitude',self.latitude),
                             ('longitude',self.longitude),
                             ('business_email',self.business_email),
                             ('yelp_page',self.yelp_page),
                             ('facebook',self.facebook),
                             ('twitter',self.twitter),
                             ('instagram',self.instagram),
                             ('venue_images',self.venue_images),
                             ('opening_hours_raw',self.opening_hours_raw)])        
        return order
    
    def toJSON(self):            
        self.__reValidInfoJSON() 
        services_tmp = []
        if self.services != None and len(self.services) > 0:
            services_tmp = []
            for serv in self.services:
                services_tmp.append(serv.toOrderDict())
        else: 
            services_tmp = [{}]    
            self.pricelist_link = None   
            
        order = OrderedDict([('adid',self.adid),
                             ('name',self.name),
                             ('name_of_contact',self.name_of_contact), 
                             ('scrape_page',self.scrape_page),                            
                             ('business_website',self.business_website),
                             ('areas_covered',self.areas_covered),                             
                             ('description',self.description),
                             ('img_link',self.img_link),
                             ('hqdb_featured_ad_type',self.hqdb_featured_ad_type),
                             ('hqdb_nr_reviews',self.hqdb_nr_reviews),
                             ('hqdb_review_score',self.hqdb_review_score),                             
                             ('accreditations',self.accreditations),                             
                             ('category',self.category),
                             ('subcategory',self.subcategory),
                             ('street',self.street),
                             ('city',self.city),
                             ('zipcode',self.zipcode),
                             ('formatted_address',self.formatted_address),
                             ('country',self.country),
                             ('office_number',self.office_number),
                             ('office_number2', self.office_number2), 
                             ('mobile_number',self.mobile_number),                             
                             ('mobile_number2', self.mobile_number2),
                             ('unidentified_phone_numbers', self.unidentified_phone_numbers),
                             ('latitude',self.latitude),
                             ('longitude',self.longitude),
                             ('business_email',self.business_email),
                             ('yelp_page',self.yelp_page),
                             ('facebook',self.facebook),
                             ('twitter',self.twitter),
                             ('instagram',self.instagram),
                             ('venue_images',self.venue_images),
                             ('opening_hours_raw',self.opening_hours_raw),
                             ('pricelist_link',self.pricelist_link),
                             ('services',services_tmp)])
        
        return json.dumps(order, default=lambda o: o.__dict__, indent=4)

    def writeToFile(self,folder, index, filename,spec=False):
        try:
            if filename != None:
                filename = Validator.RevalidName(filename)
            index = '%0*d' % (7, index) 
            outputFile = folder + "/" + index + "_" + filename + ".json"
            if spec == True:
                with codecs.open(outputFile, "w", encoding='utf-8') as f:
                    f.write(unicode(self.toJSON()).encode("utf8"))
            else:
                with io.open(outputFile, 'w',encoding='utf-8') as f:
                    f.write(self.toJSON().decode('unicode-escape'))
        except BaseException as ex:
            print ('Error when write json file: ', ex)
            raise      
        
class Service(object):    
    
    service_category = None
    service = None
    duration = None
    price = None
    description = None      
    
    def __init__(self):    
        ''
        
    def __reValidInfo(self):        
        self.service = Validator.ReValidString(self.service)
        self.description = Validator.ReValidString(self.description)
        self.service_category = Validator.ReValidString(self.service_category)

        
    def toOrderDict(self):
        self.__reValidInfo()
        order = OrderedDict([('service_category',self.service_category),
                             ('service',self.service),
                             ('duration',self.duration),
                             ('price', self.price),
                             ('description',self.description)])        
        return order 