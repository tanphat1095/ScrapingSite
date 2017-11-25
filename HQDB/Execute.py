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
    working.do(["", "url=http://es.qdq.com"]) #422
    print "DONE"

def checkDup():
    list__  =[]
    list_ = [1,2,3,4,5,6,7,8,9,1,2,3,4,5,6,7,8,9,1,3,5,7,9]
    for i in range(0,len(list_)):
        for j in range(i+1,len(list_)):
            if list_[i] == list_[j]:
                list__.append(list_[j])
    for a in list__:
        list_.remove(a)
    print str(list_)

if __name__ == '__main__':
    main()
    
    #checkDup()
                              
                                   
