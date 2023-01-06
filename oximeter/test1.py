import random
import threading
def t1():
    global datalist
    datalist=[]
    while True:
        datalist.append((random.randint(0,200),random.randint(0,200),random.randint(0,200)))
        #print("t1",len(datalist))  
def t2():
    global datalist
    kk=0
    while True:
        if datalist!=[] and kk<len(datalist):
            print("t2",len(datalist),kk)  
            kk=kk+1
if __name__=="__main__":
    threading.Thread(target=t1,args=()).start()
    threading.Thread(target=t2,args=()).start()
