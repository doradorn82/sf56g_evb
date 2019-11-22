import clr
import os
import platform
from time import time, sleep

def get_dll_path():
    dll_path = os.environ['SF56G_EVB_PATH'] + '/dll'
    if '32bit' in platform.architecture()[0]:
        dll_path += '/x86'
    else:
        dll_path += '/x64'
    return dll_path


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
