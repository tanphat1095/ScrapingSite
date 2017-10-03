
import threading
import time

exitFlag = 0

class myThread (threading.Thread):
    index_ =0
    
    
    
    def print_(self,threadname):
        for i in range(10):
            self.index_+=1
            print 'Thread : '+ str(i)+'-'+str(self.index_)
    for i in range(3):
        thread1 = threading.Thread(target=print_, args=(i,))
        thread1.start()