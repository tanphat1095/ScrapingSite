import sys
import threading
from Common import Util
import requests
import threading
import time
from Common.Working import Working



index_ = 0
def main():
    '''
    Input:
        - URL (string): url of site need scraping (REQUIRED)
        - Out (string): Output folder (By default is the same with this file)
        - Exp (boolean): Export list Venues to file xml/txt as Script1 (Default is false)        
        Example: url=http://www.cottet.es/ out="C:\output"
 
    '''
    print "Scraping..."
    working = Working()
    #working.do(sys.argv) #Comment this line then uncomment line below, if you want to run in Eclipse/PythonIDE
    #working.do(["", "url=https://www.gumtree.com"])
    #working.do(["", "url=https://www.unbiased.co.uk/"]) #374
    #working.do(["", "url=http://www.accaglobal.com/uk/en/member/find-an-accountant/find-firm.html"]) #373
    #working.do(["", "url=https://www.meilleur-garagiste.com"]) #387
    #working.do(["", "url=http://www.drivingschoolsfinder.co.uk/"]) # 391
    #working.do(["", "url=http://www.architecturalindex.com/"]) #399
    #working.do(["", "url=https://www.blauarbeit.de"]) #406
    #working.do(["", "url=https://yoganearby.com"]) #417
    #working.do(["", "url=http://es.qdq.com"]) #422
    #working.do(["", "url=http://www.garagesandrecovery.co.uk"])   #427
    #working.do(["", "url=http://www.uksecurity-directory.co.uk"])   #431 
    #working.do(["", "url=http://www.computer-systems-uk.co.uk"]) #436
    #working.do(["", "url=http://www.serrurier-a-paris.info"]) #440
    #working.do(["", "url=http://www.vet-look.ch"]) #442
    #working.do(["", "url=https://osteofrance.com"]) #443
    #working.do(["", "url=http://www.hondentrimsalon.nl"]) #449
    working.do(["", "url=http://www.computer-repairs-maintenance.co.uk"]) #450
    print "DONE"


if __name__ == '__main__':
    dict = {'1':'a','3':'a'}
    dict['2'] = 'd'
    print dict
    dict.pop('1')
    print dict
    
    
    
    main()
    
    #checkDup()
                              
                                   
