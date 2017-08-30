import importlib
from urlparse import urlparse

class Working(object):

    __help = '''
    Input:
        - URL (string): url of site need scraping (REQUIRED)
        - Out (string): Output folder (By default is the same with this file)
        - Exp (boolean): Export list Venues to file xml/txt as Script1 (Default is false)
        
        Example: url=http://www.cottet.es/ out="C:\output"
 
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
    
    def do(self, args):
        if (len(args) < 2 or "url=" not in args[1]):
            print "Missing required argument: URL"
            print help
            return
        
        '''
            Some other check here
        '''
       
        url = args[1].split("=")[1]
        (module_name, class_name) = self.__getScraptedPage(url)
        self.__start(module_name, class_name)
        
        
    def __start(self, module_name, class_name):
        class_ = getattr(importlib.import_module(module_name), class_name)
        instance = class_()
        instance.doWork()
    
    def __getScraptedPage(self, url):
        parsedUrl = urlparse(url)

        # Read ScrapedSites.txt to get list information
        with open('Data/ScrapedSites.txt') as f:
            sites = f.read().splitlines()
        x = parsedUrl.netloc
        site = [s for s in sites if x in s]
        
        if  len(site) != 1:
            print "The url '" + url + "' is not scraped."
            raise
            
        info = site[0].split(";")
        return (info[1].strip(), info[2].strip())