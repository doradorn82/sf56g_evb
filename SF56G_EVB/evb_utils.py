import clr
import os
from time import time, sleep

def add_evb_dll():
    dllpath = os.environ['SF56G_EVB_PATH'] + '/dll'
    clr.AddReference(dllpath+"/LibEVB.dll")

def get_evb_path():
    return os.environ['SF56G_EVB_PATH']

def functime_dec(func):
    def decorator(*args,**kargs):
        start = time()
        result = func(*args,**kargs)
        print ("[%s] processing time=%3.2fs" % (func.__name__,(time()-start)))
        return result
    return decorator

def Delay(ms):
    if ms != 0:
        sleep(ms*1e-3)
