from Common import Util
from Common.Logging import Log

class BaseSite(object):

    _lstVenues = [] 
    
    def __init__(self, output, name):
        self.folder = Util.createFolder(output, name)
        log = Log(self.folder, name)
        Util.log = log
        
        
    def doWork(self):
        ''
    