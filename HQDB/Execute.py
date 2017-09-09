import sys
import threading

import requests

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
   
    print "DONE"
    
if __name__ == '__main__':
    main()
    
    
    
    
    #string_ = 'The Guildhall, Street-an-Pol, St Ives, Cornwall, Tr138xq'
    #print string_[0:string_.find('St Ives')-1]
#    a ='00000100000000'
#    a= int(a)
#    print str(len(str(a)))
   

        
   
