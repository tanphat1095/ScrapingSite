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
    working.do(["", "url=https://www.unbiased.co.uk/"]) #374
    #working.do(["", "url=http://www.accaglobal.com/uk/en/member/find-an-accountant/find-firm.html"]) #373
    #working.do(["", "url=https://www.meilleur-garagiste.com"]) #387
    #working.do(["", "url=http://www.drivingschoolsfinder.co.uk/"]) # 391
    #working.do(["", "url=http://www.architecturalindex.com/"]) #399
    #working.do(["", "url=https://www.blauarbeit.de"]) #406
    #working.do(["", "url=https://yoganearby.com"]) #417
    print "DONE"



def loops(threadname):
    for i in range(0,10):
        
        print 'Thread: '+threadname+ ' '+str(i)
        time.sleep(0.2)
        
def test(country):
    listchar =[]
    for i in range(0,10) + [chr(x) for x in range(ord('a'), ord('z')+1)]:
        listchar.append(str(i))
    result = country+': '+ ','.join(listchar)
    files=  open('D:\\multitest.txt','a')
    files.write(result+'\r\n')
    files.close()
    print result+'\n'
    return result
def parse_(string):
    try:
        return int(string)
    except Exception, ex:
        print 'Ex1'
def cfscrape(url):
    scraper = cfscrape.create_scraper()
if __name__ == '__main__':
    #clickleft(103,164)
    main()
                              
                                   
