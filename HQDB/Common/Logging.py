import logging
from logging import FileHandler
from logging import Formatter


class Log(object):
    """Create Running Logging and Coordinate Loggin"""
    #Defind log level
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '[%(levelname)s]: %(message)s'
    #Define running log file
    RUNNING_LOG_FILE = ""
    running_logger = None
    running_logger_file_handler = None
    #Define coordinate log file
    COORDINATE_LOG_FILE = ""
    coordinate_logger = None
    coordinate_logger_file_handler = None
    

    def __init__(self, site_name, folder_out=""):                
        #Create Running Logger
        self.RUNNING_LOG_FILE = site_name + '/' + folder_out + "_Running.log" 
        self.running_logger = logging.getLogger(folder_out + "." + folder_out + "_Running")
        self.running_logger.setLevel(self.LOG_LEVEL)
        self.running_logger_file_handler = FileHandler(self.RUNNING_LOG_FILE)
        self.running_logger_file_handler.setLevel(self.LOG_LEVEL)   
        self.running_logger_file_handler.setFormatter(Formatter(self.LOG_FORMAT))     
        self.running_logger.addHandler(self.running_logger_file_handler)
        
        #Create Coordinate Logger
        self.COORDINATE_LOG_FILE = site_name + '/' + folder_out + "_Coordinate.log"       
        self.coordinate_logger = logging.getLogger(folder_out + "." + folder_out + "_Coordinate")
        self.coordinate_logger.setLevel(self.LOG_LEVEL)
        self.coordinate_logger_file_handler = FileHandler(self.COORDINATE_LOG_FILE)
        self.coordinate_logger_file_handler.setLevel(self.LOG_LEVEL)
        self.coordinate_logger_file_handler.setFormatter(Formatter(self.LOG_FORMAT))     
        self.coordinate_logger.addHandler(self.coordinate_logger_file_handler)
    
        
            