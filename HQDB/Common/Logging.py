import logging


class Log(object):

    def __init__(self, site_name, folder_out=""):
        file_out = site_name + '/' + folder_out + ".txt"
        #if folder_out != "":
        #    file_out = folder_out + "/" + file_out
            
        logging.basicConfig(filename=file_out, level=logging.INFO)
    
    
    def logResult(self, field, msg, isValid):
        if isValid == False:
            self.invalid(field, msg)
        #else:
        #   self.valid(field, value)
        
    
    def info(self, msg):
        logging.info(msg)
    
    
    def error(self, msg):
        logging.error(msg)
        
    
    def valid(self, field, msg):
        #msg = " - Validate " + field + ": <" + value + "> is VALID"
        logging.info(msg)  
        
        
    def invalid(self, field, msg):
        #msg = " - Validate " + field + ": <" + value + "> is INVALID"
        logging.error(msg)   
        
            